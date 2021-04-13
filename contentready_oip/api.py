import frappe
import json
import mimetypes
import platform
from frappe import _
from frappe.utils.background_jobs import enqueue
from frappe.utils.html_utils import clean_html
from frappe.email.doctype.email_template.email_template import get_email_template
from contentready_oip.google_vision import is_content_explicit
from contentready_oip import (
    problem_search,
    solution_search,
    user_search,
    organisation_search,
    ip_location_lookup
)
from user_agents import parse as ua_parse
from frappe.utils import random_string
from geopy import distance
from functools import cmp_to_key


python_version_2 = platform.python_version().startswith("2")


def nudge_guests():
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("Please login to collaborate.")


def create_profile_from_user(doc, event_name):
    if doc.doctype == 'User' and doc.email:
        print("\n\n\ncreate_profile_from_user", doc.as_dict())
        create_user_profile_if_missing(doc.email)


def create_user_profile_if_missing(email=None):
    print("\n\n\create_user_profile_if_missing", email)
    if not email:
        email = frappe.session.user
    if not frappe.db.exists('User Profile', email):
        profile = frappe.get_doc({
            'doctype': 'User Profile',
            'user': email,
            'owner': email
        })
        profile.save()
        frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def set_sector_filter(filter_sectors=[]):
    if not isinstance(filter_sectors, list):
        filter_sectors = json.loads(filter_sectors)
    if not filter_sectors:
        filter_sectors = []
    frappe.session.data["filter_sectors"] = filter_sectors
    return frappe.session.data["filter_sectors"]


@frappe.whitelist(allow_guest=True)
def get_available_sectors():
    hostname = get_url()
    try:
        domain = frappe.get_doc("OIP White Label Domain", {"url": hostname})
        sectors = [
            {"name": s.sector, "title": s.sector_title, "description": s.description}
            for s in domain.sectors
        ]
        assert (
            len(sectors) > 0
        ), "Need at least 1 sector per domain. Reverting to defaults."
        return sectors
    except:
        return frappe.get_list("Sector", ["name", "title", "description"])


@frappe.whitelist(allow_guest=True)
def get_partners():
    hostname = get_url()
    try:
        domain = frappe.get_doc("OIP White Label Domain", {"url": hostname})
        partners = [
            {"brandmark": p.brandmark, "url": p.url, "title": p.title}
            for p in domain.partners
        ]
        return partners
    except Exception as e:
        print(str(e))


@frappe.whitelist(allow_guest=True)
def get_url():
    return frappe.utils.get_host_name_from_request()


@frappe.whitelist(allow_guest=True)
def get_doc_by_type_name(doctype, name):
    return frappe.get_doc(doctype, name)


@frappe.whitelist(allow_guest=True)
def get_all_doc(doctype):
    doc_list = frappe.get_list(doctype)
    doc = []
    for doc_name in doc_list:
        d = frappe.get_doc(doctype, doc_name["name"])
        if d.is_published:
            doc.append(d)

    return doc


@frappe.whitelist(allow_guest=True)
def get_doc_field(doctype, name, field):
    try:
        field = json.loads(field)
    except:
        field = field

    return frappe.get_value(doctype, name, field)


@frappe.whitelist(allow_guest=True)
def get_child_table(child_table_doctype, parent_doctype, parent_name):
    return frappe.get_all(
        child_table_doctype,
        filters={"parenttype": parent_doctype, "parent": parent_name},
    )


@frappe.whitelist(allow_guest=True)
def search_content_by_text(doctype, text, limit_page_length=5, html=True):
    content = []
    try:
        names = frappe.db.get_list(
            doctype,
            or_filters={
                "title": ["like", "%{}%".format(text)],
                "description": ["like", "%{}%".format(text)],
            },
            filters={"is_published": True},
            limit_page_length=limit_page_length,
        )
        names = {n["name"] for n in names}
        for p in names:
            try:
                doc = frappe.get_doc(doctype, p)
                doc.photo = frappe.get_value("User Profile", doc.owner, "photo")
                if html:
                    content_type = doctype.lower()
                    template = "templates/includes/{}/{}_card.html".format(
                        content_type, content_type
                    )
                    context = {content_type: doc}
                    html = frappe.render_template(template, context)
                    content.append(html)
                else:
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content


@frappe.whitelist(allow_guest=True)
def get_orgs_list():
    all_orgs = frappe.get_list("Organisation", fields=["title", "name"])
    return [{"label": o["title"], "value": o["name"]} for o in all_orgs]


@frappe.whitelist(allow_guest=True)
def get_service_categories():
    all_categories = frappe.get_list("Service Category", fields=["title", "name"])
    return [{"label": o["title"], "value": o["name"]} for o in all_categories]


@frappe.whitelist(allow_guest=True)
def get_sdg_list():
    sdgs = frappe.get_list("Sustainable Development Goal", fields=["title", "name"])
    return [{"label": o["title"], "value": o["name"]} for o in sdgs]


