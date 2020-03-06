frappe.ready(async () => {
    openEnrichmentForm = (doctype, name) => {
        if (frappe.session.user === 'Guest') {
            frappe.throw('Please login to participate.');
        }
        frappe.call({
            method: 'contentready_oip.api.has_user_contributed',
            args: {child_doctype: 'Enrichment Table', parent_doctype: doctype, name: name},
            callback: (r) => {
                if (r.message){
                    frappe.throw(`You have already enriched this problem.`);
                } else {
                    window.location.href = `/add-enrichment?new=1&problem=${name}`;
                }
            }
        });
    }
    openValidationForm = (doctype, name) => {
        if (frappe.session.user === 'Guest') {
            frappe.throw('Please login to participate.');
        }
        frappe.call({
            method: 'contentready_oip.api.has_user_contributed',
            args: {child_doctype: 'Validation Table', parent_doctype: doctype, name: name},
            callback: (r) => {
                if (r.message){
                    frappe.throw(`You have already validated this ${doctype}`);
                } else {
                    $(`#validation-modal-${name}`).modal('toggle');
                }
            }
        });
    }
    openCollaborationForm = (doctype, name) => {
        console.log('collab form');
        if (frappe.session.user === 'Guest') {
            frappe.throw('Please login to participate.');
        }
        frappe.call({
            method: 'contentready_oip.api.has_user_contributed',
            args: {child_doctype: 'Collaboration Table', parent_doctype: doctype, name: name},
            callback: (r) => {
                console.log(r);
                if (r.message){
                    frappe.throw(`You have already collaborated on this ${doctype}`);
                } else {
                    console.log($(`#collaboration-modal-${name}`));
                    $(`#collaboration-modal-${name}`).modal('toggle');
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