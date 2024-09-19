from odoo import models, fields, api

class CwPrizeWinner(models.Model):
    _name = 'cw.bonus.prize.winner'
    _description = 'CW Bonus Prize winner'
    
    name = fields.Char(string='Name', compute='_compute_compute_field', required=False, readonly=True, store=True)
    prize_period_id = fields.Many2one('cw.bonus.prize.period', string='Prize for Period', readonly=True, required=True)
    employee_bonus_id = fields.Many2one('cw.bonus.employee', string='Employee', required=True, readonly=True)
    rank = fields.Integer(string='Period Rank')
    period_id = fields.Many2one('cw.bonus.period.tracking', string="Period", readonly=True, compute='_compute_period_id')
    
    @api.depends('prize_period_id', 'employee_bonus_id', 'rank')
    def _compute_compute_field(self):
        for record in self:
            if record.prize_period_id and record.employee_bonus_id and record.rank:
                record.name = record.employee_bonus_id.name + " - " + record.prize_period_id.name + " - " + record.rank
            else:
                currentTime = fields.Datetime.now()
                record.name = "created_at_" + currentTime.strftime("%Y_%m_%d_%H_%M_%S")
                
    @api.depends('prize_period_id')
    def _compute_period_id(self):
        for record in self:
            if record.employee_bonus_id:
                record.period_id = record.prize_period_id.period_bonus_id.id
            else:
                record.period_id = None