import frappe
from contentready_oip import api
import json

def get_context(context):
    doctype = 'Solution'
    context = api.get_content_for_context(context, doctype, 'solutions', limit_page_length=3)