from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ybo_is_warranty_product = fields.Boolean(string="Is Warranty Product")

    @api.model
    def create(self, vals):
        # Create the product
        product = super(ProductTemplate, self).create(vals)

        # Check if the product's category has a warranty product
        if product.categ_id and product.categ_id.ybo_warranty_product_id:
            warranty_product = product.categ_id.ybo_warranty_product_id

            # Add the warranty product as an optional product
            product.optional_product_ids = [(4, warranty_product.id)]

        return product
