# -*- coding: utf-8 -*-
# Copyright (c) 2022, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

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
                    title = soup.find("meta", property="og:title")
                    description = soup.find("meta", property="og:description")
                    if description:
                        description = description.get('content', None)
                        self.description = description
                    else:
                        paragraph = soup.find("p")
                        if paragraph and paragraph.text:
                            self.description = paragraph.text[:500]
                    image = soup.find("meta", property="og:image")
                    # print(image)
                    if image and not self.image:
                        if len(image):
                            image = image.get('content', None)
                            if image.startswith('http'):
                                self.image = image
                            elif image.startswith('/'):
                                self.image = urljoin(self.attachment, image)


    def before_insert(self):
        self.get_description()
