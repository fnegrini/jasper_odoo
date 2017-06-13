# encoding: utf-8

import os
import os.path
import sys
import time
import md5
import random

from jnius import autoclass

# Java DataTypes
JMap       = autoclass('java.util.HashMap')
JArrayList = autoclass('java.util.ArrayList')
JInt       = autoclass('java.lang.Integer')
JLong      = autoclass('java.lang.Long')
JFloat     = autoclass('java.lang.Float')
JDouble    = autoclass('java.lang.Double')
JString    = autoclass('java.lang.String')

# Java base classes
InputStream = autoclass('java.io.InputStream')
File = autoclass('java.io.File')

#JasperReport Classes
JRExporterParameter = autoclass('net.sf.jasperreports.engine.JRExporterParameter')
JasperExportManager = autoclass('net.sf.jasperreports.engine.JasperExportManager')
JasperFillManager = autoclass('net.sf.jasperreports.engine.JasperFillManager')
JRXmlDataSource = autoclass('net.sf.jasperreports.engine.data.JRXmlDataSource')
JasperCompileManager = autoclass('net.sf.jasperreports.engine.JasperCompileManager')
JasperDesign = autoclass('net.sf.jasperreports.engine.design.JasperDesign')
JRXmlLoader = autoclass('net.sf.jasperreports.engine.xml.JRXmlLoader')

TMPDIR = '/tmp/pyJasper'

def ensure_dirs(dirlist):
    """Ensure that a dir and all it's parents exist."""
    for thedir in dirlist:
        if not os.path.exists(thedir):
            os.makedirs(thedir)
    

def gen_uuid():
    """Generates an hopfully unique ID."""
    return md5.new("%s-%f" % (time.time(), random.random())).hexdigest()
    
def stream_to_java_file(tempdir, stream):
    ensure_dirs([tempdir])
    tmp_filename = os.path.join(tempdir, gen_uuid() + '.tmp')
    open(tmp_filename, 'wb').write(stream)
    file = File(tmp_filename)
    return file
    
    
class JasperInterface:
    """This is the new style pyJasper Interface"""
    
    def __init__(self, designdatalist, xpath, tempdir = TMPDIR):
        """Constructor
        designdatalist: a dict {"template_var_name": "JRXML data content"}.
        xpath:      The xpath expression passed to the report.
        """
        self.xpath = xpath
        self.tempdir = tempdir
        # depreciation check
        if isinstance(designdatalist, basestring):
            #warnings.warn("Passing the JRXML data as a string is deprecated. Use a dict of JRXML strings with template_var_name as key.", DeprecationWarning)
            # fix it anyway
            designdatalist = {'main': designdatalist}

        # Compile design if compiled version doesn't exist
        self.compiled_design = {}
        self.design_object = {}
        
        for design_name in designdatalist:
            self.design_object[design_name] = self._generate_design(designdatalist[design_name])
            self.compiled_design[design_name] = self._compile_design(self.design_object[design_name])

    def _generate_design(self, designdata):
        file = stream_to_java_file(self.tempdir, designdata)
        design = JasperDesign()
        design = JRXmlLoader.load(file)
        file.delete()
        return design
        
    def _compile_design(self, designobject):
        """Compile the report design if needed."""
        compiled = JasperCompileManager.compileReport(designobject)
        return compiled
    
    def generate(self, xmldata):
        """Generate Output with JasperReports."""

        # convert to a java.util.Map so it can be passed as parameters
        map = JMap()
        for i in self.compiled_design:
            map.put(i, self.compiled_design[i])
        
        xmlfile = stream_to_java_file(self.tempdir, xmldata)
        
        datasource = JRXmlDataSource(xmlfile)
        # add the original xml document source so subreports can make a new datasource.
        map['XML_FILE'] = xmlfile

        jasper_print = JasperFillManager.fillReport(self.compiled_design['main'], map, datasource)
        output = JasperExportManager.exportReportToPdf(jasper_print)
        xmlfile.delete()
        return output
        
