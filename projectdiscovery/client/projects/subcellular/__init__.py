#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\__init__.py
import collections

def nested_categories_from_json(categories):
    keyed = {cat['id']:cat for cat in categories}
    nested = collections.OrderedDict()
    for cat in categories:
        cat['children'] = []
        cat['selected'] = False
        if not cat['parentId']:
            nested[cat['id']] = cat
        elif cat['parentId'] in keyed:
            keyed[cat['parentId']]['children'].append(cat)

    return nested
