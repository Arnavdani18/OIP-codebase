import frappe
import json

RESULTS_PER_PAGE = 20

def get_context(context):
    context.resources = frappe.get_list("OIP Resource", filters={"is_published": True}, fields=["title", "image", "description", "attachment"])
    return context
    
