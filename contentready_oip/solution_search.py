# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from whoosh.fields import TEXT, ID, Schema, STORED, DATETIME, NUMERIC
from whoosh.qparser import MultifieldParser, FieldsPlugin, WildcardPlugin
from frappe.search.full_text_search import FullTextSearch
import json

INDEX_NAME = "solution"

search_fields = [
	"title",
	"description",
	"city",
	"state",
	"country",
]

class SolutionSearch(FullTextSearch):
	""" Wrapper for SolutionSearch """

	def get_schema(self):
		return Schema(
			name=ID(stored=True), 
			title=TEXT(stored=True, sortable=True, field_boost=5.0),
			description=TEXT(stored=True, field_boost=3.0),
			city=TEXT(stored=True, field_boost=2.0),
			state=TEXT(stored=True, field_boost=2.0),
			country=TEXT(stored=True, field_boost=2.0),
			# latitude=NUMERIC(numtype=float, stored=True, sortable=True, field_boost=2.0),
			# longitude=NUMERIC(numtype=float, stored=True, sortable=True, field_boost=2.0),
			sectors=TEXT(stored=True, field_boost=1.0),
			sdg=TEXT(stored=True, field_boost=1.0),
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
		solution = frappe.get_list('Solution', filters={'is_published': True})

		documents = [self.get_document_to_index(solution['name']) for solution in solution]
		return documents

	def get_document_to_index(self, name):
		"""Grab all data related to a solution and index the JSON

		Args:
			name (str): docname of the solution to index

		Returns:
			document (_dict): A dictionary with business_name, name and solution
		"""
		frappe.local.no_cache = True
		try:
			solution = frappe.get_doc('Solution', name)
			# Should be unnecessary but in case we call this in published flows...
			if not solution.is_published:
				return False
			sectors = [c.sector for c in solution.sectors]
			sdg = [c.sustainable_development_goal for c in solution.sustainable_development_goal]
			sectors = json.dumps(sectors)
			sdg = json.dumps(sdg)
			return frappe._dict(
				name=name, 
				title=solution.title,
				description=solution.description,
				city=solution.city,
				state=solution.state,
				country=solution.country,
				# latitude=solution.latitude,
				# longitude=solution.longitude,
				sectors=sectors,
				sdg=sdg,
				modified=solution.modified,
				doctype=solution.doctype,
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
	
	def search(self, text, scope=None, limit=20):
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
		if text[-1] != '*':
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

			filter_scoped = None
			if scope:
				filter_scoped = Prefix(self.name, scope)
			results = searcher.search(query, limit=limit, filter=filter_scoped)
			for r in results:
				print(r)
				out.append(self.parse_result(r))
		return out


def update_index_for_id(name):
	print('Updating search index for', name)
	ws = SolutionSearch(INDEX_NAME)
	return ws.update_index_by_name(name)

def remove_document_from_index(name):
	ws = SolutionSearch(INDEX_NAME)
	return ws.remove_document_from_index(name)

def build_index_for_all_ids():
	ws = SolutionSearch(INDEX_NAME)
	return ws.build()

def search_index(text, limit=20):
	ws = SolutionSearch(INDEX_NAME)
	return ws.search(text=text, limit=limit)