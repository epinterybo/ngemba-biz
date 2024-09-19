from odoo import models, api, fields

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    bonus_employee_id = fields.Many2one('cw.bonus.employee', 'Referral Employee', required=False, readonly=True)
    
    @api.model
    def create_from_ui(self, orders, draft=False):
        #order_ids = super().create_from_ui(orders, draft)
        order_ids = super(PosOrder, self).create_from_ui(orders)
        
        return order_ids
    
    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('bonus_employee_id'):
            result['bonus_employee_id'] = ui_order['bonus_employee_id']
        return result
    
    
    def action_pos_order_invoice(self):
        res = super().action_pos_order_invoice()
        
        for order in self:
            order_id = order.id
            self.env['cw.bonus.points.tracking'].create_new_points_history_from_pos_order(order_id)
            
        return res
    
    
    def refund(self):
        orders = super().refund()
        
        for order in orders:
            order_id = order.id
            self.env['cw.bonus.points.tracking'].remove_points_history_from_pos_order(order_id)
            
        return orders