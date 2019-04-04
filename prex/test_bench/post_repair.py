import os
import sys
import argparse
import socket

from parity_rcdb import parity_coda_parser

def get_usage():
    return """
    Usage:
         post_run_update.py <run_number> -c <db_connection_string> --update --reason=[start, end, repair]
    """

def update(run):
    """
    description = "Script for PVDB udpates after CODA run end"
    parser = argparse.ArgumentParser(description=description, usage=get_usage())
    parser.add_argument("--run", type=str, help="Run number")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
#    parser.add_argument("--update", help="Comma separated, modules to update such as coda,epics", default="")
#    parser.add_argument("--reason", help="Reason of the udpate: 'start', 'udpate', 'end' or ''", default="")
    parser.add_argument("-c", "--connection", help="connection string (eg, mysql://pvdb@localhost/pvdb)")
    args = parser.parse_args()
    """

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
    print coda_parse_result.run_number, coda_parse_result.end_time



if __name__ == "__main__":
    update()
