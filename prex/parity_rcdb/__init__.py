from rcdb.model import ConditionType

class ParityConditions(object):
    """
    Default conditions are defined in rcdb
    Below are additional names for parity DB conditions
    """
    RUN_PRESTART_TIME = 'run_prestart_time'
    TOTAL_CHARGE = 'total_charge'
    BEAM_ENERGY = 'beam_energy'
    BEAM_CURRENT = 'beam_current'
    TARGET_TYPE = 'target_type'
    TARGET_ENCODER = 'target_encoder'
    IHWP = 'ihwp'
    RHWP = 'rhwp'
    WIEN_ANGLE = 'wien_angle'

def create_condition_types(db):
    """
    Checks if condition types listed in class exist in the database and create them if not
    :param db: RCDBProvider connected to database
    :type db: RCDBProvider

    :return: None
    """

    all_types_dict = {t.name: t for t in db.get_condition_types()}

    def create_condition_type(name, value_type, description=""):
        all_types_dict[name] if name in all_types_dict.keys() \
            else db.create_condition_type(name, value_type, description)

    # create condition type
    create_condition_type(ParityConditions.RUN_PRESTART_TIME, ConditionType.TIME_FIELD, "coda prestart time")
    create_condition_type(ParityConditions.BEAM_ENERGY, ConditionType.FLOAT_FIELD, "GeV")
    create_condition_type(ParityConditions.BEAM_CURRENT, ConditionType.FLOAT_FIELD, "Average beam current in uA")
    create_condition_type(ParityConditions.TOTAL_CHARGE, ConditionType.FLOAT_FIELD)
    create_condition_type(ParityConditions.TARGET_TYPE, ConditionType.STRING_FIELD)
    create_condition_type(ParityConditions.TARGET_ENCODER, ConditionType.FLOAT_FIELD, "Target encoder position")
    create_condition_type(ParityConditions.IHWP, ConditionType.STRING_FIELD, "Insertable half-wave plate In/Out")
    create_condition_type(ParityConditions.RHWP, ConditionType.STRING_FIELD, "Rotatable quarter-wave plate")
    create_condition_type(ParityConditions.WIEN_ANGLE, ConditionType.FLOAT_FIELD, "Wien angle in deg")
