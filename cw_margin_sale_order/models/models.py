# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cm_margin_sale_order(models.Model):
#     _name = 'cm_margin_sale_order.cm_margin_sale_order'
#     _description = 'cm_margin_sale_order.cm_margin_sale_order'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

