from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwSaleInvoice(models.Model):
    _name = "cw.old.purchase.order"
    _description = "CW Old Purchase Order"
    
    
    name = fields.Char(string='PO Order Reference', compute='_compute_compute_field', readonly=True)
    x_cw_purchase_order_ref_number = fields.Char(string="PO Ref Number", required=True)
    x_cw_total_price = fields.Float(string="Line Total Price")
    x_cw_currency_identifier = fields.Char(string="Currency Identifier")
    x_cw_po_date = fields.Datetime(string="Date Order", required=True)
    x_cw_po_provider_list_id = fields.Char(string="Contact ListID", required=True)
    cw_old_po_order_line_ids = fields.One2many('cw.old.po.order.line', 'x_cw_old_purchase_order_id', string="PO Order Lines", required=False)
    x_cw_old_partner_id = fields.Many2one('res.partner', string="Contact", required=False, readonly=True)
    
    @api.depends('x_cw_purchase_order_ref_number')
    def _compute_compute_field(self):
        for record in self:
            record.name = record.x_cw_purchase_order_ref_number
            
    @api.model
    def link_provider(self):
        batch_size = 100
        offset = 0
        
        total_purchases_orders = self.search_count([
            ('x_cw_old_partner_id', '=', False)
        ])
        
        while offset < total_purchases_orders:
        
            records = self.search([
                ('x_cw_old_partner_id', '=', False)
            ], limit=batch_size, offset=offset)
        
            for record in records:
                list_id = record.x_cw_old_partner_id
                if list_id:
                    partner = self.env['res.partner'].search([
                        ('x_cw_list_id', '=', False)
                    ], limit=1)
                    if partner:
                        record.write({
                            'x_cw_old_partner_id' : partner.id
                        })
                        
            self.env.cr.commit()
            _logger.info(f"Commited link_provider batch starting at offset {offset}")
            offset += batch_size
            
        _logger.info("All batches link_provider processed successfully")
                    