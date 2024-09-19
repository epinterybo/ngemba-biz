from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwPoOrderLine(models.Model):
    _name = "cw.old.po.order.line"
    _description = "CW PO Order Line"
    
    x_cw_po_ref_number = fields.Char(string="P.O. Ref Number", required=True)
    x_cw_product_list_id = fields.Char(string="Product ListID", required=True)
    x_cw_po_line_quantity = fields.Float(string="Quantity", default="1")
    x_cw_po_unit_price = fields.Float(string="Unit Price", required=True)
    x_cw_po_total_price = fields.Float(string="Line Total Price")
    x_cw_po_line_date = fields.Datetime(string="Date Order", required=False)
    x_cw_currency_identifier = fields.Char(string="Currency Identifier", required=True)
    product_id = fields.Many2one('product.product', string='Product', required=False, readonly=True)
    x_cw_old_purchase_order_id = fields.Many2one('cw.old.purchase.order', string="CW Old Purchase Order", required=False, readonly=True)
    x_cw_currency_id = fields.Many2one('res.currency', string="Currency", required=False, readonly=True)
    x_cw_po_provider_list_id = fields.Char(string="Vendor ListID", required=False)
    x_cw_old_partner_id = fields.Many2one('res.partner', string="Contact", required=False, readonly=True)
    
    
    @api.model
    def link_product_product(self):
        batch_size = 100
        offset = 0
        
        total_purchase_order_lines = self.search_count([('product_id', '=', False)])
        
        while offset < total_purchase_order_lines:
            records = self.search([('product_id', '=', False)], limit=batch_size, offset=offset)
        
            for record in records:
                list_id = record.x_cw_product_list_id
                if list_id:
                    product = self.env['product.product'].search([
                        ('x_cw_list_id', '=', list_id)
                        ], limit=1)
                    if product:
                        record.write({
                            'product_id': product.id
                        })
            self.env.cr.commit()
            _logger.info(f"Commited link_product_product (CwPoOrderLine) batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_product_product (CwPoOrderLine) processed successfully")
    
    
    @api.model
    def link_purchase_order(self):
        batch_size = 100
        offset = 0
        
        total_purchase_orders_lines = self.search_count([
            ('x_cw_old_purchase_order_id', '=', False)
        ])
        
        while offset < total_purchase_orders_lines:
            records = self.search([
                ('x_cw_old_purchase_order_id', '=', False)
            ], limit=batch_size, offset=offset)
        
            for record in records:
                ref_po = record.x_cw_po_ref_number
                if ref_po:
                    po = self.env['cw.old.purchase.order'].search([
                        ('x_cw_purchase_order_ref_number', '=', ref_po)
                    ], limit=1)
                    if po:
                        if po.x_cw_old_partner_id:
                            pass
                        else:
                            po.link_provider()
                        
                        record.write({
                            'x_cw_old_purchase_order_id' : po.id,
                            'x_cw_po_line_date' : po.x_cw_po_date,
                            'x_cw_po_provider_list_id' : po.x_cw_po_provider_list_id,
                            'x_cw_old_partner_id' : po.x_cw_old_partner_id,
                            'x_cw_currency_identifier': po.x_cw_currency_identifier,
                            'x_cw_currency_id' : po.x_cw_currency_id
                        })
                        
            self.env.cr.commit()
            _logger.info(f"Commited link_purchase_order batch starting at offset {offset}")
            offset += batch_size
        
        _logger.info("All batches link_purchase_order processed successfully")
        
        
    
                    
    @api.model
    def link_to_currency(self):
        vuv_currency = self.env['res.currency'].search([('name', '=', 'VUV')], limit=1)
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        nzd_currency = self.env['res.currency'].search([('name', '=', 'NZD')], limit=1)
        fjd_currency = self.env['res.currency'].search([('name', '=', 'FJD')], limit=1)
        eur_currency = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1)
        aud_currency = self.env['res.currency'].search([('name', '=', 'AUD')], limit=1)
        
        batch_size = 100
        offset = 0
        
        total_purchases_orders_lines = self.search_count([
            ('x_cw_currency_id', '=', False)
        ])
        
        while offset < total_purchases_orders_lines:
            records = self.search([
                ('x_cw_currency_id', '=', False)
            ], limit=batch_size, offset=offset)
        
            for record in records:
                currency_name = record.x_cw_currency_identifier.lower()
                if currency_name == "US Dollar".lower():
                    record.write({
                        'x_cw_currency_id': usd_currency.id
                    })
                elif currency_name == "Australian Dollar".lower():
                    record.write({
                        'x_cw_currency_id': aud_currency.id
                    })
                elif currency_name == "New Zealand Dollar".lower():
                    record.write({
                        'x_cw_currency_id': nzd_currency.id
                    })
                elif currency_name == "Fiji Dollar".lower():
                    record.write({
                        'x_cw_currency_id': fjd_currency.id
                    })
                elif currency_name == "Vanuatu Vatu".lower():
                    record.write({
                        'x_cw_currency_id': vuv_currency.id
                    })
                else:
                    record.write({
                        'x_cw_currency_id': vuv_currency.id
                    })
            
            self.env.cr.commit()
            _logger.info(f"Commited link_to_currency batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_to_currency processed successfully")
        
                
    @api.model
    def link_vendor_id_to_new_contact(self):
        batch_size = 100
        offset = 0
        
        total_purchase_orders_lines = self.search_count([
            ('x_cw_old_partner_id', '=', False)
        ])
        
        while offset < total_purchase_orders_lines:
        
            records = self.search([
                ('x_cw_old_partner_id', '=', False)
            ], limit=batch_size, offset=offset)
        
            for record in records:
                if record.x_cw_po_provider_list_id:
                    partner = self.env['res.partner'].search([
                        ('x_cw_list_id', '=', record.x_cw_po_provider_list_id)
                    ], limit=1)
                    
                    if partner:
                        record.write({
                            'x_cw_old_partner_id': partner.id
                        })
                        
            self.env.cr.commit()
            _logger.info(f"Commited link_vendor_id_to_new_contact batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_vendor_id_to_new_contact processed successfully")