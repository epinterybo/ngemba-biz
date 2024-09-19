import logging
from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class CwMonthCoverExchange(models.Model):
    _name = 'cw.costing.exchange.month'
    _description = 'CW Exchange Rate By Month'
    
    name = fields.Char(string="Month", readonly=True, store=True, compute='_compute_name_field')
    period_start_date = fields.Datetime(string='Period starting Date', readonly=True)
    period_end_date = fields.Datetime(string='Period ending date', readonly=True)
    exchange_rate_line_ids = fields.One2many('cw.costing.exchange.month.rate.line', 'cw_month_id', string="Exchange Rate line")
    created_date = fields.Datetime(string='Created Date', default=lambda self: fields.Datetime.now(), readonly=True)
    
    
    
    @api.depends('period_start_date', 'period_end_date', 'created_date')
    def _compute_name_field(self):
        for record in self:
            if record.period_start_date and record.period_end_date:
                record.name = record.period_start_date.strftime("%Y-%m")
            else:
                currentTime = fields.Datetime.now()
                record.name = "created_at_" + currentTime.strftime("%Y-%m")
                
    @api.model
    def create_month_period(self):
        today = datetime.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + relativedelta(months=1) - timedelta(days=1)).replace(hour=23, minute=59, second=59)
        existing_record = self.search([
            ('period_start_date', '>=', first_day_of_month.strftime('%Y-%m-%d 00:00:00'))
        ])
        
        if not existing_record:
            existing_record = self.create({
                'name': first_day_of_month.strftime('%Y-%m'),
                'period_start_date': first_day_of_month,
                'period_end_date': last_day_of_month,
                'created_date': fields.Datetime.now() 
            })
            
            #lets see if we had entries for the previoou month and lets copy them
            day_last_month = first_day_of_month - timedelta(days=4)
            last_month_str = day_last_month.strftime("%Y-%m")
            
            preceding = self.search([
                ('name', 'ilike', last_month_str)
            ], limit=1)
            
            if not preceding:
                actives_currencies = self.env['res.currency'].search([
                    ('active', '=', True)
                ])
                
                for currency_1 in actives_currencies:
                    for currency_2 in actives_currencies:
                        if currency_1.id == currency_2.id:
                            continue
                        self.env['cw.costing.exchange.month.rate.line'].create({
                            'currency_from_id': currency_1.id,
                            'currency_to_id': currency_2.id,
                            'month_rate': 1,
                            'cw_month_id': existing_record.id,
                        })
                
            else:
                for line in preceding.exchange_rate_line_ids:
                    self.env['cw.costing.exchange.month.rate.line'].create({
                        'currency_from_id': line.currency_from_id.id,
                        'currency_to_id': line.currency_to_id.id,
                        'month_rate': line.month_rate,
                        'cw_month_id': existing_record.id,
                        'last_modified_id': line.last_modified_id.id,
                    })
            
            
            
            
        
        return existing_record