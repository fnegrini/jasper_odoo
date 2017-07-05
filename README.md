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
For correct use of JNI interface, environment variable JAVA_HOME should be set and, for correct functionality of this module, CLASS_PATH should address the /java folder. For ubuntu distributions, you can set the environment variables on /etc/enviornment file. 

##JAVA_HOME
Below a default value for this variable, check your Java installation first!
```
JAVA_HOME="/usr/lib/jvm/default-java"
```
##CLASS_PATH
To easy distribute this module, all jar files were inserted in this repository under /java folder. Check the location where you clonned it and set CLASS_PATH to this folder. Bellow an example if the repository was clonned in /opt/odoo/jasper folder:
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

# Designing your first report
TO DO!

# Working with subreports
TO DO!
