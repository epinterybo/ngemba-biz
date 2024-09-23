from odoo import models, api, fields
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    def _create_warranties_for_move_line(self, move_line):
        if move_line.move_id.sale_line_id.ybo_related_warranty_line_id:
            warranty_product = self.env['ybo.warranty.product']
            warranty_months = move_line.move_id.sale_line_id.ybo_related_warranty_line_id.duration
            if warranty_months:
                start_date = fields.Date.today()
                end_date = start_date + relativedelta(months=warranty_months)
                warranty_product.create({
                    'name': f"WAR/{move_line.lot_id.name}",
                    'sale_order_id': move_line.move_id.sale_line_id.order_id.id,
                    'product_id': move_line.product_id.id,
                    'start_date': start_date,
                    'end_date': end_date,
                    'quantity_delivered': move_line.quantity,
                    'duration': warranty_months,
                })
                _logger.info(f'Warranty created for {move_line.product_id.name}, Lot: {move_line.lot_id.name}, '
                             f'Start Date: {start_date}, End Date: {end_date}')

    def _create_warranties(self):
        for move_line in self.move_line_ids:
            _logger.info(f"CHECKING {move_line.product_id.name}, Lot: {move_line.lot_id.name}")
            if move_line.location_id.usage == 'internal' and move_line.location_dest_id.usage == 'customer':
                if move_line.move_id.sale_line_id:
                    self._create_warranties_for_move_line(move_line)

    def _action_done(self):
        """ Override _action_done to create warranties after the delivery process is complete (including backorders). """
        res = super(Picking, self)._action_done()

        # Ensure warranty creation only for outgoing pickings (stock to customer)
        if self.picking_type_id.code == 'outgoing' and self.location_id.usage == 'internal' and self.location_dest_id.usage == 'customer':
            _logger.info('Delivery marked as done, now creating warranties (if applicable).')
            self._create_warranties()

        return res

    # def button_validate(self):
    #     """ Override button_validate to handle both full and partial deliveries. """
    #     res = super(Picking, self).button_validate()
    #
    #     # Only trigger for outgoing pickings (stock to customer)
    #     if self.picking_type_id.code == 'outgoing' and self.location_id.usage == 'internal' and self.location_dest_id.usage == 'customer':
    #         _logger.info('Button Validate executed for outgoing picking.')
    #
    #         # Check if all quantities are delivered
    #         full_delivery = all(move.product_uom_qty >= move.quantity for move in self.move_ids)
    #
    #         if full_delivery:
    #             # All quantities delivered, create warranties now
    #             _logger.info('Full delivery detected, creating warranties immediately.')
    #             self._create_warranties()
    #         else:
    #             # Partial delivery, wait for _action_done to handle after backorder
    #             _logger.info('Partial delivery detected, waiting for backorder handling.')
    #
    #     return res


    # def action_done(self):
    #     self._create_warranties()
    #     _logger.debug('Checking for warranty creation after delivery completion.')
    #     """ Override action_done to create warranties after delivery is marked as done. """
    #     res = super(Picking, self).action_done()
    #     _logger.info('Triggering warranty creation after delivery completion.')
    #     return res

    # def button_validate(self):
    #     res = super(Picking, self).button_validate()
    #     if self.picking_type_id.code == 'outgoing' and self.location_id.usage == 'internal' and self.location_dest_id.usage == 'customer':
    #         _logger.info('Getting here !!!!!!!')
    #         self._create_warranties()
    #         return res

    # def _pre_action_done_hook(self):
    #     """ Hook method called before action_done in stock picking. """
    #     _logger.info('Checking if partial delivery occurred.')
    #     for move in self.move_ids:
    #         if move.quantity < move.product_uom_qty:
    #             # Partial delivery detected, trigger warranty creation
    #             _logger.info(
    #                 f"Partial delivery detected for {move.product_id.name}. Delivered: {move.quantity_done}, Ordered: {move.product_uom_qty}")
    #             self._create_warranties()
    #
    #     return super(Picking, self)._pre_action_done_hook()
    #
    # def button_validate(self):
    #     res = super(Picking, self).button_validate()
    #
    #     # Add a condition to ensure outgoing pickings from stock to customer trigger warranty
    #     if self.picking_type_id.code == 'outgoing' and self.location_id.usage == 'internal' and self.location_dest_id.usage == 'customer':
    #         _logger.info('Checking for warranty creation in button_validate method.')
    #         # Check if partial delivery is happening
    #         self._pre_action_done_hook()  # Calling hook to check partial delivery before the action is marked as done
    #     return res
