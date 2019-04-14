import sys
import subprocess

import rcdb

def epics_for_run(run):

    start_time = None
    try:
        start_time = run.start_time
    except Exception as ex:
        print run, str(ex)
        return

    conditions = {}

    import epics_helper
    for epics_name, cond_name in epics_helper.epics_list.iteritems():
        try:
            start_time_str = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")
            end_time_str = datetime.strftime(run.end_time, "%Y-%m-%d %H:%M:%S")
            if "current" in cond_name:
                cmds = ["myStats", "-b", start_time_str , "-e", end_time_str, "-c", epics_name, "-r", "1:70", "-l", epics_name]
                cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)
                
                n = 0
                for line in cond_out.stdout:
                    n += 1
                    if n == 1:    # skip header
                        continue
                    tokens = line.strip().split()
                    if len(tokens) < 3:
                        continue
                        key = tokens[0]
                        value = tokens[2]
                    if value == "N/A":
                        value = 0
                    if key == epics_name:
                        conditions[cond_name] = value
            else:
                cmds = ["myget", "-c", epics_name, "-t", start_time_str]
                cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)                    

                for line in cond_out.stdout:
                    value = line.strip().split()[2]
                    if cond_name == "ihwp":
                        if value == "1":
                            conditions[cond_name] = "IN"
                        else:
                            conditions[cond_name] = "OUT"
                    elif cond_name == "helicity_pattern":
                        if value == "1":
                            conditions[cond_name] = "Quartet"
                        elif value == "2":
                            conditions[cond_name] = "Octet"
                        else:
                            conditions[cond_name] = "-999" # undefined
                    else:
                        conditions[cond_name] = value

        except Exception as e:
            log.warn(Lf("Error in epics request : '{}',{}'", cond_name, e))

    # Get target type condition
    conditions["target_type"] = epics_helper.get_target_name(conditions["target_encoder"])

    db.add_conditions(run, conditions, True)
