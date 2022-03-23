frappe.provide('Vue');

frappe.ready(async () => {

  const doctype = 'Problem';

  const mandatory_fields = ['title', 'description', 'city', 'country', 'sectors'];

  // Start Helpers
  // Only write form specific helpers here. Use includes for common use cases.

  {% include "contentready_oip/public/js/utils.js" %}
  {% include "contentready_oip/public/js/sdg_options.js" %}
  {% include "contentready_oip/public/js/help_icon.js" %}
  {% include "contentready_oip/public/js/org_options.js" %}
  {% include "contentready_oip/public/js/org_from_profile.js" %}
  {% include "contentready_oip/public/js/beneficiary_options.js" %}
  {% include "contentready_oip/public/js/google_maps_autocomplete.js" %}
  {% include "contentready_oip/public/js/dropzone_media.js" %}
  {% include "contentready_oip/public/js/video_url_attachments.js" %}


  // Fix layout - without this, the entire form occupies col-2 due to custom CSS.
  moveDivs = () => {
    $('.section-body > div').each(function () {
      $(this).parent().before(this);
    });
    $('.web-form-wrapper').prepend(
      '<div class="row"><div class="col-md-6" id="add-problem-form"></div><div class="col-md-6"><h3>Similar Problems</h3><span id="similar-problems"></span></div></div>'
    );
    $('#add-problem-form').append($('.form-layout'));
    $('#similar-problems').append('<div></div>');
    $('.attached-file').parent().hide();
  };  

  lookForSimilarProblems = async () => {
    // Delay as the user is probably still typing
    await sleep(500);
    // Look up title again - user could have typed something since the event was triggered.
    const text = $('*[data-fieldname="title"]:text').val().trim();
    if (text.length > 2) {
      frappe.call({
        method: 'contentready_oip.api.search_content_by_text',
        args: {
          doctype: doctype,
          text: text,
        },
        callback: function (r) {
          // Add similar problems to div
          $('#similar-problems').empty();
          r.message.map((el) => {
            $('#similar-problems').append(el);
          });
        },
      });
    } else if (text.length === 0) {
      $('#similar-problems').empty();
    }
  };


  formatMultiSelectValues = () => {
    // sdg
    const sdg_select = $('select[data-fieldname="sdgs"]');
    let sdgVal = [];
    const selected_values = sdg_select.val();
    if (selected_values) {
      if (Array.isArray(selected_values)) {
        sdgVal = selected_values.val()?.map(v => ({sdg: v}));
      } else {
        // console.log(selected_values);
        sdgVal = [{sdg: selected_values}];
      }
    }
    
    frappe.web_form.doc.sdgs = sdgVal;

    // beneficiary
    const beneficiary_select = $('select[data-fieldname="beneficiaries"]');
    const beneficiariesVal = beneficiary_select.val()?.map(v => ({beneficiary: v}));
    frappe.web_form.doc.beneficiaries = beneficiariesVal;
  }

  const problemDetails = () => {
    $('.form-layout').prepend(
      `<h2 class="form-layout-problem-details">1. Problem Details</h2>`
    );
  };

  const style_form_headings = () => {
    $('.form-section-heading').prepend('<hr/>');
    $('.form-section-heading').addClass('problem-details-page-subheadings');
  };

  const pageHeadingSection = () => {

    $('#auto-save-alert').addClass('auto-saved');
    $('.page-header-actions-block').addClass('d-flex align-items-center');
    $('.page-header')
      .addClass('d-flex align-items-center')
      .css({ width: '70%' })
      .prepend(
        '<img src="/assets/contentready_oip/svg/problem_icon.svg" class="add-problem-icon" />'
      );

    const problemTitle = $('.page-header h2').text();
    $('.page-header h2')
      .addClass('text-truncate')
      .attr('title', problemTitle)
      .css({ 'margin-bottom': '0px' });

    $('#introduction').addClass('d-none');
  };

  // End Helpers

  // Delay until page is fully rendered
  while (!frappe.web_form.fields) {
    await sleep(1000);
  }

  // Start UI Fixes
  $('*[data-doctype="Web Form"]').wrap('<div class="container pt-5"></div>');
  // We hide the default form buttons (using css) and add our own
  moveDivs();
  create_org_options();
  addSdgOptions();
  problemDetails();
  control_labels();
  style_fields();
  style_form_headings();
  pageHeadingSection();
  appendAttachLink();
  hide_attachments_section();
  add_beneficiary_select2();
  prefill_org_field();
  addAsterisk(mandatory_fields);
  add_help_icon();
  $('.ql-image').hide();
  // End UI Fixes

  {% include "contentready_oip/public/js/form_actions.js" %}

  {% include "contentready_oip/public/js/resources_needed.js" %}

  {% include "contentready_oip/public/js/sector_component.js" %}
  

  // Start Google Maps Autocomplete
  const gScriptUrl =
    'https://maps.googleapis.com/maps/api/js?key=AIzaSyB6iz4qkY6H6EMvGY7sZjOBNm6S2VsjN5A&libraries=places';
  $.getScript(gScriptUrl, () => {
    init_google_maps_autocomplete();
    // Extent field relies on map script
    {% include "contentready_oip/contentready_oip/web_form/add_problem/extent.js" %}
  });
  // End Google Maps Autocomplete

  const dScriptUrl = 'assets/contentready_oip/js/dropzone.js';
  $.getScript(dScriptUrl, addDropzone);


  // Start Events
  // Look for similar problems when title is entered
  $('*[data-fieldname="title"]:text').on('keyup', (e) => {
    const value = e.target.value.trim();
    if (value.length && value.length % 3 === 0) {
      lookForSimilarProblems();
    } else if (value.length === 0) {
      $('#similar-problems').empty();
    }
  });
  // Set org link field when org title is selected
  $('*[data-fieldname="org"]').on('change', (e) => {
    frappe.web_form.set_value('org', e.target.value);
  });

  // End Events
});
