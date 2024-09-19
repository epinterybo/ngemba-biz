from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    x_cw_points_if_target_item = fields.Float(string="Points if target item", required=False, default=0)