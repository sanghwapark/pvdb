import os
import sys

# rcdb
import rcdb
from rcdb import ConfigurationProvider, UpdateContext, UpdateReasons, DefaultConditions
from rcdb.provider import RCDBProvider

# pvdb script
from scripts import post_update

def main():

    # DB Connection 
    #------------------------------------------
    update_parts = ["coda"]
    update_reason = "update"

    # Connection
    if "RCDB_CONNECTION" in os.environ:
        con_string = os.environ["RCDB_CONNECTION"]
    else:
        print ("ERROR! RCDB_CONNECTION is not set and is not given as a script parameter (-c)")
        sys.exit(2)

    # Open DB connection
    db = ConfigurationProvider(con_string)
    
    # Create update context
    update_context = rcdb.UpdateContext(db, update_reason)

    #------------------------------------------

    # Read the list

    """
    format:
    Run, #Config, Date/Time, RunType, Beam Mode, Beam Current, Beam Energy, Target, Log entries (HALOG, HAPLOG), Run analyzed?, Comment, Raster X/Y, Helicity, IHWP setting
    SAM 1 HVSAM 2 HVSAM 3 HVSAM 4 HVSAM 5 HVSAM 6 HVSAM 7 HVSAM 8 HV
    """

    run_list = sys.argv[1]
    with open('%s' % run_list, 'rb') as f:
        for line in f:
            values = []
            # ignore the first line
            if "Run #" in line:
                continue

            for item in line.split('\t'):
                if item != '\t':
                    values.append(item)

            run_type = values[3]
            comment = values[10]

            if '-' in values[0]:
                # Loop over the range
                run1=int(values[0].split('-')[0])
                run2=int(values[0].split('-')[1])
                for run in range(run1, run2+1):
                    print run
                    try:
                        post_update.update(str(run), update_parts, update_context)
                        db.add_condition(db.get_run(run), DefaultConditions.USER_COMMENT, comment)
                        if "junk" in run_type.lower():
                            db.add_condition(db.get_run(run), DefaultConditions.RUN_TYPE, "Junk", replace=True)
                    except Exception as ex:
                        print str(ex)

            else:
                if not values[0].isdigit(): 
                    continue
                else:
                    try:
                        run=values[0]
                        print run
                        post_update.update(run, update_parts, update_context)
                        db.add_condition(db.get_run(run), DefaultConditions.USER_COMMENT, comment)
                        if "junk" in run_type.lower():
                            db.add_condition(db.get_run(run), DefaultConditions.RUN_TYPE, "Junk", replace=True)
                    except Exception as ex:
                        print str(ex)

if __name__ == '__main__':
    main()
