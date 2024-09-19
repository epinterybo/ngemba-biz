# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _, tools
import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'
    _description = "Point of Sale"

    extra_info_line_ids = fields.One2many('extra.fields.line', 'extra_info_line_id',
                                          string="Fields Extra Info Lines", readonly=True, copy=False)

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders)
        for order_id in order_ids:
            try:
                pos_order_id = self.browse(order_id['id'])
                if pos_order_id:
                    ref_order = [o['data'] for o in orders if o['data'].get('name') == pos_order_id.pos_reference]
                    for order in ref_order:
                        if len(order.get('extra_info')) > 0:
                            for extra_line in order.get('extra_info'):
                                for key, val in extra_line.items():
                                    if val:
                                        pos_order_id.write({
                                            'extra_info_line_ids': [(0, 0, {
                                                'fields_id': key,
                                                'fields_value': val,
                                            })]
                                        })
            except Exception as e:
                _logger.error('Error in point of sale validation: %s', tools.ustr(e))
        return order_ids


class ExtraFieldsLine(models.Model):
    _name = "extra.fields.line"
    _description = "Point of Sale Extra Fields Lines"
    _rec_name = "fields_id"

    fields_id = fields.Many2one('pos.extra.info', string='Field Name', readonly=True,)
    fields_value = fields.Char(string="Field Value")
    extra_info_line_id = fields.Many2one('pos.order', string="Extra Info Line")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: