import logging
import os
import sys
import argparse
from datetime import datetime
import time
import traceback

# rcdb stuff
import rcdb
from rcdb.log_format import BraceMessage as Lf
from rcdb import ConfigurationProvider, UpdateReasons
from rcdb import UpdateContext, UpdateReasons, DefaultConditions
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType, Condition

# parity stuff
from parity_rcdb import parity_coda_parser
from parity_rcdb import ParityConditions
from parity_rcdb.parity_coda_parser import ParityCodaRunLogParseResult

# helper script
import epics_helper

"""
Update script at run start

Things to consider for the future:
1) adding interprocess_lock: to avoid duplicated records and ensure only one such process is running

"""

# Test flag, it will print out parse result but no udpate to DB
test_mode = True

def get_usage():
    return """

    Usage:
    minimal:
    run_start.py <session_xml_file>
    
    run_start.py <session_xml_file> -c <db_connection_string> --update=coda,epics --reason=[start, update, end]
    
    example:
    run_start.py controlSessions.xml
    
    <db_connection_string> - is optional. But if it is not set, RCDB_CONNECTION environment variable should be set

    """
    
def parse_start_run_info():
    script_start_clock = time.clock()
    script_start_time = time.time()

    log = logging.getLogger('pvdb') # create run configuration standard logger
    log.addHandler(logging.StreamHandler(sys.stdout))  # add console output for logger
    log.setLevel(logging.INFO)  # DEBUG: print everything. Changed to logging. INFO for less output

    parser = argparse.ArgumentParser(description= "Update PVDB")
#    parser.add_argument("config_xml_file", type=str, help="full path to configID.xml file")
    parser.add_argument("session_xml_file", type=str, help="full path to controlSessions.xml file")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--update", help="Comma separated, modules to update such as coda,epics", default="coda")
    parser.add_argument("--reason", help="Reason of the udpate: 'start', 'udpate', 'end' or ''", default="start")
    parser.add_argument("-c", "--connection", help="connection string (eg, mysql://pvdb@localhost/pvdb)")
    args = parser.parse_args()

    # Set log level
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # coda xml files
#    config_xml_file = args.config_xml_file
#    log.debug(Lf("config_xml_file = '{}'", config_xml_file))
    session_xml_file = args.session_xml_file
    log.debug(Lf("session_xml_file = '{}' ", session_xml_file))
    
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

    # Parse coda files and save to DB
    log.debug(Lf("Parsing coda__xml_files='{}'", session_xml_file))

    coda_parse_result = parity_coda_parser.parse_start_run_data(session_xml_file)
    run_number = coda_parse_result.run_number

    # >oO DEBUG log message
    now_clock = time.clock()
    db.add_log_record("", "Start Run Script: Parsed xml_files='{}'. run='{}'"
                      .format(session_xml_file, run_number), run_number)

    # Parse runstart.info (Run type, comment)
    dict_info = parity_coda_parser.runinfo_parser()
    if bool(dict_info["Run"]["type"]):
        coda_parse_result.run_type = dict_info["Run"]["type"]
    if bool(dict_info["comment"]["text"]):
        coda_parse_result.user_comment = dict_info["comment"]["text"]

    # Coda conditions to DB
    if "coda" in update_parts:
        log.debug(Lf("Adding coda conditions to DB", ))
        if test_mode:
            print "Run number:\t", coda_parse_result.run_number
            print "Start time:\t", coda_parse_result.start_time
            print "Run config:\t", coda_parse_result.run_config
            print "Run type:\t", coda_parse_result.run_type
            print "Comment:\t", coda_parse_result.user_comment
        else:
            update_parity_coda_conditions(update_context, coda_parse_result)
    else:
        log.debug(Lf("Skipping to add coda conditions to DB. Use --update=...,coda to update it", ))

    """
    # Do we want to save files to DB?
    log.debug(Lf("Adding coda_xml_log_file to DB", ))
    db.add_configuration_file(run_number, coda_xml_log_file, overwrite=True, importance=ConfigurationFile.IMPORTANCE_HIGH)
    """
        
    # EPICS Update
    # Get EPICS variables
    epics_start_clock = time.clock()
    if test_mode:
        conditions = epics_helper.get_run_conds()
        print conditions
    else:
        if 'epics' in update_parts and run_number:
            # noinspection PyBroadException
            try:
                conditions = epics_helper.update_db_conds(db, run_number, update_reason)
                epics_end_clock = time.clock()
                # >oO DEBUG log message
                if "beam_current" in conditions:
                    db.add_log_record("",
                                      "Update epics. beam_current:'{}', time: '{}'"
                                      .format(conditions["beam_current"], datetime.now()), run_number)
                    
            except Exception as ex:
                log.warn("update_epics.py failure. Impossible to run the script. Internal exception is:\n" + str(ex))
                epics_end_clock = time.clock()

                # >oO DEBUG log message
                db.add_log_record("",
                                  "ERROR update epics. Error type: '{}' message: '{}' trace: '{}' "
                                  "||epics_clocks:'{}' clocks:'{}' time: '{}'"
                                  .format(type(ex), ex.message, traceback.format_exc(),
                                          epics_end_clock - epics_start_clock, epics_end_clock - script_start_clock,
                                          datetime.now()), run_number)
                    
    log.debug("End of update")

    # >oO DEBUG log message
    now_clock = time.clock()
    if not test_mode:
        db.add_log_record("",
                          "End of update. Script proc clocks='{}', wall time: '{}', datetime: '{}'"
                          .format(now_clock - script_start_clock,
                                  time.time() - script_start_time,
                                  datetime.now()), run_number)

