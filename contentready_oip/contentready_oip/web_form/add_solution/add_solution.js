frappe.provide('Vue');

frappe.ready(async () => {
  // Start Helpers
  let autocomplete;
  // Simple sleep(ms) function from https://stackoverflow.com/a/48882182
  const sleep = (m) => new Promise((r) => setTimeout(r, m));

  // Fix layout - without this, the entire form occupies col-2 due to custom CSS.
  moveDivs = () => {
    $('.section-body > div').each(function () {
      $(this).parent().before(this);
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

  const sortAlphabetically = (a, b) => {
    var labelA = a.label.toUpperCase(); // ignore upper and lowercase
    var labelB = b.label.toUpperCase(); // ignore upper and lowercase
    if (labelA < labelB) {
      return -1;
    }
    if (labelA > labelB) {
      return 1;
    }

    // for equal case
    return 0;
  }

  createOrgOptions = () => {
    frappe.call({
      method: 'contentready_oip.api.get_orgs_list',
      args: {},
      callback: function (r) {
        const options = [...r.message].sort(sortAlphabetically);
        frappe.web_form.set_df_property('org', 'options', options);
      },
    });
  };

  const addSection = function () {
    // For Sectors
    $('*[data-fieldname="sectors"]').before(
      '<label class="control-label" style="padding-right: 0px;">Sectors</label><br/><div id="sectorsComp"></div>'
    );
  };

  hideTables = () => {
    $('*[data-fieldtype="Table"]').hide();
  };

  addMultiselectForSolverTeam = () => {
    const el = `
    <h6 class="mt-3">Solver Team</h6>
    <select class="select2" name="solver_team[]" multiple="multiple" id="solver-team-select">
    </select>
    <br /><br />
    `;
    $('[data-fieldname="solver_team"][data-fieldtype="Table"]').before(el);
    // $('#solver-team-select').select2({
    //   width: '100%'
    // });
    frappe.call({
      method: 'contentready_oip.api.get_user_list',
      args: {},
      callback: function (r) {
        $('#solver-team-select').select2({
          width: '100%',
          data: r.message,
        });
        setSolversMultiselectFromDoc();
      },
    });
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
      { types: ['(cities)'], componentRestrictions: { country: 'in' } }
      // { types: ['(cities)'] }
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

  setupProblemsForSelection = () => {
    $('#matching-problems')
      .children()
      .on('click', (event) => {
        // event.preventDefault();
        const selectedProblem = event.currentTarget;
        const selectedProblemName = $(selectedProblem).data('name');
        const alreadySelected = $(selectedProblem).data('selected');

        frappe.call({
          method: 'contentready_oip.api.get_problem_detail_modal',
          args: { name: selectedProblemName },
          callback: function (r) {
            $('.page_content').after(r.message[0]);
            $(`#${selectedProblemName}`).modal('show');
            $(`#${selectedProblemName} .modal-dismiss-btn`).on(
              'click',
              function () {
                $(`#${selectedProblemName}`).modal('hide');
              }
            );

            // Remove enrichment modal from the view
            const all_enrichments = r.message[1];
            if (all_enrichments) {
              all_enrichments.forEach(function (enrich) {
                $(`#enrichment-modal-${enrich.enrichment}`).remove();
              });
            }

            const select_to_solve_btn = $(
              `#${selectedProblemName} button[data-type="select_to_solve"]`
            );
            toggleBtnText(selectedProblem);

            // Add event listen to button
            select_to_solve_btn.on('click', function () {
              if (alreadySelected) {
                deselectProblemUI(selectedProblemName);
                removeProblemFromSolvedSet(selectedProblemName);
                toggleBtnText(selectedProblem);
                vm.removeTitle(selectedProblemName);
              } else {
                selectProblemUI(selectedProblemName);
                addProblemToSolvedSet(selectedProblemName);
                toggleBtnText(selectedProblem);
              }
            });
          },
        });
      });
  };

  toggleBtnText = (qSelector) => {
    const alreadySelected = $(qSelector).data('selected');
    const selectedProblemName = $(qSelector).data('name');
    const btn = $(
      `#${selectedProblemName} button[data-type="select_to_solve"]`
    );

    // Vary the button text
    if (alreadySelected) {
      btn.text('Unselect Problem');
    } else {
      btn.text('Select to solve');
    }
  };

  deselectProblemUI = (name) => {
    const id = '#problem-card-' + name;
    $(id).css('background', '#ffffff');
    $(id).data('selected', false);
  };

  selectProblemUI = (name) => {
    const id = '#problem-card-' + name;
    $(id).css('background', '#eeffee');
    $(id).data('selected', true);
  };

  getProblemCard = (name) => {
    frappe.call({
      method: 'contentready_oip.api.get_problem_card',
      args: { name: name },
      callback: function (r) {
        console.log('Get Problem Card: ', r);

        // r.message[0] is the html
        // r.message[1] is the doc_name in case we need to do any processing client side
        $('#matching-problems').append(r.message[0]);
        // disable click to navigate on the card
        $('#matching-problems')
          .find('*')
          .unbind()
          .removeAttr('onclick')
          .removeAttr('data-toggle');
        selectProblemUI(r.message[1]);
        setupProblemsForSelection();
      },
    });
  };

  addMatchingProblems = () => {
    // Read query parameter to see if routed from a problem. Add that problem to matching problems.
    const qp = frappe.utils.get_query_params();
    if (qp.problem) {
      if (!frappe.web_form.doc.problems_addressed) {
        frappe.web_form.doc.problems_addressed = [];
      }
      frappe.web_form.doc.problems_addressed.push({ problem: qp.problem });
      getProblemCard(qp.problem);
    }
    // When editing, show all the existing problems.
    else if (frappe.web_form.doc.problems_addressed) {
      frappe.web_form.doc.problems_addressed.map((p) => {
        getProblemCard(p.problem);
      });
    }
  };

  lookForMatchingProblems = async (text) => {
    // Delay as the user is probably still typing
    await sleep(500);
    // Look up text again - user could have typed something since the event was triggered.
    if (!text) {
      text = $('#problem-search-input').val().trim();
    }
    if (text.length > 3) {
      frappe.call({
        method: 'contentready_oip.api.search_content_by_text',
        args: {
          doctype: 'Problem',
          text: text,
        },
        callback: function (r) {
          // Add matching problems to div
          $('#matching-problems').empty();
          $('#matchingProblemsCount').text('');
          r.message.map((el) => {
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
        },
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
    if (text && text.length > 2) {
      frappe.call({
        method: 'contentready_oip.api.search_content_by_text',
        args: {
          doctype: 'Solution',
          text: text,
        },
        callback: function (r) {
          // Add matching solutions to div
          $('#similarSolutions').empty();
          $('#similarSolutionsCount').text('');
          r.message.map((el) => {
            $('#similarSolutions').append(el);
          });
          $('#similarSolutionsCount').text(`(${r.message.length})`);
        },
      });
    } else if (text && text.length === 0) {
      $('#similarSolutions').empty();
      $('#similarSolutionsCount').text('');
    }
  };

  addFileToDoc = (file) => {
    attachFeaturedBtn(file);

    if (file.xhr) {
      const response = JSON.parse(file.xhr.response);
      const file_url = response.message.file_url;
      if (!frappe.web_form.doc.media) {
        frappe.web_form.doc.media = [];
      }
      frappe.web_form.doc.media.push({
        attachment: file_url,
        size: file.size,
        type: file.type,
      });
    }
  };

  attachFeaturedBtn = (file) => {
    $(file['previewElement']).append(`<div id="featureBtn"></div>`);
    {% include 'public/custom_templates/featureBtn.js' %}
  };

  removeFileFromDoc = (file) => {
    frappe.web_form.doc.media = frappe.web_form.doc.media.filter(
      (i) => !i.attachment.endsWith(file.name)
    );
  };

  addDropzone = () => {
    // TODO: Allow user to select an image as featured image
    // disable autoDiscover as we are manually binding the dropzone to a form element
    Dropzone.autoDiscover = false;
    const el = `{% include "public/custom_templates/dz.html" %}`;

    $('*[data-fieldname="media"]*[data-fieldtype="Table"]').parent().after(el);
    $('#dropzone').dropzone({
      url: '/api/method/upload_file',
      autoDiscover: false,
      addRemoveLinks: true,
      acceptedFiles: 'image/*,video/*',
      clickable: ['#dropzone', '#add-multiple-files'],
      headers: {
        Accept: 'application/json',
        'X-Frappe-CSRF-Token': frappe.csrf_token,
      },
      init: function () {
        let myDropzone = this;
        // use this event to add to child table
        this.on('complete', addFileToDoc);
        // use this event to remove from child table
        this.on('removedfile', function (file) {
          toggleAddMore(myDropzone.files.length);
          removeFileFromDoc(file);
        });

        if (frappe.web_form.doc.media) {
          toggleAddMore(frappe.web_form.doc.media.length);

          frappe.web_form.doc.media.map((a) => {
            let mockFile = { name: a.attachment, size: a.size };
            myDropzone.displayExistingFile(mockFile, a.attachment);
          });
        }

        this.on('sending', function () {
          toggleAddMore(myDropzone.files.length);
        });

        const addMutipleFilesBtn = document.querySelector(
          '#add-multiple-files'
        );
        if (addMutipleFilesBtn) {
          addMutipleFilesBtn.onclick = function (e) {
            e.preventDefault();
          };
        }

        const clearDzBtn = document.querySelector('button#clear-dropzone');
        if (clearDzBtn) {
          clearDzBtn.addEventListener('click', function (e) {
            e.preventDefault();
            myDropzone.removeAllFiles();
            toggleAddMore(myDropzone.files.length);
          });
        }
      },
    });
  };

  toggleAddMore = (len) => {
    const addMore = $('#add-multiple-files').parent();
    if (len) {
      addMore.addClass('dz-preview').removeClass('hidden');
    } else {
      addMore.addClass('hidden').removeClass('dz-preview');
    }
  };

  addProblemToSolvedSet = (name) => {
    if (!frappe.web_form.doc.problems_addressed) {
      frappe.web_form.doc.problems_addressed = [];
    }
    frappe.web_form.doc.problems_addressed.push({
      problem: name,
    });

    getTitleByName(frappe.web_form.doc.problems_addressed);
  };

  getTitleByName = async function (problems_addressed_arr) {
    let result = [];

    for (const problem of problems_addressed_arr) {
      let promise = new Promise(function (resolve, reject) {
        resolve(
          frappe.call({
            method: 'contentready_oip.api.get_problem_details',
            args: { name: problem['problem'] },
          })
        );
      });

      let problemObj = await promise;
      result.push(problemObj['message']);
    }

    vm.selectedProblems = result;
  };

  removeProblemFromSolvedSet = (name) => {
    frappe.web_form.doc.problems_addressed = frappe.web_form.doc.problems_addressed.filter(
      (i) => !i.problem === name
    );
  };

  getSolversFromMultiselect = () => {
    const solvers = $('#solver-team-select').val();
    // console.log(solvers);
    if (solvers) {
      frappe.web_form.doc.solver_team = [];
      solvers.map((s) => {
        frappe.web_form.doc.solver_team.push({ user: s });
      });
    }
  };

  setSolversMultiselectFromDoc = () => {
    if (frappe.web_form.doc.solver_team) {
      const solvers = [];
      frappe.web_form.doc.solver_team.map((s) => {
        solvers.push(s.user);
      });
      // console.log(solvers);
      $('#solver-team-select').val(solvers);
      $('#solver-team-select').trigger('change');
    }
  };

  submitSolutionForm = (is_draft) => {
    const {title,description,city,country} = frappe.web_form.doc;
    if (!title && !description && !city) {
      const error_message = `
      Please enter the required field to publish.
      <ul>
        <li>Title</li>
        <li>City</li>
        <li>Country</li>
        <li>Description</li>
      </ul>
      `
      frappe.throw(error_message);
      return;
    }

    getSolversFromMultiselect();
    frappe.call({
      method: 'contentready_oip.api.add_primary_content',
      args: {
        doctype: 'Solution',
        doc: frappe.web_form.doc,
        is_draft: is_draft,
      },
      callback: function (r) {
        $(window).off('beforeunload');
        clearInterval(autosave);

        if (r.message && r.message.is_published && r.message.route) {
          window.location.href = r.message.route;
        } else {
          window.location.href = '/dashboard';
        }
      },
    });
  };

  showAutoSaveAlert = () => {
    $('#auto-save-alert').removeClass('hidden');
  };

  hideAutoSaveAlert = () => {
    $('#auto-save-alert').addClass('hidden');
  };

  autoSaveDraft = () => {
    getSolversFromMultiselect();
    if (frappe.web_form.doc.title) {
      frappe.call({
        method: 'contentready_oip.api.add_primary_content',
        args: {
          doctype: 'Solution',
          doc: frappe.web_form.doc,
          is_draft: true,
        },
        callback: function (r) {
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
            'name',
          ];
          keysToCopy.map((key) => {
            frappe.web_form.doc[key] = r.message[key];
          });

          // update delete btn vue instance
          deleteBtnInstance.btnText = deleteBtnInstance.getBtnText();

          // Replace state if exists
          const currQueryParam = window.location['search'];

          if (currQueryParam.includes('new=1')) {
            window.history.replaceState({}, null, `?name=${r.message['name']}`);
          }

          showAutoSaveAlert();
          setTimeout(hideAutoSaveAlert, 1000);
        },
      });
    }
  };

  saveAsDraft = (event) => {
    frappe.web_form.doc.is_published = false;
    const is_draft = true;
    submitSolutionForm(is_draft);
  };

  publishSolution = (event) => {
    //if(frappe.web_form.doc.problems_addressed && frappe.web_form.doc.problems_addressed.length){
    frappe.web_form.doc.is_published = true;
    const is_draft = false;
    submitSolutionForm(is_draft);
    //} else {
    //    frappe.throw('Please select at least one problem.');
    //}
  };

  addActionButtons = () => {
    const saveAsDraftBtn = `<button class="btn ml-2 btn-outline-primary outline-primary-btn" onclick="saveAsDraft()">Save as Draft</button>`;
    const publishBtn = `<button
      class="btn btn-primary ml-2 solid-primary-btn"
      onclick="publishSolution()"
      >
        Publish
      </button>`;

    const deleteBtnPlaceholder = `
      <div id="deleteBtn"></div>
    `;
    const alert = `<span class="alert alert-primary fade show hidden" role="alert" id="auto-save-alert">Saved</span>`;
    $('.page-header-actions-block').append(alert);
    $('.page-header-actions-block')
      // .append(saveAsDraftBtn)
      .append(deleteBtnPlaceholder)
      .append(publishBtn);
  };

  const styleFormHeadings = () => {
    $('h6').not(':first').prepend('<hr />');
    $('.form-section-heading').addClass('solution-details-page-subheadings');
  };

  const styleFields = () => {
    $('.input-with-feedback').addClass('field-styles');
  };

  const controlLabels = () => {
    $('.control-label').addClass('label-styles');
  };

  const pageHeadingSection = () => {
    // $('button:contains("Save as Draft")')
    //   .removeClass('btn-sm')
    //   .addClass('btn-outline-primary outline-primary-btn');

    // $('button:contains("Publish")')
    //   .removeClass('')
    //   .addClass('solid-primary-btn');

    $('#auto-save-alert').addClass('auto-saved');
    $('.page-header-actions-block').addClass('d-flex align-items-center');
    $('.page-header')
      .addClass('d-flex align-items-center')
      .css({ width: '70%' })
      .prepend(
        '<img src="/assets/contentready_oip/svg/solution_icon.svg" class="add-problem-icon" />'
      );

    const problemTitle = $('.page-header h2').text();
    $('.page-header h2')
      .addClass('text-truncate')
      .attr('title', problemTitle)
      .css({ 'margin-bottom': '0px' });
  };

  const appendAttachLink = () => {
    let btn = `
    <div class="attach-links-section pattern1">
      <button class="btn btn-primary solid-primary-btn mb-3" >Attach video link</button>
      <ul class="list-group"></ul>
    </div>`;

    $('h6:contains("Media")').parent().append(btn);

    // if media attachment already exist
    displayAttachedLinks();

    $('.attach-links-section button').click(function () {
      let links = prompt(
        'Please enter links from Youtube or Vimeo. Separate multiple links with commas.'
      );
      if (links) {
        if (!frappe.web_form.doc.media) {
          frappe.web_form.doc.media = [];
        }

        let media = frappe.web_form.doc.media;
        let linkArr = links.split(',');

        linkArr.forEach((link) => {
          // check if link exist
          let idxExist = media.findIndex((mediaObj) => {
            return mediaObj['attachment'] === link;
          });

          if (checkMedialUrl(link) && idxExist < 0) {
            media.push({ attachment: link, type: 'link' });
          } else if (idxExist > -1) {
            alert('Provided link already exists.');
          } else {
            alert('Please enter links from Youtube or Vimeo only.');
          }
        });

        displayAttachedLinks();
      }
    });
  };

  const checkMedialUrl = function (url) {
    const regex = /(youtube|youtu|vimeo)\.(com|be)\/((watch\?v=([-\w]+))|(video\/([-\w]+))|(projects\/([-\w]+)\/([-\w]+))|([-\w]+))/;

    if (url.match(regex)) {
      return true;
    } else {
      return false;
    }
  };

  const displayAttachedLinks = () => {
    if (!frappe.web_form.doc.media) {
      return;
    }
    let media = frappe.web_form.doc.media;

    let linkArr = [];
    $('.attach-links-section ul').empty();
    if (media && media.length) {
      linkArr = media.filter((mediaObj) => mediaObj['type'] === 'link');
    }

    for (const [index, link] of linkArr.entries()) {
      let unorderedList = `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        ${link['attachment']}
        <button type="button" class="close" id="removeBtn-${
          index + 1
        }" data-attachment="${link.attachment}" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
      </li>`;

      $('.attach-links-section ul').append(unorderedList);
      let btnId = `#removeBtn-${index + 1}`;

      $(btnId).click(function () {
        let linkText = $(this).attr('data-attachment');

        if (media) {
          let foundIndex = media.findIndex((linkObj) => {
            return linkObj['attachment'] === linkText;
          });

          if (foundIndex > -1) {
            media.splice(foundIndex, 1);
            displayAttachedLinks();
          }
        }
      });
    }
  };

  const addAsterisk = function (fieldnameArr) {
    for (const field of fieldnameArr) {
      $(`[data-fieldname="${field}"] label`)
        .append(`<span class="text-danger">*</span>`);
    }
  }

  insertSelectedProblem = function () {
    $('*[data-fieldname="problems_addressed"]*[data-fieldtype="Table"]')
      .parent()
      .after(`<div id="selectedProblem"></div>`);
  };

  function hideAttachmentsSection() {
    $('.attachments').hide();
  }

  // End Helpers

  // Delay until page is fully rendered
  while (!frappe.web_form.fields) {
    await sleep(1000);
  }

  // Start UI Fixes
  $('*[data-doctype="Web Form"]').wrap('<div class="container pt-5"></div>');
  // We hide the default form buttons (using css) and add our own
  addActionButtons();
  moveDivs();
  createOrgOptions();
  // createSectorOptions();
  addSection();
  styleFormHeadings();
  styleFields();
  controlLabels();
  pageHeadingSection();
  addMultiselectForSolverTeam();
  appendAttachLink();
  insertSelectedProblem();
  hideAttachmentsSection();
  // getAvailableSectors();
  addAsterisk(['title','description','city','problems_addressed','country'])

  if (frappe.web_form.doc.problems_addressed) {
    getTitleByName(frappe.web_form.doc.problems_addressed);
  }

  const vm = new Vue({
    el: '#selectedProblem',
    data: function () {
      return {
        selectedProblems: [],
      };
    },
    methods: {
      removeTitle: function (name) {
        let problemIndex = frappe.web_form.doc.problems_addressed.findIndex(
          (p) => p['problem'] === name
        );

        frappe.web_form.doc.problems_addressed.splice(problemIndex, 1);
        getTitleByName(frappe.web_form.doc.problems_addressed);
        deselectProblemUI(name);
      },
    },
    template: `
    <div>
    {% raw %}
    <ul class="list-group mb-3">
      <li 
        v-if="selectedProblems.length == 0"
        class="list-group-item text-muted"
        style="font-size:1.4rem"  
        >
        No problem selected yet
      </li>

      <li 
        v-for="(problem,i) in selectedProblems" 
        class="list-group-item"
        style="font-size:1.4rem"
        >
        {{ problem['title'] }}
        <button type="button" class="close" aria-label="Close" v-on:click="removeTitle(problem['name'])">
          <span aria-hidden="true">&times;</span>
        </button>
      </li>
    </ul>
    {% endraw %}
    </div>
    `,
  });

  const getAvailableSectors = function () {
    frappe.call({
      method: 'contentready_oip.api.get_sector_list',
      args: {},
      callback: function (r) {
        let solution_sectors;
        if (
          frappe.web_form &&
          frappe.web_form.doc &&
          frappe.web_form.doc.sectors
        ) {
          solution_sectors = frappe.web_form.doc.sectors.map((s) => s.sector);
        }

        sectorsComp.solution_sectors = solution_sectors || [];
        sectorsComp.avail_sectors = r.message;
      },
    });
  };

  const sectorsComp = new Vue({
    el: '#sectorsComp',
    data: function () {
      return {
        avail_sectors: [],
        solution_sectors: [],
      };
    },
    beforeCreate: function () {
      // https://vuejs.org/v2/api/#created
      getAvailableSectors();
    },
    methods: {
      updateSectorToDoc: function (sectorClicked) {
        if (!frappe.web_form.doc.sectors) {
          frappe.web_form.doc.sectors = [];
        }

        let index = frappe.web_form.doc.sectors.findIndex(
          (s) => s.sector === sectorClicked
        );

        if (index > 0) {
          frappe.web_form.doc.sectors.splice(index, 1);
        } else {
          frappe.web_form.doc.sectors.push({ sector: sectorClicked });
        }

        getAvailableSectors();
      },
      toggleClass: function (sector) {
        let is_present = this.solution_sectors.find((s) => sector === s);
        if (is_present) {
          return true;
        } else {
          return false;
        }
      },
    },
    template: `
      {% raw %}
        <div class="row">
          <div class="col d-flex flex-wrap">
            <button
              v-for="sector in avail_sectors"
              class="btn btn-lg mb-3 mr-3"
              :title="sector['label']"
              :class="{
                'btn-primary': toggleClass(sector['value']),
                'text-white': toggleClass(sector['value']),
                'btn-outline-primary' :!toggleClass(sector['value'])
              }"
              v-on:click="updateSectorToDoc(sector['value'])"
            >
            {{sector['label']}}
            </button>
          </div>
        </div>
      {% endraw %}
    `,
  });

  const deleteBtnInstance = new Vue({
    el: '#deleteBtn',
    delimiters: ['[[', ']]'],
    data: function () {
      return {
        btnText: this.getBtnText(),
      };
    },
    methods: {
      deleteDocument: async function () {
        const vm = this;
        if (frappe.web_form.doc.name) {
          frappe.confirm(
            'Are you sure you want to delete this solution?',
            async function () {
              // delete document
              await frappe.web_form.delete(frappe.web_form.doc.name);
              clearInterval(autosave);
              $(window).off('beforeunload');
              vm.show_progress_bar();
              // window.history.back();
              return true;
            },
            function () {
              // do nothing
              return false;
            }
          );
        } else {
          window.history.back();
        }
      },
      getBtnText: function () {
        if (frappe.web_form.doc.name) {
          return 'Delete';
        } else {
          return 'Cancel';
        }
      },
      show_progress_bar: function () {
        let i = 0;
        let loader;
        const id = setInterval(frame, 20);

        function frame() {
          if (i >= 100) {
            clearInterval(id);
            i = 0;
            loader.hide();
            window.history.back();
          } else {
            i++;
            loader = frappe.show_progress('Deleting..', i, 100, 'Please wait');
            loader.$body
              .find('.description')
              .css({ 'font-size': '1.6rem', 'padding-top': '.5rem' });
          }
        }
      },
    },
    template: `<button
      v-if="frappe.web_form.doc.is_published !== 1"
      class="btn ml-2 solid-primary-btn btn-danger bg-danger"
      title="delete"
      style="border-color: var(--danger);"
      v-on:click="deleteDocument"
      >
        [[btnText]]
      </button>`,
  });

  // setSolversMultiselectFromDoc();

  // End UI Fixes

  // Start Google Maps Autocomplete
  const gScriptUrl =
    'https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places';
  $.getScript(gScriptUrl, initAutocomplete);
  // End Google Maps Autocomplete

  // Start dropzone.js integration
  const dScriptUrl = 'assets/contentready_oip/js/dropzone.js';
  $.getScript(dScriptUrl, addDropzone);
  // End dropzone.js integration

  // Start Events
  addMatchingProblems();
  // Look for matching problems when text is entered
  $('#problem-search-input').on('keyup', (e) => {
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
  });

  // Set org link field when org title is selected
  $('*[data-fieldname="org"]').on('change', (e) => {
    frappe.web_form.doc.org = e.target.value;
  });

  const autosave = setInterval(autoSaveDraft, 5000);
  $(window).on('beforeunload', function (e) {
    e.preventDefault();
    console.log('auto saving');
    autoSaveDraft();
    return;
  });

  // End Events
});
