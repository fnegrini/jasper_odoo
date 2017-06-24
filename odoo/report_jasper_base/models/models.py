# -*- coding: utf-8 -*-

from odoo import models, fields, api
from JasperInterface import dictionary_to_xml, temp_file_name

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
    
    sub_reports = fields.One2many('jasper.sub.report', 'report', string='Subreports')
    
    model_fields = fields.One2many('jasper.model.field', 'report', string='Model Fields')
    
    def get_temp_dir(self):
        temp_dir = self.env['ir.config_parameter'].get_param('jasper.temp.directory') or '/var/jaspertemp'
        return temp_dir

    def expand_model_fields(self):
        #"many2one" - Expand as subfields separated by dosts
        #"many2many" - Expand as dataset force relation field
        #"one2many" - Expand as dataset use relation field in design
        pass
    
    @api.multi
    def get_xml_sample(self):
        model_class = self.env[self.model]
        
        # load 10 first records
        ids = model_class.search([], limit=10)
        dataset = []
        for id in ids:
            fields = id.read()
            dataset.append(fields[0])
        
        #generate dictionary to convert to xml
        jasper_data = {}
        jasper_data[self.model] = dataset
        
        #Generate temp xml file
        xml_stream = dictionary_to_xml(jasper_data)
        xml_file = temp_file_name(self.get_temp_dir())
        
        file = open(xml_file, 'wb')
        file.write(xml_stream)
        file.close()
        
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_document?path=%s&filename=sample.xml'%(xml_file),
             'target': 'self',
             }

class jasper_sub_report(models.Model):
    _name = 'jasper.sub.report'
    
    report = fields.Many2one('ir.actions.report.xml', string="Report", index=True, ondelete='cascade', required=True)
    
    param_name = fields.Char(String='Param Name', size=30, required=True, translate=False)
    
    jasper_jrxml_file = fields.Binary(string='Design file', filters='*.jrxml')
    
    jasper_jasper_file = fields.Binary(string='Compiled file', filters='*.jasper')


class jasper_model_field(models.Model):
    _name = 'jasper.model.field'
    
    report = fields.Many2one('ir.actions.report.xml', string="Report", index=True, ondelete='cascade', required=True)
    
    field = fields.Many2one('ir.model.fields', string = 'Field')
    
    related_fields = fields.One2many('jasper.sub.model.field', 'field', string='SubModel Fields')

class jasper_sub_model_field(models.Model):
    _name = 'jasper.sub.model.field'
    
    field = fields.Many2one('jasper.model.field', string='Field')
    
    model = fields.Char(string="Model", compute='_compute_parent_fields', readonly=True, store=True, size=50)
    
    sub_model_field = fields.Many2one('ir.model.fields', string = 'SubModel Field')
 
 
    @api.one
    @api.depends('field')
    def _compute_parent_fields(self):
        self.ensure_one()
        if self.field and self.field.field.ttype in ["many2many", "many2one", "one2many"]:
            self.model = self.field.field.relation
        else:
            self.model = ''
            
        
    