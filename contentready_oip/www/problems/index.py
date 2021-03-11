import frappe
from contentready_oip import api
import json

def get_context(context):
    doctype = 'Problem'
    r = api.get_filtered_paginated_content(context, doctype, 'problems')
    context.update(r)
    