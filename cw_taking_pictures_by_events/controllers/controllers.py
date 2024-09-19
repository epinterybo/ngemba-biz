# -*- coding: utf-8 -*-
# from odoo import http


# class CwTakingPicturesByEvents(http.Controller):
#     @http.route('/cw_taking_pictures_by_events/cw_taking_pictures_by_events', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cw_taking_pictures_by_events/cw_taking_pictures_by_events/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cw_taking_pictures_by_events.listing', {
#             'root': '/cw_taking_pictures_by_events/cw_taking_pictures_by_events',
#             'objects': http.request.env['cw_taking_pictures_by_events.cw_taking_pictures_by_events'].search([]),
#         })

#     @http.route('/cw_taking_pictures_by_events/cw_taking_pictures_by_events/objects/<model("cw_taking_pictures_by_events.cw_taking_pictures_by_events"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cw_taking_pictures_by_events.object', {
#             'object': obj
#         })

