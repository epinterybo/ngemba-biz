# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class rpc_xml_tests(models.Model):
#     _name = 'rpc_xml_tests.rpc_xml_tests'
#     _description = 'rpc_xml_tests.rpc_xml_tests'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

