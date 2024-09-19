# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cw_taking_pictures_by_events(models.Model):
#     _name = 'cw_taking_pictures_by_events.cw_taking_pictures_by_events'
#     _description = 'cw_taking_pictures_by_events.cw_taking_pictures_by_events'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