def update_parity_coda_conditions(context, parse_result):

    # create run configuration standard logger
    log = logging.getLogger('pvdb.update_coda')         

    # Some assertions in the beginning
    assert isinstance(parse_result, ParityCodaRunLogParseResult)
    assert isinstance(context, UpdateContext)
    assert isinstance(context.db, RCDBProvider)

    db = context.db
    
    if parse_result.run_number is None:
        log.warn("parse_result.run_number is None. (!) Run. Number. Is. None!!!")
        return
    
    """
    # enable later
    if context.reason == UpdateReasons.END and not db.get_run(parse_result.run_number):
        log.info(Lf("Run '{}' is not found in DB. But the update reason is end of run. "
                    "Considering there where no GO. Only prestart and then Stop ", parse_result.run_number))
        return
    """

    run = db.create_run(parse_result.run_number)

    conditions = []

    # Run type condition
    if parse_result.run_type is not None:
        conditions.append((DefaultConditions.RUN_TYPE, parse_result.run_type))

    # Session 
    if parse_result.coda_session is not None:
        conditions.append((DefaultConditions.SESSION, parse_result.coda_session))

    # config name
    if parse_result.run_config is not None:
        conditions.append((DefaultConditions.RUN_CONFIG, parse_result.run_config))

    #These need to be udpated by Run END
    # Set the run as not properly finished (We hope that the next section will
    if parse_result.has_run_end is not None:
        conditions.append((DefaultConditions.IS_VALID_RUN_END, parse_result.has_run_end))

    # The number of events in the run
    if parse_result.event_count is not None:
        conditions.append((DefaultConditions.EVENT_COUNT, parse_result.event_count))
        
    # Daq comment by user
    if parse_result.user_comment is not None:
        conditions.append((DefaultConditions.USER_COMMENT, parse_result.user_comment))

    # Run prestart time
    if parse_result.prestart_time is not None:
        conditions.append((ParityConditions.RUN_PRESTART_TIME, parse_result.prestart_time))

    # Run length
    if parse_result.has_run_end == True and parse_result.has_run_start == True:
        total_run_time = datetime.strptime(parse_result.end_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(parse_result.start_time, "%Y-%m-%d %H:%M:%S")
        conditions.append((DefaultConditions.RUN_LENGTH, total_run_time.seconds))
        #start and end time is read from run table, so no need to add these conditions here
#        conditions.append((DefaultConditions.RUN_START_TIME, datetime.strptime(parse_result.start_time,"%m/%d/%y %H:%M:%S")))
#        conditions.append((DefaultConditions.RUN_END_TIME, datetime.strptime(parse_result.end_time, "%m/%d/%y %H:%M:%S")))

    """
    # Conditions not added currently
    # Filename of the last evio file written by CODA ER
    if parse_result.coda_last_file is not None:
        conditions.append(('evio_last_file', parse_result.evio_last_file))

    # The number of evio files written by CODA Event Recorder
    if parse_result.coda_files_count is not None:
        conditions.append(('evio_files_count', parse_result.evio_files_count))
    """

    # SAVE CONDITIONS
    db.add_conditions(run, conditions, replace=True)

    log.info(Lf("update_coda: Saved {} conditions to DB", len(conditions)))

    # Start and end times
    if parse_result.start_time is not None:
        run.start_time = parse_result.start_time     # Time of the run start
        log.info(Lf("Run start time is {}", parse_result.start_time))

    if parse_result.end_time is not None:
        run.end_time = parse_result.end_time         # Time of the run end
        log.info(Lf("Run end time is {}. Set from end_time record", parse_result.end_time))

    """
    # update_time is not currently included in ParityCodaRunLogParseResult
    else:
        if parse_result.update_time is not None:
            run.end_time = parse_result.update_time  # Fallback, set time when the coda log file is written as end time
            log.info(Lf("Run end time is {}. Set from update_time record", parse_result.update_time))
    """

    db.session.commit()     # Save run times

if __name__== '__main__':
    parse_start_run_info()
