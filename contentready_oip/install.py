# -*- coding: utf-8 -*-
import frappe
from contentready_oip.utils import try_method


def after_install():
    try_method(seed_white_label_domain)
    try_method(seed_user_profiles)
    try_method(seed_sectors)
    try_method(seed_personas)
    try_method(seed_sdgs)


def insert_documents(doctype, rows):
    for row in rows:
        doc = frappe.get_doc(
            {
                "doctype": doctype,
            }
        )
        doc.update(row)
        doc.insert()


def seed_white_label_domain():
    doctype = "OIP White Label Domain"
    rows = [
        {
            "title": "Localhost",
            "domain": "localhost:8000",
            "url": "http://localhost:8000",
        },
    ]
    insert_documents(doctype, rows)


def seed_user_profiles():
    doctype = "User Profile"
    rows = [
        {
            "user": "Administrator",
        },
    ]
    insert_documents(doctype, rows)


def seed_sectors():
    doctype = "Sector"
    rows = [
        {"title": "Animal Husbandry "},
        {"title": "Law & Order"},
        {"title": "Waste Management"},
        {"title": "Land Administration"},
        {"title": "Financial Services"},
        {"title": "Digital Governance"},
        {"title": "Assistive Technologies"},
        {"title": "Healthcare"},
        {"title": "Social Justice "},
        {"title": "Citizen Services "},
        {"title": "Agriculture "},
        {"title": "Agri-Tech"},
        {"title": "Skilling & Entrepreneurship"},
        {"title": "Food / Nutrition"},
        {"title": "School Safety"},
        {"title": "Energy"},
        {"title": "Infrastructure"},
        {"title": "Mobility"},
        {"title": "Housing"},
        {"title": "Environment"},
        {"title": "Education"},
        {"title": "Gender"},
        {"title": "Arts, crafts and textiles"},
        {"title": "Others"},
        {"title": "Water"},
    ]
    insert_documents(doctype, rows)


def seed_personas():
    doctype = "Persona"
    rows = [
        {"title": "Beneficiary"},
        {"title": "Government"},
        {"title": "Funder"},
        {"title": "Incubator"},
        {"title": "Expert"},
        {"title": "Entrepreneur"},
        {"title": "Innovator"},
        {"title": "NGO"},
        {"title": "Service Provider"},
    ]
    insert_documents(doctype, rows)


def seed_sdgs():
    doctype = "Sustainable Development Goal"
    rows = [
        {"title": "No Poverty", "number": 1},
        {"title": "Zero Hunger", "number": 2},
        {"title": "Good Health and Well-being", "number": 3},
        {"title": "Quality Education", "number": 4},
        {"title": "Gender Equality", "number": 5},
        {"title": "Clean Water and Sanitation", "number": 6},
        {"title": "Affordable and Clean Energy", "number": 7},
        {"title": "Decent Work and Economic Growth", "number": 8},
        {"title": "Industry, Innovation and Infrastructure", "number": 9},
        {"title": "Reduced Inequality", "number": 10},
        {"title": "Sustainable Cities and Communities", "number": 11},
        {"title": "Responsible Consumption and Production", "number": 12},
        {"title": "Climate Action", "number": 13},
        {"title": "Life Below Water", "number": 14},
        {"title": "Life on Land", "number": 15},
        {"title": "Peace and Justice Strong Institutions", "number": 16},
        {"title": "Partnerships to achieve the Goal", "number": 17},
    ]
    insert_documents(doctype, rows)
