# -*- coding: utf-8 -*-
# Copyright (c) 2022, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from bs4 import BeautifulSoup
import requests

# This is a *very* simplistic way to filter but we don't have a better solution right now because URLs can be quite tricky to figure out
blacklist = ['.jpg', '.png', '.mp4', '.mp3', '.avi', '.mpg', '.mov', '.webp']

class OIPResource(Document):
    def get_description(self):
        is_blacklisted = any(el in self.attachment for el in blacklist)
        if self.attachment and self.attachment.startswith('http') and not is_blacklisted:
            response = requests.get(self.attachment)
            if response.status_code == 200:
                html = response.text
                if html:
                    soup = BeautifulSoup(html, "lxml")
                    paragraph = soup.find("p")
                    if paragraph and paragraph.text:
                        try:
                            paragraph.text.encode("utf-8")
                            self.description = paragraph.text[:500]
                        except:
                            pass

    def before_insert(self):
        self.get_description()