import os
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
        self.event_count = None          # number of events in the run
        self.has_run_start = False       # Data file has event with tag = 18
        self.has_run_end = False         # Data file has event with tag = 20
        self.coda_config_file = None     # configID.xml with full path
        self.coda_session_file = None    # controlSessions.xml with full path
        self.user_comment = None         # Daq comment by user
        self.coda_session = None         # session name
        self.coda_last_file = None       # Last data filename
        self.coda_files_count = None     # Number of coda data files

def parity_configs(config_id):
    if config_id > 3:
        return "Unknown"
    config_name=["Injector", "CH", "ALL_PREX", "BMW_test"]
    return config_name[config_id]

def parse_start_run_data(session_file):
    """
    Parse coda session files
    
    Use current time as temporary start time

    Results to be filled from here:
    start_time, coda_session, run_config, run_type, run_number, coda_session_file
 
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

#    result.coda_config_file = config_file
    result.coda_session_file = session_file

    # Disabled configID.xml parser as we get everything we need from session file
    """
    # parse configID.xml 
    log.debug(Lf("Parsing CODA Config file '{0}'", config_file))
    parse_coda_config_file(result, config_file)
    """

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
    parse_result.run_config = config_name
#    if config_name != parse_result.run_config:
#        log.warning(Lf("config name mismatch {},{}", config_name, parser_result.run_config))
        
    # coda run number
    parse_result.run_number = int(xml_root.find("session").find("runnumber").text)

    return parse_result

def parse_coda_data_file(coda_file):
    """
    Intended to use mostly for post repair scripts
    Read data file directly

    coda event tag: 17 (prestart), 18 (start), 20 (end), 131 (epics)
    """

    parse_result = ParityCodaRunLogParseResult()

    cmds = ["evio2xml", "-ev", "17", "-ev", "18", "-ev", "20", "-xtod", "-max", "3", coda_file]

    out = check_output(cmds)

    xml_root = Et.ElementTree(Et.fromstring(out)).getroot()

    xml_check = xml_root.find("event")
    if xml_check is None:
        log.debug("No event with tag=17 or 18 found in file ")
        return parse_result

    for xml_result in xml_root.findall("event"):
        tag = xml_result.attrib["tag"]
        if tag == "17":
            xml_prestart_time = int(xml_result.text.split(None)[0])
            xml_run_number = int(xml_result.text.split(None)[1])
            xml_run_config = int(xml_result.text.split(None)[2])
            try:
                parse_result.prestart_time = datetime.fromtimestamp(xml_prestart_time)
                parse_result.run_number = xml_run_number
                parse_result.run_config = parity_configs(xml_run_config)
            except Exception as ex:
                log.warning("Unable to parse prestart information. Error: " + str(ex))
        elif tag == "18":
            xml_start_time = int(xml_result.text.split(None)[0])
            try:
                parse_result.start_time = datetime.fromtimestamp(xml_start_time).strftime("%Y-%m-%d %H:%M:%S")
                parse_result.has_run_start = True
            except Exception as ex:
                log.warning("Unable to parse start time. Error: " + str(ex))
        elif tag == "20":
            xml_end_time = int(xml_result.text.split(None)[0])
            xml_event_count = int(xml_result.text.split(None)[2])
            try:
                parse_result.end_time = datetime.fromtimestamp(xml_end_time).strftime("%Y-%m-%d %H:%M:%S")
                parse_result.event_count = xml_event_count
                parse_result.has_run_end = True
            except Exception as ex:
                log.warning("Unable to parse end time. Error: " + str(ex))
        else:
            continue

    # Most likely the run was not end properly
    if parse_result.has_run_end is False:
        try:
            # use last modified time instead
            mtime = os.path.getmtime(coda_file)
            parse_result.end_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            parse_result.has_run_end = False
        except Exception as ex:
            log.warning("Unable to get last modified time for the coda file: " + str(ex))

    # CHECK IF WE WOULD END UP WITH MULTIPLE DATA FILES FOR A RUN
    parse_result.coda_last_file = coda_file
    parse_result.coda_files_count = 1

    return parse_result

def runinfo_parser():
    
    # hard-coded path for runstart.info file
    runinfo_file="/adaqfs/home/apar/scripts/.runstart.info"
    ddict={}

    """
    Read runstart.info file and return dictionary
    input file is created by runstart.tcl

    Input file format:

    [Run]
    type:Test
    
    [beam]
    current:70
    energy:1.063
    polarization:90
    raster:off
    
    [comment]
    text:test of DAQ
    
    [dithering]
    magnet:off
    magnets:
    
    [leftarm]
    p:1.063
    theta:5
    
    [parity]
    feedback:off
    ihwp:in
    
    [rightarm]
    p:1.063
    theta:5
    
    [target]
    fanspeed:0 Hz
    type:No Target, Empty
    """

    with open(runinfo_file, "rb") as f:
        output = f.read()
        d_info = filter(None, [x.strip() for x in output.strip().split("[")])
        for l in d_info:
            fd = l.split("]\n",1)[0]
            ddict[fd] = {}
            for cont in [x.strip() for x in l.split("]\n",1)[1].split("\n")]:
                group=cont.split(":",1)[0]
                var=cont.split(":",1)[1]    
                ddict[fd][group] = var

    return ddict
