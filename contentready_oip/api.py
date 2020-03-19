import frappe
import json
from frappe import _
import platform

python_version_2 = platform.python_version().startswith('2')

def nudge_guests():
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.throw('Please login to collaborate.')

@frappe.whitelist(allow_guest = True)
def set_location_filter(filter_location_name=None, filter_location_lat=None,filter_location_lng=None, filter_location_range=25):
    if filter_location_name != None:
        frappe.session.data['filter_location_name'] = filter_location_name
    if filter_location_lat != None:
        frappe.session.data['filter_location_lat'] = float(filter_location_lat)
    if filter_location_lng != None:
        frappe.session.data['filter_location_lng'] = float(filter_location_lng)
    if filter_location_range != None:
        frappe.session.data['filter_location_range'] = int(filter_location_range)
    return filter_location_lat, filter_location_lng, filter_location_range

@frappe.whitelist(allow_guest = True)
def clear_location_filter():
    frappe.session.data['filter_location_name'] = ''
    frappe.session.data['filter_location_lat'] = None
    frappe.session.data['filter_location_lng'] = None
    frappe.session.data['filter_location_range'] = None
    return True


@frappe.whitelist(allow_guest = True)
def set_sector_filter(filter_sectors=[]):
    if not isinstance(filter_sectors, list):
        filter_sectors = json.loads(filter_sectors)
    if not filter_sectors:
        filter_sectors = ['all']
    frappe.session.data['filter_sectors'] = filter_sectors
    return frappe.session.data['filter_sectors']

@frappe.whitelist(allow_guest = True)
def get_available_sectors():
    return frappe.get_list('Sector', ['name', 'title'])

