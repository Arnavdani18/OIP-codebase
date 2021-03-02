# -*- coding: utf-8 -*-
import frappe
from contentready_oip.utils import try_method

def after_install():
    try_method(seed_white_label_domain)
    try_method(seed_user_profiles)

def insert_documents(doctype, rows):
    for row in rows:
        doc = frappe.get_doc({
            "doctype": doctype,
        })
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
            'user': 'Administrator',
        },
    ]
    insert_documents(doctype, rows)