@frappe.whitelist(allow_guest=False)
def get_user_list():
    all_users = frappe.get_list(
        "User Profile",
        filters={"user": ["not in", ["Guest", "Administrator"]]},
        fields=["full_name", "user"],
    )
    return [{"text": o["full_name"], "id": o["user"]} for o in all_users]


@frappe.whitelist(allow_guest=True)
def get_persona_list():
    all_personas = frappe.get_list("Persona", fields=["title", "name"])
    return [{"label": o["title"], "value": o["name"]} for o in all_personas]


@frappe.whitelist(allow_guest=True)
def get_sector_list():
    available_sectors = get_available_sectors()
    return [
        {"label": o["title"], "value": o["name"], "description": o["description"]}
        for o in available_sectors
    ]


@frappe.whitelist(allow_guest=True)
def get_homepage_stats():
    return {
        "problems": frappe.db.count("Problem", filters={"is_published": True}),
        "solutions": frappe.db.count("Solution", filters={"is_published": True}),
        "collaborators": frappe.db.count("User Profile"),
    }


@frappe.whitelist(allow_guest=True)
def has_user_contributed(child_doctype, parent_doctype, parent_name):
    contributions_by_user = frappe.db.count(
        child_doctype,
        filters={
            "owner": frappe.session.user,
            "parent_doctype": parent_doctype,
            "parent_name": parent_name,
        },
    )
    return contributions_by_user > 0


@frappe.whitelist(allow_guest=True)
def can_user_contribute(child_doctype, parent_doctype, parent_name):
    doc_owner = frappe.get_value(parent_doctype, parent_name, "owner")
    return (
        has_user_contributed(child_doctype, parent_doctype, parent_name),
        doc_owner == frappe.session.user,
    )


@frappe.whitelist(allow_guest=False)
def toggle_contribution(child_doctype, parent_doctype, parent_name):
    nudge_guests()
    contributions = frappe.get_all(
        child_doctype,
        filters={
            "owner": frappe.session.user,
            "parent_doctype": parent_doctype,
            "parent_name": parent_name,
        },
    )
    if len(contributions) > 0:
        # user has already contributed to this document
        for c in contributions:
            frappe.delete_doc(child_doctype, c["name"])
    else:
        # add contribution for user
        doc = frappe.get_doc(
            {
                "doctype": child_doctype,
                "parent_doctype": parent_doctype,
                "parent_name": parent_name,
            }
        )
        doc.save()
        frappe.db.commit()
    return (
        has_user_contributed(child_doctype, parent_doctype, parent_name),
        get_child_table(child_doctype, parent_doctype, parent_name),
    )


@frappe.whitelist(allow_guest=False)
def add_comment(doctype, name, text, media=None, html=True):
    # Remove double quotes from text
    text = json.loads(text)
    doc = frappe.get_doc(
        {
            "doctype": "Discussion",
            "text": text,
            "owner": frappe.session.user,
            "parent_doctype": doctype,
            "parent_name": name,
        }
    )
    media = json.loads(media)
    for f in media:
        a = doc.append("media", {})
        a.attachment = f
    doc.save()
    frappe.db.commit()
    if html:
        template = "templates/includes/common/comment.html"
        context = {"comment": doc}
        html = frappe.render_template(template, context)
        return html
    else:
        return doc


@frappe.whitelist(allow_guest=False)
def get_problem_detail_modal(name, html=True):
    # Get problem detail modal on add solution and edit solution.
    # { param: string } eg. 'Problem001'
    doc = frappe.get_doc("Problem", name)
    if html:
        detail_modal_template = "templates/includes/solution/problem_detail_modal.html"
        detail_modal = frappe.render_template(detail_modal_template, doc.as_dict())
        enrichments = frappe.get_list(
            "Enrichment", filters={"parent_doctype": "Problem", "parent_name": name}
        )
        enrichment_list = [
            frappe.get_doc("Enrichment", e).as_dict() for e in enrichments
        ]
        return (detail_modal, enrichment_list)
    else:
        return doc


@frappe.whitelist(allow_guest=False)
def get_problem_card(name, html=True):
    doc = frappe.get_doc("Problem", name)
    if html:
        context = {"problem": doc}
        problem_card_template = "templates/includes/problem/problem_card.html"
        overview_tab_template = "templates/includes/problem/overview.html"

        problem_card = frappe.render_template(problem_card_template, context)
        overview_tab = frappe.render_template(overview_tab_template, doc.as_dict())
        return problem_card, doc.name, overview_tab
    else:
        return doc


@frappe.whitelist(allow_guest=False)
def get_problem_details(name):
    doc = frappe.get_doc("Problem", name)
    return doc


