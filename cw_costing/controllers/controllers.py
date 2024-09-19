# -*- coding: utf-8 -*-
# from odoo import http


# class CwCosting(http.Controller):
#     @http.route('/cw_costing/cw_costing', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cw_costing/cw_costing/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cw_costing.listing', {
#             'root': '/cw_costing/cw_costing',
#             'objects': http.request.env['cw_costing.cw_costing'].search([]),
#         })

#     @http.route('/cw_costing/cw_costing/objects/<model("cw_costing.cw_costing"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cw_costing.object', {
#             'object': obj
#         })

