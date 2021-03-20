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
        {"title": "No Poverty"},
        {"title": "Zero Hunger"},
        {"title": "Good Health and Well-being"},
        {"title": "Quality Education"},
        {"title": "Gender Equality"},
        {"title": "Clean Water and Sanitation"},
        {"title": "Affordable and Clean Energy"},
        {"title": "Decent Work and Economic Growth"},
        {"title": "Industry, Innovation and Infrastructure"},
        {"title": "Reduced Inequality"},
        {"title": "Sustainable Cities and Communities"},
        {"title": "Responsible Consumption and Production"},
        {"title": "Climate Action"},
        {"title": "Life Below Water"},
        {"title": "Life on Land"},
        {"title": "Peace and Justice Strong Institutions"},
        {"title": "Partnerships to achieve the Goal"},
    ]
    insert_documents(doctype, rows)
