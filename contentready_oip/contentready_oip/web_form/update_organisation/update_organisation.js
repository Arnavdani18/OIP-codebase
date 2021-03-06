frappe.provide('Vue');

frappe.ready(async function () {

  
  const doctype = 'User Profile';

  // Start Helpers
  // Only write form specific helpers here. Use includes for common use cases.

  {% include "contentready_oip/public/js/utils.js" %}
  {% include "contentready_oip/public/js/google_maps_autocomplete.js" %}
  {% include "contentready_oip/public/js/dropzone_photo.js" %}
  // Fix layout - without this, the entire form occupies col-2 due to custom CSS.
  moveDivs = () => {
    $('.section-body > div').each(function () {
      $(this).parent().before(this);
    });
  };

  const fixOuterDivForMobile = () => {
    $('.col-9').removeClass('col-9').addClass('col-sm-12 col-md-10');
  };

  arrangeDivs = function () {
    // $('.page_content').wrap('<div class="row justify-content-center"><div class="col-10"></div></div>');
    $('.form-layout').addClass('bg-transparent px-0');
  };

  add_action_buttons = () => {
    const publishBtn = `<button class="btn btn-sm btn-primary ml-2" onclick="publishOrg()">Update</button>`;
    $('.page-header-actions-block').append(publishBtn);
  };


  publishOrg = () => {
    frappe.call({
      method: 'contentready_oip.api.add_primary_content',
      args: {
        doctype: 'Organisation',
        doc: frappe.web_form.doc,
      },
      callback: function (r) {
        if (r.message && r.message.route) {
          window.location.href = r.message.route;
        } else {
          window.location.href = '/dashboard';
        }
      },
    });
  };


  const style_form_headings = () => {
    $('h6').not(':first').prepend('<hr />');
    $('.form-section-heading').addClass('edit-profile-subheadings');
  };

  const pageHeadingSection = () => {
    $('button:contains("Update") , button:contains("Save")')
      .removeClass('btn-primary btn-sm')
      .addClass('btn-outline-primary outline-primary-btn');

    $('.page-header-actions-block').addClass('d-flex align-items-center');
    // $('.page-header').parent().wrap('<div class="row justify-content-center"><div class="col-10"></div></div>');

    $('.page-header h2').css({ 'margin-bottom': '0px' });
    $('#introduction').addClass('d-none');
  };

  // End Helpers
  // Delay until page is fully rendered
  while (!frappe.web_form.fields) {
    await sleep(1000);
  }

  // Start UI Fixes
  // We hide the default form buttons (using css) and add our own
  $('*[data-doctype="Web Form"]').wrap(
    `<div class="container pt-5"><div class="row justify-content-center"><div class="col-9"></div></div></div>`
  );

  $('div[role="form"]').ready(function () {
    add_action_buttons();
    moveDivs();
    arrangeDivs();
    fixOuterDivForMobile();
    control_labels();
    style_form_headings();
    style_fields();
    pageHeadingSection();
  });

  {% include "contentready_oip/public/js/sector_component.js" %}


  // Start Google Maps Autocomplete
  const gScriptUrl =
    'https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places';
  $.getScript(gScriptUrl, init_google_maps_autocomplete);
  // End Google Maps Autocomplete

  // Start dropzone.js integration
  const dScriptUrl = 'assets/contentready_oip/js/dropzone.js';
  $.getScript(dScriptUrl, addDropzone);
  // End dropzone.js integration

  // set email field
  // frappe.web_form.set_df_property('user', 'read_only', 1);
  // frappe.web_form.set_value('user', frappe.session.user);
  // frappe.web_form.doc.user = frappe.session.user;
});
