from __future__ import unicode_literals

import frappe

def get_context(context):
    # Remove breadcrumbs
    # context.parents=[]
    pass

@frappe.whitelist(allow_guest = True)
def get_similar_problems(text):
    names = frappe.db.get_list('Problem', or_filters={'title': ['like', '%{}%'.format(text)], 'description': ['like', '%{}%'.format(text)]})
    similar_problems = []
    names = {n['name'] for n in names}
    for p in names:
        doc = frappe.get_doc('Problem', p)
        doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
        template = "templates/includes/problems/problem_card.html"
        context = {
            'problem': doc
        }
        html = frappe.render_template(template, context)
        similar_problems.append(html)
    return similar_problems