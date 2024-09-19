# -*- coding: utf-8 -*-
# from odoo import http


# class CwForecastReport(http.Controller):
#     @http.route('/cw_forecast_report/cw_forecast_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cw_forecast_report/cw_forecast_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cw_forecast_report.listing', {
#             'root': '/cw_forecast_report/cw_forecast_report',
#             'objects': http.request.env['cw_forecast_report.cw_forecast_report'].search([]),
#         })

#     @http.route('/cw_forecast_report/cw_forecast_report/objects/<model("cw_forecast_report.cw_forecast_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cw_forecast_report.object', {
#             'object': obj
#         })

