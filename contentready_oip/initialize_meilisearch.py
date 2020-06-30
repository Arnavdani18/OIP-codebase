""""
Initialize meilisearch and create indexes
"""
import json
import meilisearch
import frappe

INDEX_TO_ADD = ['Problem', 'Solution', 'User']
CLIENT = meilisearch.Client('http://127.0.0.1:7700', 'test123')

def refactor_sectors_list(problem_dict):
    """
    Refactor sector to list of strings.
    """
    try:
        _sectors = problem_dict['sectors']
        problem_dict['meili_sectors'] = []

        for sctr in _sectors:
            problem_dict['meili_sectors'].append(sctr["sector"])
    except Exception as _e:
        print(str(_e))

    return problem_dict


def get_detailed_doctype(doc_name):
    """
    Get doctype details from frappe and arrange as per meilisearch requirement.
    """
    detailed_doc_list = []
    doc_list = frappe.get_list(doc_name)

    # remove guest from user list
    if doc_name.lower().startswith('user'):
        guest_index = next((item for item in doc_list if item['name'] == 'Guest'), False)
        if guest_index:
            doc_list.remove(guest_index)

    for doc in doc_list:
        detail_doc = frappe.get_doc(doc_name.capitalize(), doc)
        try:
            doc_dict = detail_doc.as_dict()
            if doc_name.lower() == "problem" or "solution":
                doc_dict = refactor_sectors_list(doc_dict)
            detailed_doc_list.append(doc_dict)
        except Exception as _e:
            print(str(_e))

    return json.dumps(detailed_doc_list, indent=4, sort_keys=True, default=str)


def add_index_if_not_exist(index_name):
    """
    Create index if doesn't exist. 
    Set primaryKey as 'name'
    """
    index = CLIENT.get_indexes()
    does_index_exist = next(
        (item for item in index if item['name'] == index_name.lower()), False)

    if not does_index_exist:
        index = CLIENT.create_index(
            uid=index_name.lower(), options={
                'primaryKey': 'name'
            })
        add_documents_to_index(index_name)


def add_documents_to_index(idx_name):
    """
    Add list of dictionary to the index created
    """
    document = get_detailed_doctype(idx_name.capitalize())
    json_doc = json.loads(document)
    CLIENT.get_index(idx_name.lower()).add_documents(json_doc)


def clear_all_data(idx_name):
    """
    Remove the provided index from meilisearch
    """
    idx_name = idx_name.lower()
    CLIENT.get_index(idx_name).delete_all_documents()
    CLIENT.get_index(idx_name).delete()

def reset_meilisearch(doc_name):
    """
    Delete and re-Initialize the index and documents
    """
    clear_all_data(doc_name)
    add_index_if_not_exist(doc_name)

def main_fn():
    """
    Entry point for the file.
    """
    for doc_name in INDEX_TO_ADD:
        add_index_if_not_exist(doc_name)
