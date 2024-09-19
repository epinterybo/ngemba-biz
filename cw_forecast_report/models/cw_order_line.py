from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwOrderLine(models.Model):
    _name = "cw.old.order.line"
    _description = "CW Order Line"
    
    x_cw_invoice_ref_number = fields.Char(string="Invoice Ref Number", required=True)
    x_cw_product_list_id = fields.Char(string="Product ListID", required=True)
    x_cw_order_line_quantity = fields.Float(string="Quantity", default="1")
    x_cw_unit_price = fields.Float(string="Unit Price", required=True)
    x_cw_total_price = fields.Float(string="Line Total Price")
    x_cw_order_line_date = fields.Datetime(string="Date Order", required=False, readonly=True)
    product_id = fields.Many2one('product.product', string='Product', required=False, readonly=True)
    x_cw_old_sale_invoice_id = fields.Many2one('cw.old.sale.invoice', string="Old Sale Invoice", required=False, readonly=True)
    x_cw_order_customer_list_id = fields.Char(string="Customer List ID", required=False, readonly=True)
    x_cw_customer_id = fields.Many2one('res.partner', string="Contact", required=False, readonly=True)
    
    @api.model
    def link_product_product(self):
        batch_size = 100
        offset = 0
        
        total_orders_lines = self.search_count([('product_id', '=', False)])
        
        while offset < total_orders_lines:
            
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
            _logger.info(f"Commited link_product_product (CwOrderLine) batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_product_product (CwOrderLine) processed successfully")
    
    
    @api.model
    def link_invoice_order(self):
        batch_size = 100
        offset = 0
        total_invoices = self.search_count([
            ('x_cw_old_sale_invoice_id', '=', False)
        ])
        
        while offset < total_invoices:
            records = self.search([
                ('x_cw_old_sale_invoice_id', '=', False)
            ], limit=batch_size, offset=offset)

            for record in records:
                ref_invoice = record.x_cw_invoice_ref_number
                if ref_invoice:
                    #_logger.info("checking for invoice ref %s from order line id %s", ref_invoice, str(record.id))
                    order = self.env['cw.old.sale.invoice'].search([
                        ('x_cw_invoice_ref_number', 'ilike', ref_invoice)
                    ], limit=1)
                    if order:
                        #_logger.info("Invoice found for ref %s for record id %s and order ref is %s", ref_invoice, str(record.id), order.x_cw_invoice_ref_number)
                        record_values = {}
                        record_values['x_cw_old_sale_invoice_id'] = order.id
                        record_values['x_cw_order_line_date'] = order.x_cw_order_date

                        if order.x_cw_order_customer_list_id:
                            record_values['x_cw_order_customer_list_id'] = order.x_cw_order_customer_list_id

                        if order.x_cw_customer_id:
                            record_values['x_cw_customer_id'] = order.x_cw_customer_id.id

                        """
                        record.write({
                            'x_cw_old_sale_invoice_id' : order.id,
                            'x_cw_order_line_date': order.x_cw_order_date,
                        })

                        
                        if order.x_cw_customer_id:
                            pass
                        else:
                            order.link_customer_id()
                            
                        record.write({
                            'x_cw_order_customer_list_id': order.x_cw_order_customer_list_id,
                            'x_cw_customer_id' : order.x_cw_customer_id.id
                        })
                        """

                        record.write(record_values)
                    else:
                        _logger.info("Invoice Not NOT NOT found for ref %s for record id %s", ref_invoice, str(record.id))
                        
            self.env.cr.commit()
            _logger.info(f"Commited link_invoice_order batch starting at offset {offset}")
            offset += batch_size
        
        _logger.info("All batches link_invoice_order processed successfully")
                    