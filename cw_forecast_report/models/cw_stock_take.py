from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwStockTake(models.Model):
    _name = "cw.old.stock.take"
    _description = "CW Old StockTake"
    
    x_cw_product_list_id = fields.Char(string="Product ListID", required=True)
    x_cw_stock_counted_quantity = fields.Float(string="Counted Quantity", required=True)
    x_cw_stock_expected_quantity = fields.Float(string="Expected Quantity", required=True)
    x_cw_stock_take_difference = fields.Float(string="Stock Take Difference")
    x_cw_stock_take_ok = fields.Boolean(string="Is Stock Take OK", default=True)
    x_cw_stock_take_date = fields.Datetime(string="Stock Take Date", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=False, readonly=True)
    
    
    @api.model
    def link_product_product(self):
        batch_size = 100
        offset = 0
        total_products_stocktakes = self.search_count([('product_id', '=', False)])
        
        while offset < total_products_stocktakes:
            
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
            _logger.info(f"Commited link_product_product (CwStockTake) batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_product_product (CwStockTake) processed successfully")