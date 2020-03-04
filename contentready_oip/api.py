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
def get_filtered_content(doctype, location, sectors, limit_page_length=20, html=False, guest=True):
    if guest:
        sectors = json.loads(sectors) or []
        location = json.loads(location) or {}
    if 'all' in sectors:
        filtered = frappe.get_list(doctype, filters={'is_published': True}, limit_page_length=limit_page_length)
        content_set = {f['name'] for f in filtered}
    else:
        filtered = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': doctype, 'sector': ['in', sectors]}, limit_page_length=limit_page_length)
        content_set = {f['parent'] for f in filtered}
    # TODO: Implement location filtering using Elasticsearch
    # This approximation currently fails.
    try:
        bounds = get_lat_lng_bounds(location)
        lat_center = bounds['lat_center']
        lat_min = bounds['lat_min']
        lat_max = bounds['lat_max']
        lng_center = bounds['lng_center']
        lng_min = bounds['lng_min']
        lng_max = bounds['lng_max']
        filtered = \
            frappe.get_list(doctype, 
                filters={
                    'is_published': True,
                    'name': ['in', content_set],
                    'latitude': ['>=', lat_min],
                    'latitude': ['<=', lat_max],
                    'longitude': ['>=', lng_min],
                    'longitude': ['<=', lng_max],
                }, 
                limit_page_length=limit_page_length
            )
        content_set = {f['name'] for f in filtered}
    except Exception as e:
        print(str(e))
    content = []
    from frappe.website.context import build_context 
    for c in content_set:
        doc = frappe.get_doc(doctype, c)
        if doc.is_published:
            doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
            if html:
                # template = doc.meta.get_web_template()
                # context = build_context(doc.as_dict())
                template = "templates/includes/problem/problem_card.html"
                context = {
                    'problem': doc
                }
                html = frappe.render_template(template, context)
                content.append(html)
            else:
                content.append(doc)
    return content

@frappe.whitelist(allow_guest = True)
def search_content_by_text(doctype, text, limit_page_length=5, html=True):
    names = frappe.db.get_list(doctype, or_filters={'title': ['like', '%{}%'.format(text)], 'description': ['like', '%{}%'.format(text)]}, limit_page_length=limit_page_length)
    content = []
    names = {n['name'] for n in names}
    for p in names:
        doc = frappe.get_doc(doctype, p)
        doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
        if html:
            content_type = doctype.lower()
            template = "templates/includes/{}/{}_card.html".format(content_type, content_type)
            context = {
                content_type: doc
            }
            html = frappe.render_template(template, context)
            content.append(html)
        else:
            content.append(doc)
    return content

@frappe.whitelist(allow_guest = True)
def get_orgs_list():
    all_orgs = frappe.get_list('Organisation', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_orgs]

@frappe.whitelist(allow_guest = True)
def get_persona_list():
    all_personas = frappe.get_list('Persona', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_personas]

@frappe.whitelist(allow_guest = True)
def get_sector_list():
    all_sectors = frappe.get_list('Sector', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_sectors]

@frappe.whitelist(allow_guest = True)
def get_homepage_stats():
    return {
        'problems': frappe.db.count('Problem', filters={'is_published': True}),
        'solutions': frappe.db.count('Solution', filters={'is_published': True}),
        'collaborators': frappe.db.count('User Profile'),
    }

@frappe.whitelist(allow_guest = True)
def has_user_contributed(child_doctype, parent_doctype, name):
    contributions_by_user = frappe.db.count(child_doctype, filters={'owner': frappe.session.user, 'parenttype': parent_doctype, 'parent': name})
    return contributions_by_user > 0

@frappe.whitelist(allow_guest = False)
def toggle_contribution(child_doctype, parent_doctype, parent_name, field_name):
    nudge_guests()
    contributions = frappe.get_all(child_doctype, filters={'user': frappe.session.user, 'parenttype': parent_doctype, 'parent': parent_name})
    if len(contributions) > 0:
        # user has already contributed to this document
        for c in contributions:
            frappe.delete_doc(child_doctype, c['name'])
    else:
        # add contribution for user
        doc = frappe.get_doc(parent_doctype, parent_name)
        like = doc.append(field_name, {})
        like.user = frappe.session.user
        doc.save()
        frappe.db.commit()
    return has_user_contributed(child_doctype, parent_doctype, parent_name), get_child_table(child_doctype, parent_doctype, parent_name)

@frappe.whitelist(allow_guest = False)
def add_comment(doctype, name, text, attachments=None, html=True):
    doc = frappe.get_doc({
        'doctype': 'Discussion',
        'text': text
    })
    attachments = json.loads(attachments)
    for f in attachments:
        a = doc.append('attachments', {})
        a.image = f
    doc.save()
    parent_doc = frappe.get_doc(doctype, name)
    if doctype == 'Discussion':
        child = parent_doc.append('replies', {})
    else:
        child = parent_doc.append('discussions', {})
    child.discussion = doc.name
    parent_doc.save()
    frappe.db.commit()
    if html:
        template = "templates/includes/common/comment.html"
        context = {
            'comment': doc
        }
        html = frappe.render_template(template, context)
        return html
    else:
        return doc

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
def add_primary_content(doctype, doc):
    doc = json.loads(doc)
    if doc['name']:
        # edit
        content = frappe.get_doc(doctype, doc['name'])
        content.update(doc)
        content.save()
    else:
        # create
        content = frappe.get_doc({
            'doctype': doctype
        })
        content.update(doc)
        content.insert()
    frappe.db.commit()
    content = frappe.get_doc(doctype, content.name)
    return content.route


