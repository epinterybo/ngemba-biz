from odoo import models, api
import logging
from pprint import pformat

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_optional_products(self, order_lines):
        _logger.info("Starting _check_optional_products for order %s", self.name)
        for i in range(len(order_lines) - 1):
            current_line = order_lines[i]
            next_line = order_lines[i + 1]
            current_product = current_line.product_id
            next_product = next_line.product_id

            _logger.info("Checking products: Current - %s, Next - %s", current_product.name, next_product.name)

            # Check if the current product has an optional product
            optional_product_ids = current_product.optional_product_ids.ids
            _logger.info(
                f"Optional products for Current Product {current_product.name} with ID {current_product.id} Found Product templates ID: %s, \nNext product: %s",
                pformat(optional_product_ids), pformat(next_product._origin.product_tmpl_id.id))

            next_product_id = next_product._origin.product_tmpl_id.id
            if optional_product_ids and next_product_id in optional_product_ids and next_line.product_id.product_tmpl_id.ybo_is_warranty_product:

                current_line.ybo_related_warranty_line_id = next_line.id

                next_line.ybo_is_warranty_line = True
                next_line.ybo_related_product_line_id = current_line.id

                #Make second line quantity same as first line
                next_line.product_uom_qty = current_line.product_uom_qty
                next_line.product_uom = current_line.product_uom
                


    @api.model
    def create(self, vals):
        _logger.info("Creating new sale order")
        order = super(SaleOrder, self).create(vals)
        if order.order_line:
            self._check_optional_products(order.order_line)
        return order

    def write(self, vals):
        _logger.info("Writing sale order %s", self.name)
        res = super(SaleOrder, self).write(vals)
        if 'order_line' in vals:
            _logger.info("Order lines updated for sale order %s, checking optional products", self.name)
            for order in self:
                order._check_optional_products(order.order_line)
        return res

