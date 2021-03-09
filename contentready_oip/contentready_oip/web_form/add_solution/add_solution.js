frappe.provide('Vue');

frappe.ready(async () => {
  
  const doctype = 'Solution';

  const mandatory_fields = ['title', 'description', 'city', 'country', 'sectors', 'problems_addressed'];

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
        // console.log('Get Problem Card: ', r);

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


  addProblemToSolvedSet = (name) => {
    if (!frappe.web_form.doc.problems_addressed) {
      frappe.web_form.doc.problems_addressed = [];
    }
    frappe.web_form.doc.problems_addressed.push({
      problem: name,
    });

    vm.getTitleByName(frappe.web_form.doc.problems_addressed);
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


  formatSdgValues = ()=>{
    const sdg_select = $('[data-fieldname="sustainable_development_goal"][data-doctype="Solution"]');
    const currVal = sdg_select.val() ?? []; 
    const newVal = currVal.map(v => ({sustainable_development_goal: v}));
    frappe.web_form.doc.sustainable_development_goal = newVal;
  }

  const style_form_headings = () => {
    $('h6').not(':first').prepend('<hr />');
    $('.form-section-heading').addClass('solution-details-page-subheadings');
  };

  const pageHeadingSection = () => {
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

  insertSelectedProblem = function () {
    $('*[data-fieldname="problems_addressed"]*[data-fieldtype="Table"]')
      .parent()
      .after(`<div id="selectedProblem"></div>`);
  };


  function addAttributesToFields(){
    $('input[data-fieldname="title"]').attr('required',true);
    $('input[data-fieldname="description"]').attr('required',true);
    const websiteInput = $('input[data-fieldname="website"]');

    if (!websiteInput.val()){
      websiteInput.val('https://');
    }

    websiteInput
      .attr('type','url');

    let titleDivForm = $('div[data-fieldname="title"]').parent();
    let wesiteDivForm = $('div[data-fieldname="website"]').parent();
    titleDivForm.validate();
    wesiteDivForm.validate();
  }

  async function prefill_org_field() {
    const orgRef = $('select[data-fieldname="org"]');

    if (!frappe.web_form.doc.org) {
      set_org_from_profile(orgRef);
    } else{
      await sleep(500);
      orgRef.attr('disabled',true);
      
    }
  }

  updateTimeline = ()=>{
    let timeline = $('div[data-fieldname="timeline"] .control-input-wrapper');
    let timelineUnit = $('div[data-fieldname="timeline_unit"]');

    let inputTimline = $('input[data-fieldname="timeline"]');
    let selectTimelineUnit = $('select[data-fieldname="timeline_unit"]');

    // selectTimelineUnit.attr('required',true);

    timeline
      .addClass('input-group')
      .html(inputTimline)
      .append([$('<div/>',{ "class": "input-group-append" }).append(selectTimelineUnit)]);
    
    timelineUnit.hide();
  }

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
  style_form_headings();
  style_fields();
  control_labels();
  pageHeadingSection();
  addMultiselectForSolverTeam();
  appendAttachLink();
  insertSelectedProblem();
  hide_attachments_section();
  addAsterisk(mandatory_fields);
  addAttributesToFields();
  add_help_icon();
  updateTimeline();
  {% include "contentready_oip/public/js/resources_needed.js" %}
  {% include "contentready_oip/public/js/sector_component.js" %}
  prefill_org_field();

  const vm = new Vue({
    name: 'SelectedProblem',
    el: '#selectedProblem',
    delimiters: ['[[', ']]'],
    data() {
      return {
        selectedProblems: [],
        problemAddressed: frappe.web_form.doc.problems_addressed
      };
    },
    methods: {
      removeTitle(name) {
        let problemIndex = frappe.web_form.doc.problems_addressed.findIndex(
          (p) => p['problem'] === name
        );

        frappe.web_form.doc.problems_addressed.splice(problemIndex, 1);
        this.getTitleByName(frappe.web_form.doc.problems_addressed);
        deselectProblemUI(name);
      },
      getTitleByName: async function (problems_addressed_arr=[]) {
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
    
        this.selectedProblems = result;
      }
    },
    mounted(){
      this.$nextTick(function () {
        // Code that will run only after the
        // entire view has been rendered
        this.getTitleByName(frappe.web_form.doc.problems_addressed);
      })
    },
    template: `
    <div>
    <ul class="list-group mb-3">
      <li 
        v-if="selectedProblems.length == 0"
        class="list-group-item text-muted"
        style="font-size:1.4rem"  
        >
        Please select a problem from above
      </li>

      <li 
        v-for="(problem,i) in selectedProblems" 
        class="list-group-item d-flex"
        style="font-size:1.4rem"
        >
        <div style="width: 96%;">[[ problem['title'] ]] </div>
        <button type="button" class="close" title="remove" aria-label="Close" v-on:click="removeTitle(problem['name'])">
          <span aria-hidden="true">&times;</span>
        </button>
      </li>
    </ul>
    </div>
    `,
  });


  // End UI Fixes

  // Start Google Maps Autocomplete
  const gScriptUrl =
    'https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places';
  $.getScript(gScriptUrl, init_google_maps_autocomplete);
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

  // End Events
});
