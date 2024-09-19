from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    x_cw_costing_grouping_id = fields.Many2one('cw.costing.grouping.po', string='CW Costing Group', store=True)
    x_shipment_id = fields.Many2one('x_shipment', string="Shipment Id", required=False, compute='_compute_x_shipment_id')
    x_cw_costing_grouping_po_line_ids = fields.One2many('cw.costing.grouping.po.line', 'purchase_order_id', string='Costing PO line', readonly=True)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        grouping_ids = []
        for vals in vals_list:
            grouping_id = vals.get('x_cw_costing_grouping_id', 0)
            if  grouping_id and grouping_id > 0:
                grouping_ids.append(grouping_id)
            
        res = super().create(vals_list)
        
        for group_id in grouping_ids:
            x_cw_costing_grouping = self.env['cw.costing.grouping.po'].browse(group_id)
            if x_cw_costing_grouping:
                x_cw_costing_grouping.computer_field_cw_costing_po_line_ids()
                
        return res
    
    def _compute_x_shipment_id(self):
        list_shipments = self.env['x_shipment'].search([], order='create_date desc')
        for record in self:
            record.x_shipment_id = False
            for shipment in list_shipments:
                if any(line.x_studio_purchase_order.id == record.id for line in shipment.x_shipment_line_ids_cf925):
                    _logger.info("Record id is  %s", str(shipment.id))
                    record.x_shipment_id = shipment.id
                    break
                """
                for list_2 in shipment.x_shipment_line_ids_cf925:
                    if list_2.x_studio_purchase_order and list_2.x_studio_purchase_order.id == record.id:
                        _logger.info("Record id is  %s", str(shipment.id))
                        record.x_shipment_id = shipment.id
                        return
                """
    
                
    @api.model
    def write(self, vals):
        grouping_id = vals.get('x_cw_costing_grouping_id', 0)
        print("grouping_id")
        print("grouping_id " + str(grouping_id))
        res =  super().write(vals)
        
        if not grouping_id or grouping_id == 0:
            grouping_id = self.x_cw_costing_grouping_id.id
        
        if grouping_id and grouping_id > 0: 
            x_cw_costing_grouping = self.env['cw.costing.grouping.po'].browse(grouping_id)
            if x_cw_costing_grouping:
                print("Rien")
                print("To display" + str(x_cw_costing_grouping.id))
                for record in self:
                    x_cw_costing_grouping.delete_records_for_po(po_id=record.id)
                x_cw_costing_grouping.computer_field_cw_costing_po_line_ids()
                
        return res
        