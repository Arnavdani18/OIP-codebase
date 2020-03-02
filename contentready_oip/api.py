import frappe
import json

def nudge_guests():
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.throw('Please login to collaborate.')

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
def get_lat_lng_bounds(selectedLocation):
    from math import cos, radians
    lat_delta_1km = 0.009
    distance = selectedLocation['distance']
    lat_center = selectedLocation['center']['latitude']
    lng_center = selectedLocation['center']['longitude']
    lng_delta_1km = 0.009/cos(radians(lat_center))
    lat_min = lat_center - (distance * lat_delta_1km)
    lat_max = lat_center + (distance * lat_delta_1km)
    lng_min = lng_center - (distance * lng_delta_1km)
    lng_max = lng_center + (distance * lng_delta_1km)
    return {
        'lat_center': lat_center,
        'lat_min': lat_min,
        'lat_max': lat_max,
        'lng_center': lng_center,
        'lng_min': lng_min,
        'lng_max': lng_max
    }

@frappe.whitelist(allow_guest = True)
def get_filtered_problems(selectedLocation, selectedSectors, limit_page_length=20):
    if 'all' in selectedSectors:
        matching_problems_by_sector = frappe.get_list('Problem', filters={'is_published': True}, limit_page_length=limit_page_length)
        problem_set = {p['name'] for p in matching_problems_by_sector}
    else:
        matching_problems_by_sector = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': 'Problem', 'sector': ['in', selectedSectors]}, limit_page_length=limit_page_length)
        problem_set = {p['parent'] for p in matching_problems_by_sector}
    # TODO: Implement location filtering using Elasticsearch
    # This approximation currently fails.
    try:
        bounds = get_lat_lng_bounds(selectedLocation)
        lat_center = bounds['lat_center']
        lat_min = bounds['lat_min']
        lat_max = bounds['lat_max']
        lng_center = bounds['lng_center']
        lng_min = bounds['lng_min']
        lng_max = bounds['lng_max']
        matching_problems_by_location = \
            frappe.get_list('Problem', 
                filters={
                    'is_published': True,
                    'name': ['in', problem_set],
                    'latitude': ['>=', lat_min],
                    'latitude': ['<=', lat_max],
                    'longitude': ['>=', lng_min],
                    'longitude': ['<=', lng_max],
                }, 
                limit_page_length=limit_page_length
            )
        problem_set = {p['name'] for p in matching_problems_by_location}
    except Exception as e:
        print(str(e))
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
def get_filtered_solutions(selectedLocation, selectedSectors, limit_page_length=20):
    # TODO: Implement location filtering 
    if 'all' in selectedSectors:
        matching_solutions = frappe.get_list('Solution', filters={'is_published': True}, limit_page_length=limit_page_length)
        solution_set = {p['name'] for p in matching_solutions}
    else:
        matching_solutions = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': 'Solution', 'sector': ['in', selectedSectors]}, limit_page_length=limit_page_length)
        solution_set = {p['parent'] for p in matching_solutions}
    solutions = []
    for p in solution_set:
        doc = frappe.get_doc('Solution', p)
        if doc.is_published:
            doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
            solutions.append(doc)
    
    return {
        'solutions': solutions,
    }


@frappe.whitelist(allow_guest = True)
def get_similar_problems(text, limit_page_length=5, html=True):
    names = frappe.db.get_list('Problem', or_filters={'title': ['like', '%{}%'.format(text)], 'description': ['like', '%{}%'.format(text)]}, limit_page_length=limit_page_length)
    similar_problems = []
    names = {n['name'] for n in names}
    for p in names:
        doc = frappe.get_doc('Problem', p)
        doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
        if html:
            template = "templates/includes/problem/problem_card.html"
            context = {
                'problem': doc
            }
            html = frappe.render_template(template, context)
            similar_problems.append(html)
        else:
            similar_problems.append(doc)
    return similar_problems

@frappe.whitelist(allow_guest = True)
def get_similar_solutions(text, limit_page_length=5, html=True):
    names = frappe.db.get_list('Solution', or_filters={'title': ['like', '%{}%'.format(text)], 'description': ['like', '%{}%'.format(text)]}, limit_page_length=limit_page_length)
    similar_solutions = []
    names = {n['name'] for n in names}
    for p in names:
        doc = frappe.get_doc('Solution', p)
        doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
        if html:
            template = "templates/includes/solution/solution_card.html"
            context = {
                'solution': doc
            }
            html = frappe.render_template(template, context)
            similar_solutions.append(html)
        else:
            similar_solutions.append(doc)
    return similar_solutions

@frappe.whitelist(allow_guest = True)
def get_orgs_list():
    all_orgs = frappe.get_list('Organisation', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_orgs]

