import os
import sys
from datetime import datetime

import rcdb
from rcdb import ConfigurationProvider

run=sys.argv[1]
tstart=datetime.strptime("2019-03-15 10:55:49", "%Y-%m-%d %H:%M:%S")
tend=datetime.strptime("2019-03-15 11:53:13", "%Y-%m-%d %H:%M:%S")

con_str = os.environ["RCDB_CONNECTION"] \
    if "RCDB_CONNECTION" in os.environ.keys() \
    else "mysql://pvdb@localhost/pvdb"

db = ConfigurationProvider(con_str)

db.add_run_start_time(run, tstart)
db.add_run_end_time(run, tend)
db.add_log_record("", "Manually insert time info to DB, run = '{}'".format(run), run)
