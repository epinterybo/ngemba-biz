from odoo import _, api, fields, models
import logging
from pprint import pformat

_logger = logging.getLogger(__name__)


class LoyaltyCard(models.Model):
    _inherit = ['loyalty.card']

    reward_ids = fields.One2many('ybo.loyalty.reward.claim', 'card_id', string='Claimed Rewards')
    total_points = fields.Float(string='Total Points')
    state = fields.Selection(
        [
            ('active', 'Active'),
            ('expired', 'Expired'),
        ],
        default="active", string='State')

    def add_points(self, points):
        self.total_points += points

    def create_new_loyalty_card(self, order):
        """
        Create a new loyalty.card object if there are no active ones.
        The new loyalty.card object is based on the last expired one.
        """
        active_coupon_ids = self.env['loyalty.card'].search([
            ('partner_id', '=', order.partner_id.id),
            ('state', '=', 'active')
        ])

        if not active_coupon_ids:
            last_expired_coupon = self.env['loyalty.card'].search([
                ('partner_id', '=', order.partner_id.id),
                ('state', '=', 'expired')
            ], order='expiration_date', limit=1)

            program_id = last_expired_coupon.program_id
            _logger.info(f"\n PROGRAM COUPON IDS BEFORE: {program_id.coupon_ids}")

            total_price = sum(line.price_unit for line in order.order_line if
                              line.product_id in program_id.rule_ids.mapped('product_ids'))
            _logger.info(f"\n TOTAL PRICE: {total_price}")
            if last_expired_coupon:
                new_coupon = self.create({
                    'program_id': last_expired_coupon.program_id.id,
                    'partner_id': last_expired_coupon.partner_id.id,
                    'points': total_price,
                    'total_points': total_price,
                    'code': self._generate_code(),
                    'state': 'active',
                    'order_id': order.id,
                    'create_date': fields.Datetime.now(),
                    'create_uid': last_expired_coupon.create_uid.id,
                    'write_date': fields.Datetime.now(),
                    'write_uid': last_expired_coupon.write_uid.id,
                })
                _logger.info(f"\n PROGRAM COUPON IDS AFTER: {program_id.coupon_ids}")
                _logger.info(f"\n NEW COUPON CREATED: {new_coupon}")
                new_coupon_point = self.env['sale.order.coupon.points'].create({
                    'order_id': order.id,
                    'coupon_id': new_coupon.id,
                    'points': total_price,
                    'create_date': fields.Datetime.now(),
                    'write_date': fields.Datetime.now(),
                    'create_uid': self.env.user.id,
                    'write_uid': self.env.user.id,
                })
                _logger.info(f"\n NEW COUPON POINTS CREATED: {new_coupon_point}")
                return new_coupon_point
        return None