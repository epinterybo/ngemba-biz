import logging
from odoo import models, fields, _, api

_logger = logging.getLogger(__name__)

class CwPeriodicalPoints(models.Model):
    _name = 'cw.bonus.periodical.points'
    _description = 'CW Bonus Periodical Points'
    
    period_bonus_id = fields.Many2one('cw.bonus.period.tracking', string='Period', required=True, readonly=True)
    employee_bonus_id = fields.Many2one('cw.bonus.employee', string='Employee', readonly=True)
    volume_bonus_points = fields.Float(string="Volume Bonus", default=0, readonly=True)
    target_item_points = fields.Float(string="Target items", default=0, readonly=True)
    special_cat_points = fields.Float(string="Special Cat", default=0, readonly=True)
    stock_verify_points = fields.Float(string="Stock verify", default=0, readonly=True)
    solar_points = fields.Float(string="Solar", default=0, readonly=True)
    tills_or_onsite_points = fields.Float(string="Till or Onsite", default=0, readonly=True)
    lab_points = fields.Float(string="Lab", default=0, readonly=True)
    warranty_points = fields.Float(string="Warranty Points", default=0, readonly=True)
    strike = fields.Float(string="Strike", default=0)
    total_points = fields.Float(string="Total Points", readonly=True)
    total_points_with_strike = fields.Float(string="Total Points with strike", readonly=True)
    points_tracking_ids = fields.One2many('cw.bonus.points.tracking', 'periodical_point_id', string='Related Points tracking', readonly=True, required=False)
    created_date = fields.Datetime(string='Created Date', default=lambda self: fields.Datetime.now(), readonly=True)
    modified_at = fields.Datetime(string='Last Modified Date', readonly=True)
    
    
    
    @api.depends('total_points')
    @api.model
    def striking_point(self, *args, **kwargs):
        active_id = args[0]
        active_id = active_id[0]

        record = self.browse(active_id)
        
        strike = self.strike
        
        if not strike or strike == 0 :
            return
        
        if strike > -100 and strike < 100:
            points_with_strike = (self.total_points * strike)/100
            total_points_with_strike = self.total_points + points_with_strike
        else:
            total_points_with_strike = self.total_points + strike
            
        self.total_points_with_strike = total_points_with_strike
            
        self.write({
            'total_points_with_strike': total_points_with_strike
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Strike done'),
                'message': _('Strike done for  #%s has been done.') % self.employee_bonus_id.display_name,
                'sticky': False,
            }
        }
        
        """
        action = self.env.ref('cw_bonus_system.action_cw_bonus_periodical_points').read()[0]
        return action
        """
        
        
    """
    @api.model_create_single
    def create(self, vals_list):
        vals_list['modified_at'] = fields.Datetime.now()
        #return super(CwPeriodicalPoints, self).create(vals_list)
        return super().create(vals_list)
    """ 
    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        print("christian est la")
        ctx = dict(self.env.context)
        print("ready to print context")
        print(ctx)
        ctx['current_periodical_bonus_id'] = 1
        ctx['active_model'] = 'cw.bonus.periodical.points'
        print(ctx)
        
        pos_orders = self.env['pos.order'].search([])
        
        return super(CwPeriodicalPoints, self.with_context(**ctx)).search_fetch(domain, field_names, offset, limit, order)
    
    """
    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        ctx = dict(self.env.context)
        
        
        defaults['current_period_id'] = 1
        return defaults
    """
    @api.model
    def action_strike_boost(self, *args, **kwargs):
        active_id = args[0]
        active_id = active_id[0]
        record = self.browse(active_id)
        total_points = record.total_points
        percentage_to_add = (record.strike * total_points)
        total_points_strike = total_points + percentage_to_add
        record.write({
            'total_points_with_strike' : total_points_strike
        })
        
        """
        # Create the notification 
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Strike done'),
                'message': _('Strike for  #%s done successfully') % record.employee_bonus_id.name,
                'links': [{
                    'label': record.employee_bonus_id.name
                }],
                'sticky': False,
            }
        }
        """
        
        action = self.env.ref('cw_bonus_system.action_cw_bonus_periodical_points').read()[0]
        return action
        
    
    
    def _get_param_value(self):
        # Define the value of the parameter here
        return 1

    # Example method to call in the XML view
    @api.model
    def get_param_value(self):
        return self._get_param_value()
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['modified_at'] = fields.Datetime.now()
        return super().create(vals_list)
    
    
    def create_new_record(self, period_bonus_id, employee_bonus_id):
        new_record = self.create({
            'period_bonus_id': period_bonus_id,
            'employee_bonus_id': employee_bonus_id
        })
        return new_record
    
    @api.model
    def search_default_period_id(self):
        period_tracking = self.env['cw.bonus.period.tracking'].search([], order='created_date desc', limit=1)
        
        return period_tracking
    
    
    @api.model
    def write(self, vals_list):
        vals_list['modified_at'] = fields.Datetime.now()
        #return super(CwPeriodicalPoints, self).write(vals_list)
        return super().write(vals_list)
    
    
    def add_points_following_points_tracking(self, periodical_points_id, point_tracking_id):
        periodical = self.browse(periodical_points_id)
        strike = periodical.strike
        
        if not periodical:
            print("Point not being counted here")
            return
        
        point_tracking = self.env['cw.bonus.points.tracking'].browse(point_tracking_id)
        
        if not point_tracking:
            print("Point not being counted here")
            return
        
        total_points = periodical.total_points
        total_points += point_tracking.points
        
        record_values = {}
        record_values['total_points'] = total_points
        
        if strike:
            percentage_to_add = (strike * total_points)
            total_points_strike = total_points + percentage_to_add
            record_values['total_points_with_strike'] = total_points_strike
            
        if point_tracking.is_product_favorite:
            record_values['target_item_points'] = point_tracking.points + periodical.target_item_points
        elif point_tracking.is_lab:
            record_values['lab_points'] = point_tracking.points + periodical.lab_points
        elif point_tracking.is_solar:
            record_values['solar_points'] = point_tracking.points + periodical.solar_points
        elif point_tracking.is_special_cat:
            record_values['special_cat_points'] = point_tracking.points + periodical.special_cat_points
        elif point_tracking.is_stock_verify:
            record_values['stock_verify_points'] = point_tracking.points + periodical.stock_verify_points
        elif point_tracking.is_till_or_onsite:
            record_values['tills_or_onsite_points'] = point_tracking.points + periodical.tills_or_onsite_points
        elif point_tracking.is_warranty_points:
            record_values['warranty_points'] = point_tracking.points + periodical.warranty_points
        else:
            record_values['volume_bonus_points'] = point_tracking.points + periodical.volume_bonus_points
            pass
        
        periodical.write(record_values)
        
        return
        
    
    def remove_point_from_points_tracking(self, points,  periodical_point_id, point_tracking_id):
        periodical_point = self.browse(periodical_point_id)
        if not periodical_point:
            return
        
        point_tracking = self.env['cw.bonus.points.tracking'].browse(point_tracking_id)
        
        if not point_tracking:
            print("Point not being counted here")
            return
        
        total_points = periodical_point.total_points
        total_points -= points
        
        
        if point_tracking.is_product_favorite:
            target_point = periodical_point.target_item_points
            target_point -= points
            periodical_point.write({
                'total_points': points,
                'target_item_points' : target_point,
            })
        else:
            volume_points = periodical_point.volume_bonus_points
            volume_points -= points
            periodical_point.write({
                'total_points': points,
                'volume_bonus_points' : volume_points,
            })
            
        
        
        periodical_point.write({
            'total_points': total_points
        })
            
        
        return