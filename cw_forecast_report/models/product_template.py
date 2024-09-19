from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_cw_list_id = fields.Char(string="ListID", required=False)
    x_cw_is_active = fields.Boolean(string="Is Active", default=True)
    x_cw_non_refundable = fields.Boolean(string="Non Refundable", default=False)
    
    @api.model
    def check_and_update_list_id(self):
        batch_size = 100
        offset = 0
        
        total_products = self.search_count([
            ('x_cw_list_id', '=', False)
        ])
        
        while offset < total_products:
            records = self.search([
                ('x_cw_list_id', '=', False)
            ], limit=batch_size, offset=offset)
        
            for record in records:
                if record.x_studio_cw_listid:
                    record.write({
                        'x_cw_list_id': record.x_studio_cw_listid
                    })
                    
            self.env.cr.commit()
            _logger.info(f"Commited check_and_update_list_id batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches check_and_update_list_id (CwPoOrderLine) processed successfully")
    