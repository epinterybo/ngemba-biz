# -*- coding: utf-8 -*-
# from odoo import http


# class CwRewardCardSystem(http.Controller):
#     @http.route('/cw_reward_card_system/cw_reward_card_system', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cw_reward_card_system/cw_reward_card_system/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cw_reward_card_system.listing', {
#             'root': '/cw_reward_card_system/cw_reward_card_system',
#             'objects': http.request.env['cw_reward_card_system.cw_reward_card_system'].search([]),
#         })

#     @http.route('/cw_reward_card_system/cw_reward_card_system/objects/<model("cw_reward_card_system.cw_reward_card_system"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cw_reward_card_system.object', {
#             'object': obj
#         })

