# -*- coding: utf-8 -*-
# from odoo import http


# class CmMarginSaleOrder(http.Controller):
#     @http.route('/cm_margin_sale_order/cm_margin_sale_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cm_margin_sale_order/cm_margin_sale_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cm_margin_sale_order.listing', {
#             'root': '/cm_margin_sale_order/cm_margin_sale_order',
#             'objects': http.request.env['cm_margin_sale_order.cm_margin_sale_order'].search([]),
#         })

#     @http.route('/cm_margin_sale_order/cm_margin_sale_order/objects/<model("cm_margin_sale_order.cm_margin_sale_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cm_margin_sale_order.object', {
#             'object': obj
#         })

