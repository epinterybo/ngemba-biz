from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_multi_step_delivery = fields.Boolean(
        string="Allow multi step delivery",
        related='pos_config_id.allow_multi_step_delivery', readonly=False
    )
    pos_multi_step_route_id = fields.Many2one(related='pos_config_id.multi_step_route_id', readonly=False)
    pos_intermediate_location = fields.Many2one(related='pos_config_id.intermediate_location_id', readonly=False)
    pos_initial_location = fields.Many2one(related='pos_config_id.initial_location_id', readonly=False)
    pos_config_id = fields.Many2one(
        'pos.config',
        string='Point of Sale',
        help='The Point of Sale configuration to update with the surcharge settings.'
    )
