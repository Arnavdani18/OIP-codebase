# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.html_utils import clean_html


class Enrichment(Document):
    def before_save(self):
        if self.short_description:
            self.short_description = clean_html(self.description)[:500]
            if len(self.description) > 1000:
                self.short_description += '...'
     
    def on_update(self):
        # read all child tables and add notifications
        self.create_notifications()
    
    def create_notifications(self):
        # notify owner when someone enriches
        template = {
            'doctype': 'OIP Notification',
            'target_user': self.owner,
            'parent_doctype': self.doctype,
            'parent_name': self.name,
        }
        verbs = {
            'Like': 'liked',
        }
        doctypes = ['Like']
        for doctype in doctypes:
            try:
                contrib_list = frappe.get_list(doctype, fields=['name', 'owner'], filters={'parent_doctype': self.doctype, 'parent_name': self.name})
                for c in contrib_list:
                    # do not create notifications if the owner themselves contributed
                    if c['owner'] == self.owner:
                        continue
                    n_template = template.copy()
                    n_template['child_name'] = c['name']
                    n_template['child_doctype'] = doctype
                    n_template['source_user'] = c['owner']
                    n_name = '{}-{}-{}'.format(n_template['target_user'], n_template['source_user'], n_template['child_name'])
                    if frappe.db.exists('OIP Notification', n_name):
                        continue
                    user = frappe.get_doc('User', c['owner'])
                    n_template['text'] = '{} {} your {}: {}'.format(user.full_name, verbs[doctype], self.doctype.lower(), self.title)
                    n_template['route'] = self.route + '#' + doctype.lower() + 's'
                    notification = frappe.get_doc(n_template)
                    notification.save()
            except:
                pass
        frappe.db.commit()
