// frappe.provide('Vue');

frappe.ready(async () => {
  // Start Helpers
  let autocomplete;
  // Simple sleep(ms) function from https://stackoverflow.com/a/48882182
  const sleep = m => new Promise(r => setTimeout(r, m));

  // Fix layout - without this, the entire form occupies col-2 due to custom CSS.
  moveDivs = () => {
    $('.section-body > div').each(function() {
      $(this)
        .parent()
        .before(this);
    });
    $('.web-form-wrapper').prepend(
      `<div class="row"><div class="col-md-6" id="add-solution-form"></div><div class="col-md-6">
      <ul
      class="nav nav-tabs nav-section nav-mob-section bg-white"
      id="leftTab"
      role="tablist"
    >
      <li class="nav-item">
        <a
          class="nav-link active"
          id="matchedProblemsTab"
          data-toggle="tab"
          href="#matchedProblems"
          role="tab"
          aria-controls="matchedProblems"
          aria-selected="true"
        >
          Matching Problems <span id="matchingProblemsCount"></span>
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          id="similarSolutionsTab"
          data-toggle="tab"
          href="#similarSolutions"
          role="tab"
          aria-controls="similarSolutions"
          aria-selected="true"
        >
          Similar Solutions <span id="similarSolutionsCount"></span>
        </a>
      </li>
    </ul>

    <div class="tab-content">
      <div
        class="tab-pane fade show active"
        id="matchedProblems"
        role="tabpanel"
        aria-labelledby="matchedProblemsTab"
      >
        <input type="text" id="problem-search-input" placeholder="Search for matching problems" class="input-with-feedback form-control bold my-4"></input><span id="matching-problems"></span>
      </div>
      <div
        class="tab-pane fade"
        id="similarSolutions"
        role="tabpanel"
        aria-labelledby="similarSolutionsTab"
      >
        <p class="pattern1 my-4" id="matching-solutions">No Similar Solutions Found</p>
      </div>
    </div>

    
    </div></div>`
    );
    $('#add-solution-form').append($('.form-layout'));
    $('#matching-problems').append('<div></div>');
  };

  createOrgOptions = () => {
    frappe.call({
      method: 'contentready_oip.api.get_orgs_list',
      args: {},
      callback: function(r) {
        frappe.web_form.set_df_property('org', 'options', r.message);
      }
    });
  };

  createSectorOptions = () => {
    $('*[data-fieldname="sectors"]').before(
      '<label class="control-label" style="padding-right: 0px;">Sectors</label><br/><div id="sector-options"></div>'
    );
    frappe.call({
      method: 'contentready_oip.api.get_sector_list',
      args: {},
      callback: function(r) {
        let solution_sectors;
        if (frappe.web_form.doc.sectors) {
          solution_sectors = frappe.web_form.doc.sectors.map(s => s.sector);
        }
        r.message.map(op => {
          let has_sector = false;
          if (solution_sectors) {
            has_sector = solution_sectors.indexOf(op.value) !== -1;
          }
          const el = `<div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" id="sector-check-${op.value}" value="${op.value}"><label class="form-check-label" for="sector-check-${op.value}">${op.label}</label></div>`;
          $('#sector-options').append(el);
          $(`#sector-check-${op.value}`).attr('checked', has_sector);
        });
        $('[id^=sector-check]').on('click', addSectorToDoc);
      }
    });
  };

  addSectorToDoc = event => {
    if (!frappe.web_form.doc.sectors) {
      frappe.web_form.doc.sectors = [];
    }
    frappe.web_form.doc.sectors.push({ sector: event.target.value });
  };

  hideTables = () => {
    $('*[data-fieldtype="Table"]').hide();
  };

  initAutocomplete = () => {
    // TODO: Use domain settings to retrieve country list
    $('*[data-fieldname="city"]:text')
      .attr('id', 'autocomplete')
      .attr('placeholder', 'Search here');
    // Create the autocomplete object, restricting the search predictions to
    // geographical location types.
    autocomplete = new google.maps.places.Autocomplete(
      document.getElementById('autocomplete'),
      // { types: ['(cities)'], componentRestrictions: {country: 'in'} }
      { types: ['(cities)'] }
    );
    // Avoid paying for data that you don't need by restricting the set of
    // place fields that are returned to just the address components.
    // See https://developers.google.com/maps/documentation/javascript/places-autocomplete#add_autocomplete
    autocomplete.setFields(['address_component', 'geometry']);
    // When the user selects an address from the drop-down, populate the
    // address fields in the form.
    autocomplete.addListener('place_changed', fillInAddress);
  };

  fillInAddress = () => {
    // Get the place details from the autocomplete object.
    const place = autocomplete.getPlace();
    const addressMapping = {
      locality: {
        long_name: 'city'
      },
      administrative_area_level_1: {
        short_name: 'state_code',
        long_name: 'state'
      },
      country: {
        short_name: 'country_code',
        long_name: 'country'
      }
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

  setupProblemsForSelection = () => {
    $('#matching-problems')
      .children()
      .on('click', event => {
        // event.preventDefault();
        const selectedProblem = event.currentTarget;
        const selectedProblemName = $(selectedProblem).data('name');
        const alreadySelected = $(selectedProblem).data('selected');
        if (alreadySelected) {
          deselectProblemUI(selectedProblemName);
          removeProblemFromSolvedSet(selectedProblemName);
        } else {
          selectProblemUI(selectedProblemName);
          addProblemToSolvedSet(selectedProblemName);
        }
      });
  };

  deselectProblemUI = name => {
    const id = '#problem-card-' + name;
    $(id).css('background', '#ffffff');
    $(id).data('selected', false);
  };

  selectProblemUI = name => {
    const id = '#problem-card-' + name;
    $(id).css('background', '#eeffee');
    $(id).data('selected', true);
  };

  getProblemCard = name => {
    frappe.call({
      method: 'contentready_oip.api.get_problem_card',
      args: { name: name },
      callback: function(r) {
        // r.message[0] is the html
        // r.message[1] is the doc_name in case we need to do any processing client side
        $('#matching-problems').append(r.message[0]);
        selectProblemUI(r.message[1]);
        setupProblemsForSelection();
      }
    });
  };

  addMatchingProblems = () => {
    // Read query parameter to see if routed from a problem. Add that problem to matching problems.
    const qp = frappe.utils.get_query_params();
    if (qp.problem) {
      getProblemCard(qp.problem);
    }
    // When editing, show all the existing problems.
    if (frappe.web_form.doc.problems_addressed) {
      frappe.web_form.doc.problems_addressed.map(p => {
        getProblemCard(p.problem);
      });
    }
  };

  lookForMatchingProblems = async (text) => {
    // Delay as the user is probably still typing
    await sleep(500);
    // Look up text again - user could have typed something since the event was triggered.
    if (!text) {
      text = $('#problem-search-input')
        .val()
        .trim();
    }
    if (text.length > 3) {
      frappe.call({
        method: 'contentready_oip.api.search_content_by_text',
        args: {
          doctype: 'Problem',
          text: text
        },
        callback: function(r) {
          // Add matching problems to div
          $('#matching-problems').empty();
          $('#matchingProblemsCount').text('');
          r.message.map(el => {
            $('#matching-problems').append(el);
          });
          $('#matchingProblemsCount').text(`(${r.message.length})`);
          $('#matching-problems')
            .find('*')
            .unbind()
            .removeAttr('onclick')
            .removeAttr('data-toggle');
          // TODO: Prevent all other click events: nav, like, watch, modal
          setupProblemsForSelection();
        }
      });
    } else if (text.length === 0) {
      $('#matching-problems').empty();
      $('#matchingProblemsCount').text('');
    }
  };

  lookForSimilarSolutions = async (text) => {
    // Delay as the user is probably still typing
    await sleep(500);
    // Look up text again - user could have typed something since the event was triggered.
    if (!text) {
      text = frappe.web_form.doc.title;
    }
    if (text && text.length > 3) {
      frappe.call({
        method: 'contentready_oip.api.search_content_by_text',
        args: {
          doctype: 'Solution',
          text: text
        },
        callback: function(r) {
          // Add matching solutions to div
          $('#similarSolutions').empty();
          $('#similarSolutionsCount').text('');
          r.message.map(el => {
            $('#similarSolutions').append(el);
          });
          $('#similarSolutionsCount').text(`(${r.message.length})`);
        }
      });
    } else if (text && text.length === 0) {
      $('#similarSolutions').empty();
      $('#similarSolutionsCount').text('');
    }
  };

  addFileToDoc = file => {
    if (file.xhr) {
      const response = JSON.parse(file.xhr.response);
      const file_url = response.message.file_url;
      if (!frappe.web_form.doc.media) {
        frappe.web_form.doc.media = [];
      }
      frappe.web_form.doc.media.push({
        attachment: file_url,
        size: file.size,
        type: file.type
      });
    }
  };

  removeFileFromDoc = file => {
    frappe.web_form.doc.media = frappe.web_form.doc.media.filter(
      i => !i.attachment.endsWith(file.name)
    );
  };

  addDropzone = () => {
    // TODO: Allow user to select an image as featured image
    // disable autoDiscover as we are manually binding the dropzone to a form element
    Dropzone.autoDiscover = false;
    const el = `<form class="dropzone dz-clickable" id='dropzone'><div class="dz-default dz-message"><button class="dz-button" type="button">Drop files here to upload</button></div></form>`;
    $('*[data-fieldname="media"]*[data-fieldtype="Table"]')
      .parent()
      .after(el);
    $('#dropzone').dropzone({
      url: '/api/method/upload_file',
      autoDiscover: false,
      addRemoveLinks: true,
      acceptedFiles: 'image/*',
      headers: {
        Accept: 'application/json',
        'X-Frappe-CSRF-Token': frappe.csrf_token
      },
      init: function() {
        // use this event to add to child table
        this.on('complete', addFileToDoc);
        // use this event to remove from child table
        this.on('removedfile', removeFileFromDoc);
        let myDropzone = this;
        if (frappe.web_form.doc.media) {
          frappe.web_form.doc.media.map(a => {
            let mockFile = { name: a.attachment, size: a.size };
            myDropzone.displayExistingFile(mockFile, a.attachment);
          });
        }
      }
    });
  };

  addProblemToSolvedSet = name => {
    if (!frappe.web_form.doc.problems_addressed) {
      frappe.web_form.doc.problems_addressed = [];
    }
    frappe.web_form.doc.problems_addressed.push({
      problem: name
    });
  };

  removeProblemFromSolvedSet = name => {
    frappe.web_form.doc.problems_addressed = frappe.web_form.doc.problems_addressed.filter(
      i => !i.problem === name
    );
  };

  submitSolutionForm = is_draft => {
    frappe.call({
      method: 'contentready_oip.api.add_primary_content',
      args: {
        doctype: 'Solution',
        doc: frappe.web_form.doc,
        is_draft: is_draft
      },
      callback: function(r) {
        if (r.message && r.message.is_published && r.message.route) {
          window.location.href = r.message.route;
        } else {
          window.location.href = '/dashboard';
        }
      }
    });
  };

  showAutoSaveAlert = () => {
    $('#auto-save-alert').removeClass('hidden');
  };

  hideAutoSaveAlert = () => {
    $('#auto-save-alert').addClass('hidden');
  };

  autoSaveDraft = () => {
    if (frappe.web_form.doc.title) {
      frappe.call({
        method: 'contentready_oip.api.add_primary_content',
        args: {
          doctype: 'Solution',
          doc: frappe.web_form.doc,
          is_draft: true
        },
        callback: function(r) {
          // console.log(r);
          // update local form technical fields so that they are up to date with server values
          // Important: do no update fields on the UI as that will interfere with user experience.
          const keysToCopy = [
            'creation',
            'modified',
            'docstatus',
            'doctype',
            'idx',
            'owner',
            'modified_by',
            'name'
          ];
          keysToCopy.map(key => {
            frappe.web_form.doc[key] = r.message[key];
          });
          showAutoSaveAlert();
          setTimeout(hideAutoSaveAlert, 1000);
        }
      });
    }
  };

  saveAsDraft = event => {
    frappe.web_form.doc.is_published = false;
    const is_draft = true;
    submitSolutionForm(is_draft);
  };

  publishSolution = event => {
    frappe.web_form.doc.is_published = true;
    const is_draft = false;
    submitSolutionForm(is_draft);
  };

  addActionButtons = () => {
    const saveAsDraftBtn = `<button class="btn btn-sm ml-2" onclick="saveAsDraft()">Save as Draft</button>`;
    const publishBtn = `<button class="btn btn-sm btn-primary ml-2" onclick="publishSolution()">Publish</button>`;
    const alert = `<span class="alert alert-primary fade show hidden" role="alert" id="auto-save-alert">Saved</span>`;
    $('.page-header-actions-block').append(alert);
    $('.page-header-actions-block')
      .append(saveAsDraftBtn)
      .append(publishBtn);
  };

  const styleFormHeadings = () => {
    $('h6')
      .not(':first')
      .prepend('<hr />');
    $('.form-section-heading').addClass('solution-details-page-subheadings');
  };

  const styleFields = () => {
    $('.input-with-feedback').addClass('field-styles');
  };

  const controlLabels = () => {
    $('.control-label').addClass('label-styles');
  };

  const pageHeadingSection = () => {
    $('button:contains("Save as Draft")')
      .removeClass('btn-sm')
      .addClass('btn-outline-primary outline-primary-btn');

    $('button:contains("Publish")')
      .removeClass('')
      .addClass('solid-primary-btn');

    $('#auto-save-alert').addClass('auto-saved');
    $('.page-header-actions-block').addClass('d-flex align-items-center');
    $('.page-header')
      .addClass('d-flex align-items-center')
      .prepend(
        '<img src="/files/solution_dark.svg" class="add-problem-icon" />'
      );

    $('.page-header h2').css({ 'margin-bottom': '0px' });
  };
  // End Helpers

  // Delay until page is fully rendered
  await sleep(500);

  // Start UI Fixes
  $('*[data-doctype="Web Form"]').wrap('<div class="container pt-5"></div>');
  fixNavBar();
  // We hide the default form buttons (using css) and add our own
  addActionButtons();
  moveDivs();
  createOrgOptions();
  createSectorOptions();
  styleFormHeadings();
  styleFields();
  controlLabels();
  pageHeadingSection();

  // End UI Fixes

  // Start Google Maps Autocomplete
  const gScriptUrl =
    'https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places';
  $.getScript(gScriptUrl, initAutocomplete);
  // End Google Maps Autocomplete

  // Start dropzone.js integration
  // const scriptPath = "public/js/dropzone.js";
  const dScriptUrl = '/files/dropzone.js';
  $.getScript(dScriptUrl, addDropzone);
  // End dropzone.js integration

  // Start Events
  addMatchingProblems();
  // Look for matching problems when text is entered
  $('#problem-search-input').on('keyup', e => {
    const value = e.target.value.trim();
    if (value.length && value.length % 3 === 0) {
      lookForMatchingProblems();
    }
  });
  // Look for similar solutions when title is typed
  // $('*[data-fieldname="title"]:input').on('keyup', e => {
  //   const value = e.target.value.trim();
  //   if (value.length && value.length % 3 === 0) {
  //     console.log(value);
  //     lookForSimilarSolutions();
  //   }
  // });
  frappe.web_form.on('title', () => {
    const value = frappe.web_form.doc.title.trim();
    if (value.length >= 3) {
      lookForSimilarSolutions(value);
    }
  })


  // Set org link field when org title is selected
  $('*[data-fieldname="org"]').on('change', e => {
    frappe.web_form.doc.org = e.target.value;
  });

  setInterval(autoSaveDraft, 10000);

  // End Events
});

fixNavBar = () => {
  $('main').removeClass('container my-5');
  $('nav.navbar').addClass('navbar-section');
  $('ul.navbar-nav:even').addClass('nav-left-list');
  $('ul.navbar-nav:odd').addClass('nav-right-list');
  $('ul.navbar-nav:even .nav-link.active').addClass('tab-focus');

  let search = $('a[href="/search"]');
  search.addClass('d-md-flex align-items-md-center');
  search.html('<span class="d-block d-lg-none">Search</span>');
  search.prepend(
    '<img src="/files/Search.svg" class="mr-4" height="20" width="20" />'
  );

  $('li.nav-item.dropdown.logged-in a').addClass(
    'd-flex align-items-center mr-4'
  );
  $('li.nav-item.dropdown.logged-in a span.full-name').attr('hidden', true);
  $('div.standard-image').css({
    height: '3rem',
    width: '3rem',
    'text-align': 'center'
  });

  $('ul.dropdown-menu').addClass('dropdown-section');
  // menu button
  $('button.navbar-toggler').addClass('py-2');

  // changing My Account to Edit Profile
  const dropdownList = $('a[href="/me"]');
  dropdownList.attr('href', '/update-profile');
  dropdownList.text('Profile');

  if (frappe.session.user === 'Guest') {
    $('a:contains("Add a Problem / Solution")').hide();
  } else {
    $('a:contains("Add a Problem / Solution")').addClass('add-problem-btn');
    $('a:contains("Add a Problem / Solution")')
      .next()
      .addClass('dropdown-menu-right');

    // fix moving of nav while clicking menu icon
    $('nav div.container').addClass('nav-container');

    // chnge the list order
    $('.nav-right-list')
      .find('li:eq(0)')
      .insertAfter('.nav-right-list li:eq(2)');

    // insert add problem/solution and search logo
    let addProblem = $('a[href="/add-problem?new=1"]');
    let addSolution = $('a[href="/add-solution?new=1"]');

    addProblem.prepend(
      '<img src="/files/problem_dark.svg" height="22" width="30" />'
    );

    addSolution.prepend(
      '<img src="/files/solution_dark.svg" height="22" width="30" />'
    );

    addProblem.addClass('py-2');
    addSolution.addClass('py-2');
  }
};
