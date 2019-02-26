import os
import sys
import rcdb

from rcdb.model import ConditionType

"""
Example script for adding condition types
Modify the list below
"""
new_list = {
    "beam_energy": ConditionType.FLOAT_FIELD,
    "target_type": ConditionType.STRING_FIELD
}

if __name__ == '__main__':

    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://pvdb@localhost/pvdb"
    
    db = rcdb.RCDBProvider(con_str, check_version=False)

    for cnd_name, cnd_type in new_list.iteritems():
        db.create_condition_type(cnd_name, cnd_type, "")
