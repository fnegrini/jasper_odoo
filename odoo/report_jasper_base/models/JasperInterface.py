# encoding: utf-8

import os
import os.path
import sys
import time
import md5
import random
import codecs

from jnius import autoclass
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import pprint
import collections
import json

# Java base classes
JMap       = autoclass('java.util.HashMap')
File = autoclass('java.io.File')
StringReader = autoclass('java.io.StringReader')
String = autoclass('java.lang.String')
StringBufferInputStream = autoclass('java.io.StringBufferInputStream')
ByteArrayInputStream = autoclass('java.io.ByteArrayInputStream')
InputSource = autoclass('org.xml.sax.InputSource')

#JasperReport Classes
JRExporterParameter = autoclass('net.sf.jasperreports.engine.JRExporterParameter')
JasperExportManager = autoclass('net.sf.jasperreports.engine.JasperExportManager')
JasperFillManager = autoclass('net.sf.jasperreports.engine.JasperFillManager')
#JRXmlDataSource = autoclass('net.sf.jasperreports.engine.data.JRXmlDataSource')
JasperCompileManager = autoclass('net.sf.jasperreports.engine.JasperCompileManager')
JasperDesign = autoclass('net.sf.jasperreports.engine.design.JasperDesign')
JRXmlLoader = autoclass('net.sf.jasperreports.engine.xml.JRXmlLoader')
JRXmlUtils  = autoclass('net.sf.jasperreports.engine.util.JRXmlUtils')
JRLoader = autoclass('net.sf.jasperreports.engine.util.JRLoader')
JRCsvExporter = autoclass('net.sf.jasperreports.engine.export.JRCsvExporter')
JRRtfExporter = autoclass('net.sf.jasperreports.engine.export.JRRtfExporter')
JRHtmlExporter = autoclass('net.sf.jasperreports.engine.export.JRHtmlExporter')
JRTextExporter = autoclass('net.sf.jasperreports.engine.export.JRTextExporter')
JRTextExporterParameter = autoclass('net.sf.jasperreports.engine.export.JRTextExporterParameter')

TMPDIR = '/tmp/pyJasper'


def ensure_dirs(dirlist):
    """Ensure that a dir and all it's parents exist."""
    for thedir in dirlist:
        if not os.path.exists(thedir):
            os.makedirs(thedir)
    

def gen_uuid():
    """Generates an hopfully unique ID."""
    return md5.new("%s-%f" % (time.time(), random.random())).hexdigest()

def temp_file_name(tempdir, extention = 'TMP'):
    #ensure_dirs([tempdir])
    return os.path.join(tempdir, gen_uuid() + '.' + extention)
    
def stream_to_java_file(tempdir, stream, extention = 'TMP'):
    tmp_filename = temp_file_name(tempdir, extention)
    pfile = open(tmp_filename, 'wb')
    pfile.write(stream)
    pfile.close()
    file = File(tmp_filename)
    return file

def stream_to_java_stream(stream):
    str = String(stream);
    byte_array = ByteArrayInputStream(str.getBytes())
    return byte_array
    
def compile_jrxml(tempdir, designdata):
    xml = parseString(designdata)
    file = stream_to_java_file(tempdir, xml.toprettyxml(), 'xml')
    design = JasperDesign()
    design = JRXmlLoader.load(file)
    compiled = JasperCompileManager.compileReport(design)
    file.delete()
    return compiled

def convert_unicode_dict(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode_dict, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode_dict, data))
    else:
        return data
    
    
def dictionary_to_json(dict_data):
    outdict = {'odoo': convert_unicode_dict(dict_data)}
    json_stream = json.dumps(outdict, indent=2)
    return json_stream
    
def dictionary_to_xml(dict_data):
    xml_string = dicttoxml(dict_data, root=True, custom_root='odoo', attr_type=False)
    xml = parseString(xml_string)
    return xml.toprettyxml(encoding = 'UTF-8')

