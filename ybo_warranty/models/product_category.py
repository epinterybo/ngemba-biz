from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'
#domain="[('product_tag_ids.name', 'ilike', 'warranty')]"
    ybo_warranty_product_id = fields.Many2one(
        'product.template',
        string='Warranty Product',
        domain="[('ybo_is_warranty_product', '=', 'True')]",
    )
    ybo_warranty_cost_for_sixmonth_percent = fields.Float(string='Warranty Cost for Six Months (%)', default=0)
    ybo_standard_warranty_in_month = fields.Integer(string='Standard Warranty (Months)', default=0)

    @api.onchange('ybo_warranty_product_id')
    def _onchange_warranty_product_id(self):
        products = self.env['product.template'].search([('categ_id', '=', self._origin.id)])
        if not products:
            _logger.error(f"No products found for category: {self.name}")
            return

        for product in products:
            if self.ybo_warranty_product_id:
                product.optional_product_ids = [(4, self.ybo_warranty_product_id.id)]
            else:
                _logger.error(f"No warranty product set for {product.name}")

            _logger.info(f"Warranty product set successfully for prodcut category: {self.name}")

    def remove_warranty_products(self):
        self.ensure_one()
        products = self.env['product.template'].search([('categ_id', '=', self.id)])
        removed_count = 0

        for product in products:
            warranty_products = product.optional_product_ids.filtered(lambda p: p.ybo_is_warranty_product)
            if warranty_products:
                product.optional_product_ids = [(3, wp.id) for wp in warranty_products]
                removed_count += len(warranty_products)

        _logger.info(f"Removed {removed_count} warranty products from {len(products)} products in category {self.name}")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Warranty Products Removed',
                'message': f'Removed {removed_count} warranty products from {len(products)} products.',
                'type': 'success',
                'sticky': False,
            }
        }
