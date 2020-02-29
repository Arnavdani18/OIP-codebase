# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from frappe.utils.html_utils import clean_html


class Enrichment(Document):
	def before_save(self):
		self.short_description = clean_html(self.description)[:500]
		if len(self.description) > 1000:
			self.short_description += '...'
