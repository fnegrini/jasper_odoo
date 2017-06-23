# -*- coding: utf-8 -*-

from odoo import models, fields, api
from JasperInterface import dictionary_to_xml

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
    
    sub_reports = fields.One2many('jasper.sub.report', 'report', string="Subreports") 

    def get_xml_sample(self):
        model_class = self.env[self.model]
        
        ids = model_class.search([], limit=10)
        
        dataset = []
        
        for id in ids:
            dataset.append(id.read())
        
        
        jasper_data = {}
        jasper_data['odoo'] = {}
        jasper_data['odoo'][self.model] = dataset
        
        xml_stream = dictionary_to_xml(jasper_data)
        
        #Como interfacear com o cliente e baixar o arquivo???
        pass

class jasper_sub_report(models.Model):
    _name = 'jasper.sub.report'
    
    report = fields.Many2one('ir.actions.report.xml', string="Report", index=True, ondelete='cascade', required=True)
    
    param_name = fields.Char(String='Param Name', size=30, required=True, translate=False)
    
    jasper_jrxml_file = fields.Binary(string='Design file', filters='*.jrxml')
    
    jasper_jasper_file = fields.Binary(string='Compiled file', filters='*.jasper')
    