# -*- coding: utf-8 -*-

from odoo import models, fields, api
from JasperInterface import JasperInterface, dictionary_to_xml, temp_file_name
from dbus.proxies import Interface
from base64 import encodestring, decodestring

JASPER_DATA = 'jasper_data'

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

    @api.multi
    def get_model_fields(self):
        self.ensure_one()
        
        #initialize return mapping
        fields = {}
        fields['normal'] = []
        fields['many2many'] = []
        fields['many2one'] = []
        fields['one2many'] = []
        
        for field in self.model_fields:
            if field.field.ttype  in ['many2many', 'many2one', 'one2many']:
                record = {}
                record['field'] = field.field.name
                record['sub_fields'] = []
                # create record with subfields
                for sub_field in field.related_fields:
                    record['sub_fields'].append(sub_field.sub_model_field.name)
                    
                
                fields[field.field.ttype].append(record)
            else:
              fields['normal'].append(field.field.name)  
        
        return fields
    
    def generate_data_for_record(self, jasper_data, id, map_fields):

        record = id.read(map_fields['normal'])[0]
        #many2one fields
        for m2o_fld in map_fields['many2one']:
            if id[m2o_fld['field']]:
                m2o_fields = id[m2o_fld['field']].read(m2o_fld['sub_fields'])[0]
                for m2o_field in m2o_fields:
                    field_name = m2o_fld['field'] + '.' + m2o_field
                    record[field_name] = m2o_fields[m2o_field]
                    
        #one2many subrecords TODO!
        
        #many2many subrecords TODO!
        
        jasper_data[self.model].append(record)
        
    @api.multi
    def get_xml_sample(self):
        model_class = self.env[self.model]
        
        # load 10 first records
        ids = model_class.search([], limit=10)

        # convert do dictionary data
        jasper_data = self.generate_model_data(ids)       
        
        #Generate temp xml file
        xml_stream = dictionary_to_xml(jasper_data)
        xml_file = temp_file_name(self.get_temp_dir())
        
        file = open(xml_file, 'wb')
        file.write(xml_stream)
        file.close()
        
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_document?path=%s&filename=%s.xml'%(xml_file, self.model),
             'target': 'self',
             }
    
    def generate_model_data(self, res_ids):
        model_class = self.env[self.model]
        result = {}
        result[self.model] = []
        map_fields = self.get_model_fields()
        for id in res_ids:
            self.generate_data_for_record(result, id, map_fields)
        
        return result
            
    @api.model
    def render_report(self, res_ids, name, data):
        uid = self.env.context['params']['action']
        report = self.browse(uid)
        
        # if data['jasper_data'] does not generate data from model
        if JASPER_DATA in data:
            jasper_data = data[JASPER_DATA]
        else:
            model_ids = self.env[report.model].browse(res_ids)
            jasper_data = report.generate_model_data(model_ids)
        
        
        designs = {}
        compileds = {}
        # Fill binary reports
        designs['main'] = decodestring(report.jasper_jrxml_file)
        compileds['main'] = decodestring(report.jasper_jasper_file)
        
        # call Jasper Interface
        interface = JasperInterface(designs, compileds, self.get_temp_dir())
        
        report = interface.generate(jasper_data, report.jasper_output_type)
        
        # return output file and extension
        return (report, report.jasper_output_type)
    
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
    
    model = fields.Char(string="Model", compute='_compute_parent_fields', readonly=True, store=True, size=50)

    related_fields = fields.One2many('jasper.sub.model.field', 'field', string='SubModel Fields')
 
    @api.one
    @api.depends('field')
    def _compute_parent_fields(self):
        self.ensure_one()
        if self.field and self.field.ttype in ['many2many', 'many2one', 'one2many']:
            self.model = self.field.relation
        else:
            self.model = ''

class jasper_sub_model_field(models.Model):
    _name = 'jasper.sub.model.field'
    
    field = fields.Many2one('jasper.model.field', string='Field')
   
    sub_model_field = fields.Many2one('ir.model.fields', string = 'SubModel Field')
 
 
            
        
    