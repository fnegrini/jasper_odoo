# -*- coding: utf-8 -*-

from odoo import models, fields, api

class jasper_report(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[('jasper','Jasper Report')])
    jasper_output_type = fields.Selection([("PDF", " PDF"),\
                                           ("HTML", "HTML"),\
                                           ("CSV", "CSV"),\
                                           ("RTF", "RTF"),\
                                           ("TEXT", "Plain text"),\
                                           ("XML", "XML")],\
                                            string = 'Output format')
    jasper_jrxml_file = fields.Binary(string='Design file', filters='*.jrxml')
    jasper_jasper_file = fields.Binary(string='Compiled file', filters='*.jasper')