@frappe.whitelist(allow_guest = True)
def get_filters():
    filter_sectors = ['all']
    filter_location_name = ''
    filter_location_lat = None
    filter_location_lng = None
    filter_location_range = None
    if 'filter_location_name' in frappe.session.data:
        filter_location_name = frappe.session.data.filter_location_name
    if 'filter_location_lat' in frappe.session.data:
        filter_location_lat = frappe.session.data.filter_location_lat
    if 'filter_location_lng' in frappe.session.data:
        filter_location_lng = frappe.session.data.filter_location_lng
    if 'filter_location_range' in frappe.session.data:
        filter_location_range = frappe.session.data.filter_location_range
    if 'filter_sectors' in frappe.session.data:
        filter_sectors = frappe.session.data.filter_sectors
    available_sectors = frappe.get_list('Sector', ['name', 'title'])
    return {
        'filter_location_name': filter_location_name,
        'filter_location_lat': filter_location_lat,
        'filter_location_lng': filter_location_lng,
        'filter_location_range': filter_location_range,
        'filter_sectors': filter_sectors,
        'available_sectors': available_sectors
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

def convert_if_json(value):
    cmp_type = str
    if python_version_2:
        cmp_type = basestring
    if isinstance(value, cmp_type):
        value = json.loads(value)
    return value

def get_content_for_context(context, doctype, key, limit_page_length=20):
    context.available_sectors = get_available_sectors()
    parameters = frappe.form_dict
    # page
    try:
        context.page = int(parameters['page'])
    except:
        context.page = 1
    limit_start = context.page - 1
    # limit_page_length = 20
    filtered_content = get_filtered_content(doctype)
    context.start = limit_start*limit_page_length
    context.end = context.start + limit_page_length
    context.total_count = len(filtered_content)
    if context.end > context.total_count:
        context.end = context.total_count
    context.has_next_page = False
    if context.total_count > limit_page_length*context.page:
        context.has_next_page = True
    context[key] = filtered_content[context.start:context.end]
    return context


@frappe.whitelist(allow_guest = True)
def get_filtered_content(doctype):
    parameters = frappe.form_dict
    # filter_location_name
    try:
        filter_location_name = parameters['loc']
    except:
        filter_location_name = None
    # filter_location_lat
    try:
        filter_location_lat = float(parameters['lat'])
    except:
        filter_location_lat = None
    # filter_location_lng
    try:
        filter_location_lng = float(parameters['lng'])
    except:
        filter_location_lng = None
    # filter_location_range
    try:
        filter_location_range = int(parameters['rng'])
    except:
        filter_location_range = None
    # filter_sectors
    try:
        filter_sectors = json.loads(parameters['sectors'])
    except Exception as e:
        filter_sectors = ['all']
    if not filter_sectors:
        filter_sectors = ['all']
    if 'all' in filter_sectors:
        filtered = frappe.get_list(doctype, filters={'is_published': True})
        content_set = {f['name'] for f in filtered}
    else:
        filtered = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': doctype, 'sector': ['in', filter_sectors]})
        content_set = {f['parent'] for f in filtered}
    # TODO: Implement location filtering using Elasticsearch
    from geopy import distance
    content = []
    for c in content_set:
        doc = frappe.get_doc(doctype, c)
        if doc.is_published:
            if (doc.latitude != None) and (doc.longitude != None) and (filter_location_lat != None) and (filter_location_lng != None) and (filter_location_range != None):
                distance_km = distance.distance((filter_location_lat, filter_location_lng), (float(doc.latitude), float(doc.longitude))).km
                if distance_km > filter_location_range:
                    # skip this document as it's outside our bounds
                    continue
            content.append(doc)
    return content

@frappe.whitelist(allow_guest = True)
def search_content_by_text(doctype, text, limit_page_length=5, html=True):
    names = frappe.db.get_list(doctype, or_filters={'title': ['like', '%{}%'.format(text)], 'description': ['like', '%{}%'.format(text)], 'is_published': True}, limit_page_length=limit_page_length)
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
def global_search_content_by_text(text, limit_page_length=5, html=True):
    sectors = set()
    payload = {}
    for doctype in ['Problem', 'Solution']:
        payload[doctype] = []
        content = search_content_by_text(doctype, text, limit_page_length, html=False)
        for c in content:
            content_type = doctype.lower()
            template = "templates/includes/{}/{}_card.html".format(content_type, content_type)
            context = {
                content_type: c
            }
            html = frappe.render_template(template, context)
            payload[doctype].append(html)
            for s in c.sectors:
                sectors.add(s.sector)
    contributors = get_content_recommended_for_user('User Profile', sectors, limit_page_length=limit_page_length)
    doctype = 'User Profile'
    payload[doctype] = []
    for c in contributors:
        template = "templates/includes/common/user_card.html"
        context = {
            'user': c
        }
        html = frappe.render_template(template, context)
        payload[doctype].append(html)
    return payload

@frappe.whitelist(allow_guest = True)
def search_contributors_by_text(text, limit_page_length=5, html=True):
    doctype = 'User Profile'
    names = frappe.db.get_list(doctype, or_filters={'full_name': ['like', '%{}%'.format(text)]}, limit_page_length=limit_page_length)
    content = []
    names = {n['name'] for n in names}
    for p in names:
        doc = frappe.get_doc(doctype, p)
        doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
        if html:
            template = "templates/includes/common/user_card.html"
            context = {
                'user': doc
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
def has_user_contributed(child_doctype, parent_doctype, parent_name):
    contributions_by_user = frappe.db.count(child_doctype, filters={'user': frappe.session.user, 'parenttype': parent_doctype, 'parent': parent_name})
    return contributions_by_user > 0

@frappe.whitelist(allow_guest = True)
def can_user_contribute(child_doctype, parent_doctype, parent_name):
    doc_owner = frappe.get_value(parent_doctype, parent_name, 'owner')
    print(doc_owner, frappe.session.user)
    return has_user_contributed(child_doctype, parent_doctype, parent_name), doc_owner == frappe.session.user

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
def add_comment(doctype, name, text, media=None, html=True):
    doc = frappe.get_doc({
        'doctype': 'Discussion',
        'text': text,
        'user': frappe.session.user,
        'parent_doctype': doctype,
        'parent_name': name
    })
    media = json.loads(media)
    for f in media:
        a = doc.append('media', {})
        a.attachment = f
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
def get_problem_overview(name, html=True):
    doc = frappe.get_doc('Problem', name)
    if html:
        context = {
            'problem': doc
        }
        template = "templates/includes/problem/problem_card.html"
        html = frappe.render_template(template, context)
        context = doc.as_dict()
        template = "templates/includes/problem/overview.html"
        html += '<div style="background-color: white;">' + frappe.render_template(template, context) + '</div>'
        return html, doc.name
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def add_primary_content(doctype, doc, is_draft=False):
    doc = json.loads(doc)
    if isinstance(is_draft,str):
        is_draft = json.loads(is_draft)
    if 'name' in doc and doc['name']:
        # edit
        content = frappe.get_doc(doctype, doc['name'])
        content.update(doc)
        content.flags.ignore_mandatory = is_draft
        content.save()
    else:
        # create
        content = frappe.get_doc({
            'doctype': doctype
        })
        content.update(doc)
        content.insert(ignore_mandatory=is_draft)
    frappe.db.commit()
    content = frappe.get_doc(doctype, content.name)
    return content


@frappe.whitelist(allow_guest = False)
def add_enrichment(doc,is_draft=False):
    doc = json.loads(doc)
    if isinstance(is_draft,str):
        is_draft = json.loads(is_draft)
    if not ('problem' in doc or doc['problem']):
        return False
    doctype = 'Enrichment'
    if 'name' in doc and doc['name']:
        # edit
        content = frappe.get_doc(doctype, doc['name'])
        content.update(doc)
        content.flags.ignore_mandatory = is_draft
        content.save()
    else:
        # create
        if has_user_contributed('Enrichment Table', 'Problem', doc['problem']):
            frappe.throw('You have already enriched this problem.')
        content = frappe.get_doc({
            'doctype': doctype
        })
        content.update(doc)
        content.insert(ignore_mandatory=is_draft)
    frappe.db.commit()
    content = frappe.get_doc(doctype, content.name)
    route = frappe.get_value('Problem', content.problem, 'route')
    return content, route

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
def get_content_by_user(doctype, limit_page_length=5):
    filtered = frappe.get_list(doctype, filters={'owner': frappe.session.user, 'is_published': True}, limit_page_length=limit_page_length)
    content = []
    for f in filtered:
        doc = frappe.get_doc(doctype, f['name'])
        if doc.is_published:
            content.append(doc)
    return content

@frappe.whitelist(allow_guest = False)
def get_contributions_by_user(parent_doctype, child_doctypes, limit_page_length=5):
    # content_set = set()
    content_dict = {}
    for child_doctype in child_doctypes:
        filtered = frappe.get_list(child_doctype, fields=['parent', 'modified'], filters={'user': frappe.session.user, 'parenttype': parent_doctype})
        for f in filtered:
            if f['parent'] not in content_dict:
                content_dict[f['parent']] = []
            content_dict[f['parent']].append({'type': child_doctype, 'modified': f['modified']})
            # content_set.add(f['parent'])
    content = []
    # print(content_dict)
    # for c in content_set:
    for c in content_dict:
        doc = frappe.get_doc(parent_doctype, c)
        if doc.is_published:
            doc.enriched = False
            doc.validated = False
            doc.collaborated = False
            doc.discussed = False
            for e in content_dict[c]:
                contribution_type = e['type']
                if contribution_type == 'Enrichment Table':
                    doc.enriched = e['modified']
                elif contribution_type == 'Validation Table':
                    doc.validated = e['modified']
                elif contribution_type == 'Collaboration Table':
                    doc.collaborated = e['modified']
                elif contribution_type == 'Discussion Table':
                    doc.discussed = e['modified']
            content.append(doc)
    return content

@frappe.whitelist(allow_guest = False)
def get_content_watched_by_user(doctype, limit_page_length=5):
    filtered = frappe.get_list('Watch Table', fields=['parent'], filters={'parenttype': doctype, 'user': frappe.session.user}, limit_page_length=limit_page_length)
    content_set = {f['parent'] for f in filtered}
    content = []
    for c in content_set:
        doc = frappe.get_doc(doctype, c)
        if doc.is_published:
            content.append(doc)
    return content

@frappe.whitelist(allow_guest = False)
def get_content_recommended_for_user(doctype, sectors, limit_page_length=5):
    content = []
    try:
        filtered = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': doctype, 'sector': ['in', sectors], 'owner': ['!=', frappe.session.user]}, limit_page_length=limit_page_length)
        content_set = {f['parent'] for f in filtered}
        for c in content_set:
            doc = frappe.get_doc(doctype, c)
            if doc.is_published:
                doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
                content.append(doc)
    except:
        pass
    return content

@frappe.whitelist(allow_guest = False)
def get_dashboard_content(limit_page_length=5):
    try:
        user = frappe.get_doc('User Profile', frappe.session.user)
        sectors = [sector.sector for sector in user.sectors]
    except:
        sectors = []
        # frappe.throw('Please create your user profile to personalise this page')
    return {
        'problems': get_content_recommended_for_user('Problem', sectors, limit_page_length=limit_page_length),
        'solutions': get_content_recommended_for_user('Solution', sectors, limit_page_length=limit_page_length),
        'users': get_content_recommended_for_user('User Profile', sectors, limit_page_length=limit_page_length),
        'user_problems': get_content_by_user('Problem', limit_page_length=limit_page_length),
        'user_solutions': get_content_by_user('Solution', limit_page_length=limit_page_length),
        'watched_problems': get_content_watched_by_user('Problem', limit_page_length=limit_page_length),
        'watched_solutions': get_content_watched_by_user('Solution', limit_page_length=limit_page_length),
        'problem_contributions': get_contributions_by_user('Problem', ['Enrichment Table', 'Validation Table', 'Collaboration Table', 'Discussion Table'], limit_page_length=limit_page_length),
        'solution_contributions': get_contributions_by_user('Solution', ['Validation Table', 'Collaboration Table', 'Discussion Table'], limit_page_length=limit_page_length),
    }

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

@frappe.whitelist(allow_guest=True)
def register(form=None):
    if not form:
        form = dict(frappe.form_dict)
    frappe.set_user('Administrator')
    form['doctype'] = 'User'
    user_by_email = frappe.db.get("User", {"email": form['email']})
    if not user_by_email:
        from frappe.utils import random_string
        user = frappe.get_doc({
            "doctype":"User",
            "email": form['email'],
            "first_name": form['first_name'],
            "last_name": form['last_name'],
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": False
        })
        user.flags.ignore_permissions = True
        user.insert()
        # set default signup role as per Portal Settings
        default_role = frappe.db.get_value("Portal Settings", None, "default_role")
        if default_role:
            user.add_roles(default_role)
        frappe.db.commit()
        success_msg = "You will shortly receive a verification email with a link to set your password and start the application process."
        frappe.respond_as_web_page(_("Sign up successful"),
            _(success_msg),
            http_status_code=200, indicator_color='green', fullpage = True, primary_action='/')
        return frappe.website.render.render("message", http_status_code=200)
    else:
        error_msg = 'You have already signed up with this email. Try logging in instead.'
        # frappe.throw(error_msg)
        frappe.respond_as_web_page(_("Sign up error"),
            _(error_msg),
            http_status_code=400, indicator_color='red', fullpage = True, primary_action='/')
        return frappe.website.render.render("message", http_status_code=400)
    