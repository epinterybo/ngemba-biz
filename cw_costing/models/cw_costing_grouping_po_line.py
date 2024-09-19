from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwCostingGroupingPoLine(models.Model):
    _name = 'cw.costing.grouping.po.line'
    _description = 'CW Costing grouping PO line'
    
    name = fields.Char(string='Name', required=False)
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', readonly=True)
    cw_costing_grouping_po_id = fields.Many2one('cw.costing.grouping.po', string='Costing Group', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Qty', default=1, required=True)
    unit_price = fields.Float(string='U. Price')
    total_price = fields.Float(string='T. Price')
    currency_id = fields.Many2one('res.currency', string='Cur')
    harmonized_code_id = fields.Many2one('cw.costing.harmonized.code', string='H.S Code')
    duty = fields.Float(string='Duty')
    warranty = fields.Float(string='Warranty')
    hs_vat = fields.Float(string="HS Vat")
    freight_share_amount = fields.Float(string='Freight cost')
    percentage_freight_share = fields.Float(string='Percentage Freight')
    is_freight_cost_adjusted = fields.Boolean(string="Freight Adjusted ?", default=False)
    landed_cost = fields.Float(string='PL. Landed Cost', readonly=True)
    profit = fields.Float(string='Profit %')
    price_excluded_vat = fields.Float(string='Price Ex')
    price_include_vat = fields.Float(string='Price Inc')
    conversion_rate = fields.Float(string='Fx')
    is_costing_completed = fields.Boolean(string='Is Costing Completed', default=False)
    
    
    
    @api.onchange('duty', 'warranty', 'freight_share_amount', 'hs_vat', 'conversion_rate')
    @api.depends('total_price', 'duty', 'warranty', 'freight_share_amount', 'hs_vat')
    def set_landed_cost_product(self):
        total_price = self.unit_price * self.quantity
        total_price_converted = self.conversion_rate * total_price
        freight_amount = self.freight_share_amount
        
        duty_price = (total_price_converted + freight_amount) * self.duty
        
        warranty_price = (total_price_converted + freight_amount) * self.warranty
        
        full_amount_for_po_line = total_price_converted + duty_price + warranty_price + freight_amount
        
        landed_cost =  full_amount_for_po_line / self.quantity
        
        profit = (self.price_excluded_vat - landed_cost) / landed_cost
        
        self.write({
            'profit' : profit,
            'landed_cost' : landed_cost
        })
        
        
    @api.onchange('profit')
    @api.depends('landed_cost', 'product_id')
    def profit_changed(self):
        profit = self.profit
        landed_cost = self.landed_cost
        product_template = self.product_id.product_tmpl_id
        taxes = product_template.taxes_id
        
        price_exclude_vat = (landed_cost * profit) + landed_cost
        
        if taxes:
            price_with_vat = taxes.compute_all(price_exclude_vat, currency=None, quantity=1.0)['total_included']
        else:
            price_with_vat = price_exclude_vat
            
        self.write({
            'price_excluded_vat' : price_exclude_vat,
            'price_include_vat' : price_with_vat
        })
        
    
    @api.onchange('price_excluded_vat')
    @api.depends('landed_cost', 'product_id')
    def price_excluded_vat_changed(self):
        price_exclude_vat = self.price_excluded_vat
        landed_cost = self.landed_cost
        product_template = self.product_id.product_tmpl_id
        taxes = product_template.taxes_id
        
        if taxes:
            price_with_vat = taxes.compute_all(price_exclude_vat, currency=None, quantity=1.0)['total_included']
        else:
            price_with_vat = price_exclude_vat
            
        profit = (price_exclude_vat - landed_cost) / landed_cost
        
        self.write({
            'profit' : profit,
            'price_include_vat' : price_with_vat
        })
        
        
    
    @api.onchange('price_include_vat')
    @api.depends('landed_cost', 'product_id')
    def price_include_vat_change(self):
        price_with_vat = self.price_include_vat
        landed_cost = self.landed_cost
        product_template = self.product_id.product_tmpl_id
        taxes = product_template.taxes_id
        
        if not taxes:
            price_exclude_vat = price_with_vat
        else:
            vat_tax = taxes[0]
            vat_rate = vat_tax.amount / 100
            price_factor = 1 + vat_rate
            price_exclude_vat = price_with_vat / price_factor
        
        profit = (price_exclude_vat - landed_cost) / landed_cost
        
        self.write({
            'profit' : profit,
            'price_excluded_vat' : price_exclude_vat
        })
        
    
    @api.onchange('freight_share_amount')
    @api.depends('cw_costing_grouping_po_id')
    def freight_share_amount_has_changed(self):
        self.write({
            'is_freight_cost_adjusted' : True
        })
        
        self.freight_cost_adjustment()
        
    
    
    @api.onchange('is_freight_cost_adjusted')
    @api.depends('cw_costing_grouping_po_id')
    def is_freight_cost_adjusted_has_changed(self):
        cw_costing_group = self.cw_costing_grouping_po_id
        self.freight_cost_adjustment()
        
    
    
    def freight_cost_adjustment(self):
        cw_costing_group = self.cw_costing_grouping_po_id
        cw_costing_group.define_freight_shares_for_group(self.id)
        
        if cw_costing_group.freight_cost_amount and cw_costing_group.freight_cost_amount >= self.freight_share_amount:
            cw_costing_group.set_freight_share_amount(self.id)
            