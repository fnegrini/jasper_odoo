# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64
import os

class Binary(http.Controller):
    
 @http.route('/web/binary/download_document', type='http', auth="public")
 @serialize_exception
 def download_document(self, path, filename='file.txt', delete_file=True, **kw):
     """ Download link for files stored as system files.
     :param str path: full path to binary file
     :param str filename: output file name
     :param bool delete_file: if True, delete file after send content
     :returns: :class:`werkzeug.wrappers.Response`
     """
     if not os.path.isfile(path):
         return request.not_found()
     else:
         #load file content
         file_bin = open(path,'rb').read()
         
         #delete file
         if delete_file:
             os.remove(path)
             
         # return request response to download file
         return request.make_response(file_bin,
                            [('Content-Type', 'application/octet-stream'),
                             ('Content-Disposition', content_disposition(filename))])