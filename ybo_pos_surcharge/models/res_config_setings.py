from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    int_card_percentage = fields.Float(
        string="Surcharge Percentage",
        related='pos_config_id.int_card_percentage',  # Link to the corresponding field in pos_config
        readonly=False
    )
    pos_surcharge_product_id = fields.Many2one(
        'product.product', string="Surcharge Product",
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param(
            'pos.config.pos_surcharge_product_id.id', default=False)) if self.env['ir.config_parameter'].sudo().get_param(
            'pos.config.pos_surcharge_product_id.id', default=False) else False,
        config_parameter='pos.config.pos_surcharge_product_id'
    )
    pos_cw_surcharge_product_id = fields.Many2one(
        'product.product',
        string="Surcharge Product New",
        related='pos_config_id.pos_cw_surcharge_product_id',
        readonly=False
    )
    pos_config_id = fields.Many2one(
        'pos.config',
        string='Point of Sale',
        help='The Point of Sale configuration to update with the surcharge settings.'
    )

    def _compute_pos_surcharge_product_id(self):
        default_product = self.env.ref("point_of_sale.product_product_consumable", raise_if_not_found=False) or self.env['product.product']
        for res_config in self:
            surcharge_product = res_config.pos_config_id.pos_cw_surcharge_product_id or default_product
            if surcharge_product:
                res_config.pos_cw_surcharge_product_id = surcharge_product
            else:
                res_config.pos_surcharge_product_id = False