class JasperInterface:
    """Jasper interface to Odoo models"""
    
    def __init__(self, jrxml_list, jasper_list = {}, tempdir = TMPDIR):
        """Constructor
        designdatalist: a dict {"template_var_name": "JRXML data content"}.
        compiled_design: a dict {"template_var_name: "JASPER data content"}.
          If not supplied, the related design will be compiled
        tempdir: a temporary directory to read and write files
        """
        
        self.tempdir = tempdir

        # Compile design if compiled version doesn't exist
        self.compiled_design = {}
        
        for design_name in jrxml_list:
            if design_name in jasper_list:
                file = stream_to_java_file(self.tempdir, jasper_list[design_name], 'jasper')
                self.compiled_design[design_name] = JRLoader.loadObject(file)
                #file.delete()
            else:
                self.compiled_design[design_name] = compile_jrxml(self.tempdir, jrxml_list[design_name])
    
    def generate(self, dict_data, outputformat = 'PDF'):
        """Generate Output with JasperReports."""

        # convert to a java.util.Map so it can be passed as parameters
        map = JMap()
        for i in self.compiled_design:
            map.put(i, self.compiled_design[i])
        
        # create datasource
        xml_stream = dictionary_to_xml(dict_data)
        file = stream_to_java_file(self.tempdir, xml_stream, 'xml')
        xml_document = JRXmlUtils.parse(file)
        
        # passing base parameters
        map.put('XML_DATA_DOCUMENT', xml_document)
        map.put('XML_DATE_PATTERN', 'yyyy-MM-dd')
        map.put('XML_NUMBER_PATTERN', '#,##0.##')
        map.put('net.sf.jasperreports.xpath.executer.factory', 'net.sf.jasperreports.engine.util.xml.JaxenXPathExecuterFactory')
        jasper_print = JasperFillManager.fillReport(self.compiled_design['main'], map)
        file.delete()
        # generate report to file according to format
        output_filename = temp_file_name(self.tempdir)
        
        if outputformat == 'PDF':
            self._generate_pdf(jasper_print, output_filename)
        elif outputformat == 'RTF':
            self._generate_rtf(jasper_print, output_filename)
        elif outputformat == 'CSV':
            self._generate_csv(jasper_print, output_filename)
        elif outputformat == 'TEXT':
            self._generate_text(jasper_print, output_filename)
        elif outputformat == 'HTML':
            self._generate_html(jasper_print, output_filename)
        elif outputformat == 'XML':
            self._generate_xml(jasper_print, output_filename)
        else:
            raise RuntimeError("Unknown output type %r" % (outputformat))
        
        # export file stream and delete temporary file
        output = open(output_filename).read()
        os.remove(output_filename)
        
        return output
    
    def _generate_xml(self, jasper_print, output_filename):
        JasperExportManager.exportReportToXmlFile(jasper_print, output_filename)
    
    def _generate_pdf(self, jasper_print, output_filename):
        JasperExportManager.exportReportToPdfFile(jasper_print, output_filename)

    def _generate_rtf(self, jasper_print, output_filename):
        rtf_exporter = JRRtfExporter()
        rtf_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        rtf_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        rtf_exporter.exportReport()

    def _generate_csv(self, jasper_print, output_filename):
        csv_exporter = JRCsvExporter()
        csv_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        csv_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        csv_exporter.exportReport()

    def _generate_text(self, jasper_print, output_filename):
        text_exporter = JRTextExporter()
        text_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        text_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        text_exporter.setParameter(JRTextExporterParameter.PAGE_WIDTH, 80)
        text_exporter.setParameter(JRTextExporterParameter.PAGE_HEIGHT, 60)
        text_exporter.exportReport()

    def _generate_html(self, jasper_print, output_filename):
        html_exporter = JRHtmlExporter()
        html_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        html_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        html_exporter.exportReport()        
