# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class PosConfig(models.Model):
	_inherit = 'pos.config'

	allow_extra_info = fields.Boolean(string="Enable Extra Info")
	extra_info_ids = fields.Many2many('pos.extra.info', string="Allow Take Away")
	allow_info_show_receipt = fields.Boolean(string="Extra Information On Receipt" )


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pos_allow_extra_info = fields.Boolean(related='pos_config_id.allow_extra_info', readonly=False)
	pos_extra_info_ids = fields.Many2many(related='pos_config_id.extra_info_ids', readonly=False)
	pos_allow_info_show_receipt = fields.Boolean(related='pos_config_id.allow_info_show_receipt', readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: