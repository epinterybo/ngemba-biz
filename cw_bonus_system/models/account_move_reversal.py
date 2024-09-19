from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"
    
    
    def refund_moves(self):
        res = super().refund_moves()
        
        moves = self.move_ids
        
        sale_orders = moves.mapped('invoice_origin')
        
        # Loop through each sale order
        for order_name in sale_orders:
            # Do something with each sale order
            sale_order = self.env['sale.order'].search([('name', '=', order_name)])
            self.env['cw.bonus.points.tracking'].remove_points_history_from_sale_order(sale_order.id)
            
        
        return res