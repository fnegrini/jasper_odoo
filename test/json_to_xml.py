import json
import codecs
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString

if __name__ == '__main__':

	json_file = open('northwind.json')
	json_dict = json.load(json_file)
	xml_string = dicttoxml(json_dict, root=False, attr_type=False)
	xml = parseString(xml_string)
	file = codecs.open('northwind.xml', 'wb', 'utf-8')
	file.write(xml.toprettyxml())
	file.close()
