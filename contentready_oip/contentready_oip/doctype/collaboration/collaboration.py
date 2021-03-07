# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from contentready_oip import api

class Collaboration(Document):
	def before_save(self):
		self.recipient = frappe.db.get_value(self.parent_doctype, self.parent_name, 'owner')
		if frappe.session.user not in [self.owner, self.recipient] or not api.has_admin_role():
			frappe.throw('Insufficient privileges to modify this document.')
		personas_list = [p.persona.title() for p in self.personas]
		self.personas_list = ', '.join(personas_list)
		self.maybe_notify_owner()
	
	def maybe_notify_owner(self):
		old = self.get_doc_before_save()
		if old.status == 'New' and self.status == 'Accept':
			# Recipient has accepted
			# For now, send an email connecting the two parties
			recipients = ['tej@contentready.co' if r == 'Administrator' else r for r in [self.owner, self.recipient]]
			content_title, content_route = frappe.db.get_value(self.parent_doctype, self.parent_name, ['title', 'route'])
			context = {
				'sender_full_name': frappe.db.get_value('User Profile', self.owner, 'full_name'),
				'recipient_full_name': frappe.db.get_value('User Profile', self.recipient, 'full_name'),
				'domain': api.get_url(),
				'content_doctype': self.parent_doctype,
				'content_title': content_title,
				'content_route': content_route,
			}
			template = 'templates/emails/collaboration_email.html'
			html = frappe.render_template(template, context)
			subject = 'OIP - Collaboration on {}'.format(content_title)
			frappe.sendmail(recipients, subject=subject, message=html, delayed=False)
	
	def after_insert(self):
		self.create_insert_notifications()
	
	def create_insert_notifications(self):
		source_full_name = frappe.db.get_value('User Profile', self.owner, 'full_name')
		content_title, content_route = frappe.db.get_value(self.parent_doctype, self.parent_name, ['title', 'route'])
		notification = frappe.get_doc({
            'doctype': 'OIP Notification',
            'source_user': self.owner,
            'target_user': self.recipient,
            'parent_doctype': self.parent_doctype,
            'parent_name': self.parent_name,
            'child_doctype': self.doctype,
            'child_name': self.name,
            'text': '{} wants to collaborate on your {}: {}'.format(source_full_name, self.parent_doctype.lower(), content_title),
			'route': content_route + '#' + self.doctype.lower() + 's',
        })
		notification.save()


