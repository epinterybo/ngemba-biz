from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class CwPeriodTracking(models.Model):
    _name = 'cw.bonus.period.tracking'
    _description = 'CW Bonus Period'
    
    name = fields.Char(string='Name', compute='_compute_compute_field', readonly=True, store=True)
    period_start_date = fields.Datetime(string='Period starting Date', required=True)
    period_end_date = fields.Datetime(string='Period ending date', required=True)
    created_date = fields.Datetime(string='Created Date', default=lambda self: fields.Datetime.now(), readonly=True)
    periodical_point_ids = fields.One2many('cw.bonus.periodical.points', 'period_bonus_id', readonly=True, string='Periods Point')
    
    @api.depends('period_start_date', 'period_end_date', 'created_date')
    def _compute_compute_field(self):
        for record in self:
            if record.period_start_date and record.period_end_date:
                record.name = record.period_start_date.strftime("%Y_%m_%d_%H_%M_%S") + "_to_" + record.period_end_date.strftime("%Y_%m_%d_%H_%M_%S")
            else:
                currentTime = fields.Datetime.now()
                record.name = "created_at_" + currentTime.strftime("%Y_%m_%d_%H_%M_%S")
                
    @api.model
    def create_period_tracking_record(self):
        today = datetime.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + relativedelta(months=1) - timedelta(days=1)).replace(hour=23, minute=59, second=59)
        existing_record = self.env['cw.bonus.period.tracking'].search([
            ('period_start_date', '>=', first_day_of_month.strftime('%Y-%m-%d 00:00:00'))
        ])
        
        if not existing_record:
            existing_record = self.create({
                'name': first_day_of_month.strftime('%Y_%m_%d_%H_%M_%S') + "_to_" + last_day_of_month.strftime('%Y_%m_%d_%H_%M_%S'),
                'period_start_date': first_day_of_month,
                'period_end_date': last_day_of_month,
                'created_date': fields.Datetime.now() 
            })
        
        return existing_record
