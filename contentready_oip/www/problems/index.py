import frappe
def get_context(context):
    context.problems = frappe.get_list('Problem', fields=['title', 'featured_image', 'owner', 'creation'], filters={'is_published': True})