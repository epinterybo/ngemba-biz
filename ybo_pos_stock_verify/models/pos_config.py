from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_multi_step_delivery = fields.Boolean(
        string="Allow multi step delivery",
        help="Allow multi step picking for POS purchased products",
        default=False
    )
    multi_step_route_id = fields.Many2one('stock.route', string="Multi-step route for products picking.")
    intermediate_location_id = fields.Many2one('stock.location', string="Intermediate Location.")
    initial_location_id = fields.Many2one('stock.location', string="Initial Location.")

    def open_ui(self):
        for config in self:
            if config.allow_multi_step_delivery:
                # Check if the intermediate location is set when multi-step delivery is allowed
                if not self.current_session_id and not config.intermediate_location_id:
                    raise UserError(_('An Intermediate Location is needed to use the multi-step delivery feature. Go to Settings > Point of Sale to set it.'))

                # Check if the initial location is set when multi-step delivery is allowed
                if not self.current_session_id and not config.initial_location_id:
                    raise UserError(_('An Initial Location is needed to use the multi-step delivery feature. Go to Settings > Point of Sale to set it.'))

        return super(PosConfig, self).open_ui()
