from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwSaleInvoice(models.Model):
    _name = "cw.old.sale.invoice"
    _description = "CW Old Sale Invoice"
    
    name = fields.Char(string='Order Reference', compute='_compute_compute_field', readonly=True)
    x_cw_invoice_ref_number = fields.Char(string="Ref Number", required=True)
    x_cw_total_price = fields.Float(string="Line Total Price")
    x_cw_order_date = fields.Datetime(string="Date Order", required=True)
    x_cw_order_customer_list_id = fields.Char(string="Customer List ID", required=True)
    x_cw_old_order_line_ids = fields.One2many('cw.old.order.line', 'x_cw_old_sale_invoice_id', string="Order Lines", required=False)
    x_cw_customer_id = fields.Many2one('res.partner', string="Contact", required=False, readonly=True)
    
    @api.depends('x_cw_invoice_ref_number')
    def _compute_compute_field(self):
        for record in self:
            record.name = record.x_cw_invoice_ref_number
    
    @api.model
    def link_customer_id(self):
        batch_size = 100
        offset = 0
        
        total_sales_invoices = self.search_count([
            ('x_cw_customer_id', '=', False)
        ])
        
        while offset < total_sales_invoices:
            
            records = self.search([
                ('x_cw_customer_id', '=', False)
            ], limit=batch_size, offset=offset)
        
            for record in records:
                list_id = record.x_cw_order_customer_list_id
                if list_id:
                    partner = self.env['res.partner'].search([
                        ('x_cw_list_id', '=', list_id)
                    ], limit=1)
                    if partner:
                        record.write({
                            'x_cw_customer_id' : partner.id
                        })
                        
            self.env.cr.commit()
            _logger.info(f"Commited link_customer_id batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_customer_id processed successfully")