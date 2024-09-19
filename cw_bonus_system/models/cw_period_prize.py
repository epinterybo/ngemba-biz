from odoo import models, fields, api

class CwPrizePeriod(models.Model):
    _name = 'cw.bonus.prize.period'
    _description = 'CW Bonus Prize for period'
    
    name = fields.Char(string='Prize Name', required=True)
    description = fields.Text(string='Prize description')
    image_prize = fields.Image(string='Image Prize', max_width=1920, max_height=1920, store=True)
    for_rank = fields.Integer(string='Prize for rank', default=1)
    period_bonus_id = fields.Many2one('cw.bonus.period.tracking', string='Period')
    added_by = fields.Many2one('res.users', 'Added by', readonly=True, required=False)
    created_date = fields.Datetime(string='Created Date', default=lambda self: fields.Datetime.now(), readonly=True)
    modified_at = fields.Datetime(string='Last Modified Date', default=lambda self: fields.Datetime.now(), readonly=True)
    modified_by = fields.Many2one('res.users', 'Modified by', readonly=True, required=False)
    
    """
    @api.model_create_single
    def create(self, vals_list):
        vals_list['added_by'] = vals_list['modified_by'] = self.env.user.id
        #return super(CwPeriodicalPoints, self).create(vals_list)
        return super().create(vals_list)
    """
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['added_by'] = vals['modified_by'] = self.env.user.id
        return super().create(vals_list)
    
    @api.model
    def write(self, vals_list):
        vals_list['modified_at'] = fields.Datetime.now()
        vals_list['modified_by'] = self.env.user.id
        #return super(CwPeriodicalPoints, self).write(vals_list)
        return super().write(vals_list)
    