@frappe.whitelist(allow_guest=False)
def get_problem_overview(name, html=True):
    doc = frappe.get_doc("Problem", name)
    if html:
        context = {"problem": doc}
        template = "templates/includes/problem/problem_card.html"
        html = frappe.render_template(template, context)
        context = doc.as_dict()
        template = "templates/includes/problem/overview.html"
        html += (
            '<div style="background-color: white;">'
            + frappe.render_template(template, context)
            + "</div>"
        )
        return html, doc.name
    else:
        return doc

@frappe.whitelist(allow_guest = True)
def add_primary_content(doctype, doc, is_draft=False):
    doc = json.loads(doc)
    if isinstance(is_draft, str):
        is_draft = json.loads(is_draft)
    # loop over all fields and call clean_html
    # to sanitize the input by removing html, css and JS
    for fieldname, value in doc.items():
        doc[fieldname] = clean_html(value)
    if "name" in doc and doc["name"]:
        # edit
        content = frappe.get_doc(doctype, doc["name"])
        content.update(doc)
        content.flags.ignore_mandatory = is_draft
        content.save()
    else:
        # create
        content = frappe.get_doc({"doctype": doctype})
        content.update(doc)
        content.insert(ignore_mandatory=is_draft)
    frappe.db.commit()
    content = frappe.get_doc(doctype, content.name)
    return content


@frappe.whitelist(allow_guest=False)
def add_enrichment(doc, is_draft=False):
    doc = json.loads(doc)
    if isinstance(is_draft, str):
        is_draft = json.loads(is_draft)
    if not ("problem" in doc or doc["problem"]):
        return False
    doctype = "Enrichment"
    if doc.get("name"):
        # edit
        content = frappe.get_doc(doctype, doc["name"])
        content.update(doc)
        content.flags.ignore_mandatory = is_draft
        content.save()
    else:
        # create
        if has_user_contributed("Enrichment", "Problem", doc["problem"]):
            frappe.throw("You have already enriched this problem.")
        content = frappe.get_doc(
            {
                "doctype": doctype,
                "parent_doctype": "Problem",
                "parent_name": doc["problem"],
            }
        )
        content.update(doc)
        content.insert(ignore_mandatory=is_draft)
    frappe.db.commit()
    content = frappe.get_doc(doctype, content.name)
    route = frappe.get_value("Problem", content.problem, "route")
    return content, route


@frappe.whitelist(allow_guest=False)
def add_or_edit_validation(doctype, name, validation, html=True):
    validation = json.loads(validation)
    if doctype == "Validation":
        # in edit mode
        doc = frappe.get_doc("Validation", name)
        doc.update(validation)
        doc.save()
        total_count = frappe.db.count(
            "Validation",
            filters={"parent_doctype": v.parent_doctype, "parent_name": v.parent_name},
        )
    else:
        if has_user_contributed("Validation", doctype, name):
            frappe.throw(
                "You have already validated this {}.".format(doctype).capitalize()
            )
        doc = frappe.get_doc(
            {"doctype": "Validation", "parent_doctype": doctype, "parent_name": name}
        )
        doc.update(validation)
        doc.save()
        total_count = frappe.db.count(
            "Validation", filters={"parent_doctype": doctype, "parent_name": name}
        )
    frappe.db.commit()
    if html:
        context = {"validation": doc}
        template = "templates/includes/common/validation_card.html"
        html = frappe.render_template(template, context)
        return html, total_count
    else:
        return doc


@frappe.whitelist(allow_guest=False)
def add_or_edit_collaboration(doctype, name, collaboration, html=True):
    collaboration = json.loads(collaboration)
    if doctype == "Collaboration":
        # in edit mode
        doc = frappe.get_doc("Collaboration", name)
        doc.comment = collaboration["comment"]
        doc.personas = []
        doc.personas_list = ",".join(collaboration["personas"])
        for p in collaboration["personas"]:
            row = doc.append("personas", {})
            row.persona = p
        doc.save()
        total_count = frappe.db.count(
            "Collaboration",
            filters={
                "parent_doctype": doc.parent_doctype,
                "parent_name": doc.parent_name,
            },
        )
    else:
        # creating new collaboration
        if has_user_contributed('Collaboration', doctype, name):
            frappe.throw('You have already added your collaboration intent on this {}.'.format(doctype).capitalize())
        doc = frappe.get_doc({
            'doctype': 'Collaboration',
            'comment': collaboration['comment'],
            'parent_doctype': doctype,
            'parent_name': name
        })
        if has_service_provider_role():
            collaboration['personas'].append('service_provider')
        for p in collaboration['personas']:
            row = doc.append('personas', {})
            row.persona = p
        doc.save()
        frappe.db.commit()
        total_count = frappe.db.count(
            "Collaboration", filters={"parent_doctype": doctype, "parent_name": name}
        )
    frappe.db.commit()
    if html:
        context = {"collaboration": doc, "personas": get_persona_list()}
        template = "templates/includes/common/collaboration_card.html"
        html = frappe.render_template(template, context)
        return html, total_count
    else:
        return doc


