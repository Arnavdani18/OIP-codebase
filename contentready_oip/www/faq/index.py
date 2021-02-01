import frappe
from contentready_oip import api

def get_context(context):
    context.faq_list = frappe.get_list('FAQ',fields=['question','answer','name'])
    