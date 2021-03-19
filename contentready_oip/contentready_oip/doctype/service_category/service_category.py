# -*- coding: utf-8 -*-
# Copyright (c) 2021, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from frappe.website.utils import cleanup_page_name

class ServiceCategory(Document):
	def autoname(self):
		self.name = cleanup_page_name(self.title).replace('-', '_')
