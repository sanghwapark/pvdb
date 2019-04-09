import subprocess

from rcdb.model import ConditionType, Condition
from parity_rcdb import ParityConditions

epics_list = {
    "HALLA:p":ParityConditions.BEAM_ENERGY,
    "IBC1H04CRCUR2":ParityConditions.BEAM_CURRENT,
    "APEXPOS":ParityConditions.TARGET_ENCODER,
    "IGL1I00OD16_16":ParityConditions.IHWP,
    "psub_pl_pos":ParityConditions.RQWP,
    "HWienAngle":ParityConditions.HWIEN,
    "VWienAngle":ParityConditions.VWIEN,
    "ibcm1":"HallC current"
}

"""
for epics_name, cond_name in epics_list.iteritems():
    cmds = ['caget', '-t', epics_name]
    test_str = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    for line in test_str.stdout.readlines():
        print line
"""
