from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)
import re

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ybo_is_warranty_line = fields.Boolean(string='Is Warranty Line', default=False)
    ybo_related_warranty_line_id = fields.Many2one('sale.order.line', string='Related Warranty Line')
    ybo_related_product_line_id = fields.Many2one('sale.order.line', string='Related Product Line')
    duration = fields.Integer(string='Warranty Duration(months)', required=True, default=0,
                              compute='_compute_duration_from_name', store=True)
    ybo_warranty_display = fields.Char(string='Warranty Display', compute='_compute_warranty_display')
    ybo_product_warranty_display = fields.Char(string='Product Warranty Display',
                                               compute='_compute_product_warranty_display')

    ybo_synced_quantity = fields.Float(string='Synced Quantity', compute='_compute_synced_quantity', store=True)

    def _extract_warranty_duration(self, name):
        match = re.search(r'(\d+)\s*(?:month|months)?', name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    @api.depends('name')
    def _compute_duration_from_name(self):
        for line in self.filtered('ybo_is_warranty_line'):
            line.duration = self._extract_warranty_duration(line.name) or 0

    @api.depends('ybo_related_product_line_id')
    def _compute_warranty_display(self):
        for line in self:
            line.ybo_warranty_display = str(
                line.ybo_related_product_line_id.id) if line.ybo_related_product_line_id else ''

    @api.depends('ybo_related_warranty_line_id')
    def _compute_product_warranty_display(self):
        for line in self:
            line.ybo_product_warranty_display = str(
                line.ybo_related_warranty_line_id.id) if line.ybo_related_warranty_line_id else ''

    @api.depends('product_uom_qty', 'ybo_related_warranty_line_id.product_uom_qty',
                 'ybo_related_product_line_id.product_uom_qty')
    def _compute_synced_quantity(self):
        for line in self:
            if line.ybo_related_warranty_line_id:
                # Set the synced quantity to the related warranty line's product quantity
                line.ybo_synced_quantity = line.ybo_related_warranty_line_id.product_uom_qty
            elif line.ybo_related_product_line_id:
                # Set the synced quantity to the related product line's product quantity
                line.ybo_synced_quantity = line.ybo_related_product_line_id.product_uom_qty
            else:
                line.ybo_synced_quantity = line.product_uom_qty

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        if not self.env.context.get('skip_quantity_sync'):
            # Sync quantity of related warranty line, if it exists
            if self.ybo_related_warranty_line_id:
                self.ybo_related_warranty_line_id.with_context(
                    skip_quantity_sync=True).product_uom_qty = self.product_uom_qty
            # Otherwise, sync quantity of related product line, if it exists
            elif self.ybo_related_product_line_id:
                self.ybo_related_product_line_id.with_context(
                    skip_quantity_sync=True).product_uom_qty = self.product_uom_qty

        # Trigger compute for the synced quantity of the related line
        self._update_related_synced_quantity()

    def _update_related_synced_quantity(self):
        """Update the synced quantity on the related lines"""
        if self.ybo_related_warranty_line_id:
            # Update the synced quantity of the related warranty line
            self.ybo_related_warranty_line_id.ybo_synced_quantity = self.product_uom_qty
        elif self.ybo_related_product_line_id:
            # Update the synced quantity of the related product line
            self.ybo_related_product_line_id.ybo_synced_quantity = self.product_uom_qty

    def write(self, vals):
        # Call the base write method
        res = super(SaleOrderLine, self).write(vals)
        # Check if product_uom_qty has changed, and update related line quantities
        if 'product_uom_qty' in vals:
            for line in self:
                line._onchange_product_uom_qty()
        return res
