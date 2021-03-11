const addSdgOptions = () => {
    const sdg_select = $('select[data-fieldname="sdgs"]');
    console.log(sdg_select);
    // add multiple attr 
    sdg_select.attr('multiple',true);

    // remove icon
    sdg_select.next().hide();
    sdg_select.select2();

    frappe.call({
      method: 'contentready_oip.api.get_sdg_list',
      args: {},
      callback: function (r) {
        const options = [...r.message].sort(sortAlphabetically);
        frappe.web_form.set_df_property('sdgs', 'options', options);
        const existing_sdgs = frappe.web_form.doc.sustainable_development_goal
        const sdgValues = existing_sdgs?.map(v => v.sustainable_development_goal);
        
        sdg_select.val(sdgValues);
      },
    });
  }