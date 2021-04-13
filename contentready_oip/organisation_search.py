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

INDEX_NAME = "organisation"

DOCTYPE = 'Organisation'

search_fields = [
	"title",
	"website",
	"city",
	"state",
	"country",
	"latitude",
	"longitude",
]

class OrganisationSearch(FullTextSearch):
	""" Wrapper for OrganisationSearch """

	def get_schema(self):
		return Schema(
			name=ID(stored=True), 
			title=TEXT(stored=True, sortable=True, field_boost=5.0),
			website=TEXT(stored=True, sortable=True, field_boost=5.0),
			city=TEXT(stored=True, field_boost=2.0),
			state=TEXT(stored=True, field_boost=2.0),
			country=TEXT(stored=True, field_boost=2.0),
			latitude=NUMERIC(numtype=float, stored=True),
			longitude=NUMERIC(numtype=float, stored=True),
			sectors=TEXT(stored=True, field_boost=1.0),
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
		organisations = frappe.get_list(DOCTYPE)

		documents = [self.get_document_to_index(organisation['name']) for organisation in organisations]
		return documents

	def get_document_to_index(self, name):
		"""Grab all data related to a organisation and index the JSON

		Args:
			name (str): docname of the organisation to index

		Returns:
			document (_dict): A dictionary with business_name, name and organisation
		"""
		frappe.local.no_cache = True
		try:
			organisation = frappe.get_doc(DOCTYPE, name)
			if not organisation.is_published or not organisation.route:
				return False
			sectors = [c.sector for c in organisation.sectors]
			sectors = json.dumps(sectors)
			return frappe._dict(
				name=name, 
				title=organisation.title,
				website=organisation.website,
				city=organisation.city,
				state=organisation.state,
				country=organisation.country,
				latitude=organisation.latitude,
				longitude=organisation.longitude,
				sectors=sectors,
				modified=organisation.modified,
				doctype=organisation.doctype,
			)
		except Exception as e:
			print(str(e))
			pass

	def parse_result(self, result):
		return frappe._dict(
			name=result["name"],
			title=result["title"],
			website=result["website"],
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
			terms = []
			sector_filters = []
			center = (0, 0)
			if type(scope) == dict:
				sectors = scope.get('sectors')
				if type(sectors) == list:
					for s in sectors:
						sector_filters.append(Term('sectors', s))
					if len(sector_filters):
						terms.append(Or(sector_filters))
				if type(scope.get('center')) == list:
					center = scope.get('center')
			filter_scoped = And(terms)
			results = searcher.search(query, limit=limit, filter=filter_scoped)
			out = api.sort_by_distance(results, center)
		return out


def update_index_for_id(name):
	ws = OrganisationSearch(INDEX_NAME)
	return ws.update_index_by_name(name)

def remove_document_from_index(name):
	ws = OrganisationSearch(INDEX_NAME)
	return ws.remove_document_from_index(name)

def build_index_for_all_ids():
	ws = OrganisationSearch(INDEX_NAME)
	return ws.build()

def search_index(text, scope=None, limit=20):
	ws = OrganisationSearch(INDEX_NAME)
	return ws.search(text=text, scope=scope, limit=limit)