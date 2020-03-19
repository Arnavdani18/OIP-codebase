# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Discussion(Document):
    def on_update(self):
        # read all child tables and add notifications
        self.create_notifications()
    
    def create_notifications(self):
        # notify owner when someone enriches
        template = {
            'doctype': 'OIP Notification',
            'target_user': self.user,
            'parent_doctype': self.doctype,
            'parent_name': self.name,
        }
        verbs = {
            'Discussion Table': 'replied to',
            'Like Table': 'liked',
        }
        for c in self.replies + self.likes:
            try:
                # do not create notifications if the owner themselves contributed
                if c.user == self.user:
                    continue
                n_template = template.copy()
                n_template['parent_field'] = c.parentfield
                n_template['child_name'] = c.name
                n_template['child_doctype'] = c.doctype
                n_template['source_user'] = c.user
                n_name = '{}-{}-{}'.format(n_template['target_user'], n_template['source_user'], n_template['child_name'])
                if frappe.db.exists('OIP Notification', n_name):
                    continue
                user = frappe.get_doc('User', c.user)
                parent_doc = frappe.get_doc(self.parent_doctype, self.parent_name)
                n_template['text'] = '{} {} your comment on the {}: {}'.format(user.full_name, verbs[c.doctype], self.parent_doctype.lower(), parent_doc.title)
                n_template['route'] = parent_doc.route + '#discussion'
                notification = frappe.get_doc(n_template)
                notification.save()
            except:
                pass
        frappe.db.commit()
