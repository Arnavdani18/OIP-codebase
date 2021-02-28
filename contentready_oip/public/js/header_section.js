frappe.ready(async () => {
    openEnrichmentForm = (doctype, name) => {
        if (frappe.session.user === 'Guest') {
            frappe.throw('Please login to participate.');
        }
        frappe.call({
            method: 'contentready_oip.api.can_user_contribute',
            args: {child_doctype: 'Enrichment', parent_doctype: doctype, parent_name: name},
            callback: (r) => {
                const has_contributed = r.message[0];
                const is_owner = r.message[1];
                if (!has_contributed && !is_owner) {
                    window.location.href = `/add-enrichment?new=1&problem=${name}`;
                } else if (has_contributed) {
                    frappe.throw(`You have already enriched this ${doctype}`);
                }
                else if (is_owner){
                    frappe.throw(`You cannot enrich your own ${doctype}`);
                }
            }
        });
    }
    openValidationForm = (doctype, name) => {
        if (frappe.session.user === 'Guest') {
            frappe.throw('Please login to participate.');
        }
        frappe.call({
            method: 'contentready_oip.api.can_user_contribute',
            args: {child_doctype: 'Validation', parent_doctype: doctype, parent_name: name},
            callback: (r) => {
                const has_contributed = r.message[0];
                const is_owner = r.message[1];
                if (!has_contributed && !is_owner) {
                    $(`#validation-modal-${name}`).modal('toggle');
                } else if (has_contributed) {
                    frappe.throw(`You have already validated this ${doctype}`);
                }
                else if (is_owner){
                    frappe.throw(`You cannot validate your own ${doctype}`);
                }
            }
        });
    }
    openCollaborationForm = (doctype, name) => {
        if (frappe.session.user === 'Guest') {
            frappe.throw('Please login to participate.');
        }
        frappe.call({
            method: 'contentready_oip.api.can_user_contribute',
            args: {child_doctype: 'Collaboration', parent_doctype: doctype, parent_name: name},
            callback: (r) => {
                const has_contributed = r.message[0];
                const is_owner = r.message[1];
                if (!has_contributed && !is_owner) {
                    $(`#collaboration-modal-${name}`).modal('toggle');
                } else if (has_contributed) {
                    frappe.throw(`You have already collaborated on this ${doctype}`);
                }
                else if (is_owner){
                    frappe.throw(`You cannot collaborate on your own ${doctype}`);
                }
            }
        });
    }
    openSolutionForm = (name) => {
        if (frappe.session.user === 'Guest') {
            frappe.throw('Please login to participate.');
        } else {
            window.location.href = `/add-solution?new=1&problem=${name}`;
        }
    }
})