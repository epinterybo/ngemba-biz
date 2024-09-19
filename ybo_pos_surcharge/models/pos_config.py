from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv.expression import OR
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    int_card_percentage = fields.Float(
        string="Surcharge Percentage",
        help="Percentage to be added as a surcharge to the total amount of the order",
        default=3.5
    )
    
    surcharge_product_id = fields.Many2one('product.product', string='Surcharge Product',
        domain="[('sale_ok', '=', True)]", help='The product used to apply surcharge on the ticket.')
    
    pos_cw_surcharge_product_id = fields.Many2one('product.product', string="Surcharge Product New",required=False)
    
    @api.model
    def _default_surcharge_value_on_module_install(self):
        configs = self.env['pos.config'].search([])
        open_configs = (
            self.env['pos.session']
            .search(['|', ('state', '!=', 'closed'), ('rescue', '=', True)])
            .mapped('config_id')
        )
        # Do not modify configs where an opened session exists.
        product = self.env.ref("point_of_sale.product_product_consumable", raise_if_not_found=False)
        for conf in (configs - open_configs):
            _logger.info("Getting conf here and I have %s", conf)
            conf.pos_cw_surcharge_product_id = product if product else False
            _logger.info("Going through pos_config _default_surcharge_value_on_module_install with val of surchage_product_id is %s", conf.pos_cw_surcharge_product_id)
            
    def open_ui(self):
        for config in self:
            if not self.current_session_id and not config.pos_cw_surcharge_product_id:
                raise UserError(_('A Surcharge product is needed to use the Surcharge feature. Go to Settings > Point of Sale >Bills & Receipts to set it.'))
        return super().open_ui()
    
    def _get_special_products(self):
        res = super()._get_special_products()
        return res | self.env['pos.config'].search([]).mapped('surcharge_product_id')
    
    def _get_available_product_domain(self):
        domain = super()._get_available_product_domain()
        return OR([domain, [('id', '=', self.surcharge_product_id.id)]])