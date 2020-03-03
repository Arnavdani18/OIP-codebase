# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class UserProfile(Document):
	def before_insert(self):
		try:
			org = frappe.get_doc('Organisation', {'org_title': self.org_title})
		except:
			org = frappe.get_doc({
				'doctype': 'Organisation',
				'title': self.org_title
			})
			org.insert()
		self.org = org.name
