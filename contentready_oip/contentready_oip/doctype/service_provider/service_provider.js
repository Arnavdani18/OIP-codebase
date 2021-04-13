// Copyright (c) 2021, ContentReady and contributors
// For license information, please see license.txt

const approve = (frm) => {
	frm.call('approve')
    .then(r => {
        if (r.message) {
            frappe.msgprint('Approved and invited user. They will receive a welcome email.');
			frm.reload_doc();
        }
    })
}

frappe.ui.form.on('Service Provider', {
	refresh: function(frm) {
		frm.add_custom_button('Approve Service Provider', () => approve(frm));
	}
});