@frappe.whitelist(allow_guest=False)
def change_collaboration_status(docname, status):
    doc = frappe.get_doc("Collaboration", docname)
    if frappe.session.user == doc.recipient:
        doc.status = status
        doc.save()
        frappe.db.commit()
        return True


@frappe.whitelist(allow_guest=True)
def add_subscriber(email, first_name="", last_name=""):
    contact = frappe.get_doc(
        {
            "doctype": "OIP Contact",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
    )
    contact.insert()
    frappe.db.commit()
    r = get_email_template("New Subscriber", {})
    frappe.sendmail([email], subject=r["subject"], message=r["message"], delayed=True)
    return True


@frappe.whitelist(allow_guest=True)
def unsubscribe_email(email):
    try:
        contact = frappe.get_doc("OIP Contact", {"email": email})
        contact.is_unsubscribed = True
        contact.save()
        frappe.db.commit()
        success_msg = "You have been unsubscribed from our emails."
        frappe.respond_as_web_page(
            _("Unsubscribe Successful"),
            _(success_msg),
            http_status_code=200,
            indicator_color="green",
            fullpage=True,
            primary_action="/",
        )
        return frappe.website.render.render("message", http_status_code=200)
    except Exception as e:
        print(str(e))
        error_msg = "Error while unsubscribing. {}".format(str(e))
        frappe.respond_as_web_page(
            _("Unsubscribe Unsuccessful"),
            _(error_msg),
            http_status_code=503,
            indicator_color="red",
            fullpage=True,
            primary_action="/",
        )
        return frappe.website.render.render("message", http_status_code=503)


@frappe.whitelist(allow_guest=False)
def get_content_by_user(doctype, limit_page_length=5):
    content = []
    try:
        filtered = frappe.get_list(
            doctype,
            filters={"owner": frappe.session.user, "is_published": True},
            limit_page_length=limit_page_length,
        )
        for f in filtered:
            try:
                doc = frappe.get_doc(doctype, f["name"])
                if doc.is_published:
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content


@frappe.whitelist(allow_guest=False)
def get_contributions_by_user(parent_doctype, child_doctypes, limit_page_length=5):
    content = []
    try:
        content_dict = {}
        for child_doctype in child_doctypes:
            filtered = frappe.get_list(
                child_doctype,
                fields=["parent_name", "modified"],
                filters={"user": frappe.session.user, "parent_doctype": parent_doctype},
            )
            for f in filtered:
                if f["parent_name"] not in content_dict:
                    content_dict[f["parent_name"]] = []
                content_dict[f["parent_name"]].append(
                    {"type": child_doctype, "modified": f["modified"]}
                )
        content = []
        for c in content_dict:
            try:
                doc = frappe.get_doc(parent_doctype, c)
                if doc.is_published:
                    doc.enriched = False
                    doc.validated = False
                    doc.collaborated = False
                    doc.discussed = False
                    for e in content_dict[c]:
                        contribution_type = e["type"]
                        if contribution_type == "Enrichment":
                            doc.enriched = e["modified"]
                        elif contribution_type == "Validation":
                            doc.validated = e["modified"]
                        elif contribution_type == "Collaboration":
                            doc.collaborated = e["modified"]
                        elif contribution_type == "Discussion":
                            doc.discussed = e["modified"]
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content


@frappe.whitelist(allow_guest=False)
def get_content_watched_by_user(doctype, limit_page_length=5):
    content = []
    try:
        filtered = frappe.get_list(
            "Watch",
            fields=["parent"],
            filters={"parenttype": doctype, "user": frappe.session.user},
            limit_page_length=limit_page_length,
        )
        content_set = {f["parent"] for f in filtered}
        for c in content_set:
            try:
                doc = frappe.get_doc(doctype, c)
                if doc.is_published:
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content


@frappe.whitelist(allow_guest=False)
def get_content_recommended_for_user(
    doctype, sectors, limit_page_length=5, creation=None, html=False
):
    content = []
    try:
        if creation:
            filtered = frappe.get_list(
                "Sector Table",
                fields=["parent"],
                filters={
                    "parenttype": doctype,
                    "sector": ["in", sectors],
                    "owner": ["!=", frappe.session.user],
                    "creation": [">=", creation],
                },
            )
            content_set = {f["parent"] for f in filtered}
        else:
            if "all" in sectors:
                filtered = frappe.get_list(
                    doctype, filters={"owner": ["!=", frappe.session.user]}
                )
                content_set = {f["name"] for f in filtered}
            else:
                filtered = frappe.get_list(
                    "Sector Table",
                    fields=["parent"],
                    filters={
                        "parenttype": doctype,
                        "sector": ["in", sectors],
                        "owner": ["!=", frappe.session.user],
                    },
                )
                content_set = {f["parent"] for f in filtered}
        for c in content_set:
            try:
                doc = frappe.get_doc(doctype, c)
                # don't show content that the user has already contributed to
                if (
                    doc.is_published
                    and not has_user_contributed("Like", doctype, c)
                    and not has_user_contributed("Watch", doctype, c)
                    and not has_user_contributed("Validation", doctype, c)
                    and not has_user_contributed("Collaboration", doctype, c)
                    and not has_user_contributed("Enrichment", doctype, c)
                ):
                    doc.photo = frappe.get_value("User Profile", doc.owner, "photo")
                    if html:
                        if doctype == "Problem":
                            context = {"problem": doc}
                            template = "templates/includes/problem/problem_card.html"
                        elif doctype == "Solution":
                            context = {"solution": doc}
                            template = "templates/includes/solution/solution_card.html"
                        elif doctype == "User Profile":
                            context = {"user": doc}
                            template = "templates/includes/common/user_card.html"
                        html = frappe.render_template(template, context)
                        content.append(html)
                    else:
                        content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content


@frappe.whitelist(allow_guest=False)
def get_drafts_by_user(doctypes=None, limit_page_length=5):
    content = []
    if not doctypes:
        doctypes = ["Problem", "Solution", "Enrichment"]
    filtered = []
    try:
        for doctype in doctypes:
            # using frappe.db.sql here to allow insertion of doctype into the results
            # post-sorting we need the doctype to retrieve the full document
            query = """select modified,name,'{}' as doctype from `tab{}` where is_published=false and owner='{}';""".format(
                doctype, doctype, frappe.session.user
            )
            sublist = frappe.db.sql(query)
            filtered += sublist
        # Sorts by first element, which is, conveniently, `modified`
        # reverse=True ensures descending order
        filtered.sort(reverse=True)
        for f in filtered:
            try:
                doc = frappe.get_doc(f[2], f[1])
                doc.photo = frappe.get_value("User Profile", doc.owner, "photo")
                content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content


@frappe.whitelist(allow_guest=False)
def get_dashboard_content(limit_page_length=5, content_list=None):
    if not content_list:
        content_list = [
            "recommended_problems",
            "recommended_solutions",
            "recommended_users",
            "user_problems",
            "user_solutions",
            "watched_problems",
            "watched_solutions",
            "contributed_problems",
            "contributed_solutions",
            "drafts",
            "self_profile",
        ]
    try:
        user = frappe.get_doc("User Profile", frappe.session.user)
        sectors = [sector.sector for sector in user.sectors]
    except:
        sectors = []
        # frappe.throw('Please create your user profile to personalise this page')
    payload = {}
    if "recommended_problems" in content_list:
        payload["recommended_problems"] = get_content_recommended_for_user(
            "Problem", sectors, limit_page_length=limit_page_length
        )
    if "recommended_solutions" in content_list:
        payload["recommended_solutions"] = get_content_recommended_for_user(
            "Solution", sectors, limit_page_length=limit_page_length
        )
    if "recommended_users" in content_list:
        payload["recommended_users"] = get_content_recommended_for_user(
            "User Profile", sectors, limit_page_length=limit_page_length
        )
    if "user_problems" in content_list:
        payload["user_problems"] = get_content_by_user(
            "Problem", limit_page_length=limit_page_length
        )
    if "user_solutions" in content_list:
        payload["user_solutions"] = get_content_by_user(
            "Solution", limit_page_length=limit_page_length
        )
    if "self_profile" in content_list:
        payload["self_profile"] = frappe.get_doc(
            "User Profile", frappe.session.user
        ).as_dict()
    if "watched_problems" in content_list:
        payload["watched_problems"] = get_content_watched_by_user(
            "Problem", limit_page_length=limit_page_length
        )
    if "watched_solutions" in content_list:
        payload["watched_solutions"] = get_content_watched_by_user(
            "Solution", limit_page_length=limit_page_length
        )
    if "contributed_problems" in content_list:
        payload["contributed_problems"] = get_contributions_by_user(
            "Problem",
            ["Enrichment", "Validation", "Collaboration", "Discussion"],
            limit_page_length=limit_page_length,
        )
    if "contributed_solutions" in content_list:
        payload["contributed_solutions"] = get_contributions_by_user(
            "Solution",
            ["Validation", "Collaboration", "Discussion"],
            limit_page_length=limit_page_length,
        )
    if "drafts" in content_list:
        payload["drafts"] = get_drafts_by_user(limit_page_length=limit_page_length)
    return payload


@frappe.whitelist(allow_guest=False)
def delete_contribution(child_doctype, name):
    try:
        frappe.delete_doc(child_doctype, name)
        return True
    except:
        frappe.throw("{} not found in {}.".format(name, child_doctype))


@frappe.whitelist(allow_guest=False)
def delete_reply(reply):
    try:
        reply = json.loads(reply)
        frappe.delete_doc_if_exists("Discussion", reply["name"])
        frappe.db.commit()
        return True
    except:
        frappe.throw("Discussion not found.")


@frappe.whitelist(allow_guest=False)
def set_notification_as_read(notification_name):
    frappe.set_value("OIP Notification", notification_name, "is_read", True)
    return True


@frappe.whitelist(allow_guest=True)
def complete_linkedin_login(code, state):
    from frappe.integrations.oauth2_logins import decoder_compat
    from frappe.utils import oauth

    oauth2_providers = oauth.get_oauth2_providers()
    provider = "linkedin"
    flow = oauth.get_oauth2_flow(provider)
    args = {
        "data": {
            "code": code,
            "redirect_uri": oauth.get_redirect_uri(provider),
            "grant_type": "authorization_code",
        },
        "decoder": decoder_compat,
    }
    session = flow.get_auth_session(**args)
    api_endpoint = oauth2_providers[provider].get("api_endpoint")
    api_endpoint_args = oauth2_providers[provider].get("api_endpoint_args")
    info = session.get(api_endpoint, params=api_endpoint_args).json()
    profile_endpoint = "https://api.linkedin.com/v2/me"
    profile_params = {
        "projection": "(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"
    }
    profile = session.get(profile_endpoint, params=profile_params).json()
    info = unpack_linkedin_response(info, profile)
    if not (info.get("email_verified") or info.get("email")):
        frappe.throw(_("Email not verified with {0}").format(provider.title()))
    oauth.login_oauth_user(info, provider=provider, state=state)


def unpack_linkedin_response(info, profile=None):
    # info = {'elements': [{'handle~': {'emailAddress': 'tej@iotready.co'}, 'handle': 'urn:li:emailAddress:7957229897'}]}
    payload = {}
    payload["email"] = info["elements"][0]["handle~"]["emailAddress"]
    payload["handle"] = info["elements"][0]["handle"]
    if not profile:
        # needs a second API call to get name info, we should save the user even if that fails
        payload["first_name"] = payload["email"]
    else:
        import requests

        lang = list(profile["firstName"]["localized"].keys())[0]
        payload["first_name"] = profile["firstName"]["localized"][lang]
        payload["last_name"] = profile["lastName"]["localized"][lang]
        # The last element of the pictures array is the largest image
        picture_element = profile["profilePicture"]["displayImage~"]["elements"][-1]
        picture_url = picture_element["identifiers"][0]["identifier"]
        try:
            r = requests.get(picture_url)
            new_file = frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": "{}_profile.jpg".format(payload["email"]),
                    "content": r.content,
                    "decode": False,
                }
            )
            new_file.save()
            frappe.db.commit()
            payload["picture"] = new_file.file_url
        except Exception as e:
            print(str(e))
            payload["picture"] = picture_url
    return payload


