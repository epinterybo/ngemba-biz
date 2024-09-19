from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
import logging
from itertools import groupby
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_picking_vals(self, partner, picking_type, location_id, location_dest_id):
        """Prepare the values for creating a stock picking"""
        return {
            'partner_id': partner.id if partner else False,
            'user_id': False,
            'picking_type_id': picking_type.id,
            'move_type': 'direct',
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'state': 'draft',
        }

    def _prepare_stock_move_vals(self, first_line, order_lines):
        """Prepare the values for creating a stock move"""
        return {
            'name': first_line.name,
            'product_uom': first_line.product_id.uom_id.id,
            'picking_id': self.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': first_line.product_id.id,
            'product_uom_qty': abs(sum(order_lines.mapped('qty'))),
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
        }

    def _create_move_from_pos_order_lines(self, picking, lines):
        """Create stock moves from POS order lines and assign them to a picking"""
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        move_vals = []
        for _, order_lines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*order_lines)
            move_vals.append({
                'name': order_lines[0].name,
                'product_uom': order_lines[0].product_id.uom_id.id,
                'picking_id': picking.id,
                'product_id': order_lines[0].product_id.id,
                'product_uom_qty': abs(sum(order_lines.mapped('qty'))),
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'company_id': picking.company_id.id,
            })
        moves = self.env['stock.move'].create(move_vals)
        moves._action_confirm()  # Confirm moves to create move lines
        moves._action_assign()  # Assign moves to reserve stock
        return moves

    @api.model
    def _create_picking_from_pos_order_lines(self, location_init_id, location_dest_id, lines, picking_type,
                                             partner=False):
        """Create stock pickings from POS order lines"""
        pickings = self.env['stock.picking']
        stockable_lines = lines.filtered(
            lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
                                                                                      precision_rounding=l.product_id.uom_id.rounding)
        )
        if not stockable_lines:
            return pickings

        positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
        negative_lines = stockable_lines - positive_lines

        if positive_lines:
            location_id = location_init_id
            positive_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(partner, picking_type, location_id, location_dest_id)
            )

            # Create moves and log the created moves
            self._create_move_from_pos_order_lines(positive_picking, positive_lines)

            self.env.cr.commit()  # Commit to ensure move lines are in the database

            pickings |= positive_picking

        if negative_lines:
            if picking_type.return_picking_type_id:
                return_picking_type = picking_type.return_picking_type_id
                return_location_id = return_picking_type.default_location_dest_id.id
            else:
                return_picking_type = picking_type
                return_location_id = picking_type.default_location_src_id.id

            negative_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(partner, return_picking_type, location_dest_id, return_location_id)
            )

            # Create moves and log the created moves
            self._create_move_from_pos_order_lines(negative_picking, negative_lines)

            self.env.cr.commit()  # Commit to ensure move lines are in the database

            pickings |= negative_picking

        return pickings

    def _get_last_customer_with_location(self):
        """Retrieve the last customer with a location set"""
        return self.env['res.partner'].search([('name', '=', "Dummy Client")], order='create_date desc',
                                              limit=1)

    @api.model
    def _create_order_picking(self):
        """Create stock pickings for the POS order"""
        self.ensure_one()
        if self.config_id.allow_multi_step_delivery:

            intermediate_location = self.config_id.intermediate_location_id
            initial_location = self.config_id.initial_location_id
            customer_location = self.partner_id.property_stock_customer

            if not intermediate_location:
                raise UserError(_("Intermediate Location not found"))
            if not initial_location:
                raise UserError(_("Initial Location not found"))
            if not customer_location:
                last_customer = self._get_last_customer_with_location()
                _logger.info("Last customer: %s", last_customer)
                if last_customer:
                    customer_location = last_customer.property_stock_customer
                else:
                    super(PosOrder, self)._create_order_picking()


            picking_type_internal = self.env.ref('stock.picking_type_internal')
            picking_type_out = self.env.ref('stock.picking_type_out')

            # First picking: from stock to intermediate location
            first_picking = self._create_picking_from_pos_order_lines(
                initial_location.id, intermediate_location.id,
                self.lines,
                picking_type_internal,
                self.partner_id
            )
            first_picking.write({
                'pos_session_id': self.session_id.id,
                'pos_order_id': self.id,
                'origin': self.name
            })

            # Confirm and mark the first picking as done
            first_picking.action_confirm()
            first_picking.action_assign()
            first_picking.button_validate()  # This marks it as done

            # Second picking: from intermediate location to customer
            second_picking = self._create_picking_from_pos_order_lines(
                intermediate_location.id, customer_location.id,
                self.lines,
                picking_type_out,
                self.partner_id
            )
            second_picking.write({
                'pos_session_id': self.session_id.id,
                'pos_order_id': self.id,
                'origin': self.name,
                'state': 'assigned'
            })

            # Confirm and assign the second picking to reserve quantities
            second_picking.action_confirm()
            second_picking.action_assign()
        else:
            super(PosOrder, self)._create_order_picking()

    def _launch_stock_rule_from_pos_order_lines(self):
        """Launch stock rules from POS order lines"""
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.product_id.type not in ('consu', 'product'):
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.qty
            procurement_uom = line.product_id.uom_id
            procurements.append(self.env['procurement.group'].Procurement(
                line.product_id, product_qty, procurement_uom,
                line.order_id.partner_id.property_stock_customer,
                line.name, line.order_id.name, line.order_id.company_id, values
            ))

        if procurements:
            self.env['procurement.group'].run(procurements)

        orders = self.mapped('order_id')
        for order in orders:
            pickings_to_confirm = order.picking_ids
            if pickings_to_confirm:
                pickings_to_confirm.action_confirm()
                tracked_lines = order.lines.filtered(lambda l: l.product_id.tracking != 'none')
                lines_by_tracked_product = groupby(sorted(tracked_lines, key=lambda l: l.product_id.id),
                                                   key=lambda l: l.product_id.id)
                for product_id, lines in lines_by_tracked_product:
                    lines = self.env['pos.order.line'].concat(*lines)
                    moves = pickings_to_confirm.move_ids.filtered(lambda m: m.product_id.id == product_id)
                    moves.move_line_ids.unlink()
                    moves._add_mls_related_to_order(lines, are_qties_done=False)
                    moves._recompute_state()
        return True
