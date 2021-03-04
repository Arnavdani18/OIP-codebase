frappe.provide('Vue');

frappe.ready(async function () {

  {% include "contentready_oip/public/js/utils.js" %}
  // Start helpers
  // Simple sleep(ms) function from https://stackoverflow.com/a/48882182
  const sleep = (m) => new Promise((r) => setTimeout(r, m));

  let orgs = {};

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


  add_brandmark_to_doc = ( file ) => {
    if ( file.xhr ) {
      const response = JSON.parse( file.xhr.response );
      frappe.web_form.doc.brandmark = response.message.file_url;
    }
  };

  removeFileFromDoc = (file) => {
    // console.log('removed', file);
    frappe.web_form.doc.brandmark = '';
  };

  addDropzone = () => {
    // disable autoDiscover as we are manually binding the dropzone to a form element
    Dropzone.autoDiscover = false;
    const el = `<form class="dropzone dz-clickable d-flex align-items-center justify-content-center flex-wrap mb-4" style="font-size:var(--f14);" id='dropzone'><div class="dz-default dz-message"><button class="dz-button" type="button">Drop files here to upload</button></div></form>`;
    $('*[data-fieldname="brandmark"]').after(el);
    $('#dropzone').dropzone({
      url: '/api/method/contentready_oip.api.upload_file',
      autoDiscover: false,
      maxFiles: 1,
      addRemoveLinks: true,
      acceptedFiles: 'image/*',
      headers: {
        Accept: 'application/json',
        'X-Frappe-CSRF-Token': frappe.csrf_token,
      },
      init: function () {
        // use this event to add to child table
        this.on('complete', (file) => {
          const response = JSON.parse(file.xhr.response);
          if (response.message === false) {
            this.removeFile(file);
            frappe.msgprint('Explicit content detected. This file will not be uploaded.');
          } else {
            add_brandmark_to_doc(file);
          }
        });
        // use this event to remove from child table
        this.on('removedfile', removeFileFromDoc);
        if (frappe.web_form.doc.brandmark) {
          const file_url = frappe.web_form.doc.brandmark;
          let mockFile = { name: file_url, size: null };
          this.displayExistingFile(mockFile, file_url);
        }
      },
    });
  };

  add_action_buttons = () => {
    const publishBtn = `<button class="btn btn-sm btn-primary ml-2" onclick="publishOrg()">Update</button>`;
    $('.page-header-actions-block').append(publishBtn);
  };

  init_google_maps_autocomplete = () => {
    // TODO: Use domain settings to retrieve country list
    $('*[data-fieldname="city"]:text')
      .attr('id', 'autocomplete')
      .attr('placeholder', 'Search here');
    // Create the autocomplete object, restricting the search predictions to
    // geographical location types.
    autocomplete = new google.maps.places.Autocomplete(
      document.getElementById('autocomplete'),
      { types: ['(cities)'], componentRestrictions: { country: 'in' } }
      // { types: ['(cities)'] }
    );
    // Avoid paying for data that you don't need by restricting the set of
    // place fields that are returned to just the address components.
    // See https://developers.google.com/maps/documentation/javascript/places-autocomplete#add_autocomplete
    autocomplete.setFields(['address_component', 'geometry']);
    // When the user selects an address from the drop-down, populate the
    // address fields in the form.
    autocomplete.addListener('place_changed', fill_address_from_google_maps);
  };

  fill_address_from_google_maps = () => {
    // Get the place details from the autocomplete object.
    const place = autocomplete.getPlace();
    const addressMapping = {
      locality: {
        long_name: 'city',
      },
      administrative_area_level_1: {
        short_name: 'state_code',
        long_name: 'state',
      },
      country: {
        short_name: 'country_code',
        long_name: 'country',
      },
    };

    // Get each component of the address from the place details,
    // and then fill-in the corresponding field on the form.
    for (let i = 0; i < place.address_components.length; i++) {
      const address_type = place.address_components[i].types[0];
      if (addressMapping[address_type]) {
        if (addressMapping[address_type]['short_name']) {
          frappe.web_form.set_value(
            addressMapping[address_type]['short_name'],
            place.address_components[i]['short_name']
          );
        }
        if (addressMapping[address_type]['long_name']) {
          frappe.web_form.set_value(
            addressMapping[address_type]['long_name'],
            place.address_components[i]['long_name']
          );
        }
      }
    }
    frappe.web_form.set_value('latitude', place.geometry.location.lat());
    frappe.web_form.set_value('longitude', place.geometry.location.lng());
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

  const control_labels = () => {
    $('.control-label').addClass('label-styles');
    $('span.label-area.small').removeClass('small');
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

  const style_fields = () => {
    $('.input-with-feedback').addClass('field-styles');
  };

  const addSection = function () {
    // For Sectors
    $('*[data-fieldname="sectors"]').before(
      '<label class="control-label" style="padding-right: 0px;">Sectors</label><br/><div id="sectorsComp"></div>'
    );
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
    addSection();
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
