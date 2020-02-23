import frappe
def get_context(context):
    context.stats = {
        'problems': frappe.db.count('Problem', filters={'is_published': True}),
        'solutions': frappe.db.count('Problem', filters={'is_published': True}),
        'collaborators': frappe.db.count('User Profile'),
    }