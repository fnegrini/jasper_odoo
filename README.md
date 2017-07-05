# jasper_odoo
Jasper Reports for Oddo (No Jasper Server needed)

# Before insall this module

## Install python packages

### pyJNIus package
For ubuntu distributions, PyJNIus library can be installed through PIP installer:

```
#sudo pip install Cython
#sudo pip install pyjnius
```
### dicttoxml package
For ubuntu distributions, dicttoxml can be installed through PIP installer:
```
#sudo pip install dicttoxml
```
## Check/create environment variables
For ubuntu distributions, you can set the environment variables at /etc/environment file. Edit this file in order to set the variables every time your system run.

##JAVA_HOME
For correct use of JNI interface, environment variable JAVA_HOME should be set. Below a default value for this variable, check your Java installation first!
```
JAVA_HOME="/usr/lib/jvm/default-java"
```
##CLASSPATH
To easy distribute this module, all jar files were inserted in this repository under /java folder. So, the easier way to JNI access these files is set CLASSPATH with this folder. Bellow an example of CLASSPATH if the repository was clonned in /opt/odoo/jasper/ folder:
```
CLASSPATH="/opt/odoo/jasper/jasper_odoo/java/*"
```
## Temporary folder
When this module is in use, it creates temporary files in order to generate the reports. A temporary folder with read an write access to odoo user is needed. The insallation sugest /var/jaspertemp/ (check odoo system parameters after module installed), but you can set any other folder. Below a set of commands to create and set access:
```
#sudo mkdir /var/jaspertemp
#sudo chown odoo:odoo /var/jaspertemp
#sudo chmod u+rw /var/jaspertemp
```

# Designing a report
After activate the *developer mode*, you can create reports under the action -> reports on Settings menu.
Create a new folder choosing _Jasper_ as *Report Type*. After that, new options appear on *Jasper" tab.

## Accelerate the design using a XML sample file
To generate Jasper reports without need to a connection to PostgreSQL, this module generates XML documents as source to your reports. You can create a XML sample file to accelerate the design of your report by clicking the "Get XML sample" button under model field.
- Set the model field to the model you want to create
- Under Model tab on Jasper tab, set the fields you want to use. If none is set, all fields will be exported (not a good idea!)

The XML structure is something like this:
```XML
<?xml version="1.0" ?>
<odoo>
	<model_name>
		<item>
			<field1>value_of_field1</field1>
			<field2>value_of_field2</field2>
			<many2one_field.subfield>value subfield</many2one_field.subfield>
		</item>
			...
	</model_name>
	<one2many_field>
		<item>
			<model_name>id_of_model</model_name>
			<field1>value_of_field1</field2>
			<field2>value_of_field2</field2>
		</item>
			...
	<one2many_field>
</odoo>
```
### Base fields
Base fields are exported to XML file as is. Take care with binary fields, they are exported as Base64.

### Many2one fields
Many2one fields are exported as base fields on the source with the name _field.subfield_
You can choose the subfields of your model on the fields screen.

### One2Many fields and Many2Many fields
One2Many fields and Many2Many fields are exported as an extra source. The reference to the model is created with a field with the model name on this extra source. You can use thees extra source on your subreport (check next topic)

## Uploading Jasper fields
Once you designed and tested your Jasper report with the XML sample file. You need only to upload the *jrxml* and *jasper* files to the *Design file (jrxml)* and *Compiled file (.jasper)* fields respectively on the report action and save your report. After that just click on "Add report to model" button and done! Go to your folder menu, select one or several records and call your jasper report.

# Working with subreports
TO DO!
