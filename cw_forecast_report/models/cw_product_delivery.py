from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwProductDelivery(models.Model):
    _name = "cw.old.product.delivery"
    _description = "CW Product Delivery Tracking"
    
    x_cw_po_ref_number = fields.Char(string="Invoice Ref Number", required=True)
    x_cw_product_list_id = fields.Char(string="Product ListID", required=True)
    x_cw_quantity_received = fields.Float(string="Quantity Received", required=True)
    x_cw_quantity_remaining = fields.Float(string="Quantity Remaining on PO", required=False)
    x_cw_received_date = fields.Datetime(string="Date Received", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=False)
    x_cw_old_purchase_order_id = fields.Many2one('cw.old.purchase.order', string="CW Old Purchase Order", required=False)
    
    
    @api.model
    def link_product_product(self):
        batch_size = 100
        offset = 0
        
        total_products_deliveries = self.search_count([('product_id', '=', False)])
        
        while offset < total_products_deliveries:
            
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
            _logger.info(f"Commited link_product_product (CwProductDelivery) batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_product_product (CwProductDelivery) processed successfully")
    
    
    @api.model
    def link_purchase_order(self):
        batch_size = 100
        offset = 0
        
        total_products_deliveries = self.search_count([
            ('x_cw_old_purchase_order_id', '=', False)
        ])
        
        while offset < total_products_deliveries:
            
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
                        record.write({
                            'x_cw_old_purchase_order_id' : po.id
                        })
            self.env.cr.commit()
            _logger.info(f"Commited link_purchase_order batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_purchase_order processed successfully")
            