import logging
from odoo import models, fields, api
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class CwExchangeRateLine(models.Model):
    _name = 'cw.costing.exchange.month.rate.line'
    _description = "CW Monthly exchange rate line "
    
    name = fields.Char(string="Name", required=False)
    currency_from_id = fields.Many2one('res.currency', string='From', required=True)
    currency_to_id = fields.Many2one('res.currency', string='To', required=True)
    month_rate = fields.Float(string="Rate", default=1)
    cw_month_id = fields.Many2one('cw.costing.exchange.month', string="Month", required=True)
    last_modified_id = fields.Many2one('res.users', string="Created/Modified", required=False)
    
    
    @api.depends('currency_from_id', 'currency_to_id', "cw_month_id")
    def _compute_name_field(self):
        for record in self:
            if record.currency_from_id and record.currency_to_id and record.cw_month_id:
                record.name = record.currency_from_id.name + " To " + record.currency_to_id.name + " -- " + record.cw_month_id.name
            else:
                record.name = "Still Determining"
                
    @api.model
    def write(self, vals):
        for record in self:
            cw_month_id = record.cw_month_id.id
            previous_from_id = record.currency_from_id
            previous_to_id = record.currency_to_id
            
        if not cw_month_id:
            cw_month_id = vals.get('cw_month_id', False)
        
        from_id = vals.get('currency_from_id', False)
        to_id = vals.get('currency_to_id', False)
        
        
        if cw_month_id and from_id and to_id and (previous_from_id.id != from_id or previous_to_id.id != to_id):
            is_exist = self.search([
                ('currency_from_id', '=', from_id),
                ('currency_to_id', '=', to_id),
                ('cw_month_id', '=', cw_month_id)
            ], limit=1)
            
            if is_exist:
                raise UserError("A line with corresponding currencies already exist")
        
        user_id = self.env.user.id
        if user_id:
            vals['last_modified_id'] = self.env.user.id
            
        return super().write(vals)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        user_id = self.env.user.id
        
        for vals in vals_list:
            if user_id:
                vals['last_modified_id'] = self.env.user.id
            
            from_id = vals.get('currency_from_id', False)
            to_id = vals.get('currency_to_id', False)
            cw_month_id = vals.get('cw_month_id', False)
            
            if not cw_month_id:
                last_exchange_rate_period = self.env['cw.costing.exchange.month'].search([], limit=1, order="created_date desc")
                if not last_exchange_rate_period:
                    last_exchange_rate_period = self.env['cw.costing.exchange.month'].create_month_period()
                
                cw_month_id = last_exchange_rate_period.id
                vals['cw_month_id'] = cw_month_id
            
            if from_id and to_id and cw_month_id:
                is_exist = self.search([
                    ('currency_from_id', '=', from_id),
                    ('currency_to_id', '=', to_id),
                    ('cw_month_id', '=', cw_month_id)
                ], limit=1)
                
                if is_exist:
                    raise UserError("A line with corresponding currencies already exist")
                
        return super().create(vals_list)