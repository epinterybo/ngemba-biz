from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwTakingPositionsCameras(models.Model):
    _name = 'cw.taking.positions.cameras'
    _description = 'CW Taking Positions Cameras'

    name = fields.Char(string="Name", compute='_compute_name')
    pos_config_id = fields.Many2one('pos.config', string='Point of Sale', domain=lambda self: self._get_pos_config_domain())
    stock_location_id = fields.Many2one('stock.location', string="Incoming Stock Location", domain=lambda self: self._get_stock_location_domain())
    cw_taking_positions_cameras_lines_ids = fields.One2many('cw.taking.positions.cameras.lines', 'cw_taking_positions_cameras_id', string='Cameras List')


    @api.model
    def _get_pos_config_domain(self):
        # Get the IDs of the POS configs already selected
        taken_pos_config_ids = self.search([]).mapped('pos_config_id.id')
        return [('id', 'not in', taken_pos_config_ids)]

    @api.model
    def _get_stock_location_domain(self):
        # Get the IDs of the stock locations already selected
        taken_stock_location_ids = self.search([]).mapped('stock_location_id.id')
        return [('id', 'not in', taken_stock_location_ids)]

    @api.model
    def _compute_name(self):
        for record in self:
            if record.pos_config_id:
                record.name = record.pos_config_id.name
            elif record.stock_location_id:
                record.name = record.stock_location_id.complete_name
            else:
                record.name = False