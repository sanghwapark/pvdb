import argparse
from subprocess import check_output
import xml.etree.ElementTree as Et
import logging
import datetime

log = logging.getLogger("pvdb.parity_coda_parser")
log.addHandler(logging.NullHandler())

class ParityCodaRunLogParseResult(object):
    def __init__(self):
        self.prestart_time = None        # CODA prestart time
        self.run_config = None           # Run type (0-4?)
        self.run_number = None           # Run number
        self.has_run_prestart = False    # File has event with tag = 17
        self.coda_last_file = None       # Last data filename
        self.coda_files_count = None     # Number of coda data files

def parse_run_prestart(parse_result, coda_file)

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
        log.debug("No event with tag=17 found in file")
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

    run_config = xml_root.find("event").text.split(None)[2]
    parse_result.run_config = run_config

    return parse_result