@frappe.whitelist(allow_guest=True)
def send_sms_to_recipients(recipients, message):
    from frappe.core.doctype.sms_settings.sms_settings import send_sms

    send_sms(recipients, message)


@frappe.whitelist(allow_guest=True)
def share_doctype(recipients, doctype, docname, mode="email"):
    try:
        if isinstance(recipients, str):
            recipients = json.loads(recipients)
        if frappe.session.user != "Guest":
            user = frappe.get_doc("User Profile", frappe.session.user).as_dict()
        else:
            user = {"first_name": "An OIP contributor"}
        context = {}
        context.update(user)
        context["doctype"] = doctype.lower()
        hostname = get_url()
        if not hostname:
            hostname = "https://openinnovationplatform.org"
        context["url"] = hostname + "/" + frappe.get_value(doctype, docname, "route")
        r = get_email_template("Share Content", context)
        subject = r["subject"].replace("doctype", doctype.lower())
        frappe.sendmail(recipients, subject=subject, message=r["message"], delayed=True)
        return True
    except Exception as e:
        print(str(e))
        return False


def send_weekly_updates(emails=[]):
    from datetime import datetime, timedelta

    if emails:
        profiles = frappe.get_all("User Profile", filters={"user": ["in", emails]})
    else:
        profiles = frappe.get_all("User Profile")
    hostname = get_url()
    if not hostname:
        hostname = "https://openinnovationplatform.org"
    response = {}
    for p in profiles:
        try:
            user = frappe.get_doc("User Profile", p["name"])
            sectors = [sector.sector for sector in user.sectors]
            today = datetime.now()
            start = today - timedelta((today.weekday()) % 7)
            midnight = datetime.combine(start, datetime.min.time())
            context = {}
            context["problems"] = get_content_recommended_for_user(
                "Problem", sectors, limit_page_length=5, creation=midnight
            )
            context["solutions"] = get_content_recommended_for_user(
                "Solution", sectors, limit_page_length=5, creation=midnight
            )
            template = "templates/includes/common/homepage_showcase_content.html"
            context["content_html"] = frappe.render_template(template, context)
            context[
                "unsubscribe_link"
            ] = '<a href="{}/api/method/contentready_oip.api.unsubscribe_email?email={}">Click here</a>'.format(
                hostname, user.user
            )
            r = get_email_template("Weekly Updates", context)
            print(r)
            frappe.sendmail(
                user.user, subject=r["subject"], message=r["message"], delayed=True
            )
            response[user.user] = r
        except Exception as e:
            print(str(e))
            response[p["name"]] = str(e)
    return response


