from odoo import models, fields, api
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class CwEmployeeForBonus(models.Model):
    _name = 'cw.bonus.employee'
    _description = 'CW Bonus Employee'
    
    name = fields.Char(string='Employee Name', compute='_compute_compute_fields', readonly=True, required=False, store=True)
    user_id = fields.Many2one('res.users', string='User', required=False)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=False)
    code_employee = fields.Char(string="Code employee", help="Enter employee code here", required=False)
    image_employee = fields.Image(string="Picture", max_width=1920, max_height=1920, store=True)
    periodical_point_ids = fields.One2many('cw.bonus.periodical.points', 'employee_bonus_id', string='Periodical Points', readonly=True)
    
    
    @api.depends('user_id', 'employee_id')
    def _compute_compute_fields(self):
        for record in self:
            if record.user_id:
                record.name = record.user_id.name
                
                #let's see if we have a code employee coming from res.users table and put it here
                
            elif record.employee_id:
                record.name = record.employee_id.display_name
                #let's see if we have a code employee coming from hr.employee table and put it here
            else:
                record.name = None
    
    
    @api.depends('user_id', 'employee_id')
    def _compute_compute_image_employee(self):
        for record in self:
            if record.user_id and record.user_id.image_1024:
                record.image_employee = record.user_id.image_1024
                
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            
            
            if vals['user_id'] and vals['image_employee'] is False:
                user_record = self.env['res.users'].browse(vals['user_id'])
                if user_record and user_record.image_1024:
                    vals['image_employee'] = user_record.image_1024
                    
            #let's see if we have a code employee coming from res.users table and put it here
            
        return super().create(vals_list)
    
    
    @api.model
    def write(self, vals):
        for record in self:
            previous_user_id = record.user_id
            previous_employee_id = record.employee_id
            
            user_id = vals.get('user_id', False)
            employee_id = vals.get('employee_id', False)
            
            if user_id and employee_id:
                raise UserError("The Employee can either a Employee or a User, not Both")
        
        if user_id:
            vals['employee_id'] = None
            user_record = self.env['res.users'].browse(user_id)
            if user_record and previous_user_id != user_record.id:
                vals['name'] = record.name
                image_employee = vals.get('image_employee', False)
                if user_record.image_1024 and image_employee is False:
                    vals['image_employee'] = user_record.image_1024
        elif employee_id:
            vals['user_id'] = None
            employee_record = self.env['hr.employee'].browse(employee_id)
            if employee_record:
                vals['name'] = employee_record.display_name
                
        
        return super().write(vals)
        
        """
        for record in self:
            record_values = {}
            if record.user_id:
                record_values['name'] = record.user_id.name
                
                if previous_user_id != record.user_id and record.user_id.image_1024:
                    record_values['image_employee'] = record.user_id.image_1024
                    
            elif record.employee_id:
                record_values['name'] = record.employee_id.display_name
                
            
            print(record_values)    
            record.write(record_values)
        
        return
        """
        
    def _get_employee_bonus_domain(self):
        return []
    
    def _loader_params_employee_bonus(self):
        return {
            'search_params': {
                'domain': self._get_employee_bonus_domain(),
                'fields': [
                    'name', 'code_employee'
                ],
            },
        }
        
    def get_pos_ui_employee_bonus_by_params(self, custom_search_params):
        _logger.info("Going through function get_pos_ui_employee_bonus_by_params and params are %s", custom_search_params)
        """
        :param custom_search_params: a dictionary containing params of a search_read()
        """
        params = self._loader_params_employee_bonus()
        # custom_search_params will take priority
        params['search_params'] = {**params['search_params'], **custom_search_params}
        bonus_employees = self.env['cw.bonus.employee'].search_read(**params['search_params'])
        return bonus_employees
    
