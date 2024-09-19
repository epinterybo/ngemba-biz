# -*- coding: utf-8 -*-
# from odoo import http


# class CwBonusSystem(http.Controller):
#     @http.route('/cw_bonus_system/cw_bonus_system', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cw_bonus_system/cw_bonus_system/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cw_bonus_system.listing', {
#             'root': '/cw_bonus_system/cw_bonus_system',
#             'objects': http.request.env['cw_bonus_system.cw_bonus_system'].search([]),
#         })

#     @http.route('/cw_bonus_system/cw_bonus_system/objects/<model("cw_bonus_system.cw_bonus_system"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cw_bonus_system.object', {
#             'object': obj
#         })
from odoo import http
from odoo.tools import html_escape, html_sanitize
from markupsafe import Markup
#from odoo.http import request, route, Controller

class CwBonusSystem(http.Controller):
    @http.route('/cw_bonus_system/demo-info', type='http', auth='public')
    def cw_bonus_front_start(self):
        
        def some_function():
            return "This is just a function"
        
        
        some_data_model = http.request.env['cw.bonus.periodical.points'].sudo().search([])
        
        data = {
            'string' : "CW Bonus System",
            'integer': '1000',
            'some_float': 10.05,
            'boolean': True,
            'some_list': [1, 2, 3, 4, 5],
            'some_dict': {'any_key': 'any_value'},
            'some_function' : some_function(),
            'model': some_data_model,
            'html': '<h3>This is an HTML value!</h3> Added by attacker <script>alert("Do something!!")</script>',
            'html_escape': '<h3>This is an HTML value!</h3> %s'
                           % html_escape('Added by attacker <script>alert("Do something!!")</script>'),
            'html_sanitize': '<h3>This is an HTML value!</h3> %s'
                           % html_sanitize('Added by attacker <script>alert("Do something!!")</script>'),
            'markup': Markup('<h3>This is an HTML value!</h3> %s')
                      % 'Added by attacker <script>alert("Do something!!")</script>',
        }
        
        return http.request.render("cw_bonus_system.cw_front_template_start", data)
        
        
#    @route("/cw_bonus_system/standalone_app", auth="public", website=True)
#    def standalone_app(self):
#        return request.render(
#            'cw_bonus_system.standalone_app',
#            {
#                'session_info': request.env['ir.http'].get_frontend_session_info(),
#            }
#        )

