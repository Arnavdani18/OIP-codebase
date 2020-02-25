import frappe
from contentready_oip import api

def get_context(context):
    context.stats = api.get_homepage_stats()