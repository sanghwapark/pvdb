import os.path
import xml.etree.ElementTree as Et

#check if file exists
os.path.isfile(filepath)

xml_root = Et.parse("configID.xml").getroot()

# name
coda_config = xml_root[0][0]
run_type = xml_root[0][1]

# check if child exists
xml_result = xml_root.find("session").find("name")
if xml_result is None:
    print "warning"
    return parse_result

coda_name = xml_root.find("session").find("name").text
coda_runnum = int(xml_root.find("session").find("runnumber").text)


"""
for controlSessions.xml

>>> root = Et.parse("controlSessions.xml").getroot()
>>> root[0][1].text
'ALL_PREX'
>>> root[0][2].text
'1464'

"""
