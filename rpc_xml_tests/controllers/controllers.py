# -*- coding: utf-8 -*-
# from odoo import http


# class RpcXmlTests(http.Controller):
#     @http.route('/rpc_xml_tests/rpc_xml_tests', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rpc_xml_tests/rpc_xml_tests/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rpc_xml_tests.listing', {
#             'root': '/rpc_xml_tests/rpc_xml_tests',
#             'objects': http.request.env['rpc_xml_tests.rpc_xml_tests'].search([]),
#         })

#     @http.route('/rpc_xml_tests/rpc_xml_tests/objects/<model("rpc_xml_tests.rpc_xml_tests"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rpc_xml_tests.object', {
#             'object': obj
#         })

