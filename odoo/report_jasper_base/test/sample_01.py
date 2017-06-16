# encoding: utf-8

import os
import sys

sys.path.insert(0, '../base')
from JasperInterface import JasperInterface

from jnius import autoclass

JRML_FILE = 'JsonCustomersReportSingle.jrxml'
JSON_FILE = 'northwind.json'
PDF_FILE  = 'JsonCustomersReportSingle.pdf'

if __name__ == '__main__':
    files = {}
    files['main'] = open(JRML_FILE).read()
    
    jasper = JasperInterface(files, '/var/jaspertemp')
    
    jsons_stream = open(JSON_FILE).read()
    
    try:
        os.remove(PDF_FILE)
    except:
        pass
    
    open(PDF_FILE, 'wb').write(jasper.generate(jsons_stream))