@frappe.whitelist(allow_guest = True)
def get_persona_list():
    all_personas = frappe.get_list('Persona', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_personas]

@frappe.whitelist(allow_guest = True)
def get_homepage_stats():
    return {
        'problems': frappe.db.count('Problem', filters={'is_published': True}),
        'solutions': frappe.db.count('Solution', filters={'is_published': True}),
        'collaborators': frappe.db.count('User Profile'),
    }

@frappe.whitelist(allow_guest = True)
def has_user_liked(doctype, name):
    likes = frappe.get_all('Like Table', filters={'user': frappe.session.user, 'parenttype': doctype, 'parent': name})
    return len(likes) > 0

@frappe.whitelist(allow_guest = False)
def toggle_like(doctype, name):
    nudge_guests()
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

@frappe.whitelist(allow_guest = True)
def has_user_watched(doctype, name):
    watchers = frappe.get_all('Watch Table', filters={'user': frappe.session.user, 'parenttype': doctype, 'parent': name})
    return len(watchers) > 0

@frappe.whitelist(allow_guest = False)
def toggle_watcher(doctype, name):
    nudge_guests()
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
        return html, doc.name
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def has_user_enriched(name):
    enrichments_by_user = frappe.get_list('Enrichment', filters={'owner': frappe.session.user, 'problem': name})
    return len(enrichments_by_user) > 0

@frappe.whitelist(allow_guest = False)
def add_enrichment(doc):
    doc = json.loads(doc)
    if not ('problem' in doc or doc['problem']):
        return False
    if has_user_enriched(doc['problem']):
        frappe.throw('You have already enriched this problem.')
    enrichment = frappe.get_doc({
        'doctype': 'Enrichment'
    })
    enrichment.update(doc)
    enrichment.insert()
    frappe.db.commit()
    return True

@frappe.whitelist(allow_guest = False)
def has_user_validated(doctype, name):
    validations_by_user = frappe.get_list('Validation Table', filters={'owner': frappe.session.user, 'parenttype': doctype, 'parent': name})
    return len(validations_by_user) > 0

@frappe.whitelist(allow_guest = False)
def add_or_edit_validation(doctype, name, validation, html=True):
    validation = json.loads(validation)
    if doctype == 'Validation Table':
        # in edit mode
        v = frappe.get_doc('Validation Table', name)
        v.update(validation)
        v.save()
        total_count = frappe.db.count('Validation Table', filters={'parenttype': v.parenttype, 'parent': v.parent})
    else:
        if has_user_validated(doctype, name):
            frappe.throw('You have already validated this {}.'.format(doctype).capitalize())
        doc = frappe.get_doc(doctype, name)
        v = doc.append('validations', {})
        v.update(validation)
        doc.save()
        total_count = frappe.db.count('Validation Table', filters={'parenttype': doctype, 'parent': name})
    frappe.db.commit()
    if html:
        context = {
            'validation': v
        }
        template = "templates/includes/common/validation_card.html"
        html = frappe.render_template(template, context)
        return html, total_count
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def has_user_collaborated(doctype, name):
    collaborations_by_user = frappe.get_list('Collaboration Table', filters={'owner': frappe.session.user, 'parenttype': doctype, 'parent': name})
    return len(collaborations_by_user) > 0

@frappe.whitelist(allow_guest = False)
def add_or_edit_collaboration(doctype, name, collaboration, html=True):
    collaboration = json.loads(collaboration)
    if doctype == 'Collaboration Table':
        # in edit mode
        c = frappe.get_doc('Collaboration Table', name)
        c.update(collaboration)
        c.save()
        total_count = frappe.db.count('Collaboration Table', filters={'parenttype': c.parenttype, 'parent': c.parent})
    else:
        if has_user_collaborated(doctype, name):
            frappe.throw('You have already added your collaboration intent on this {}.'.format(doctype).capitalize())
        doc = frappe.get_doc(doctype, name)
        c = doc.append('collaborations', {})
        c.update(collaboration)
        doc.save()
        total_count = frappe.db.count('Collaboration Table', filters={'parenttype': doctype, 'parent': name})
    frappe.db.commit()
    print('saved collaboration')
    if html:
        context = {
            'collaboration': c,
            'personas': get_persona_list()
        }
        template = "templates/includes/common/collaboration_card.html"
        html = frappe.render_template(template, context)
        print('returning html')
        return html, total_count
    else:
        return doc

@frappe.whitelist(allow_guest = True)
def add_subscriber(email, first_name=None):
    if not first_name:
        first_name = email # the contact docytpe needs first_name. If the form doesn't give us this, use email instead. 
    contact = frappe.get_doc({
        'doctype': 'Contact',
        'first_name': email, 
        'email_ids': [{
            'email_id': email,
            'is_primary': True
        }]
    })
    contact.insert()
    frappe.db.commit()
    return contact