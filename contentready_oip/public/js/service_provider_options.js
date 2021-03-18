const create_service_provider_options = () => {
    frappe.call({
      method: 'contentready_oip.api.get_service_categories',
      args: {},
      callback: function (r) {
        const options = [...r.message].sort(sortAlphabetically);
        frappe.web_form.set_df_property('service_category', 'options', options);
      },
    });
  };