@frappe.whitelist(allow_guest=False)
def add_custom_domain(domain):
    import shlex, subprocess
    from subprocess import Popen, PIPE
    site = frappe.get_site_path()
    # Add domain to site_config.json
    cmd = shlex.split("bench setup add-domain {} --site {}".format(domain, site))
    subprocess.check_output(cmd)
    # Generate SSL certs and nginx config
    # The command waits for a response from the user before generating the nginx config
    cmd = shlex.split("sudo -H bench setup lets-encrypt -n {} --custom-domain {}".format(site, domain))
    foo_proc = Popen(cmd, stdin=PIPE, stdout=PIPE)
    foo_proc.communicate(input=b"y")
    # Restart nginx
    cmd = shlex.split("sudo systemctl restart nginx")
    subprocess.check_output(cmd)
    doc = frappe.get_doc("OIP White Label Domain", domain)
    doc.url = "https://{}".format(domain)
    doc.save()
    frappe.db.commit()


def setup_domain_hook(doc=None, event_name=None):
    try:
        add_custom_domain(doc.domain)
    except Exception as e:
        print(str(e))


@frappe.whitelist(allow_guest=False)
def set_document_value(doctype, docname, fieldname, fieldvalue):
    return frappe.set_value(doctype, docname, fieldname, fieldvalue)


