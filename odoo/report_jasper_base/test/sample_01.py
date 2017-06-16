# encoding: utf-8

import os
import sys
import json

sys.path.insert(0, '../base')
from JasperInterface import JasperInterface

from jnius import autoclass

JRXML_FILE = 'CustomersReportSingle.jrxml'
JSON_FILE = 'northwind.json'
PDF_FILE  = 'CustomersReportSingle.pdf'
TMP_DIRECTORY = '/var/jaspertemp'

if __name__ == '__main__':
    files = {}
    files['main'] = open(JRXML_FILE).read()
    
    jasper = JasperInterface(files, TMP_DIRECTORY)
    
    json_dict = json.load(open(JSON_FILE))
    
    try:
        os.remove(PDF_FILE)
    except:
        pass
    
    open(PDF_FILE, 'wb').write(jasper.generate(json_dict))