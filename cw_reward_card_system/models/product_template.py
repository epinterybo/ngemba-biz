from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cw_points_cost = fields.Integer(string='Reward Points Cost', compute='_compute_points_cost')

    @api.depends('standard_price')
    def _compute_points_cost(self):
        for product in self:
            if product.standard_price :
                product.cw_points_cost = int(product.standard_price * 3)  # Assuming standard_price field exists
            else :
                product.cw_points_cost = 9999999999999
