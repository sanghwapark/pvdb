from datetime import datetime
import argparse
import xml.etree.ElementTree as Et

parser = argparse.ArgumentParser(description="coda parser test")
parser.add_argument("config_file", type=str, help="config xml file full path")
parser.add_argument("session_file", type=str, help="session xml file full path")
args=parser.parse_args()

class ParityCodaRunLogParseResult(object):
    def __init__(self):
        self.start_time = None           # run start time
        self.end_time = None             # run end time
        self.prestart_time = None        # run prestart time
        self.run_config = None           # Run config (ALL, INJ, CH..)
        self.run_type = None             # Run type (production, junk, ..)
        self.run_number = None           # Run number
        self.has_run_start = False       # Data file has event with tag = 18
        self.has_run_end = False         # Data file has event with tag = 20?
        self.coda_config_file = None     # configID.xml with full path
        self.coda_session_file = None    # controlSessions.xml with full path
        self.coda_session = None         # session name
        self.coda_last_file = None       # Last data filename
        self.coda_files_count = None     # Number of coda data files

def main():
    parse_result = parse_start_run_data(args.config_file, args.session_file)
    print parse_result.start_time, parse_result.run_number, parse_result.run_config, parse_result.run_type, parse_result.coda_session

def parse_start_run_data(config_file, session_file):
    # start time
    script_start_time = datetime.now()

    result = ParityCodaRunLogParseResult()

    try:
        temp_start_time = script_start_time.strftime("%Y-%m-%d %H:%M:%S")
        result.start_time = temp_start_time
    except Exception as ex:
        print ("Error with temp run start time " + str(ex))
        
    # parse configID.xml 
    parse_coda_config_file(result, config_file)

    # parse controlSessions.xml
    parse_coda_session_file(result, session_file)

    return result

def parse_coda_config_file(parse_result, filename):

    """
    Open and parse coda config xml file
    Return parse_result

    Example structure:
    <control>
       <runtype>
          <name>ALL_PREX</name>
          <id>1</id>
       </runtype>
    </control>
    """

    xml_root = Et.parse(filename).getroot()

    xml_result = xml_root.find("runtype").text
    if xml_result is None:
        return parse_result

    parse_result.run_config = xml_root.find("runtype").find("name").text
    parse_result.run_type = int(xml_root.find("runtype").find("id").text)

    return parse_result

def parse_coda_session_file(parse_result, filename):

    """
    Open and parse controlSessions.xml file
    Return parse_result

    Example structure:
    <control>
       <session>
          <name>par1</name>
          <config>ALL_PREX</config>
          <runnumber>####</runnumber>
       </session>
    </control>
    """

    xml_root = Et.parse(filename).getroot()
    xml_result = xml_root.find("session").text
    
    if xml_result is None:
        print ("No <session> section found in controlSessions.xml")
        return parse_result

    # coda session name
    parse_result.coda_session = xml_root.find("session").find("name").text

    # coda config name, check consistency with configID.xml
    config_name = xml_root.find("session").find("config").text
    if config_name != parse_result.run_config:
        print "config name mismatch: %s, %s" % (config_name, parse_result.run_config)
        
    # coda run number
    parse_result.run_number = int(xml_root.find("session").find("runnumber").text)

    return parse_result
    
if __name__== '__main__':
    main()
