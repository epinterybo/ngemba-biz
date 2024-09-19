# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class POSSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if self.config_id.allow_extra_info:
            result.append('pos.extra.info')
        return result

    def _loader_params_pos_extra_info(self):
        data = {
            'search_params': {
                'domain': [('id', 'in', self.config_id.extra_info_ids.ids)],
                'fields': [],
            },
        }
        return data

    def _get_pos_ui_pos_extra_info(self, params):
        return self.env['pos.extra.info'].search_read(**params['search_params'])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: