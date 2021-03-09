import frappe
from contentready_oip import api

def get_context(context):
    context.collaborations = frappe.get_list(
        'Collaboration', 
        filters={'recipient': frappe.session.user}, 
        fields=['name', 'owner', 'comment', 'personas_list', 'parent_doctype', 'parent_name', 'status'],
    )
    context.title = 'Collaborations'