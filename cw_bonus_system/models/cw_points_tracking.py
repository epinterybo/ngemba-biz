from odoo import models, fields, api

class CwPointsTracking(models.Model):
    _name = 'cw.bonus.points.tracking'
    _description = 'CW Bonus Points Tracking'
    
    product_id = fields.Many2one('product.product', string='Product', required=True)
    employee_bonus_id = fields.Many2one('cw.bonus.employee', string='Employee', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=False)
    pos_order_id = fields.Many2one('pos.order', string='POS Order', required=False)
    is_product_favorite = fields.Boolean(string='Product is in Favorite', default=False)
    is_volume_bonus = fields.Boolean(string='Is volume points', default=False)
    is_special_cat = fields.Boolean(string='Is Special Cat', default=False)
    is_stock_verify = fields.Boolean(string='Is stock verify', default=False)
    is_solar = fields.Boolean(string='Is Solar', default=False)
    is_till_or_onsite = fields.Boolean(string='Is till or onsite', default=False)
    is_lab = fields.Boolean(string='Is lab', default=False)
    is_warranty_points = fields.Boolean(string='Is Warranty points', default=False)
    points = fields.Float(string='Point for sale of product', default=0)
    periodical_point_id = fields.Many2one('cw.bonus.periodical.points', string="Full Period Tracking", readonly=True)
    created_date = fields.Datetime(string='Created Date', default=lambda self: fields.Datetime.now(), readonly=True)
    
    
    def create_new_points_history_from_sale_order(self, order_id):
        order = self.env['sale.order'].browse(order_id)
        
        if not order:
            print("Order N° " + order_id + " not found in the method create_new_points_history_from_sale_order")
            return
        
        employee_user = order.employee_bonus_id
        
        if not employee_user:
            created_user_id = order.create_uid.id
            #created_user = self.env['res.users'].browse(created_user_id)
            
            #we may also check if the sale order has another fields like code employee and in such case we look for that directly.
            
            #check if user is found in employees table
            employee_user = self.env['cw.bonus.employee'].search([
                ('user_id', '=', created_user_id)
            ], limit=1)
        
        
        if not employee_user:
            return
        
        period_tracking = self.env['cw.bonus.period.tracking'].search([], order='created_date desc', limit=1)
        
        if not period_tracking:
            period_tracking = self.env['cw.bonus.period.tracking'].create_period_tracking_record()
            
        periodical_points = self.env['cw.bonus.periodical.points'].search([
            ('period_bonus_id', '=', period_tracking.id),
            ('employee_bonus_id', '=', employee_user.id),
        ], limit=1)
        
        if not periodical_points:
            periodical_points = self.env['cw.bonus.periodical.points'].create_new_record(employee_bonus_id=employee_user.id, period_bonus_id=period_tracking.id)
        
        
        
        for order_line in order.order_line:
            product = order_line.product_id
            quantity = order_line.product_uom_qty
            price = order_line.price_unit
            self.process_points_trackings(product.id, periodical_points=periodical_points, employee_user=employee_user, order_id=order_id, quantity=quantity, price=price, is_pos_order=False, is_sale_order=True)
            
        return
    
    
    
    def create_new_points_history_from_pos_order(self, order_id):
        pos_order = self.env['pos.order'].browse(order_id)
        
        if not pos_order:
            print("Order N° " + order_id + " not found in the method create_new_points_history_from_pos_order")
            return
        
        #get Pos_order extra info
        field_name = 'Sale User'
        code_employee = None
        employee_user = None
        if pos_order.bonus_employee_id:
            employee_user = pos_order.bonus_employee_id
        """
        for extra_info_line in pos_order.bonus_employee_id:
            employee_user = extra_info_field
            
            extra_info_field = self.env['pos.extra.info'].browse(extra_info_line.fields_id.id)
            if extra_info_field and field_name.lower() == extra_info_field.field_name.lower():
                code_employee = extra_info_line.fields_value
                print("code_employee " + code_employee + " for order id " + str(pos_order.id))
            """   
        """
        if code_employee:
            employee_user = self.env['cw.bonus.employee'].search([
                ('code_employee', 'ilike', code_employee)
            ], limit=1)
        """
        if not employee_user:
            created_user_id = pos_order.create_uid.id
        
            #check if user is found in employees table
            employee_user = self.env['cw.bonus.employee'].search([
                ('user_id', '=', created_user_id)
            ], limit=1)
        
        
        if not employee_user:
            return
        
        period_tracking = self.env['cw.bonus.period.tracking'].search([], order='created_date desc', limit=1)
        
        if not period_tracking:
            period_tracking = self.env['cw.bonus.period.tracking'].create_period_tracking_record()
        
            
        periodical_points = self.env['cw.bonus.periodical.points'].search([
            ('period_bonus_id', '=', period_tracking.id),
            ('employee_bonus_id', '=', employee_user.id),
        ], limit=1)
        
        if not periodical_points:
            periodical_points = self.env['cw.bonus.periodical.points'].create_new_record(employee_bonus_id=employee_user.id, period_bonus_id=period_tracking.id)
            
        for line in pos_order.lines:
            product = line.product_id
            quantity = line.qty
            price = line.price_unit
            self.process_points_trackings(product.id, periodical_points=periodical_points, employee_user=employee_user, order_id=order_id, quantity=quantity, price=price, is_pos_order=True, is_sale_order=False)
            
        return
    
    
    def create_new_points_history_from_inventory(self, product_id, employer_id: int, points: float):
        
        periodical_points = self.env['cw.bonus.period.tracking'].search([], order='created_date desc', limit=1)
        
        if not periodical_points:
            periodical_points = self.env['cw.bonus.period.tracking'].create_period_tracking_record()
            
        record_values = {}
        record_values['product_id'] = product_id
        record_values['points'] = points
        record_values['employee_bonus_id'] = employer_id
        record_values['periodical_point_id'] = periodical_points.id
        record_values['created_date'] = fields.Datetime.now()
        record_values['is_stock_verify'] = True
        
        points_tracking = self.create(record_values)
        self.env['cw.bonus.periodical.points'].add_points_following_points_tracking(point_tracking_id=points_tracking.id, periodical_points_id=periodical_points.id)
        
        return
    
    
    def  process_points_trackings(self, product_id: int, periodical_points, employee_user, order_id: int, quantity: int, price: float, is_pos_order = False, is_sale_order= False):
        is_solar = False
        is_special_cat = False
        
        product = self.env['product.product'].browse(product_id)
        
        if not product:
            return
        
        
        record_values = {}
        if is_pos_order:
            record_values['pos_order_id'] = order_id
            pass
        elif is_sale_order:
            record_values['sale_order_id'] = order_id
            
        point_category = product.categ_id.get_bonus_point_for_category()
        
        if product.categ_id:
            for category in product.categ_id:
                if 'solar' in category.name.lower():
                    #Here we are dealing with Solar Product
                    record_values['is_solar']= is_solar = True
                    points = 100
                    break
                elif point_category and point_category > 0:
                    #doing what should be done for special category here
                    record_values['is_special_cat'] = is_special_cat = True
                    points = point_category
                    pass
                
        if not is_solar and not is_special_cat:
            
            if int(product.priority) != 0 and product.product_tmpl_id.x_cw_points_if_target_item:
                record_values['is_product_favorite'] = True
                points = product.product_tmpl_id.x_cw_points_if_target_item * quantity
            else:
                record_values['is_volume_bonus'] = True
                points = quantity * price * 0.00172
            
        record_values['product_id'] = product.id
        record_values['employee_bonus_id'] = employee_user.id
        record_values['points'] = points
        record_values['periodical_point_id'] = periodical_points.id
        record_values['created_date'] = fields.Datetime.now()
        
        
        points_tracking = self.create(record_values)
        self.env['cw.bonus.periodical.points'].add_points_following_points_tracking(point_tracking_id=points_tracking.id, periodical_points_id=periodical_points.id)
        
    
    
    
    def remove_points_history_from_sale_order(self, order_id):
        order = self.env['sale.order'].browse(order_id)
        
        if not order:
            print("Order N° " + order_id + " not found in the method create_new_points_history_from_sale_order")
            return
        
        created_user_id = order.create_uid.id
        
        #check if user is found in employees table
        employee_user = self.env['cw.bonus.employee'].search([
            ('user_id', '=', created_user_id)
        ], limit=1)
        
        if not employee_user:
            return
        
        
        for order_line in order.order_line:
            product = order_line.product_id
            
            point_tracking = self.search([
                ('product_id', '=', product.id),
                ('sale_order_id', '=', order_id)
            ], limit=1)
            
            if point_tracking:
                points = point_tracking.points
                periodical_point_id = point_tracking.periodical_point_id.id
                self.env['cw.bonus.periodical.points'].remove_point_from_points_tracking(points=points, periodical_point_id=periodical_point_id)
                point_tracking.unlink()
                
        return
    
    
    
    
    
    def remove_points_history_from_pos_order(self, order_id):
        pos_order = self.env['pos.order'].browse(order_id)
        
        if not pos_order:
            print("Order N° " + order_id + " not found in the method create_new_points_history_from_pos_order")
            return
        
        #get Pos_order extra info
        field_name = 'Sale User'
        code_employee = None
        employee_user = None
        for extra_info_line in pos_order.extra_info_line_ids:
            extra_info_field = self.env['pos.extra.info'].browse(extra_info_line.fields_id.id)
            if extra_info_field and field_name.lower() == extra_info_field.field_name.lower():
                code_employee = extra_info_line.fields_value
                print("code_employee " + code_employee + " for order id " + str(pos_order.id))
                
        if code_employee:
            employee_user = self.env['cw.bonus.employee'].search([
                ('code_employee', 'ilike', code_employee)
            ], limit=1)
            
        if not employee_user:
            created_user_id = pos_order.create_uid.id
        
            #check if user is found in employees table
            employee_user = self.env['cw.bonus.employee'].search([
                ('user_id', '=', created_user_id)
            ], limit=1)
        
        
        if not employee_user:
            return
        
        for line in pos_order.lines:
            product = line.product_id
            refunded_qty = line.refunded_qty
            price = line.price_unit
            
            point_tracking = self.search([
                ('product_id', '=', product.id),
                ('pos_order_id', '=', pos_order.id)
            ], limit=1)
            
            if point_tracking:
                points = refunded_qty * price * 0.00172
                
                if point_tracking.is_product_favorite:
                    points = points * 2
                    
                periodical_point_id = point_tracking.periodical_point_id.id
                self.env['cw.bonus.periodical.points'].remove_point_from_points_tracking(points=points, periodical_point_id=periodical_point_id)
                
                pre_points = point_tracking.points
                pre_points -= points
                
                point_tracking.write({
                    'points': pre_points
                })
                
        return