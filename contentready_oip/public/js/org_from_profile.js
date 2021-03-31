const set_org_from_profile = (orgRef)=>{
    frappe.call({
      method: 'contentready_oip.api.get_doc_field',
      args: {
        doctype: 'User Profile',
        name: frappe.session.user,
        field: ['org','org_title']
      },
      callback: function (r) {
        const organisation = r.message;
        const [org,orgTitle] = organisation;
        if (org) {
          frappe.web_form.set_value('org', org);
          orgRef.attr('disabled',true);
          orgRef.val(org);
        } 
      },
    });
  }

  async function prefill_org_field() {
    const orgRef = $('select[data-fieldname="org"]');
    if (!frappe.web_form.doc.org) {
      // set_org_from_profile(orgRef);
    } else{
      await sleep(500);
      orgRef.attr('disabled',true);
    }
  }