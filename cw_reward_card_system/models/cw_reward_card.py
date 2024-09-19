from odoo import models, fields, api

class CwRewardCard(models.Model):
    _name = 'cw.reward.card'
    _description = 'CW Reward Card'

    name = fields.Char(string='Card Number', required=True)
    total_points = fields.Integer(string='Total Points', compute='_compute_total_points')
    points_history_ids = fields.One2many('cw.reward.points.history', 'reward_card_id', string='Points History')

    @api.depends('points_history_ids')
    def _compute_total_points(self):
        for card in self:
            card.total_points = sum(card.points_history_ids.mapped('points'))
