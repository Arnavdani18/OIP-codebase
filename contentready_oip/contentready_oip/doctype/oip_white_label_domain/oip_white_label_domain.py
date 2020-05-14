# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from contentready_oip import api

class OIPWhiteLabelDomain(Document):
	def on_update(self):
		if '/' in self.domain:
			frappe.throw('Please enter only the domain, e.g. sub.domain.org or domain.org')
		