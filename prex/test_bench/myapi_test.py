import subprocess
import epics_helper

for epics_name, cond_name in epics_helper.epics_list.iteritems():
    cmds = ""
    if cond_name == "beam_current" or cond_name=="HallC current":
        cmds = ["myStats", "-b", "2019-04-09 10:00:00", "-e", "2019-04-09 10:30:00", "-c", epics_name, "-r", "0.5:70", "-l", epics_name]
    else:
        cmds = ["myget", "-c", epics_name, "-t", "2019-04-09 14:00:00"]
    cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)

    if "current" in cond_name:
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
                print cond_name, value
    else:
        for line in cond_out.stdout:
            print cond_name, line.strip().split()[2]
