# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models


class POSExtraInfo(models.Model):
    _name = "pos.extra.info"
    _description = "Point of Sale Extra Information"
    _rec_name = 'field_name'

    field_name = fields.Char(string='Name')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: