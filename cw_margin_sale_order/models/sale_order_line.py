from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    markup_percentage = fields.Float(string='Markup Percentage',  compute='_compute_markup_percentage', store=True, readonly=False)
    
    @api.onchange('markup_percentage', 'purchase_price', 'discount', 'product_id')
    def _onchange_markup_percentage(self):
        for line in self:
            if line.product_id and line.markup_percentage:
                cost_price = 0
                cost_price = line.product_id.standard_price
                
                if line.purchase_price:
                    cost_price = line.purchase_price
                    
                if cost_price and cost_price > 0:
                    line.price_unit = cost_price * (1 + line.markup_percentage)
                
                #line.price_subtotal = line.price_unit * line.product_uom_qty
                # Recompute the price subtotal with tax consideration
                #taxes = line.tax_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                #line.price_subtotal = taxes['total_excluded']
                
                """
                margin = (line.margin_percentage / 100.0) * cost_price
                margin = line.price_subtotal - (line.purchase_price * line.product_uom_qty)
                line.margin_percentage = line.price_subtotal and margin/line.price_subtotal
                line.price_unit = cost_price + margin
                """
                
    @api.depends('product_id', 'price_unit')
    def _compute_markup_percentage(self):
        for line in self:
            if line.product_id and line.product_id.standard_price and line.price_unit:
                cost_price = line.product_id.standard_price
                line.markup_percentage = (line.price_unit - cost_price)/cost_price
    
    """
    @api.depends('price_unit', 'tax_id', 'product_uom_qty')
    def _compute_amount(self):
        #Compute the amounts of the SO line.
        for line in self:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    """