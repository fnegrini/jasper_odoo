# -*- coding: utf-8 -*-
from odoo import http

# class ReportJasperBase(http.Controller):
#     @http.route('/report_jasper_base/report_jasper_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_jasper_base/report_jasper_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_jasper_base.listing', {
#             'root': '/report_jasper_base/report_jasper_base',
#             'objects': http.request.env['report_jasper_base.report_jasper_base'].search([]),
#         })

#     @http.route('/report_jasper_base/report_jasper_base/objects/<model("report_jasper_base.report_jasper_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_jasper_base.object', {
#             'object': obj
#         })