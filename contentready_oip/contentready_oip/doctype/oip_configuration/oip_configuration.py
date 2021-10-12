# -*- coding: utf-8 -*-
# Copyright (c) 2021, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class OIPConfiguration(Document):
	def before_save(self):
		for row in self.slideshow:
			if row.heading:
				row.heading = row.heading.strip()
			if row.description:
				row.description = row.description.strip()
