from odoo import models, fields
import logging
from pprint import pformat

_logger = logging.getLogger(__name__)

class YBOLoyaltyRewardClaim(models.Model):
    _name = 'ybo.loyalty.reward.claim'
    _description = 'Track claimed rewards by users'

    card_id = fields.Many2one('loyalty.card', string='Loyalty Card', required=True)
    reward_id = fields.Many2one('loyalty.reward', string='Reward', required=True)
    points_earned = fields.Float(string='Points Earned')
    quantity_redeemed = fields.Float(string='Quantity Redeemed')
    claim_date = fields.Date(string='Claim Date', default=fields.Date.today, required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)

    _sql_constraints = [
        ('card_reward_unique', 'UNIQUE(card_id, reward_id)', 'This reward has already been claimed for this card.')
    ]
