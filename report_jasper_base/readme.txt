Jasper Reports for Odoo without jasper server

PRE REQUISITES!!!

1. PyJNIus python library
For ubuntu distributions, PyJNIus library can be easy instaled through PIP installer:
#sudo pip instal Cython
#sudo pip instal pyjnius

2. Jasper Reports Jar file
The jasper version tested was 6.3.1, use that one preferencialy. Choose a folder for download and unzip (/opt for instance):
#cd /opt
#sudo wget https://sourceforge.net/projects/jasperreports/files/jasperreports/JasperReports%206.3.1/jasperreports-6.3.1.jar/download

3. Apache Common Collections
#cd /opt
#wget http://ftp.unicamp.br/pub/apache//commons/collections/binaries/commons-collections4-4.1-bin.zip

4. Environment variables
PyJNIus uses JNI interface, because of that you should set some environent variables: JAVA_HOME and CLASSPATH.
In ubuntu distributions, you can set it on /etc/environment file. Use your default editor and include the following lines (sudo access required)

JAVA_HOME="/usr/lib/jvm/default-java"
CLASSPATH="/opt/jasper/jasperreports-6.3.1/dist/jasperreports-6.3.1.jar:/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/rt.jar:/opt/apache-common/commons-collections4-4.1/commons-collections4-4.1.jar"


