Jasper Reports for Odoo without jasper server

PRE REQUISITES!!!

1. PyJNIus python library
For ubuntu distributions, PyJNIus library can be easy instaled through PIP installer:
#sudo pip install Cython
#sudo pip install pyjnius
#sudo pip install dicttoxml

#sudo apt-get install cython

2. Environment variables
PyJNIus uses JNI interface, because of that you should set some environent variables: JAVA_HOME and CLASSPATH.
In ubuntu distributions, you can set it on /etc/environment file. Use your default editor and include the following lines (sudo access required)
The sample below is an example where the git repository was downloaded to "/opt/odoo/jasper" directory:

JAVA_HOME="/usr/lib/jvm/default-java"
CLASSPATH="/opt/odoo/jasper/jasper_odoo/java/*"

3. Temporary file
For report creation, project will create some temporary files. So, its important to create an specific folder todo so.
Also, the folder shold be ownded by de user wich runs odoo, normally odoo.
The sample below is an example for a jaspertemp folder created in "/var/" directory:

#sudo mkdir /var/jaspertemp
#sudo chown odoo:odoo /var/jaspertemp
#sudo chmod 777 /var/jaspertemp

4. Design basics
4.1. SubReports will be passed as parameters, so you need to create a parameter with type java.lang.Object and name matching the Subreport name
4.2. DataSources should have the name format: /odoo/model*/item - *Model name will replace "." by "_"

