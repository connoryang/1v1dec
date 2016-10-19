#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\infobubbles\converter.py
import os
import fsd.common.fsdYamlExtensions as fsdYaml
import yaml
data_path = 'c:\\perforce\\eve\\branches\\development\\MAINLINE\\eve\\staticData\\infoBubbleElements'
new_data = {}

def get_bonuses_as_list(bonuses):
    l = []
    for importance, bonus in sorted(bonuses.iteritems()):
        bonus['importance'] = importance
        l.append(bonus)

    return l


with open(os.path.join(data_path, 'old_infoBubbleTypeBonuses.staticdata'), 'r') as f:
    for ship_type_id, skill_bonuses in yaml.load(f).iteritems():
        new_data[ship_type_id] = {}
        for skill_type_id, bonuses in skill_bonuses.iteritems():
            bonuses_as_list = get_bonuses_as_list(bonuses)
            if skill_type_id == -1:
                new_data[ship_type_id]['roleBonuses'] = bonuses_as_list
                continue
            elif skill_type_id == -2:
                new_data[ship_type_id]['miscBonuses'] = bonuses_as_list
                continue
            if 'types' not in new_data[ship_type_id]:
                new_data[ship_type_id]['types'] = {}
            new_data[ship_type_id]['types'][skill_type_id] = bonuses_as_list

    with open(os.path.join(data_path, 'infoBubbleTypeBonuses.staticdata'), 'w') as f:
        yaml.dump(new_data, f, Dumper=fsdYaml.FsdYamlDumper)
    print new_data
