import logging
import os, sys
import rcdb
import subprocess
from parity_rcdb import ParityConditions

from rcdb.log_format import BraceMessage as Lf

"""
EPICS variables

:IGL1I00OD16_16: Insertable waveplate, string (IN/OUT)
:psub_pl_pos: Rotating waveplate (Readback)
:HWienAngle: Horizontal wien angle
:VWienAngle: Vertical wien angle
:haBDSPOS: Target encoder pos. Not filled for APEX. APEXPOS is used. Need to check before PREX
"""

epics_list = {
    "HALLA:p":ParityConditions.BEAM_ENERGY,
    "IBC1H04CRCUR2":ParityConditions:BEAM_CURRENT,
    "APEXPOS":ParityConditions.TARGET_ENCODER,
    "IGL1I00OD16_16":ParityConditions.IHWP,
    "psub_pl_pos":ParityConditions.RQWP,
    "HWienAngle":ParityConditions.HWIEN,
    "VWienAngle":ParityConditions.VWIEN
}

def get_run_conds():

    conditions = {}

    for epics_name, cond_name in epics_list.iteritems():
        cmds = ['caget', '-t', epics_name]
        cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip()

        if "Invalid" in cond_out:
            print "ERROR Invalid epics channel name, check with caget again "
            cond_out = "-1"


        conditions[cond_name] = cond_out

    return conditions

def udpate_db_conds(db, run, reason):
    """
    add_conditions(run, name_values, replace=True/False)
    :name_values: dictionary or list of name-value pairs
    :replace: default is False?
    :Defined in provider.py, takes care of incorrect ConditionType
    """

    log = logging.getLogger('pvdb.udpate.epics')
    log.debug(Lf("Running 'update_rcdb_conds(db={},   run={})'", db, run))

    conditions = {}
    
    conditions.update( get_run_conds() )
    db.add_conditions(run, conditions, True)
    log.debug("Commited to DB. End of update_db_conds()")


if __name__ == "__main__":
    log = logging.getLogger('pvdb.update')               # create run configuration standard logger
    log.addHandler(logging.StreamHandler(sys.stdout))    # add console output for logger
    log.setLevel(logging.DEBUG)                          # print everything. Change to logging.INFO for less output

    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://pvdb@localhost/pvdb"

    db = rcdb.RCDBProvider(con_str)

    # argv = run number
    update_db_conds(db, int(sys.argv[1]), "update")
