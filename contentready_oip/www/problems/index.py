import frappe
from contentready_oip import api
import json

def get_context(context):
    doctype = 'Problem'
    context = api.get_content_for_context(context, doctype, 'problems')
    