def calc_distance(result, center):
    d = distance.distance(center, (result["latitude"], result["longitude"])).km
    return {"name": result["name"], "distance": d}


def sort_by_distance(results, center=(0, 0), range=None):
    results = [calc_distance(r, center) for r in results]
    results.sort(key=lambda r: r["distance"])
    return results


@frappe.whitelist(allow_guest=True)
def has_admin_role(user=None):
    if not user:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    allowed_roles = ["Administrator", "System Manager"]
    is_allowed = False
    for role in allowed_roles:
        if role in roles:
            is_allowed = True
    return is_allowed


@frappe.whitelist(allow_guest=True)
def has_collaborator_role(user=None):
    if not user:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    allowed_roles = ["Collaborator"]
    is_allowed = False
    for role in allowed_roles:
        if role in roles:
            is_allowed = True
    return is_allowed


@frappe.whitelist(allow_guest=True)
def has_service_provider_role(user=None):
    if not user:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    allowed_roles = ["Service Provider"]
    is_allowed = False
    for role in allowed_roles:
        if role in roles:
            is_allowed = True
    return is_allowed


@frappe.whitelist(allow_guest=True)
def get_url_metadata(url):
    import requests
    import re

    rejex = "((http(s)?:\/\/)?)(www\.)?((youtube\.com\/)|(youtu.be\/))[\S]+"
    pattern = re.compile(rejex)

    if pattern.match(url):
        youtubeApi = "https://www.youtube.com/oembed?url={}&format=json".format(url)
        r = requests.get(youtubeApi)
        response = {}
        response["provider"] = "youtube"
        response["data"] = r.json()
        return response
    else:
        vimeoId = url.split("https://vimeo.com/")[1]
        vimeoApi = "https://vimeo.com/api/v2/video/{}.json".format(vimeoId)
        r = requests.get(vimeoApi)
        response = {}
        response["provider"] = "vimeo"
        response["data"] = r.json()[0]
        return response


@frappe.whitelist(allow_guest=False)
def get_beneficiaries_from_sectors(sectors):
    beneficiary_list = set()
    try:
        sectors = json.loads(sectors)
        for sector in sectors:
            s = frappe.get_doc("Sector", sector)
            for b in s.beneficiaries:
                beneficiary_list.add(b.beneficiary)

        return beneficiary_list
    except Exception as e:
        print(str(e))


@frappe.whitelist(allow_guest=True)
def get_sectors_help():
    available_sectors = get_available_sectors()
    template = "templates/includes/common/sectors_help.html"
    html = frappe.render_template(template, {"available_sectors": available_sectors})
    return html


@frappe.whitelist(allow_guest=False)
def upload_file():
    IMAGE_TYPES = ("image/png", "image/jpeg")
    should_check_explicit = int(
        frappe.get_value("OIP Configuration", "", "enable_explicit_content_detection")
    )
    if "file" in frappe.request.files:
        file = frappe.request.files["file"]
        content = file.stream.read()
        filename = file.filename
        filetype = mimetypes.guess_type(filename)[0]
        if (
            filetype in IMAGE_TYPES
            and should_check_explicit
            and is_content_explicit(content)
        ):
            return False
        else:
            ret = frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": filename,
                    "is_private": False,
                    "content": content,
                }
            )
            ret.save(ignore_permissions=False)
            return ret
    else:
        frappe.throw("No file detected.")


