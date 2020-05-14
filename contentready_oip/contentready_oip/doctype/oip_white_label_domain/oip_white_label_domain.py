# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from contentready_oip import api

class OIPWhiteLabelDomain(Document):
	def after_insert(self):
		api.add_custom_domain(self.url)
