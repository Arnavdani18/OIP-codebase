import frappe
from contentready_oip import api

def get_context(context):
    if frappe.session.user == 'Guest' or not api.has_collaborator_role():
        frappe.local.flags.redirect_location = '/'
        raise frappe.Redirect
    context.logs = {
        'Problem': [],
        'Solution': [],
        # 'User Profile': [],
        # 'Organisation': [],
    }
    for doctype in context.logs:
        context.logs[doctype] = frappe.get_list('OIP Route Aggregate', filters={'parent_doctype': doctype, 'owner': frappe.session.user}, fields=['route', 'parent_doctype', 'parent_name', 'total_visits', 'unique_visitors', 'unique_organisations', 'modified'])
    context.title = 'Analytics'