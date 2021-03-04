const create_org_options = () => {
    frappe.call({
      method: 'contentready_oip.api.get_orgs_list',
      args: {},
      callback: function (r) {
        const options = [...r.message].sort(sortAlphabetically);
        frappe.web_form.set_df_property('org', 'options', options);
      },
    });
  };