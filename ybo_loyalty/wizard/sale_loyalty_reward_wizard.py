# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
import logging
from pprint import pformat

_logger = logging.getLogger(__name__)


class SaleLoyaltyRewardWizard(models.TransientModel):
    _inherit = ['sale.loyalty.reward.wizard']
    reward_ids = fields.Many2many('loyalty.reward', compute='_compute_claimable_reward_ids')

    @api.depends('order_id')
    def _compute_claimable_reward_ids(self):
        # super(SaleLoyaltyRewardWizard, self)._compute_claimable_reward_ids()
        for wizard in self:
            if not wizard.order_id:
                wizard.reward_ids = False
            else:
                claimed_rewards = []
                loyalty_card = self.env['sale.order'].get_loyalty_card_id(wizard.order_id)
                # Fetch the claimed rewards for the loyalty card
                # for coupon_point in wizard.order_id.coupon_point_ids:
                if loyalty_card:
                    claimed_rewards = self.env['ybo.loyalty.reward.claim'].search([
                        ('card_id', '=', loyalty_card.id)
                    ]).mapped('reward_id')
                _logger.info(pformat(claimed_rewards))
                # Exclude claimed rewards
                wizard.reward_ids = wizard.reward_ids - claimed_rewards

    def action_apply(self):
        # Call the original Odoo logic using super
        res = super(SaleLoyaltyRewardWizard, self).action_apply()
        loyalty_card = self.env['sale.order'].get_loyalty_card_id(self.order_id)

        reward_line = self.order_id.order_line.filtered(lambda line: line.reward_id == self.selected_reward_id)

        if reward_line:
            quantity_redeemed = reward_line.product_uom_qty
        else:
            _logger.error(f"NO QUANTITY FOUND !!!!!!")
            quantity_redeemed = 0

        # After applying the reward, save the claim to the custom model
        self.env['ybo.loyalty.reward.claim'].create({
            'card_id': loyalty_card.id,
            'quantity_redeemed': quantity_redeemed,
            'reward_id': self.selected_reward_id.id,
            'sale_order_id': self.order_id.id,
            'claim_date': fields.Datetime.now(),
        })

        # Call the new method to compare rewards and update the card
        self.compare_rewards_and_update_card(loyalty_card)

        return res

    def compare_rewards_and_update_card(self,loyalty_card):

        claimed_rewards = self.env['ybo.loyalty.reward.claim'].search([
            ('card_id', '=', loyalty_card.id),
        ])
        claimable_rewards = self.env['loyalty.reward'].search([
            ('program_id', '=', loyalty_card.program_id.id),
        ])

        # Create sets of reward IDs for easy comparison
        claimed_reward_ids = set(claimed_rewards.mapped('reward_id.id'))
        claimable_reward_ids = set(claimable_rewards.mapped('id'))

        # Check if all claimable rewards have been claimed
        all_claimed = claimed_reward_ids == claimable_reward_ids

        # Check if any reward has been claimed more than once
        duplicate_claims = any(
            len(claimed_rewards.filtered(lambda r: r.reward_id.id == reward_id)) > 1
            for reward_id in claimed_reward_ids
        )

        if all_claimed and not duplicate_claims:
            loyalty_card.write({
                'state': "expired",
                'expiration_date': fields.Date.today(),
            })
            _logger.info(f"Loyalty card {loyalty_card.id} deactivated. All rewards have been claimed exactly once.")
        else:
            if not all_claimed:
                _logger.info(f"Loyalty card {loyalty_card.id} remains active. Not all rewards have been claimed.")
            if duplicate_claims:
                _logger.warning(
                    f"Loyalty card {loyalty_card.id} has duplicate claims. This should be handled elsewhere.")

        _logger.info(f"Claimed reward IDs: {claimed_reward_ids}")
        _logger.info(f"Claimable reward IDs: {claimable_reward_ids}")