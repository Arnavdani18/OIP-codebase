const add_beneficiary_select2 = () => {
    const beneficiary_select = $('select[data-fieldname="beneficiaries"]');
    beneficiary_select.attr('multiple', true);
    beneficiary_select.next().hide();
    beneficiary_select.select2();
}


const add_beneficiary_options = (sectors) => {
    const beneficiary_select = $('select[data-fieldname="beneficiaries"]');
    frappe.call({
        method: 'contentready_oip.api.get_beneficiaries_from_sectors',
        args: {
            sectors
        },
        callback: function (r) {
            const message = r.message;
            // adding already selected values to options
            const existing_beneficiaries = frappe.web_form.doc.beneficiaries ?? [];
            const beneficiary_values = existing_beneficiaries.map(val => val.beneficiary);
            const optionsSet = new Set([...message, ...beneficiary_values]);

            const sorted_beneficiaries = [...optionsSet].map(b => ({
                label: b,
                value: b
            })).sort(sortAlphabetically);
            frappe.web_form.set_df_property('beneficiaries', 'options', sorted_beneficiaries);

            // re-iterating based on options available
            // console.log('object', optionsSet);
            beneficiary_select.val(beneficiary_values);
        }
    })
}