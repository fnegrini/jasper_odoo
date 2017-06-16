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
File = autoclass('java.io.File')
ByteArrayInputStream = autoclass('java.io.ByteArrayInputStream')

#JasperReport Classes
JRExporterParameter = autoclass('net.sf.jasperreports.engine.JRExporterParameter')
JasperExportManager = autoclass('net.sf.jasperreports.engine.JasperExportManager')
JasperFillManager = autoclass('net.sf.jasperreports.engine.JasperFillManager')
JsonDataSource = autoclass('net.sf.jasperreports.engine.data.JsonDataSource')
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
    
def stream_to_java_stream(stream):
    return ByteArrayInputStream(stream)   
    
class JasperInterface:
    """This is the new style pyJasper Interface"""
    
    def __init__(self, designdatalist, tempdir = TMPDIR):
        """Constructor
        designdatalist: a dict {"template_var_name": "JRXML data content"}.
        
        tempdir: a temporary directory to read and write files
        """
        
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
    
    def generate(self, jsondata):
        """Generate Output with JasperReports."""

        # convert to a java.util.Map so it can be passed as parameters
        map = JMap()
        for i in self.compiled_design:
            map.put(i, self.compiled_design[i])
        
        # create datasource        
        jsonfile = stream_to_java_file(self.tempdir, jsondata)
        datasource = JsonDataSource(jsonfile)
        
        # passing base parameters
        map.put('net.sf.jasperreports.json.date.pattern', 'yyyy-MM-dd')
        map.put('net.sf.jasperreports.json.number.pattern', '#,##0.##')
        map.put('net.sf.jasperreports.json.source', jsonfile.toString())
        
        # generate report to file
        jasper_print = JasperFillManager.fillReport(self.compiled_design['main'], map, datasource)
        tmp_filename = os.path.join(self.tempdir, gen_uuid() + '.pdf')
        JasperExportManager.exportReportToPdfFile(jasper_print, tmp_filename)
        jsonfile.delete()
        
        # export pdf stream and delete temporary file
        output = open(tmp_filename).read()
        os.remove(tmp_filename)
        
        return output
        
