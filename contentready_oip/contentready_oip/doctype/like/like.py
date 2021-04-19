# -*- coding: utf-8 -*-
# Copyright (c) 2021, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Like(Document):
	def after_insert(self):
		self.maybe_create_insert_notifications()
	
	def maybe_create_insert_notifications(self):
		try:
			source_full_name = frappe.db.get_value('User Profile', self.owner, 'full_name')
			content_title, content_route = frappe.db.get_value(self.parent_doctype, self.parent_name, ['title', 'route'])
			recipient = frappe.db.get_value(self.parent_doctype, self.parent_name, 'owner')
			notification = frappe.get_doc({
				'doctype': 'OIP Notification',
				'source_user': self.owner,
				'target_user': recipient,
				'parent_doctype': self.parent_doctype,
				'parent_name': self.parent_name,
				'child_doctype': self.doctype,
				'child_name': self.name,
				'text': '{} liked your {}: {}'.format(source_full_name, self.parent_doctype.lower(), content_title),
				'route': content_route,
			})
			notification.save()
		except:
			pass
