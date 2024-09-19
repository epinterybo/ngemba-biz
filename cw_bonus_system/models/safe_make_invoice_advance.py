from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    
    def create_invoices(self):
        invoices_created = super().create_invoices()
        
        for sale_order in self.sale_order_ids:
            order_id = sale_order.id
            self.env['cw.bonus.points.tracking'].create_new_points_history_from_sale_order(order_id)
        
        return invoices_created
    