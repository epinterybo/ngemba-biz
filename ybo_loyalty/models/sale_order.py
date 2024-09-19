from collections import defaultdict
from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.tools.float_utils import float_is_zero, float_round
from odoo.exceptions import UserError, ValidationError
import logging
from pprint import pformat

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_loyalty_card_id(self, order_id):
        """
        Returns the ID of the loyalty.card associated with the given sale.order ID.

        :param order_id: ID of the sale.order
        :return: Object of the loyalty.card or None if not found
        """
        order = self.browse(order_id.id)
        if order.coupon_point_ids:
            # Filter coupon_point_ids where the state is not expired
            valid_coupon_points = order.coupon_point_ids.filtered(lambda cp: cp.coupon_id.state != 'expired')
            if valid_coupon_points:
                return valid_coupon_points[0].coupon_id
        return None

    def action_confirm(self):
        # Call the original action_confirm method
        res = super(SaleOrder, self).action_confirm()

        # Iterate through each sale order
        for order in self:
            # Check if there are any coupon points entries
            if order.coupon_point_ids:
                # Iterate through each coupon points entry
                for coupon_point in order.coupon_point_ids:
                    program_id = coupon_point.coupon_id.program_id
                    # Check if the current product of the sale.order.line exists in the product selected for the loyalty rule
                    for line in order.order_line:
                        if line.product_id in program_id.rule_ids.mapped('product_ids'):
                            coupon_point.coupon_id.add_points(line.price_unit)

        return res

    def _get_claimable_rewards(self, forced_coupons=None):
        """
               Fetch all rewards that are currently claimable from all concerned coupons,
               meaning coupons from applied programs and applied rewards or the coupons given as parameter.

               Returns a dict containing the all the claimable rewards grouped by coupon.
               Coupons that can not claim any reward are not contained in the result.
               """
        self.ensure_one()
        all_coupons = forced_coupons or (
                self.coupon_point_ids.coupon_id | self.order_line.coupon_id | self.applied_coupon_ids)
        has_payment_reward = any(line.reward_id.program_id.is_payment_program for line in self.order_line)
        total_is_zero = float_is_zero(self.amount_total, precision_digits=2)
        result = defaultdict(lambda: self.env['loyalty.reward'])
        global_discount_reward = self._get_applied_global_discount()
        for coupon in all_coupons:
            points = self._get_real_points_for_coupon(coupon)
            total_points = coupon.total_points  # Fetch the total points of the coupon/loyalty card
            # Fetch the claimed rewards for this loyalty card (coupon)
            claimed_rewards = self.env['ybo.loyalty.reward.claim'].search([
                ('card_id', '=', coupon.id)
            ]).mapped('reward_id')
            for reward in coupon.program_id.reward_ids:
                # Check if the reward has been claimed, skip it if it has been claimed
                if reward in claimed_rewards:
                    continue  # Skip already claimed rewards

                if reward.is_global_discount and global_discount_reward and global_discount_reward.discount >= reward.discount:
                    continue

                # Discounts are not allowed if the total is zero unless there is a payment reward
                if reward.reward_type == 'discount' and total_is_zero and (
                        not has_payment_reward or reward.program_id.is_payment_program):
                    continue

                # New condition: Check if total points are greater than or equal to allowed total points
                if points >= reward.required_points and total_points >= reward.allowed_total_points:
                    result[coupon] |= reward  # Add the reward to the result if it meets the criteria

        return result

    def _try_apply_code(self, code):
        """
        Tries to apply a promotional code to the sales order.
        It can be either from a coupon or a program rule.

        Returns a dict with the following possible keys:
         - 'not_found': Populated with True if the code did not yield any result.
         - 'error': Any error message that could occur.
         OR The result of `_get_claimable_rewards` with the found or newly created coupon, it will be empty if the coupon was consumed completely.
        """
        self.ensure_one()

        base_domain = self._get_trigger_domain()
        domain = expression.AND([base_domain, [('mode', '=', 'with_code'), ('code', '=', code)]])
        rule = self.env['loyalty.rule'].search(domain)
        program = rule.program_id
        coupon = False

        if rule in self.code_enabled_rule_ids:
            return {'error': _('This promo code is already applied.')}

        # No trigger was found from the code, try to find a coupon
        if not program:
            # Try to find a coupon with the same code
            coupon = self.env['loyalty.card'].search([('code', '=', code)])
            if not coupon or \
                    not coupon.program_id.active or \
                    not coupon.program_id.reward_ids or \
                    not coupon.program_id.filtered_domain(self._get_program_domain()):
                return {'error': _('This code is invalid (%s).', code), 'not_found': True}
            elif coupon.expiration_date and coupon.expiration_date < fields.Date.today() or coupon.state == 'expired':
                return {'error': _('This coupon is expired.')}
            elif coupon.points < min(coupon.program_id.reward_ids.mapped('required_points')):
                return {'error': _('Sufficient points are required to redeem this coupon.')}

            program = coupon.program_id
        if not program or not program.active:
            return {'error': _('This code is invalid (%s).', code), 'not_found': True}
        elif (program.limit_usage and program.total_order_count >= program.max_usage):
            return {'error': _('This code is expired (%s).', code)}

        # Rule will count the next time the points are updated
        if rule:
            self.code_enabled_rule_ids |= rule
        program_is_applied = program in self._get_points_programs()
        # Condition that need to apply program (if not applied yet):
        # current -> always
        # future -> if no coupon
        # nominative -> non blocking if card exists with points
        if coupon:
            self.applied_coupon_ids += coupon
        if program_is_applied:
            # Update the points for our programs, this will take the new trigger in account
            self._update_programs_and_rewards()
        elif program.applies_on != 'future' or not coupon:
            apply_result = self._try_apply_program(program, coupon)
            if 'error' in apply_result and (not program.is_nominative or (program.is_nominative and not coupon)):
                if rule:
                    self.code_enabled_rule_ids -= rule
                if coupon and not apply_result.get('already_applied', False):
                    self.applied_coupon_ids -= coupon
                return apply_result
            coupon = apply_result.get('coupon', self.env['loyalty.card'])
        return self._get_claimable_rewards(forced_coupons=coupon)
