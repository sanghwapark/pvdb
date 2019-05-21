import logging
import os, sys
import rcdb
import subprocess
import socket
from datetime import datetime

#pvdb
from parity_rcdb import ParityConditions

#rcdb stuff
from rcdb.model import ConditionType, Condition
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
    "IBC1H04CRCUR2":ParityConditions.BEAM_CURRENT,
    "APEXPOS":ParityConditions.TARGET_ENCODER,
    "IGL1I00OD16_16":ParityConditions.IHWP,
    "psub_pl_pos":ParityConditions.RQWP,
    "HWienAngle":ParityConditions.HWIEN,
    "VWienAngle":ParityConditions.VWIEN,
    "HELPATTERNd":ParityConditions.HELICITY_PATTERN,
    "HELFREQ":ParityConditions.HELICITY_FREQUENCY
}

def get_run_conds():
    conditions = {}

    for epics_name, cond_name in epics_list.iteritems():
        cmds = ['caget', '-t', epics_name]
        cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip()
        if "Invalid" in cond_out:
            print "ERROR Invalid epics channel, check with caget again:\t", epics_name
            cond_out = "-999"

        conditions[cond_name] = cond_out

    conditions["target_type"] = get_target_name(conditions["target_encoder"])

    return conditions

def mya_get_run_conds(run, log):
    
    conditions = {}

    start_time_str = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")
    for epics_name, cond_name in epics_list.iteritems():
        end_time_str = datetime.strftime(run.end_time, "%Y-%m-%d %H:%M:%S")

        # skip period when APEXPOS was not available 
        if cond_name == "target_encoder" and start_time_str < "2019-02-18 08:00:00":
            continue
        if "current" in cond_name:
            try:
                cmds = ["myStats", "-b", start_time_str , "-e", end_time_str, "-c", epics_name, "-r", "1:80", "-l", epics_name]
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
            except Exception as ex:
                log.warn(Lf("Error in beam_current request : '{}'", e))
                conditions["beam_current"] = "-999"
        else:
            try:
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
                conditions[cond_name] = "-999"

    # Get target type condition
    if start_time_str > "2019-02-18 08:00:00":
        conditions["target_type"] = get_target_name(conditions["target_encoder"])

    return conditions

def print_conds():
    conditions = get_run_conds()
    print conditions["target_type"]

def get_target_name(enc_pos):
    """
    Compare encoder position with target BDS table
    Return corresponding target name
    Based on the APEX target system for now
    Need to udpate for PREX
    """

    if enc_pos == "-999":
        return "Invalid"

    tar_bds = [-18526,
               3197,
               47255,
               165223,
               297861,
               427509,
               603200,
               710189,
               994363,
               1248916,
               1722284,
               1743072]

    tar_name = ["Hard_Stop",
                "Up-hole_2x2",
                "Down-hole_2x2",
                "Optics 1 (UP)",
                "Optics 2 (MIDDLE)",
                "Optics 3 (DOWN)",
                "W wire (for BW)",
                "W wires",
                "HOME",
                "Carbon 0.53%RL",
                "Tungsten 2.8%RL",
                "Hard_Stop"]

    bds_close = min(tar_bds, key=lambda x:abs(x-float(enc_pos)))

    if abs(float(enc_pos)-bds_close) > 100:
        return "Unknown"
    else:
        tar_index = tar_bds.index(bds_close)
        return tar_name[tar_index]


def update_db_conds(db, run, reason):
    """
    add_conditions(run, name_values, replace=True/False)
    :name_values: dictionary or list of name-value pairs
    :replace: default is False?
    :Defined in provider.py, takes care of incorrect ConditionType
    """

    log = logging.getLogger('pvdb.update.epics')
    log.debug(Lf("Running 'update_rcdb_conds(db={},   run={})'", db, run))

    conditions = {}
    
    if reason == "start":
        conditions.update( get_run_conds() )
    if reason == "update" or reason == "end":
        conditions.update( mya_get_run_conds(run, log) )

    db.add_conditions(run, conditions, True)
    log.debug("Commited to DB. End of update_db_conds()")

    return conditions


if __name__ == "__main__":
    # check if it would have caget available 
    host = socket.gethostname()
    if not ("adaq" in host or "aonl" in host or "ops" in host):
        print "You may  not have caget available. Check first"
        sys.exit()

    log = logging.getLogger('pvdb.update')               # create run configuration standard logger
    log.addHandler(logging.StreamHandler(sys.stdout))    # add console output for logger
    log.setLevel(logging.DEBUG)                          # print everything. Change to logging.INFO for less output

    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://pvdb@localhost/pvdb"

    db = rcdb.RCDBProvider(con_str)

    # argv = run number
    update_db_conds(db, int(sys.argv[1]), "update")
