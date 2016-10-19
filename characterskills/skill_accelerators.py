#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\characterskills\skill_accelerators.py
from .attribute import ATTRIBUTEBONUS_BY_ATTRIBUTEID
import gametime

class BoosterInfo(object):

    def __init__(self, expiry_time, booster_bonus, booster_type_id):
        self.expiry_time = expiry_time
        self.booster_bonus = booster_bonus
        self.booster_type_id = booster_type_id

    def get_attribute_bonus(self, attribute_id):
        return self.booster_bonus.get(attribute_id, 0)

    def is_active_at_time(self, start_time):
        return self.expiry_time and self.expiry_time > start_time

    def __repr__(self):
        return 'BoosterInfo(%s)' % ', '.join(('%s=%s' % (k, v) for k, v in self.__dict__.iteritems()))

    def get_inverted_bonuses(self):
        return {attribute_id:-bonus_value for attribute_id, bonus_value in self.booster_bonus.iteritems()}


class SkillAcceleratorBoosters(object):

    def __init__(self, get_type_attribute_func):
        self._boosters = []
        self._get_current_time_func = None
        self._get_type_attribute_func = get_type_attribute_func
        self.reset_current_time_function()

    def set_current_time_function(self, function):
        self._get_current_time_func = function

    def reset_current_time_function(self):
        self._get_current_time_func = gametime.GetWallclockTime

    def get_current_time(self):
        return self._get_current_time_func()

    def get_type_attribute(self, type_id, attribute_id):
        return self._get_type_attribute_func(type_id, attribute_id)

    def add_booster(self, expiry_time, booster_type_id):
        booster_bonus = {}
        for attribute_id, bonus_attribute_id in ATTRIBUTEBONUS_BY_ATTRIBUTEID.iteritems():
            booster_bonus[attribute_id] = self.get_type_attribute(booster_type_id, bonus_attribute_id)

        self._boosters.append(BoosterInfo(expiry_time, booster_bonus, booster_type_id))

    def get_attribute_bonus(self, attribute_id):
        attribute_bonus = 0
        for booster in self._boosters:
            attribute_bonus += booster.get_attribute_bonus(attribute_id)

        return attribute_bonus

    def get_attribute_bonus_expired_at_time_offset(self, attribute_id, time_offset = 0):
        attribute_bonus = 0
        for booster in self._boosters:
            if booster.expiry_time and self.is_booster_expired_at_time_offset(time_offset, booster.expiry_time):
                attribute_bonus += booster.get_attribute_bonus(attribute_id)

        return attribute_bonus

    def is_booster_expired_at_time_offset(self, time_offset, booster_expiry_time):
        return booster_expiry_time <= self.get_current_time() + time_offset

    def get_expiry_times_after_time(self, start_time):
        active_booster_expiry_times = []
        for booster in self._boosters:
            if booster.is_active_at_time(start_time):
                active_booster_expiry_times.append(booster.expiry_time)

        active_booster_expiry_times.sort()
        return active_booster_expiry_times

    def is_any_booster_active_at_time(self, start_time):
        for booster in self._boosters:
            if booster.is_active_at_time(start_time):
                return True

        return False

    def apply_expired_attributes_at_time_offset(self, attribute_dict, time_offset):
        for attribute_id in attribute_dict:
            attribute_dict[attribute_id] -= self.get_attribute_bonus_expired_at_time_offset(attribute_id, time_offset)

    def get_boosters(self):
        return self._boosters[:]

    def _set_boosters(self, boosters):
        self._boosters = boosters
