# -*- coding: utf-8 -*-

from odoo import models, fields, api
from JasperInterface import JasperInterface, dictionary_to_xml, dictionary_to_json, temp_file_name, convert_unicode_dict
from dbus.proxies import Interface
from base64 import encodestring, decodestring
import collections

JASPER_DATA = 'jasper_data'
JASPER_IDS = 'jasper_ids'
PARAMETERS = 'parameters'


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
    
    jasper_jrxml_file = fields.Binary(string='Design file (.jrxml)', filters='*.jrxml')
    
    jasper_jasper_file = fields.Binary(string='Compiled file (.jasper)', filters='*.jasper')
    
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
    
    def split_dictionary_field(self, new_record, record, field_name):
        
        for field in record[field_name]:
            new_field = field_name + '.' + field
            new_record[new_field] = data_dict[field]
            
        
    def split_tuple_field(self, new_record, record, field):
        new_record[field+'.id'] = record[field][0]
        new_record[field+'.name'] = record[field][1]
           
    def generate_data_for_record(self, jasper_data, id, map_fields):

        record = id.read(map_fields['normal'])[0]
        
        #many2one fields
        for m2o_fld in map_fields['many2one']:
            
            field_name = m2o_fld['field']
            record[field_name + '.id'] = id[m2o_fld['field']].id
            record[field_name + '.name'] = id[m2o_fld['field']].name
            if len(m2o_fld['sub_fields']) > 0:
                m2o_fields = id[m2o_fld['field']].read(m2o_fld['sub_fields'])[0]
                for m2o_field in m2o_fields:
                    field_name = m2o_fld['field'] + '.' + m2o_field
                    record[field_name] = m2o_fields[m2o_field]
                    
        #one2many subrecords
        for o2m_fld in map_fields['one2many']:
            results_o2m = id[o2m_fld['field']].read(o2m_fld['sub_fields'])
            for result_o2m in results_o2m:
                result_o2m[self.model] = id.id
                jasper_data[o2m_fld['field']].append(result_o2m)
        
        #many2many subrecords
        for m2m_fld in map_fields['many2many']:
            results_m2m = id[m2m_fld['field']].read(m2m_fld['sub_fields'])
            for result_m2m in results_m2m:
                result_m2m[self.model] = id.id
                jasper_data[m2m_fld['field']].append(result_m2m)
                
        new_record = {}
        
        # Eliminate tuples and dictionaries - a flat record
        for field in record:
            if isinstance(record[field], collections.Mapping):
                self.split_dictionary_field(new_record, record, field)
            elif isinstance(record[field], tuple):
                self.split_tuple_field(new_record, record, field)
            else:
                new_record[field] = record[field]
        
        jasper_data[self.model].append(new_record)
        
    @api.multi
    def get_json_sample(self):
        model_class = self.env[self.model]
        
        # load 10 first records
        ids = model_class.search([], limit=10)

        # convert do dictionary data
        jasper_data = self.generate_model_data(ids)       
        
        #Generate temp xml file
        json_stream = dictionary_to_json(jasper_data)
        json_file = temp_file_name(self.get_temp_dir(), 'json')
        
        file = open(json_file, 'wb')
        file.write(json_stream)
        file.close()
        
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_document?path=%s&filename=%s.json'%(json_file, self.model),
             'target': 'self',
             }
        
    @api.multi
    def get_xml_sample(self):
        model_class = self.env[self.model]
        
        # load 10 first records
        ids = model_class.search([], limit=10)

        # convert do dictionary data
        jasper_data = self.generate_model_data(ids)       
        
        #Generate temp xml file
        xml_stream = dictionary_to_xml(jasper_data)
        xml_file = temp_file_name(self.get_temp_dir(), 'xml')
        
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
        map_fields = self.get_model_fields()

        #initialize resultsets
        result = {}
        result[self.model] = []
        
        for o2m_fld in map_fields['one2many']:
            result[o2m_fld['field']] = []
       
        for m2m_fld in map_fields['many2many']:
            result[m2m_fld['field']] = []
        
        for id in res_ids:
            self.generate_data_for_record(result, id, map_fields)
        
        return result
    
    @api.multi
    def generate_report(self, res_ids, name, data):
        self.ensure_one()
        
        # if data['jasper_data'] does not generate data from model
        if JASPER_DATA in self.env.context:
            
            jasper_data = self.env.context[JASPER_DATA]
            
        else:
            if JASPER_IDS in self.env.context:
                model_ids = self.env[self.model].browse(self.env.context[JASPER_IDS])
            else:
                model_ids = self.env[self.model].browse(res_ids)
                
            jasper_data = self.generate_model_data(model_ids)
        
        
        if PARAMETERS in self.env.context:
            params = self.env.context[PARAMETERS]
        else:
            params = {}
            
        designs = {}
        compileds = {}
        
        # Fill binary reports
        if self.jasper_jrxml_file:
            designs['main'] = decodestring(self.jasper_jrxml_file)
        
        if self.jasper_jasper_file:
            compileds['main'] = decodestring(self.jasper_jasper_file)
        
        # Fill binary subreports    
        for subreport in self.sub_reports:
            if subreport.jasper_jrxml_file:
                designs[subreport.param_name] = decodestring(subreport.jasper_jrxml_file)
            if subreport.jasper_jasper_file:
                compileds[subreport.param_name] = decodestring(subreport.jasper_jasper_file) 
        
        # call Jasper Interface
        interface = JasperInterface(designs, compileds, self.get_temp_dir())
        
        report = interface.generate(jasper_data, params, self.jasper_output_type)
        
        # return output file and extension
        return (report, self.jasper_output_type)
            
    @api.model
    def render_report(self, res_ids, name, data):
        reports = self.search([('report_name', '=', name), ('report_type', '=', 'jasper')])
        if reports:
            return reports[0].generate_report(res_ids, name, data)
        
        return super(jasper_report, self).render_report(res_ids, name, data)
        
    
class jasper_sub_report(models.Model):
    _name = 'jasper.sub.report'
    
    report = fields.Many2one('ir.actions.report.xml', string="Report", index=True, ondelete='cascade', required=True)
    
    param_name = fields.Char(String='Param Name', size=30, required=True, translate=False)
    
    jasper_jrxml_file = fields.Binary(string='Design file (.jrxml)', filters='*.jrxml')
    
    jasper_jasper_file = fields.Binary(string='Compiled file (.jasper)', filters='*.jasper')


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
 
 
            
        
    