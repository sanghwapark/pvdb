import logging
import xml.etree.ElementTree as Et
from subprocess import check_output
from datetime import datetime
from rcdb.log_format import BraceMessage as Lf

log = logging.getLogger("pvdb.parity_coda_parser")
log.addHandler(logging.NullHandler())

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

def parse_start_run_data(config_file, session_file):
    """
    Parse coda config and session files
    
    Use current time as temporary start time

    Results to be filled from here:
    start_time, coda_session, run_config, run_type, run_number, coda_config_file, coda_session_file
 
    Return result
    """

    # start time
    script_start_time = datetime.now()

    result = ParityCodaRunLogParseResult()

    try:
        temp_start_time = script_start_time.strftime("%Y-%m-%d %H:%M:%S")
        result.start_time = temp_start_time
        result.has_run_start = True
    except Exception as ex:
        log.warning("Error with temp run start time " + str(ex))

    result.coda_config_file = config_file
    result.coda_session_file = session_file

    # parse configID.xml 
    log.debug(Lf("Parsing CODA Config file '{0}'", config_file))
    parse_coda_config_file(result, config_file)

    # parse controlSessions.xml
    log.debug(Lf("Parsing controlSessions file '{0}'", session_file))
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
        log.warning("No <runtype> section found in configID.xml")
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
        log.warning("No <session> section found in controlSessions.xml")
        return parse_result

    # coda session name
    parse_result.coda_session = xml_root.find("session").find("name").text

    # coda config name, check consistency with configID.xml
    config_name = xml_root.find("session").find("config").text
    if config_name != parse_result.run_config:
        log.warning(Lf("config name mismatch {},{}", config_name, parser_result.run_config))
        
    # coda run number
    parse_result.run_number = int(xml_root.find("session").find("runnumber").text)

    return parse_result

def parse_run_prestart(parse_result, coda_file):

    """
    Return run prestart time
    Parse directly from coda data file

    coda event tag: 17 (prestart), 18 (start), 20 (end)
    """

    cmds = ["evio2xml", "-ev", "17", "-xtod", coda_file]

    out = check_output(cmds)

    xml_root = Et.ElementTree(Et.fromstring(out)).getroot()
    xml_run_start = xml_root.find("event")

    # Sanity check
    if xml_run_start is None:
        log.debug("No event with tag=17 found in file ")
        return parse_result

    # Prestart time
    parse_result.has_run_prestart = True

    try:
        prestart_time = datetime.utcfromtimestamp(int(xml_root.find("event").text.split(None)[0]).strftime("%m/%d/%y %H:%M:%S"))
        parse_result.prestart_time = prestart_time
    except Exception as ex:
        log.warning("Unable to parse prestart time. Error: " + str(ex))

    # Run number
    run_number = xml_root.find("event").text.split(None)[1]
    parse_result.run_number = run_number

#    run_config = xml_root.find("event").text.split(None)[2]
#    parse_result.run_config = run_config

    return parse_result