def index_document(doc=None, event_name=None):
    search_modules = {
        "Problem": problem_search,
        "Solution": solution_search,
        "User Profile": user_search,
        "Organisation": organisation_search,
    }
    try:
        if doc.is_published:
            search_modules[doc.doctype].update_index_for_id(doc.name)
        else:
            search_modules[doc.doctype].remove_document_from_index(doc.name)
    except Exception as e:
        print(str(e))


@frappe.whitelist(allow_guest=False)
def get_suggested_titles(text, scope=None):
    if type(scope) == type("hello"):
        scope = json.loads(scope)
    return [
        r["title"]
        for r in problem_search.search_title(text, scope=scope)
        + solution_search.search_title(text, scope=scope)
    ]


@frappe.whitelist(allow_guest=True)
def enqueue_log_route_visit(
    route, user_agent=None, parent_doctype=None, parent_name=None
):
    ip_address = frappe.request.headers.get('X-Forwarded-For')
    enqueue(
        log_route_visit,
        timeout=1200,
        route=route,
        user_agent=user_agent,
        parent_doctype=parent_doctype,
        parent_name=parent_name,
        ip_address=ip_address
    )


@frappe.whitelist(allow_guest=True)
def log_route_visit(route, user_agent=None, parent_doctype=None, parent_name=None, ip_address=None):
    if frappe.db.exists("User Profile", frappe.session.user):
        organisation = frappe.get_value("User Profile", frappe.session.user, "org")
    else:
        organisation = None
    ua_string = user_agent
    user_agent = ua_parse(ua_string)
    doc = frappe.get_doc(
        {
            "doctype": "OIP Route Log",
            "route": route,
            "user": frappe.session.user,
            "organisation": organisation,
            "parent_doctype": parent_doctype,
            "parent_name": parent_name,
            "user_agent": ua_string,
            "browser": user_agent.browser.family,
            "os": user_agent.os.family,
            "device": user_agent.device.family,
        }
    )
    if ip_address:
        geo = ip_location_lookup.get_location(ip_address)
        doc.ip_address = ip_address
        doc.country_code = geo.country_short
        doc.country = geo.country_long
        doc.region = geo.region
        doc.city = geo.city
        doc.latitude = geo.latitude
        doc.longitude = geo.longitude
        doc.zipcode = geo.zipcode
        doc.timezone = geo.timezone
    doc.save()
    frappe.db.commit()


def enqueue_aggregate_analytics(doc, event_name):
    enqueue(aggregate_analytics, timeout=1200, doc=doc, event_name=event_name)


def aggregate_analytics(doc, event_name):
    frappe.set_user("Administrator")
    existing = frappe.get_list(
        "OIP Route Aggregate",
        {"parent_doctype": doc.parent_doctype, "parent_name": doc.parent_name},
    )
    if len(existing) > 0:
        agg = frappe.get_doc("OIP Route Aggregate", existing[0])
    else:
        agg = frappe.get_doc(
            {
                "doctype": "OIP Route Aggregate",
                "route": doc.route,
                "parent_doctype": doc.parent_doctype,
                "parent_name": doc.parent_name,
                "owner": frappe.db.get_value(
                    doc.parent_doctype, doc.parent_name, "owner"
                ),
            }
        )
    query = """select count(name), count(distinct ip_address), count(distinct organisation) from `tabOIP Route Log` where parent_doctype='{}' and parent_name='{}';""".format(
        doc.parent_doctype, doc.parent_name
    )
    agg.total_visits, agg.unique_visitors, agg.unique_organisations = frappe.db.sql(
        query
    )[0]
    loc_query = """select city, region, country, country_code, count(*) as num from `tabOIP Route Log` where parent_doctype='{}' and parent_name='{}' group by city;""".format(doc.parent_doctype, doc.parent_name)
    results = frappe.db.sql(loc_query)
    agg.location_route_aggregates = []
    for r in results:
        if r[2] and r[2] != '-':
            row = agg.append('location_route_aggregates', {})
            row.city, row.region, row.country, row.country_code, row.count = r
    agg.save(ignore_permissions=True)
    frappe.db.commit()


def invite_user(email, first_name=None, last_name=None, roles=[]):
    if not frappe.db.exists('User', email):
        user = frappe.get_doc({
            "doctype":"User",
            "email": email,
            "first_name": first_name or email,
            "last_name": last_name,
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": True
        })
        user.flags.ignore_permissions = True
        user.insert()
        frappe.db.commit()
        # set if roles is empty add default signup role as per Portal Settings
        default_role = frappe.db.get_value("Portal Settings", None, "default_role")
        if default_role and len(roles) == 0:
            roles.append(default_role)
        for role in roles:
            user.add_roles(role)
        return True
    return False


def add_user_to_org(email, org_id):
    pass