@frappe.whitelist(allow_guest = False)
def add_enrichment(doc):
    doc = json.loads(doc)
    if not ('problem' in doc or doc['problem']):
        return False
    if has_user_contributed('Enrichment Table', 'Problem', doc['problem']):
        frappe.throw('You have already enriched this problem.')
    enrichment = frappe.get_doc({
        'doctype': 'Enrichment'
    })
    enrichment.update(doc)
    enrichment.insert()
    frappe.db.commit()
    route = frappe.get_value('Problem', enrichment.problem, 'route')
    return route

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
        if has_user_contributed('Validation Table', doctype, name):
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
def add_or_edit_collaboration(doctype, name, collaboration, html=True):
    collaboration = json.loads(collaboration)
    if doctype == 'Collaboration Table':
        # in edit mode
        c = frappe.get_doc('Collaboration Table', name)
        c.update(collaboration)
        c.save()
        total_count = frappe.db.count('Collaboration Table', filters={'parenttype': c.parenttype, 'parent': c.parent})
    else:
        if has_user_contributed('Collaboration Table', doctype, name):
            frappe.throw('You have already added your collaboration intent on this {}.'.format(doctype).capitalize())
        doc = frappe.get_doc(doctype, name)
        c = doc.append('collaborations', {})
        c.update(collaboration)
        doc.save()
        total_count = frappe.db.count('Collaboration Table', filters={'parenttype': doctype, 'parent': name})
    frappe.db.commit()
    if html:
        context = {
            'collaboration': c,
            'personas': get_persona_list()
        }
        template = "templates/includes/common/collaboration_card.html"
        html = frappe.render_template(template, context)
        return html, total_count
    else:
        return doc

@frappe.whitelist(allow_guest = True)
def add_subscriber(email, first_name=None):
    if not first_name:
        first_name = email # the contact docytpe needs first_name. If the form doesn't give us this, use email instead. 
    frappe.set_user('Administrator')
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

@frappe.whitelist(allow_guest = False)
def get_content_by_user(doctype, limit_page_length=20):
    filtered = frappe.get_list(doctype, filters={'owner': frappe.session.user})
    content = []
    for f in filtered:
        doc = frappe.get_doc(doctype, f['name'])
        content.append(doc)
    return content

@frappe.whitelist(allow_guest = False)
def get_content_watched_by_user(doctype, limit_page_length=20):
    filtered = frappe.get_list('Watch Table', fields=['parent'], filters={'parenttype': doctype, 'owner': frappe.session.user}, limit_page_length=limit_page_length)
    content_set = {f['parent'] for f in filtered}
    content = []
    for c in content_set:
        doc = frappe.get_doc(doctype, c)
        content.append(doc)
    return content

@frappe.whitelist(allow_guest = False)
def get_content_recommended_for_user(doctype, sectors, limit_page_length=20):
    filtered = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': doctype, 'sector': ['in', sectors], 'owner': ['!=', frappe.session.owner]}, limit_page_length=limit_page_length)
    content_set = {f['parent'] for f in filtered}
    content = []
    for c in content_set:
        doc = frappe.get_doc(doctype, c)
        if doc.is_published:
            doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
            content.append(doc)
    return content

@frappe.whitelist(allow_guest = False)
def get_interesting_content():
    print('getting interesting content for {}'.format(frappe.session.user))
    try:
        user = frappe.get_doc('User Profile', frappe.session.user)
        sectors = [sector.sector for sector in user.sectors]
        return {
            'problems': get_content_recommended_for_user('Problem', sectors),
            'solutions': get_content_recommended_for_user('Solution', sectors),
            'users': get_content_recommended_for_user('User Profile', sectors),
            'user_problems': get_content_by_user('Problem'),
            'user_solutions': get_content_by_user('Solution'),
            'watched_problems': get_content_watched_by_user('Problem'),
            'watched_solutions': get_content_watched_by_user('Solution'),
        }
    except:
        frappe.throw('Please create your user profile to personalise this page')

@frappe.whitelist(allow_guest = False)
def delete_contribution(child_doctype, name):
    try:
        frappe.delete_doc(child_doctype, name)
        return True
    except:
        frappe.throw('{} not found in {}.'.format(name, child_doctype))

@frappe.whitelist(allow_guest = False)
def delete_enrichment(name):
    try:
        e = frappe.get_doc('Enrichment Table', {'enrichment': name})
        # delete from the problem child table
        frappe.delete_doc('Enrichment Table', e.name)
        # delete the primary document
        frappe.delete_doc('Enrichment', name)
        return True
    except:
        frappe.throw('Enrichment not found.')