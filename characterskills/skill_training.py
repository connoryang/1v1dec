#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\characterskills\skill_training.py
from contextlib import contextmanager
from characterskills.util import GetSkillPointsPerMinute, GetSPForLevelRaw
import gametime
from carbon.common.lib.const import MIN

class SkillAttributeMissingError(Exception):
    pass


class CharacterSkillInterface(object):

    def get_primary_attribute_id(self, skill_type_id):
        raise NotImplementedError()

    def get_secondary_attribute_id(self, skill_type_id):
        raise NotImplementedError()

    def get_skill_rank(self, skill_type_id):
        raise NotImplementedError()

    def get_skill_level(self, skill_type_id):
        raise NotImplementedError()

    def get_character_attribute_at_time(self, attribute_id, time_offset):
        raise NotImplementedError()

    def get_skill_points(self, skill_type_id):
        raise NotImplementedError()

    def get_skill_accelerator_boosters(self):
        raise NotImplementedError()


class SkillLevelAlreadyTrainedError(Exception):
    pass


class SkillPointsTrainedPerMinuteError(Exception):
    pass


class SkillTrainingTimeCalculator(object):

    def __init__(self, character_skill_interface):
        self._character_skill_interface = character_skill_interface
        self._current_time_function = None
        self.reset_current_time_function()

    def _get_primary_attribute_value_at_time(self, skill_type_id, time_offset):
        attribute_id = self._character_skill_interface.get_primary_attribute_id(skill_type_id)
        if not attribute_id:
            raise SkillAttributeMissingError("Skill %s is missing it's primary attribute")
        return self._character_skill_interface.get_character_attribute_at_time(attribute_id, time_offset)

    def _get_secondary_attribute_value_at_time(self, skill_type_id, time_offset):
        attribute_id = self._character_skill_interface.get_secondary_attribute_id(skill_type_id)
        if not attribute_id:
            raise SkillAttributeMissingError("Skill %s is missing it's secondary attribute")
        return self._character_skill_interface.get_character_attribute_at_time(attribute_id, time_offset)

    def _get_starting_skill_points(self, skill_level, skill_rank, skill_type_id, to_level):
        if skill_level == to_level - 1:
            from_skillpoints = self._character_skill_interface.get_skill_points(skill_type_id)
        else:
            from_skillpoints = GetSPForLevelRaw(skill_rank, to_level - 1)
        return from_skillpoints

    def _get_time_offset(self, training_start_time):
        time_offset = 0
        if training_start_time:
            time_offset = training_start_time - self._get_current_time()
        return time_offset

    def _get_current_time(self):
        return self._current_time_function()

    def _get_skill_points_per_minute_at(self, skill_type_id, time_offset):
        primary_attribute_value = self._get_primary_attribute_value_at_time(skill_type_id, time_offset)
        secondary_attribute_value = self._get_secondary_attribute_value_at_time(skill_type_id, time_offset)
        sp_per_minute = GetSkillPointsPerMinute(primary_attribute_value, secondary_attribute_value)
        if sp_per_minute <= 0:
            raise SkillPointsTrainedPerMinuteError('Skill points trained per minute is %s which suggests bad character attribute values. Skill type=%s, primary attribute=s, secondary attribute=%s.', sp_per_minute, skill_type_id, primary_attribute_value, secondary_attribute_value)
        return sp_per_minute

    def _get_remaining_skill_points(self, skill_type_id, to_level):
        skill_rank = self._character_skill_interface.get_skill_rank(skill_type_id)
        skill_level = self._character_skill_interface.get_skill_level(skill_type_id)
        from_skillpoints = self._get_starting_skill_points(skill_level, skill_rank, skill_type_id, to_level)
        to_skillpoints = GetSPForLevelRaw(skill_rank, to_level)
        remaining_skillpoints = to_skillpoints - from_skillpoints
        return remaining_skillpoints

    def _get_remaining_skill_points_given_existing_skill_points(self, skill_type_id, to_level, existing_skill_points):
        skill_rank = self._character_skill_interface.get_skill_rank(skill_type_id)
        to_skillpoints = GetSPForLevelRaw(skill_rank, to_level)
        remaining_skillpoints = to_skillpoints - existing_skill_points
        if remaining_skillpoints <= 0:
            raise SkillLevelAlreadyTrainedError('Skill type %s already trained to level %s. Has %s skill points while needing only %s to achieve the level', skill_type_id, to_level, existing_skill_points, to_skillpoints)
        return remaining_skillpoints

    def _get_booster_expiry_time_offsets(self, training_start_time):
        boosters = self._character_skill_interface.get_skill_accelerator_boosters()
        if not boosters:
            return []
        expiry_times = boosters.get_expiry_times_after_time(training_start_time)
        return [ expiry_time - training_start_time for expiry_time in expiry_times ]

    def _get_training_time_given_skill_points_to_train(self, skill_type_id, skillpoints_to_train, training_start_time):
        time_offset = self._get_time_offset(training_start_time)
        skillpoints_per_minute = self._get_skill_points_per_minute_at(skill_type_id, time_offset)
        accumulated_skillpoints = 0
        accumulated_time = 0
        for expiry_time_offset in self._get_booster_expiry_time_offsets(training_start_time):
            time_left_until_expiry = expiry_time_offset - accumulated_time
            skillpoints_until_expiry = time_left_until_expiry / MIN * skillpoints_per_minute
            if accumulated_skillpoints + skillpoints_until_expiry >= skillpoints_to_train:
                break
            accumulated_skillpoints += skillpoints_until_expiry
            accumulated_time += time_left_until_expiry
            skillpoints_per_minute = self._get_skill_points_per_minute_at(skill_type_id, time_offset + expiry_time_offset)

        remaining_skillpoints = skillpoints_to_train - accumulated_skillpoints
        total_time = accumulated_time + long(float(remaining_skillpoints) / float(skillpoints_per_minute) * MIN)
        return total_time

    def get_skill_points_and_time_to_train(self, skill_type_id, to_level, training_start_time):
        skillpoints_to_train = self._get_remaining_skill_points(skill_type_id, to_level)
        total_time = self._get_training_time_given_skill_points_to_train(skill_type_id, skillpoints_to_train, training_start_time)
        return (skillpoints_to_train, total_time)

    def get_training_time(self, skill_type_id, to_level, training_start_time = None):
        skillpoints_to_train, training_time = self.get_skill_points_and_time_to_train(skill_type_id, to_level, training_start_time)
        return training_time

    def get_skill_points_and_time_to_train_given_existing_skill_points(self, skill_type_id, to_level, training_start_time, existing_skill_points):
        skillpoints_to_train = self._get_remaining_skill_points_given_existing_skill_points(skill_type_id, to_level, existing_skill_points)
        total_time = self._get_training_time_given_skill_points_to_train(skill_type_id, skillpoints_to_train, training_start_time)
        return (skillpoints_to_train, total_time)

    def get_skill_points_trained_at_sample_time(self, skill_type_id, training_start_time, sample_time):
        time_offset = self._get_time_offset(training_start_time)
        skillpoints_per_minute = self._get_skill_points_per_minute_at(skill_type_id, time_offset)
        sample_offset = sample_time - training_start_time
        time_left_until_sample = sample_offset
        accumulated_skillpoints = 0
        accumulated_time = 0
        for expiry_time_offset in self._get_booster_expiry_time_offsets(training_start_time):
            if expiry_time_offset >= sample_offset:
                time_left_until_sample = sample_offset - accumulated_time
                break
            time_left_until_expiry = expiry_time_offset - accumulated_time
            skillpoints_until_expiry = time_left_until_expiry / float(MIN) * skillpoints_per_minute
            accumulated_skillpoints += skillpoints_until_expiry
            accumulated_time += time_left_until_expiry
            skillpoints_per_minute = self._get_skill_points_per_minute_at(skill_type_id, time_offset + expiry_time_offset)

        accumulated_skillpoints += time_left_until_sample / float(MIN) * skillpoints_per_minute
        starting_skillpoints = self._character_skill_interface.get_skill_points(skill_type_id)
        return int(accumulated_skillpoints + starting_skillpoints)

    def get_skill_accelerator_boosters(self):
        return self._character_skill_interface.get_skill_accelerator_boosters()

    def set_current_time_function(self, function):
        self._current_time_function = function

    def reset_current_time_function(self):
        self.set_current_time_function(gametime.GetWallclockTime)

    @contextmanager
    def specific_current_time_context(self, time):

        def get_current_time():
            return time

        sab = self.get_skill_accelerator_boosters()
        sab.set_current_time_function(get_current_time)
        self.set_current_time_function(get_current_time)
        try:
            yield self
        finally:
            sab.reset_current_time_function()
            self.reset_current_time_function()
