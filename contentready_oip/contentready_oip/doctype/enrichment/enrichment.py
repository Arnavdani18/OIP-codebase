# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.html_utils import clean_html


class Enrichment(Document):
	def before_save(self):
		try:
			self.short_description = clean_html(self.description)[:500]
			if len(self.description) > 1000:
				self.short_description += '...'
		except:
			pass
		if not self.parent_doctype:
			self.parent_doctype = 'Problem'
			self.parent_name = self.problem
		old = self.get_doc_before_save()
		if old and not old.is_published and self.is_published:
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
				'text': '{} enriched your {}: {}'.format(source_full_name, self.parent_doctype.lower(), content_title),
				'route': content_route + '#' + self.doctype.lower() + 's',
			})
			notification.save()
		except:
			pass
