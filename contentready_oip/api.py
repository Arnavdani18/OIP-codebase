import frappe
import json

@frappe.whitelist(allow_guest = True)
def set_location_filter(selectedLocation=None, distance=25):
    if not 'location_filter' in frappe.session.data or not isinstance(frappe.session.data['location_filter'], dict):
        frappe.session.data['location_filter'] = {}
    selectedLocation = json.loads(selectedLocation)
    distance = int(distance)
    if not distance:
        distance = 25
    if selectedLocation:
        frappe.session.data['location_filter']['center'] = selectedLocation
    # if distance:
    frappe.session.data['location_filter']['distance'] = distance
    return frappe.session.data['location_filter']

@frappe.whitelist(allow_guest = True)
def set_sector_filter(sectors=[]):
    if not 'sector_filter' in frappe.session.data or not isinstance(frappe.session.data['sector_filter'], list):
        frappe.session.data['sector_filter'] = []
    if sectors:
        frappe.session.data['sector_filter'] = json.loads(sectors)
    return frappe.session.data['sector_filter']

@frappe.whitelist(allow_guest = True)
def get_filters():
    selectedLocation = {}
    selectedSectors = ['all']
    if 'location_filter' in frappe.session.data:
        selectedLocation = frappe.session.data.location_filter
    if 'sector_filter' in frappe.session.data:
        selectedSectors = frappe.session.data.sector_filter
    availableSectors = frappe.get_list('Sector', ['name', 'title'])
    return {
        'selectedLocation': selectedLocation,
        'selectedSectors': selectedSectors,
        'availableSectors': availableSectors
    }

@frappe.whitelist(allow_guest = True)
def get_doc_by_type_name(doctype, name):
    return frappe.get_doc(doctype, name)

@frappe.whitelist(allow_guest = True)
def get_doc_field(doctype, name, field):
    return frappe.get_value(doctype, name, field)

@frappe.whitelist(allow_guest = True)
def get_child_table(child_table_doctype, parent_doctype, parent_name):
    return frappe.get_all(child_table_doctype, filters={'parenttype': parent_doctype, 'parent': parent_name})

@frappe.whitelist(allow_guest = True)
def get_filtered_problems(selectedLocation, selectedSectors):
    # TODO: Implement location filtering 
    if 'all' in selectedSectors:
        # matching_problems = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': 'Problem'})
        matching_problems = frappe.get_list('Problem', filters={'is_published': True})
        problem_set = {p['name'] for p in matching_problems}
    else:
        matching_problems = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': 'Problem', 'sector': ['in', selectedSectors]})
        problem_set = {p['parent'] for p in matching_problems}
    problems = []
    for p in problem_set:
        doc = frappe.get_doc('Problem', p)
        if doc.is_published:
            doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
            problems.append(doc)
    
    return {
        'problems': problems,
    }

@frappe.whitelist(allow_guest = True)
def get_similar_problems(text, limit_page_length=5):
    names = frappe.db.get_list('Problem', or_filters={'title': ['like', '%{}%'.format(text)], 'description': ['like', '%{}%'.format(text)]}, limit_page_length=limit_page_length)
    similar_problems = []
    names = {n['name'] for n in names}
    for p in names:
        doc = frappe.get_doc('Problem', p)
        doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
        template = "templates/includes/problem/problem_card.html"
        context = {
            'problem': doc
        }
        html = frappe.render_template(template, context)
        similar_problems.append(html)
    return similar_problems

@frappe.whitelist(allow_guest = True)
def get_orgs_list():
    all_orgs = frappe.get_list('Organisation', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_orgs]

@frappe.whitelist(allow_guest = True)
def get_homepage_stats():
    return {
        'problems': frappe.db.count('Problem', filters={'is_published': True}),
        'solutions': frappe.db.count('Solution', filters={'is_published': True}),
        'collaborators': frappe.db.count('User Profile'),
    }

@frappe.whitelist(allow_guest = False)
def has_user_liked(doctype, name):
    likes = frappe.get_all('Like Table', filters={'user': frappe.session.user, 'parenttype': doctype, 'parent': name})
    return len(likes) > 0

@frappe.whitelist(allow_guest = False)
def toggle_like(doctype, name):
    likes = frappe.get_all('Like Table', filters={'user': frappe.session.user, 'parenttype': doctype, 'parent': name})
    if len(likes) > 0:
        # user has already liked this document
        for l in likes:
            frappe.delete_doc('Like Table', l['name'])
    else:
        # add like for user
        doc = frappe.get_doc(doctype, name)
        like = doc.append('likes', {})
        like.user = frappe.session.user
        doc.save()
        frappe.db.commit()
    return has_user_liked(doctype, name), get_child_table('Like Table', doctype, name)

@frappe.whitelist(allow_guest = False)
def has_user_watched(doctype, name):
    watchers = frappe.get_all('Watch Table', filters={'user': frappe.session.user, 'parenttype': doctype, 'parent': name})
    return len(watchers) > 0

@frappe.whitelist(allow_guest = False)
def toggle_watcher(doctype, name):
    watchers = frappe.get_all('Watch Table', filters={'user': frappe.session.user, 'parenttype': doctype, 'parent': name})
    if len(watchers) > 0:
        # user has already watched this document
        for l in watchers:
            frappe.delete_doc('Watch Table', l['name'])
    else:
        # add watch for user
        doc = frappe.get_doc(doctype, name)
        watch = doc.append('watchers', {})
        watch.user = frappe.session.user
        doc.save()
        frappe.db.commit()
    return has_user_watched(doctype, name), get_child_table('Watch Table', doctype, name)

@frappe.whitelist(allow_guest = False)
def add_comment(doctype, name, text, html=True):
    doc = frappe.get_doc({
        'doctype': 'Discussion',
        'text': text
    })
    doc.save()
    parent_doc = frappe.get_doc(doctype, name)
    if doctype == 'Discussion':
        child = parent_doc.append('replies', {})
    else:
        child = parent_doc.append('discussions', {})
    child.discussion = doc.name
    parent_doc.save()
    frappe.db.commit()
    template = "templates/includes/common/comment.html"
    context = {
        'comment': doc
    }
    html = frappe.render_template(template, context)
    return html

@frappe.whitelist(allow_guest = False)
def get_problem_card(name, html=True):
    doc = frappe.get_doc('Problem', name)
    if html:
        context = {
            'problem': doc
        }
        template = "templates/includes/problem/problem_card.html"
        html = frappe.render_template(template, context)
        return html
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def add_enrichment(doc):
    doc = json.loads(doc)
    if not ('problem' in doc or doc['problem']):
        return False
    enrichments_by_user = frappe.get_list('Enrichment', filters={'owner': frappe.session.user, 'problem': doc['problem']})
    if len(enrichments_by_user) > 0:
        frappe.throw('You have already enriched this problem.')
    return True

@frappe.whitelist(allow_guest = False)
def add_validation(doctype, name, validation, html=True):
    validations_by_user = frappe.get_list('Validation Table', filters={'owner': frappe.session.user, 'parenttype': doctype, 'parent': name})
    if len(validations_by_user) > 0:
        frappe.throw('You have already validated this {}.'.format(doctype).capitalize())
    validation = json.loads(validation)
    doc = frappe.get_doc(doctype, name)
    v = doc.append('validations', {})
    v.update(validation)
    doc.save()
    frappe.db.commit()
    if html:
        context = {
            'validation': v
        }
        template = "templates/includes/problem/validation_card.html"
        html = frappe.render_template(template, context)
        return html, frappe.db.count('Validation Table', filters={'parenttype': doctype, 'parent': name})
    else:
        return doc