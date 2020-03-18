import frappe
from contentready_oip import api

def get_context(context):
    doctype = 'User Profile'
    context = api.get_content_for_context(context, doctype, 'users')