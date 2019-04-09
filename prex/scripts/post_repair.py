import os
import sys
import argparse
import socket
import glob
import logging
from datetime import datetime

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
    run = args.run

    # Connection
    if args.connection:
        con_string = args.connection
    elif "RCDB_CONNECTION" in os.environ:
        con_string = os.environ["RCDB_CONNECTION"]
    else:
        print ("ERROR! RCDB_CONNECTION is not set and is not given as a script parameter (-c)")
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

    for files in glob.glob(coda_path+"*"+run+"*.dat"):
        if not "parity18" in files:
            coda_file_name = files

    if "coda" in update_parts and coda_file_name is None:
        print "CODA file is not found", run
        sys.exit()

    # Udpate db (coda)
    if "coda" in update_parts:
        # Parse coda info (start, end time, ..)
        coda_parse_result = parity_coda_parser.parse_coda_data_file(coda_file_name)
        run_start.update_parity_coda_conditions(update_context, coda_parse_result)

    # Update epics
    if "epics" in udpate_parts:
        log.debug(Lf("Update epics, run={}", run))
        if not "ops" in host:
            print "You probably don't have myget available from your machine"
            sys.exit()
        
        if not db.get_run(run):
            log.info(Lf("Run '{}' is not found in DB", run))
            return

        conditions = {}
        try:
            """
            myget -c[channel name] -t[time] 
            :if time is not specified, it returns data for last 1min
            :Use myStats to get the average current where the BCM reads 1-70 uA 
            excluding periods when the beam is off
            """
            import epics_helper
            for epics_name, cond_name in epics_helper.epics_list.iteritems():
                if cond_name == "beam_current":
                    cmds = ["myStats", "-b", run.start_time, "-e", run.end_time, "-c", epics_name, "-r", "1:70", "-l", epics_name]
                else:
                    cmds = ["myget", "-c", epics_name, "-t", run.start_time]
                    
                cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip()
                if "Invalid" in cond_out:
                    print "ERROR Invalid epics channel name, check with caget again "
                    cond_out = "-999"
                else:
                    conditions[cond_name] = cond_out
            # Get target type condition
            conditions["target_type"] = epics_helper.get_target_name(conditions["targer_encoder"])
        except Exception as e:
            log.warn(Lf("Error in epics request : '{}'", e))

        db.add_conditions(run, conditions, True)

    # >oO DEBUG log message
    db.add_log_record("",
                      "End of update. datetime: '{}'"
                      .format(datetime.now()), run_number)

if __name__ == "__main__":
    update()
