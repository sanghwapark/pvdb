import os
import sys
import logging
import argparse
from datetime import datetime
import traceback

# rcdb
import rcdb
from rcdb.provider import RCDBProvider
from rcdb.log_format import BraceMessage as Lf

# prex script
from scripts import epics_helper

log = logging.getLogger('pvdb.update')                        # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))             # add console output for logger

def update_run(db, run_number, reason):

    if not db.get_run(run_number):
        log.warn(Lf("Run '{}' is not found in DB", run_number))
        return

    run = db.get_run(run_number)

    start_time = None
    try:
        start_time = run.start_time
    except Exception as ex:
        log.warn(Lf("Error in start_time request : run='{}', '{}'", run_number, e))

    if start_time is not None:
        try:
            conditions = epics_helper.update_db_conds(db, run, reason)
#            conditions = epics_helper.mya_get_run_conds(run, log)

            db.add_log_record("", 
                              "Update epics. beam_current:'{}', time: '{}'"
                              .format(conditions["beam_current"], datetime.now()), run_number)

        except Exception as ex:
            log.warn("Update epics failed :" + str(ex))
            db.add_log_record("",
                              "ERROR update epics. Error type: '{}' message: '{}' trace: '{}' "
                              "||time: '{}'"
                              .format(type(ex), ex.message, traceback.format_exc(),
                                      datetime.now()), run_number)

    log.debug("End of Update")

def print_conds(db, run_number):
    
    if not db.get_run(run_number):
        log.warn(Lf("Run '{}' is not found in DB", run_number))
        return

    run = db.get_run(run_number)

    start_time = None
    try:
        start_time = run.start_time
    except Exception as ex:
        log.warn(Lf("Error in start_time request : run='{}', '{}'", run_number, e))

    if start_time is not None:
        try:
            conditions = epics_helper.mya_get_run_conds(run, log)
            print run_number, conditions
        except Exception as ex:
            log.warn("Getting conditions failed :" + str(ex))

if __name__=="__main__":

    parser = argparse.ArgumentParser("update epics conditions")
    parser.add_argument("--run-range", type=str, help="Run range to update")
    parser.add_argument("--test", type=bool, help="no db update, print conditions when True", default=False)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    print(args)

    test_flag = args.test

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO) #DEBUG: print everything

    brun = args.run_range.split('-')[0]
    erun = args.run_range.split('-')[1]

    #connection
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://pvdb@localhost/pvdb"

    db = RCDBProvider(con_str)

    if test_flag:
        for run_number in range(int(brun), int(erun)+1):
            print_conds(db, run_number)
    else:

        for run_number in range(int(brun), int(erun)+1):
            update_run(db, run_number, "update")
