import subprocess

epics_list = {
    'HALLA:p',
    'IGL1I00OD16_16',
    'psub_pl_pos',
    'APEXPOS',
    'HWienAngle',
    'VWienAngle'
}

for epics_name in epics_list:
    cmds = ['caget', '-t', epics_name]
    test_str = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    for line in test_str.stdout.readlines():
        print line
