# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import json
from whoosh.query import Term, And, Or
from whoosh.fields import TEXT, ID, Schema, STORED, DATETIME, NUMERIC
from whoosh.qparser import MultifieldParser, FieldsPlugin, WildcardPlugin
from frappe.search.full_text_search import FullTextSearch
from contentready_oip import api

INDEX_NAME = "service_provider"

DOCTYPE = 'Service Provider'

search_fields = [
	"full_name",
	"org_title",
	"city",
	"state",
	"country",
]

class ServiceProviderSearch(FullTextSearch):
	""" Wrapper for ServiceProviderSearch """

	def get_schema(self):
		return Schema(
			name=ID(stored=True), 
			full_name=TEXT(stored=True, sortable=True, field_boost=5.0),
			org_title=TEXT(stored=True, sortable=True, field_boost=5.0),
			city=TEXT(stored=True, field_boost=2.0),
			state=TEXT(stored=True, field_boost=2.0),
			country=TEXT(stored=True, field_boost=2.0),
			# latitude=NUMERIC(numtype=float, stored=True, sortable=True, field_boost=2.0),
			# longitude=NUMERIC(numtype=float, stored=True, sortable=True, field_boost=2.0),
			service_category=TEXT(stored=True, field_boost=1.0),
			modified=DATETIME(stored=True, sortable=True),
			doctype=STORED(),
		)

	def get_name(self):
		return "name"

	def get_items_to_index(self):
		"""Get all names to be indexed and index the JSON for each.
		Returns:
			self (object): FullTextSearch Instance
		"""
		service_providers = frappe.get_list(DOCTYPE, filters={'is_published': True})

		documents = [self.get_document_to_index(service_provider['name']) for service_provider in service_providers]
		return documents

	def get_document_to_index(self, name):
		"""Grab all data related to a service_provider and index the JSON

		Args:
			name (str): docname of the service_provider to index

		Returns:
			document (_dict): A dictionary with business_name, name and service_provider
		"""
		frappe.local.no_cache = True
		try:
			service_provider = frappe.get_doc(DOCTYPE, name)
			# Should be unnecessary but in case we call this in published flows...
			if not service_provider.is_published:
				return False
			return frappe._dict(
				name=name, 
				full_name=service_provider.full_name,
				org_title=service_provider.org_title,
				city=service_provider.city,
				state=service_provider.state,
				country=service_provider.country,
				# latitude=service_provider.latitude,
				# longitude=service_provider.longitude,
				service_category=service_provider.service_category,
				modified=service_provider.modified,
				doctype=service_provider.doctype,
			)
		except Exception as e:
			print(str(e))
			pass

	def parse_result(self, result):
		return frappe._dict(
			name=result["name"],
			full_name=result["full_name"],
			org_title=result["org_title"],
			city=result.get('city'),
			state=result.get("state"),
			country=result.get("country"),
		)
	
	def search(self, text, scope=None, limit=20):
		"""Search from the current index

		Args:
			text (str): String to search for
			scope (dict, optional): Scope to limit the search. Defaults to None.
			limit (int, optional): Limit number of search results. Defaults to 20.

		Returns:
			[List(_dict)]: Search results
		"""
		ix = self.get_index()

		results = None
		out = []

		# Add wildcard if not already present to force search for partial text
		if text and text[-1] != '*':
			text = text + '*'

		# the parser does not seem to like the '@' symbol
		# for now we replace with a space but we need a better solution
		text = text.replace('@', ' ')

		with ix.searcher() as searcher:
			parser = MultifieldParser(search_fields, ix.schema)
			parser.remove_plugin_class(FieldsPlugin)
			# We are going to actively use wildcards unless there are performance issues.
			# parser.remove_plugin_class(WildcardPlugin)
			query = parser.parse(text)

			# if scope is provided, then we construct a query from the filters
			filter_scoped = None
			if type(scope) == dict:
				service_category = scope.get('service_category')
				if service_category:
					filter_scoped = Term('service_category', service_category)
			results = searcher.search(query, limit=limit, filter=filter_scoped)
			for r in results:
				out.append({'name': r['name']})
		return out


def update_index_for_id(name):
	ws = ServiceProviderSearch(INDEX_NAME)
	return ws.update_index_by_name(name)

def remove_document_from_index(name):
	ws = ServiceProviderSearch(INDEX_NAME)
	return ws.remove_document_from_index(name)

def build_index_for_all_ids():
	ws = ServiceProviderSearch(INDEX_NAME)
	return ws.build()

def search_index(text, scope=None, limit=20):
	ws = ServiceProviderSearch(INDEX_NAME)
	return ws.search(text=text, scope=scope, limit=limit)