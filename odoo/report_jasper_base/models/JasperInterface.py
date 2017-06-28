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

def temp_file_name(tempdir):
    #ensure_dirs([tempdir])
    return os.path.join(tempdir, gen_uuid() + '.TMP')
    
def stream_to_java_file(tempdir, stream):
    tmp_filename = temp_file_name(tempdir)
    pfile = codecs.open(tmp_filename, 'wb', 'utf-8')
    #pfile = open(tmp_filename, 'wb')
    pfile.write(stream)
    pfile.close()
    file = File(tmp_filename)
    return file
    
def compile_jrxml(tempdir, designdata):
    xml = parseString(designdata)
    file = stream_to_java_file(tempdir, xml.toprettyxml())
    design = JasperDesign()
    design = JRXmlLoader.load(file)
    file.delete()
    compiled = JasperCompileManager.compileReport(design)
    return compiled

def dictionary_to_xml(dict_data):
    xml_string = dicttoxml(dict_data, root=True, custom_root='odoo', attr_type=False)
    xml = parseString(xml_string)
    return xml.toprettyxml()

    
class JasperInterface:
    """Jasper interface to Odoo models"""
    
    def __init__(self, designdatalist, compiled_design = {}, tempdir = TMPDIR):
        """Constructor
        designdatalist: a dict {"template_var_name": "JRXML data content"}.
        compiled_design: a dict {"template_var_name: "JASPER data content"}.
          If not supplied, the related design will be compiled
        tempdir: a temporary directory to read and write files
        """
        
        self.tempdir = tempdir

        # Compile design if compiled version doesn't exist
        self.compiled_design = compiled_design
        
        for design_name in designdatalist:
            if not design_name in self.compiled_design:
                self.compiled_design[design_name] = compile_jrxml(self.tempdir, designdatalist[design_name])
    
    def generate(self, dict_data, outputformat = 'PDF'):
        """Generate Output with JasperReports."""

        # convert to a java.util.Map so it can be passed as parameters
        map = JMap()
        for i in self.compiled_design:
            map.put(i, self.compiled_design[i])
        
        # create datasource
        xml_stream = dictionary_to_xml(dict_data)
        xml_string = String(xml_stream)
        byte_array = ByteArrayInputStream(xml_string.getBytes("UTF-8"))
        java_source = InputSource(byte_array)
        xml_document = JRXmlUtils.parse(java_source);
        
        # passing base parameters
        map.put('XML_DATA_DOCUMENT', xml_document)
        map.put('XML_DATE_PATTERN', 'yyyy-MM-dd')
        map.put('XML_NUMBER_PATTERN', '#,##0.##')
        map.put('net.sf.jasperreports.xpath.executer.factory', 'net.sf.jasperreports.engine.util.xml.JaxenXPathExecuterFactory')
        jasper_print = JasperFillManager.fillReport(self.compiled_design['main'], map)
        xml_file.delete()

        
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