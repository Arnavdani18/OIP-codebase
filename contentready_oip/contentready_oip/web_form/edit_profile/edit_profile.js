frappe.provide('Vue');

frappe.ready(async function () {
  
  const doctype = 'User Profile';

  // Start Helpers
  // Only write form specific helpers here. Use includes for common use cases.

  {% include "contentready_oip/public/js/utils.js" %}
  {% include "contentready_oip/public/js/org_options.js" %}
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
    const publishBtn = `<button class="btn btn-sm btn-primary ml-2" onclick="publishProfile()">Update</button>`;
    $('.page-header-actions-block').append(publishBtn);
  };


  isValidLinkedInUrl = (url) => {
    const LINKEDIN_REGEX = /((https?:\/\/)?((www|\w\w)\.)?linkedin\.com\/)((([\w]{2,3})?)|([^\/]+\/(([\w|\d-&#?=])+\/?){1,}))$/;
    const re = new RegExp(LINKEDIN_REGEX);
    return re.test(url);
  };

  publishProfile = () => {
    const data = frappe.web_form.get_values();
    const { linkedin_profile } = data;

    if (linkedin_profile && !isValidLinkedInUrl(linkedin_profile)) {
      frappe.msgprint('Enter valid LinkedIn profile url');
      return false;
    }

    frappe.call({
      method: 'contentready_oip.api.add_primary_content',
      args: {
        doctype: 'User Profile',
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

    $('.page-header h2').css({ 'margin-bottom': '0px' });
    $('#introduction').addClass('d-none');
  };

  const addNewOrgButton = () => {
    const button = `<a class="btn btn-primary text-light ml-3 mb-2 btn-xs" href="/organisation">
      <i class="octicon octicon-plus"></i>
    </a>`;

    $('label:contains("Organisation")').parent().append(button);

  }


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
    create_org_options();
    fixOuterDivForMobile();
    control_labels();
    style_form_headings();
    // style_fields();
    pageHeadingSection();
    addNewOrgButton();
    {% include "contentready_oip/public/js/sector_component.js" %}
    {% include "contentready_oip/public/js/personas_component.js" %}
  });

  // Start Google Maps Autocomplete
  const gScriptUrl =
    'https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places';
  $.getScript(gScriptUrl, init_google_maps_autocomplete);
  // End Google Maps Autocomplete

  // Start dropzone.js integration
  const dScriptUrl = 'assets/contentready_oip/js/dropzone.js';
  $.getScript(dScriptUrl, addDropzone);
  // End dropzone.js integration
});
