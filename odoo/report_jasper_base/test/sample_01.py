# encoding: utf-8

import os
import sys

sys.path.insert(0, '../base')
from JasperInterface import JasperInterface

from jnius import autoclass

if __name__ == '__main__':
    jasper = JasperInterface('sample_01.jrxml', '', '/tmp/jaspertmp')
    open('./sample_01.pdf', 'wb').write(jasper.generate([], 'pdf'))