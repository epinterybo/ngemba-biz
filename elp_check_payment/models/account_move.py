from odoo import _, api, fields, models, tools 
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    total_payement = fields.Float(string="Total payment")


class AccountMove(models.Model):

    _inherit = 'account.move'

    def _compute_payment_state(self):
        result = super()._compute_payment_state()
        for rec in self:
            sale_order_id = self.env['sale.order'].search([('name','=',rec.invoice_origin)], limit=1)
            if sale_order_id:
                sale_order_id.write({
                    'total_payement':rec.amount_total - rec.amount_residual
                })
                if rec.payment_state == 'in_payment' or rec.payment_state == 'paid':
                    if sale_order_id.total_payement >= sale_order_id.amount_total:
                        stock_pickings = self.env['stock.picking'].search([('sale_id','=',sale_order_id.id)])
                        for stock_picking in stock_pickings:
                            if stock_picking.state in ['waiting','confirmed']:
                                stock_picking.action_assign()

        return result