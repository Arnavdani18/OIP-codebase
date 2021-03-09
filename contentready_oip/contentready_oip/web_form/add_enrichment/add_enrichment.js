// prettier-ignore
frappe.provide( 'Vue' );

// prettier-ignore
frappe.ready( async () => {
  const doctype = 'Enrichment';

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
  {% include "contentready_oip/public/js/form_actions.js" %}

  // Fix layout - without this, the entire form occupies col-2 due to custom CSS.
  moveDivs = () => {
    $( ".section-body > div" ).each( function () {
      $( this )
        .parent()
        .before( this );
    } );
    $( ".web-form-wrapper" ).prepend(
      '<div class="row"><div class="col-md-6" id="add-problem-form"></div><div class="col-md-6" id="parent-problem"></div></div>'
    );
    $( "#add-problem-form" ).append( $( ".form-layout" ) );
  };

  formatMultiSelectValues = () => {
    // beneficiary
    const beneficiary_select = $('select[data-fieldname="beneficiaries"]');
    const beneficiariesVal = beneficiary_select.val()?.map(v => ({beneficiary: v}));
    frappe.web_form.doc.beneficiaries = beneficiariesVal;
  }


  getProblemCard = () => {
    frappe.call( {
      method: "contentready_oip.api.get_problem_overview",
      args: { name: frappe.web_form.doc.problem },
      callback: function ( r ) {
        // r.message[0] is the html
        // r.message[1] is the doc_name in case we need to do any processing client side
        $( "#parent-problem" ).append( r.message[ 0 ] );
      }
    } );
  };

  const pageHeadingSection = () => {

    $( '#auto-save-alert' ).addClass( 'auto-saved' );
    $( '.page-header-actions-block' ).addClass( 'd-flex align-items-center' );

    $( '.page-header' )
      .css( { 'width': '70%' } );

    const problemTitle = $( '.page-header h2' ).text();
    $( '.page-header h2' )
      .addClass( 'text-truncate' )
      .attr( 'title', problemTitle )
      .css( { 'margin-bottom': '0px' } );
  };

  // End Helpers

  // Delay until page is fully rendered
  while ( !frappe.web_form.fields ) {
    await sleep( 1000 );
  }

  // Start UI Fixes
  $( '*[data-doctype="Web Form"]' ).wrap( '<div class="container pt-5"></div>' );
  // We hide the default form buttons (using css) and add our own
  moveDivs();
  create_org_options();
  getProblemCard();
  style_form_headings();
  style_fields();
  control_labels();
  appendAttachLink();
  pageHeadingSection();
  hide_attachments_section();
  add_beneficiary_select2();
  addAsterisk(mandatory_fields);
  {% include "contentready_oip/public/js/resources_needed.js" %}
  {% include "contentready_oip/public/js/sector_component.js" %}
  // End UI Fixes


  // Start Google Maps Autocomplete
  const gScriptUrl =
    'https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places';
  $.getScript(gScriptUrl, () => {
    init_google_maps_autocomplete();
    // Extent field relies on map script
    {% include "contentready_oip/contentready_oip/web_form/add_problem/extent.js" %}
  });
  // End Google Maps Autocomplete

  // Start dropzone.js integration
  const dScriptUrl = 'assets/contentready_oip/js/dropzone.js';
  $.getScript( dScriptUrl, addDropzone );
  // End dropzone.js integration

  // Start Events
  // Set org link field when org title is selected
  $( '*[data-fieldname="org"]' ).on( "change", e => {
    frappe.web_form.doc.org = e.target.value;
  } );

  // End Events
} );

const style_form_headings = () => {
  $('h6').not(':first').prepend('<hr />');
  $('.form-section-heading').addClass('enrichment-details-page-subheadings');
};

