#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\characterskills\client\skill_training.py


class ClientCharacterSkillInterface(object):

    def __init__(self, skill_service):
        self.skill_service = skill_service

    def get_primary_attribute_id(self, skill_type_id):
        return self.skill_service.GetPrimarySkillAttribute(skill_type_id)

    def get_secondary_attribute_id(self, skill_type_id):
        return self.skill_service.GetSecondarySkillAttribute(skill_type_id)

    def get_skill_rank(self, skill_type_id):
        return self.skill_service.GetSkillRank(skill_type_id)

    def get_skill_level(self, skill_type_id):
        return self.skill_service.GetSkill(skill_type_id).skillLevel

    def get_character_attribute_at_time(self, attribute_id, time_offset):
        attribute_dict = self.skill_service.GetCharacterAttributes()
        attribute = attribute_dict[attribute_id]
        skill_boosters = self.get_skill_accelerator_boosters()
        attribute -= skill_boosters.get_attribute_bonus_expired_at_time_offset(attribute_id, time_offset)
        return attribute

    def get_skill_points(self, skill_type_id):
        return self.skill_service.GetSkill(skill_type_id).skillPoints

    def get_skill_accelerator_boosters(self):
        return self.skill_service.GetSkillAcceleratorBoosters()
