from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    employee_bonus_id = fields.Many2one('cw.bonus.employee', string="Referring Employee", help="Specify user who should take Bonus in case it should be earn it", required=False)
    
    """
    def action_confirm(self):
        res =  super().action_confirm()
        
        for order in self:
            order_id = order.id
            self.env['cw.bonus.points.tracking'].create_new_points_history_from_sale_order(order_id)
            
        return res
    """
    
    """
    def action_cancel(self):
        res = super().action_cancel()
        
        for order in self:
            self.env['cw.bonus.points.tracking'].remove_points_history_from_sale_order(order.id)
            
        return res
    """
    
    