# -*- coding: utf-8 -*-
from openerp import http

# class Huduma(http.Controller):
#     @http.route('/huduma/huduma/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/huduma/huduma/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('huduma.listing', {
#             'root': '/huduma/huduma',
#             'objects': http.request.env['huduma.huduma'].search([]),
#         })

#     @http.route('/huduma/huduma/objects/<model("huduma.huduma"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('huduma.object', {
#             'object': obj
#         })