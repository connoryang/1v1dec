#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\infobubbles\__init__.py
import fsdlite
INFO_BUBBLE_DATA = None
INFO_BUBBLE_TYPE_BONUSES = None
SHIP_SKILL_BONUSES = None

def get_info_bubble_type_bonuses():
    global INFO_BUBBLE_TYPE_BONUSES
    global INFO_BUBBLE_DATA
    if INFO_BUBBLE_DATA is None:
        INFO_BUBBLE_DATA = fsdlite.EveStorage(data='infoBubbleElements', cache='infoBubbles.static')
    if INFO_BUBBLE_TYPE_BONUSES is None:
        INFO_BUBBLE_TYPE_BONUSES = {int(t):b for t, b in INFO_BUBBLE_DATA['infoBubbleTypeBonuses'].iteritems()}
    return INFO_BUBBLE_TYPE_BONUSES


def iter_ship_skill_bonuses(ship_type_id):
    for skill_type_id, skill_bonuses in sorted(get_info_bubble_type_bonuses()[ship_type_id].get('types', {}).iteritems()):
        yield (skill_type_id, skill_bonuses)


def get_role_bonus(ship_type_id):
    return get_info_bubble_type_bonuses()[ship_type_id].get('roleBonuses', [])


def get_misc_bonus(ship_type_id):
    return get_info_bubble_type_bonuses()[ship_type_id].get('miscBonuses', [])


def has_traits(ship_type_id):
    return ship_type_id in get_info_bubble_type_bonuses()
