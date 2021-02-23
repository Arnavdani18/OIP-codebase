# -*- coding: utf-8 -*-
import pytz
from datetime import datetime
import frappe

def try_method(method):
    try:
        method()
    except:
        pass

def is_dst(dt=None, timezone="UTC"):
    if dt is None:
        dt = datetime.utcnow()
    timezone = pytz.timezone(timezone)
    timezone_aware_date = timezone.localize(dt, is_dst=None)
    return timezone_aware_date.tzinfo._dst.seconds != 0

def remove_private_keys(_dict):
    private_fields = ['owner', 'modified_by', 'creation', 'modified', 'parent', 'parentfield', 'parenttype', 'doctype', 'docstatus', 'idx', 'name']
    return delete_keys_from_dict(_dict, private_fields)

def delete_keys_from_dict(dictionary, keys):
    from collections import MutableMapping
    keys_set = set(keys)  # Just an optimization for the "if key in keys" lookup.
    modified_dict = {}
    for key, value in dictionary.items():
        if key not in keys_set:
            if isinstance(value, MutableMapping):
                modified_dict[key] = delete_keys_from_dict(value, keys_set)
            elif isinstance(value, list):
                new_value = []
                for v in value:
                    new_value.append(delete_keys_from_dict(v, keys_set))
                modified_dict[key] = new_value
            else:
                modified_dict[key] = value  # or copy.deepcopy(value) if a copy is desired for non-dicts.
    return modified_dict
