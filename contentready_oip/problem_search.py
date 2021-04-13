# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from whoosh.analysis import NgramWordAnalyzer
from whoosh.query import Term, And, Or
from whoosh.fields import TEXT, ID, Schema, STORED, DATETIME, NUMERIC
from whoosh.qparser import MultifieldParser, FieldsPlugin, WildcardPlugin
from frappe.search.full_text_search import FullTextSearch
import json
from contentready_oip import api

INDEX_NAME = "problem"

search_fields = [
	"title",
	"description",
	"city",
	"state",
	"country",
	"latitude",
	"longitude",
]

class ProblemSearch(FullTextSearch):
	""" Wrapper for ProblemSearch """

	def get_schema(self):
		analyzer = NgramWordAnalyzer(3)
		return Schema(
			name=ID(stored=True), 
			title=TEXT(stored=True, analyzer=analyzer, phrase=False, sortable=True, field_boost=5.0),
			description=TEXT(stored=True, field_boost=3.0),
			city=TEXT(stored=True, field_boost=2.0),
			state=TEXT(stored=True, field_boost=2.0),
			country=TEXT(stored=True, field_boost=2.0),
			latitude=NUMERIC(numtype=float, stored=True),
			longitude=NUMERIC(numtype=float, stored=True),
			sectors=TEXT(stored=True, field_boost=1.0),
			sdg=TEXT(stored=True, field_boost=1.0),
			beneficiaries=TEXT(stored=True, field_boost=1.0),
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
		problem = frappe.get_list('Problem', filters={'is_published': True})

		documents = [self.get_document_to_index(problem['name']) for problem in problem]
		return documents

	def get_document_to_index(self, name):
		"""Grab all data related to a problem and index the JSON

		Args:
			name (str): docname of the problem to index

		Returns:
			document (_dict): A dictionary with business_name, name and problem
		"""
		frappe.local.no_cache = True
		try:
			problem = frappe.get_doc('Problem', name)
			# Should be unnecessary but in case we call this in published flows...
			if not problem.is_published or not problem.route:
				return False
			sectors = [c.sector for c in problem.sectors]
			sdg = [c.sdg for c in problem.sdgs]
			beneficiaries = [c.beneficiary for c in problem.beneficiaries]
			return frappe._dict(
				name=name, 
				title=problem.title,
				description=problem.description,
				city=problem.city,
				state=problem.state,
				country=problem.country,
				latitude=problem.latitude,
				longitude=problem.longitude,
				sectors=json.dumps(sectors),
				sdg=json.dumps(sdg),
				beneficiaries=json.dumps(beneficiaries),
				modified=problem.modified,
				doctype=problem.doctype,
			)
		except Exception as e:
			print(str(e))
			pass

	def parse_result(self, result):
		title_highlights = result.highlights("title")
		description_highlights = result.highlights("description")

		return frappe._dict(
			name=result["name"],
			title=result["title"],
			description=result["description"],
			city=result["city"],
			state=result["state"],
			country=result["country"],
			title_highlights=title_highlights,
			description_highlights=description_highlights,
		)

	def search(self, text, scope=None, limit=20, title_only=False):
		"""Search from the current index

		Args:
			text (str): String to search for
			scope (str, optional): Scope to limit the search. Defaults to None.
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

		# title_only search is used for search-as-you-type

		if title_only:
			fields = ['title']
		else:
			fields = search_fields

		with ix.searcher() as searcher:
			parser = MultifieldParser(fields, ix.schema)
			parser.remove_plugin_class(FieldsPlugin)
			# We are going to actively use wildcards unless there are performance issues.
			# parser.remove_plugin_class(WildcardPlugin)
			query = parser.parse(text)
			# if scope is provided, then we construct a query from the filters
			filter_scoped = None
			terms = []
			sector_filters = []
			sdg_filters = []
			beneficiary_filters = []
			center = (0, 0)
			if type(scope) == dict:
				sectors = scope.get('sectors')
				if type(sectors) == list:
					for s in sectors:
						sector_filters.append(Term('sectors', s))
					if len(sector_filters):
						terms.append(Or(sector_filters))
				sdg = scope.get('sdgs')
				if type(sdg) == list:
					for s in sdg:
						sdg_filters.append(Term('sdg', s))
					if len(sdg_filters):
						terms.append(Or(sdg_filters))
				beneficiaries = scope.get('beneficiaries')
				if type(beneficiaries) == list:
					for s in beneficiaries:
						beneficiary_filters.append(Term('beneficiaries', s))
					if len(beneficiary_filters):
						terms.append(Or(beneficiary_filters))
				if type(scope.get('center')) == list:
					center = scope.get('center')
			filter_scoped = And(terms)
			results = searcher.search(query, limit=limit, filter=filter_scoped, terms=True)
			if title_only:
				out = [{'title': r['title']} for r in results]
			else:
				out = api.sort_by_distance(results, center)
		return out


def update_index_for_id(name):
	ws = ProblemSearch(INDEX_NAME)
	return ws.update_index_by_name(name)

def remove_document_from_index(name):
	ws = ProblemSearch(INDEX_NAME)
	return ws.remove_document_from_index(name)

def build_index_for_all_ids():
	ws = ProblemSearch(INDEX_NAME)
	return ws.build()

def search_index(text, scope=None, limit=20):
	ws = ProblemSearch(INDEX_NAME)
	return ws.search(text=text, scope=scope, limit=limit)

def search_title(text, scope=None, limit=10):
	ws = ProblemSearch(INDEX_NAME)
	return ws.search(text=text, scope=scope, limit=limit, title_only=True)