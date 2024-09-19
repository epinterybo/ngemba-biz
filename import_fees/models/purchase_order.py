# add hs code tp purchase order line model
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    harmonized_code_id = fields.Many2one(related='product_id.harmonized_code_id', store=True, readonly=True,
                                     help="Harmonized System Code, used to classify a product in import/export trade.")
