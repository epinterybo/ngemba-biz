from odoo import models, fields, api
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class CwCostingUniqueProduct(models.Model):
    _name = 'cw.costing.unique.product'
    _description = 'Cw Costing for unique product'
    
    name = fields.Char(string='Identifier', compute='_compute_name_field')
    product_id = fields.Many2one('product.product', string='Product', required=False, domain="[('detailed_type', '=', 'product')]")
    currency_id = fields.Many2one('res.currency', string="Currency", domain="[('active', '=', True)]", default=lambda self: self.env.ref('base.USD'))
    conversion_rate = fields.Float(string='Conversion Rate', help='Conversion Rate to VUV')
    purchase_amount = fields.Float(string='Purchase amount')
    duty_rate = fields.Float(string='Duty Rate', help='Duty rate in percentage')
    shipping_rate = fields.Float(string='Shipping Rate', help='Shipping rate in percentage')
    warranty_rate = fields.Float(string='Warranty Rate', help='Warranty Rate')
    vat_duty_others = fields.Float(string='Vat on Duties  & Others', default=0.15)
    margin_rate = fields.Float(string='Margin rate', help='Margin Rate')
    landed_cost = fields.Float(string='Landed Cost', default=0, readonly=True, compute='get_final_costing_infos', store=True)
    price_exc = fields.Float(string='Price exc.', default=0,   store=True)
    price_inc = fields.Float(string="Price Inc", default=0,  store=True)
    profit_amount = fields.Float(string='Profit', default=0,  store=True)
    created_at = fields.Datetime(string='Created at', default=lambda self: fields.Datetime.now(), readonly=True)
    modified_at = fields.Datetime(string='Modified at', readonly=True)
    last_modified_id = fields.Many2one('res.users', string="Created/Modified by", required=False, readonly=True)
    
    
    
    @api.depends('product_id')
    def _compute_name_field(self):
        for record in self:
            if record.product_id:
                record.name = record.product_id.name + "_" + fields.Datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            else:
                record.name = ""
                #record.name = fields.Datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            
    @api.model
    def write(self, vals):
        vals['modified_at'] = fields.Datetime.now()
        
        user_id = self.env.user.id
        if user_id:
            vals['last_modified_id'] = self.env.user.id
            
        return super().write(vals)
        
    
    
    @api.model_create_multi
    def create(self, vals_list):
        user_id = self.env.user.id
        
        for vals in vals_list:
            if user_id:
                vals['last_modified_id'] = self.env.user.id
                
            vals['modified_at'] = vals['created_at'] = fields.Datetime.now()
            
                
        return super().create(vals_list)
    
    @api.onchange('product_id')
    @api.depends('currency_id')
    def product_id_changed(self):
        
        if self.product_id:
            product = self.product_id
            
            most_recent_order_line = self.get_most_recent_purchase_order_line(product=product)
            
            if most_recent_order_line:
                self.purchase_amount = most_recent_order_line.price_unit
                self.currency_id = most_recent_order_line.currency_id.id
                
            
            conversion_rate = self.get_conversion_rate()
            
            if conversion_rate:
                self.conversion_rate = conversion_rate
                
            categ_id = product.categ_id
            
            if categ_id:
                duty_rate = categ_id.search_costing_duty_rate()
                warranty_rate = categ_id.search_costing_warranty_rate()
                vat_ship_rate = categ_id.search_costing_vat_rate()
                shipping_rate = categ_id.search_shipping_rate()
            
            
                if not duty_rate and not warranty_rate:
                    harmonized_code = product.cw_search_harmonized_code_id()
                    self.duty_rate = harmonized_code.cid_rate
                    self.warranty_rate = harmonized_code.warranty_rate
                    self.vat_duty_others = harmonized_code.vat_rate
                    self.shipping_rate = harmonized_code.shipment_rate
                else:
                    self.warranty_rate = warranty_rate
                    self.shipping_rate = shipping_rate
                    self.vat_duty_others = vat_ship_rate
                    self.duty_rate = duty_rate

                
            existing_landed_costing = self.env['cw.costing.grouping.po.line'].search([
                ('product_id', '=', product.id)
            ], order='id desc', limit=1)
            
            if existing_landed_costing and existing_landed_costing.profit > 0:
                self.margin_rate = existing_landed_costing.profit
        
        self.get_final_costing_infos()
        
    
    @api.onchange('currency_id')
    def set_currency_rate(self):
        self.conversion_rate = self.get_conversion_rate()
        
        if self.currency_id and self.purchase_amount and self.conversion_rate:
            self.get_final_costing_infos()
            
        
    
    def get_conversion_rate(self):
        currency = self.currency_id
        vuv_currency = self.env['res.currency'].search([('name', '=', 'VUV')], limit=1)
        
        if currency.id == vuv_currency.id:
            return 1
        
        return self.env['cw.costing.grouping.po'].get_conversion_rate(source_currency_code_id=currency.id, target_currency_code_id=vuv_currency.id)
    
    
    
    def get_most_recent_purchase_order_line(self, product):
        order_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            #('order_id.state', 'in', ['draft', 'done']),
            ('order_id.state', 'in', ['purchase', 'done']),  # Consider purchase orders in purchase or done state
        ])

        # Extract the distinct purchase orders from those lines
        purchase_orders = order_lines.mapped('order_id')

        # Sort the purchase orders by the date_order in descending order and take the first
        most_recent_purchase_order = purchase_orders.sorted(key=lambda r: r.date_order, reverse=True)[:1]

        if most_recent_purchase_order:
            po_id = most_recent_purchase_order.id
            first_order_line2 = self.env['purchase.order.line'].search([
                ('product_id', '=', product.id),
                ('order_id', '=', po_id)
            ], limit=1)
            return first_order_line2
        else:
            return 
        
    
    @api.onchange('purchase_amount', 'conversion_rate', 'duty_rate', 'shipping_rate', 'warranty_rate', 'vat_duty_others', 'margin_rate')
    @api.depends('purchase_amount', 'conversion_rate', 'duty_rate', 'shipping_rate', 'warranty_rate', 'vat_duty_others', 'margin_rate' )
    def get_final_costing_infos(self, write_data=False):
        purchase_amount = self.purchase_amount
        purchase_amount_converted = purchase_amount * self.conversion_rate
        
        
        shipment_price_inc = 0
        if self.shipping_rate and self.shipping_rate > 0:
            shipment_price_inc = purchase_amount_converted * self.shipping_rate
        
        duty_price_inc = (purchase_amount_converted + shipment_price_inc) *  self.duty_rate
        
        warranty_price_inc = (purchase_amount_converted + shipment_price_inc) * self.warranty_rate
        
        landed_cost = purchase_amount_converted + duty_price_inc + warranty_price_inc + shipment_price_inc
        
        price_exc = 0
        price_inc = 0
        profit_amount = 0
        
        if landed_cost and isinstance(self.margin_rate, float):
            margin_rate = self.margin_rate
            price_exc = landed_cost * (1 + margin_rate)
            
            
            if self.product_id:
                product_template = self.product_id.product_tmpl_id
                taxes = product_template.taxes_id
                
                if taxes:
                    price_inc = taxes.compute_all(price_exc, currency=None, quantity=1.0)['total_included']
                else:
                    price_inc = price_exc
            else:
                self.price_inc = price_inc = (1 + 0.15) * price_exc
            
            
            profit_amount = price_exc - landed_cost
            
        if write_data:
            return {
                'landed_cost': landed_cost,
                'price_exc': price_exc,
                'price_inc': price_inc,
                'profit_amount': profit_amount
            }
            """
            record_value = {}
            record_value['landed_cost'] = landed_cost
            record_value['price_exc'] = price_exc
            record_value['price_inc'] = price_inc
            record_value['profit_amount'] = profit_amount
            self.write(record_value)
            """
        else:
            self.landed_cost = landed_cost
            self.price_exc = price_exc
            self.price_inc = price_inc
            self.profit_amount = profit_amount
        
        
    @api.onchange('price_exc')
    @api.depends('landed_cost')
    def price_exc_changed(self):
        price_exc = self.price_exc
        landed = self.landed_cost
        if self.product_id:
            product_template = self.product_id.product_tmpl_id
            taxes = product_template.taxes_id
            
            if taxes:
                price_with_vat = taxes.compute_all(price_exc, currency=None, quantity=1.0)['total_included']
            else:
                price_with_vat = price_exc
        else:
            price_with_vat = (1 + 0.15) * price_exc
            
        profit_amount = price_exc - landed
        
        if landed and landed > 0:
            margin_rate = profit_amount / landed
        else:
            margin_rate = 0
        
        self.margin_rate = margin_rate
        self.price_inc = price_with_vat
        self.profit_amount = profit_amount
        self.price_exc = price_exc
        
        
    @api.onchange('price_inc')
    @api.depends('landed_cost')
    def price_inc_changed(self):
        price_inc = self.price_inc
        landed = self.landed_cost
        
        if self.product_id:
            product_template = self.product_id.product_tmpl_id
            taxes = product_template.taxes_id
            
            if not taxes:
                price_exc = price_inc
            else:
                vat_tax = taxes[0]
                vat_rate = vat_tax.amount / 100
                price_factor = 1 + vat_rate
                price_exc = price_inc / price_factor
        else:
            price_exc = price_inc / (1 + 0.15)
            
        profit_amount = price_exc - landed
        
        if landed and landed > 0:
            margin_rate = profit_amount / landed
        else:
            margin_rate = 0
        
        self.margin_rate = margin_rate
        self.price_exc = price_exc
        self.price_inc = price_inc
        self.profit_amount = profit_amount
        
        
    @api.onchange('profit_amount')
    @api.depends('landed_cost')
    def profit_amount_changed(self):
        landed = self.landed_cost
        profit_amount = self.profit_amount
        self.price_exc = landed + profit_amount
        self.price_exc_changed()
        