import os.path
import xml.etree.ElementTree as Et


xml_root = Et.parse("test.xml").getroot()

for xml_result in xml_root.findall("event"):
    tag = xml_result.attrib['tag']
    if tag == "17":
        prestart_time = int(xml_result.text.split(None)[0],16)
        run_number = int(xml_result.text.split(None)[1],16)
        run_config = int(xml_result.text.split(None)[2],16)
    elif tag == "18":
        start_time = int(xml_result.text.split(None)[0],16)
    else:
        continue

"""
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


#for controlSessions.xml
#
#>>> root = Et.parse("controlSessions.xml").getroot()
#>>> root[0][1].text
#'ALL_PREX'
#>>> root[0][2].text
#'1464'

"""
