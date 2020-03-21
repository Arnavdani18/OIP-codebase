import frappe
from contentready_oip import api
import json

def get_context(context):
    doctype = 'Solution'
    r = api.get_filtered_paginated_content(context, doctype, 'solutions')
    context.update(r)