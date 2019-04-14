import os
import sys
import argparse
import socket
import glob
import logging

# rcdb stuff
import rcdb
from rcdb.log_format import BraceMessage as Lf
from rcdb import ConfigurationProvider, UpdateReasons
from rcdb import UpdateContext, UpdateReasons, DefaultConditions
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType, Condition

# rcdb stuff
from parity_rcdb import parity_coda_parser
import run_start

log = logging.getLogger('pvdb') # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))  # add console output for logger
log.setLevel(logging.INFO)  # DEBUG: print everything. Changed to logging. INFO for less output

def get_usage():
    return """
    Usage:
         post_repair.py --run <run_number> -c <db_connection_string> --update=[coda,epics] --reason=[start, update, end]
    """

def update():
    description = "Script for DB udpate after CODA run end"
    parser = argparse.ArgumentParser(description=description, usage=get_usage())
    parser.add_argument("--run", type=str, help="Run number")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--update", help="Comma separated, modules to update such as coda,epics", default="")
    parser.add_argument("--reason", help="Reason of the udpate: 'start', 'udpate', 'end' or ''", default="")
    parser.add_argument("-c", "--connection", help="connection string (eg, mysql://pvdb@localhost/pvdb)")
    args = parser.parse_args()

    # Connection
    if args.connection:
        con_string = args.connection
    elif "RCDB_CONNECTION" in os.environ:
        con_string = os.environ["RCDB_CONNECTION"]
    else:
        print ("ERROR! RCDB_CONNECTION is not set and is not given as a script parameter (-c)")
        parser.print_help()
        sys.exit(2)
    log.debug(Lf("con_string = '{}'", con_string))

   # What to update                                                                   
    update_parts = []                                                                  
    if args.update:                                                                    
        update_parts = args.update.split(',')                                          
    log.debug(Lf("update_parts = {}", update_parts))

   # Update reason
    update_reason = args.reason
    log.debug(Lf("update_reason = '{}'", update_reason))

    # Open DB connection
    db = ConfigurationProvider(con_string)
    
    # Create update context
    update_context = rcdb.UpdateContext(db, update_reason)


    coda_path = None
    coda_file_name = None

    host = socket.gethostname()
    if "adaq" in host:
        coda_path = "/adaq2/data1/apar/"
    elif "aonl" in host:
        coda_path = "/adaq2/data1/apar/"
    else:
        coda_path = "/cache/halla/parity/raw/"

    for files in glob.glob(coda_path+"*"+str(run)+"*.dat"):
        if not "parity18" in files:
            coda_file_name = files

    if coda_file_name is None:
        print "CODA file is not found", run
        sys.exit()

    coda_parse_result = parity_coda_parser.parse_coda_data_file(coda_file_name)

    if "coda" in update_parts:
        run_start.update_parity_coda_conditions(update_context, coda_parse_result)

if __name__ == "__main__":
    update()
