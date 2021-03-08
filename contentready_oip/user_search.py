# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from whoosh.fields import TEXT, ID, Schema, STORED, DATETIME, NUMERIC
from whoosh.qparser import MultifieldParser, FieldsPlugin, WildcardPlugin
from frappe.search.full_text_search import FullTextSearch
import json

INDEX_NAME = "user"

search_fields = [
	"full_name",
	"city",
	"state",
	"country",
]

class UserSearch(FullTextSearch):
	""" Wrapper for UserSearch """

	def get_schema(self):
		return Schema(
			id=ID(stored=True), 
			full_name=TEXT(stored=True, sortable=True, field_boost=5.0),
			city=TEXT(stored=True, field_boost=2.0),
			state=TEXT(stored=True, field_boost=2.0),
			country=TEXT(stored=True, field_boost=2.0),
			# latitude=NUMERIC(numtype=float, stored=True, sortable=True, field_boost=2.0),
			# longitude=NUMERIC(numtype=float, stored=True, sortable=True, field_boost=2.0),
			sectors=TEXT(stored=True, field_boost=1.0),
			personas=TEXT(stored=True, field_boost=1.0),
			modified=DATETIME(stored=True, sortable=True),
			doctype=STORED(),
		)

	def get_id(self):
		return "id"

	def get_items_to_index(self):
		"""Get all ids to be indexed and index the JSON for each.
		Returns:
			self (object): FullTextSearch Instance
		"""
		user = frappe.get_list('User Profile')

		documents = [self.get_document_to_index(user['name']) for user in user]
		return documents

	def get_document_to_index(self, id):
		"""Grab all data related to a user and index the JSON

		Args:
			id (str): docname of the user to index

		Returns:
			document (_dict): A dictionary with business_name, id and user
		"""
		frappe.local.no_cache = True
		try:
			user = frappe.get_doc('User Profile', id) 
			sectors = [c.sector for c in user.sectors]
			personas = [c.persona for c in user.personas]
			sectors = json.dumps(sectors)
			personas = json.dumps(personas)
			return frappe._dict(
				id=id, 
				full_name=user.full_name,
				city=user.city,
				state=user.state,
				country=user.country,
				# latitude=user.latitude,
				# longitude=user.longitude,
				sectors=sectors,
				personas=personas,
				modified=user.modified,
				doctype=user.doctype,
			)
		except Exception as e:
			print(str(e))
			pass

	def parse_result(self, result):
		return frappe._dict(
			id=result["id"],
			full_name=result["full_name"],
			city=result["city"],
			state=result["state"],
			country=result["country"],
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
				filter_scoped = Prefix(self.id, scope)
			results = searcher.search(query, limit=limit, filter=filter_scoped)
			for r in results:
				out.append(self.parse_result(r))
				# out.append(r)
		return out


def update_index_for_id(id):
	print('Updating search index for', id)
	ws = UserSearch(INDEX_NAME)
	return ws.update_index_by_name(id)

def remove_document_from_index(id):
	ws = UserSearch(INDEX_NAME)
	return ws.remove_document_from_index(id)

def build_index_for_all_ids():
	ws = UserSearch(INDEX_NAME)
	return ws.build()

def search_index(text, limit=20):
	ws = UserSearch(INDEX_NAME)
	return ws.search(text=text, limit=limit)