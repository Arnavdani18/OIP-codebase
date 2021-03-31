# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Discussion(Document):
	def after_insert(self):
		self.maybe_create_insert_notifications()
	
	def maybe_create_insert_notifications(self):
		try:
			# For replies, we still want to reference the original content title and route
			if self.parent_doctype == 'Discussion':
				parent_doctype, parent_name = frappe.db.get_value(self.parent_doctype, self.parent_name, ['parent_doctype', 'parent_name'])
				action = 'replied to your comment on'
			else:
				parent_doctype, parent_name = self.parent_doctype, self.parent_name
				action = 'commented on your {}'.format(parent_doctype.lower())
			content_title, content_route = frappe.db.get_value(parent_doctype, parent_name, ['title', 'route'])
			source_full_name = frappe.db.get_value('User Profile', self.owner, 'full_name')
			recipient = frappe.db.get_value(self.parent_doctype, self.parent_name, 'owner')
			notification = frappe.get_doc({
				'doctype': 'OIP Notification',
				'source_user': self.owner,
				'target_user': recipient,
				'parent_doctype': self.parent_doctype,
				'parent_name': self.parent_name,
				'child_doctype': self.doctype,
				'child_name': self.name,
				'text': '{} {} : {}'.format(source_full_name, action, content_title),
				'route': content_route + '#' + self.doctype.lower() + 's',
			})
			notification.save()
		except:
			pass
	
