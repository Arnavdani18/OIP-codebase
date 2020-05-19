frappe.provide( 'Vue' );

frappe.ready( async () => {
  // Start Helpers
  let autocomplete;
  // Simple sleep(ms) function from https://stackoverflow.com/a/48882182
  const sleep = m => new Promise( r => setTimeout( r, m ) );

  // Fix layout - without this, the entire form occupies col-2 due to custom CSS.
  moveDivs = () => {
    $( '.section-body > div' ).each( function () {
      $( this )
        .parent()
        .before( this );
    } );
    $( '.web-form-wrapper' ).prepend(
      '<div class="row"><div class="col-md-6" id="add-problem-form"></div><div class="col-md-6"><h3>Similar Problems</h3><span id="similar-problems"></span></div></div>'
    );
    $( '#add-problem-form' ).append( $( '.form-layout' ) );
    $( '#similar-problems' ).append( '<div></div>' );
  };

  createOrgOptions = () => {
    frappe.call( {
      method: 'contentready_oip.api.get_orgs_list',
      args: {},
      callback: function ( r ) {
        frappe.web_form.set_df_property( 'org', 'options', r.message );
      }
    } );
  };

  // createSectorOptions = () => {
  //   $('*[data-fieldname="sectors"]').before(
  //     '<label class="control-label" style="padding-right: 0px;">Sectors</label><br/><div id="sector-options"></div>'
  //   );
  //   frappe.call({
  //     method: 'contentready_oip.api.get_sector_list',
  //     args: {},
  //     callback: function (r) {
  //       let problem_sectors;
  //       if (frappe.web_form.doc.sectors) {
  //         problem_sectors = frappe.web_form.doc.sectors.map(s => s.sector);
  //       }
  //       r.message.map(op => {
  //         let has_sector = false;
  //         if (problem_sectors) {
  //           has_sector = problem_sectors.indexOf(op.value) !== -1;
  //         }
  //         const el = `<div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" id="sector-check-${op.value}" value="${op.value}"><label class="form-check-label" for="sector-check-${op.value}">${op.label}</label></div>`;
  //         $('#sector-options').append(el);
  //         $(`#sector-check-${op.value}`).attr('checked', has_sector);
  //       });
  //       $('[id^=sector-check]').on('click', addSectorToDoc);
  //     }
  //   });
  // };

  // addSectorToDoc = (event) => {
  //   if (!frappe.web_form.doc.sectors) {
  //     frappe.web_form.doc.sectors = [];
  //   }
  //   frappe.web_form.doc.sectors.push({ sector: event.target.value });
  // };

  hideTables = () => {
    $( '*[data-fieldtype="Table"]' ).hide();
  };

  initAutocomplete = () => {
    // TODO: Use domain settings to retrieve country list
    $( '*[data-fieldname="city"]:text' )
      .attr( 'id', 'autocomplete' )
      .attr( 'placeholder', 'Search here' );
    // Create the autocomplete object, restricting the search predictions to
    // geographical location types.
    autocomplete = new google.maps.places.Autocomplete(
      document.getElementById( 'autocomplete' ),
      { types: [ '(cities)' ], componentRestrictions: { country: 'in' } }
      // { types: ['(cities)'] }
    );
    // Avoid paying for data that you don't need by restricting the set of
    // place fields that are returned to just the address components.
    // See https://developers.google.com/maps/documentation/javascript/places-autocomplete#add_autocomplete
    autocomplete.setFields( [ 'address_component', 'geometry' ] );
    // When the user selects an address from the drop-down, populate the
    // address fields in the form.
    autocomplete.addListener( 'place_changed', fillInAddress );
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
    for ( let i = 0; i < place.address_components.length; i++ ) {
      const address_type = place.address_components[ i ].types[ 0 ];
      if ( addressMapping[ address_type ] ) {
        if ( addressMapping[ address_type ][ 'short_name' ] ) {
          frappe.web_form.set_value(
            addressMapping[ address_type ][ 'short_name' ],
            place.address_components[ i ][ 'short_name' ]
          );
        }
        if ( addressMapping[ address_type ][ 'long_name' ] ) {
          frappe.web_form.set_value(
            addressMapping[ address_type ][ 'long_name' ],
            place.address_components[ i ][ 'long_name' ]
          );
        }
      }
    }
    frappe.web_form.set_value( 'latitude', place.geometry.location.lat() );
    frappe.web_form.set_value( 'longitude', place.geometry.location.lng() );
  };

  lookForSimilarProblems = async () => {
    // Delay as the user is probably still typing
    await sleep( 500 );
    // Look up title again - user could have typed something since the event was triggered.
    const text = $( '*[data-fieldname="title"]:text' )
      .val()
      .trim();
    if ( text.length > 3 ) {
      frappe.call( {
        method: 'contentready_oip.api.search_content_by_text',
        args: {
          doctype: 'Problem',
          text: text
        },
        callback: function ( r ) {
          // Add similar problems to div
          $( '#similar-problems' ).empty();
          r.message.map( el => {
            $( '#similar-problems' ).append( el );
          } );
        }
      } );
    } else if ( text.length === 0 ) {
      $( '#similar-problems' ).empty();
    }
  };

  addFileToDoc = ( file ) => {
    attachFeaturedBtn( file );

    // Since we are showing previously added, remote
    if ( file.xhr ) {
      const response = JSON.parse( file.xhr.response );
      const file_url = response.message.file_url;
      if ( !frappe.web_form.doc.media ) {
        frappe.web_form.doc.media = [];
      }
      frappe.web_form.doc.media.push( {
        attachment: file_url,
        size: file.size,
        type: file.type
      } );
    }
  };

  attachFeaturedBtn = ( file ) => {
    if ( !frappe.web_form.doc.media ) {
      frappe.web_form.doc.media = [];
    }

    let found = frappe.web_form.doc.media.find( m => m.attachment.endsWith( file.name ) );

    $( file[ 'previewElement' ] ).append( `
    <div class="d-flex justify-content-center" data-feature="${file.name }">
      <button class="close" title="featured photo">
        <i class="fa ${found && found[ 'is_featured' ] === 1 ? 'fa-bookmark' : 'fa-bookmark-o' }" aria-hidden="true"></i>
      </button>
    </div>`);

    $( `div[data-feature="${ file.name }"]` ).on( 'click', function ( e ) {
      e.preventDefault();
      let currentMediaName = $( this ).data( 'feature' );
      let currentMediaIndex = frappe.web_form.doc.media.findIndex( m => m.attachment.endsWith( currentMediaName ) );

      for ( const section of $( 'div[data-feature]' ) ) {
        const mediaName = $( section ).data( 'feature' )
        if ( mediaName === currentMediaName ) {
          current_item = frappe.web_form.doc.media[ currentMediaIndex ];
          if ( current_item[ 'is_featured' ] ) {
            current_item[ 'is_featured' ] = false;
            $( section )
              .find( 'i' )
              .addClass( 'fa-bookmark-o' )
              .removeClass( 'fa-bookmark' );
          } else {
            current_item[ 'is_featured' ] = true;
            $( section )
              .find( 'i' )
              .addClass( 'fa-bookmark' )
              .removeClass( 'fa-bookmark-o' );
          }

        } else {
          let index = frappe.web_form.doc.media.findIndex( m => m.attachment.endsWith( mediaName ) );
          frappe.web_form.doc.media[ index ][ 'is_featured' ] = false;
          $( section )
            .find( 'i' )
            .addClass( 'fa-bookmark-o' )
            .removeClass( 'fa-bookmark' );

        }
      }
    } )
  }

  removeFileFromDoc = ( file ) => {
    frappe.web_form.doc.media = frappe.web_form.doc.media.filter(
      i => !i.attachment.endsWith( file.name )
    );
  };

  addDropzone = () => {
    // TODO: Allow user to select an image as featured image
    // disable autoDiscover as we are manually binding the dropzone to a form element

    // d-flex align-items-center justify-content-center flex-wrap
    Dropzone.autoDiscover = false;
    const el = `{% include "public/custom_templates/dz.html" %}`;
    $( '*[data-fieldname="media"]*[data-fieldtype="Table"]' )
      .parent()
      .after( el );
    $( '#dropzone' ).dropzone( {
      url: '/api/method/upload_file',
      autoDiscover: false,
      addRemoveLinks: true,
      acceptedFiles: 'image/*,video/*',
      clickable: [ '#dropzone', '#add-multiple-files' ],
      headers: {
        Accept: 'application/json',
        'X-Frappe-CSRF-Token': frappe.csrf_token
      },
      init: function () {
        let myDropzone = this;
        // use this event to add to child table
        this.on( 'complete', addFileToDoc );
        // use this event to remove from child table
        this.on( 'removedfile', function ( file ) {
          toggleAddMore( myDropzone.files.length );
          removeFileFromDoc( file );
        } );

        if ( frappe.web_form.doc.media ) {
          toggleAddMore( frappe.web_form.doc.media.length );
          frappe.web_form.doc.media.map( a => {
            let mockFile = { name: a.attachment, size: a.size };
            myDropzone.displayExistingFile( mockFile, a.attachment );
          } );
        }

        this.on( 'sending', function () {
          toggleAddMore( myDropzone.files.length );
        } )

        const addMutipleFilesBtn = document.querySelector( "#add-multiple-files" );
        if ( addMutipleFilesBtn ) {
          addMutipleFilesBtn.onclick = function ( e ) {
            e.preventDefault();
          };
        }

        const clearDzBtn = document.querySelector( "button#clear-dropzone" );
        if ( clearDzBtn ) {
          clearDzBtn.addEventListener( "click", function ( e ) {
            e.preventDefault();
            myDropzone.removeAllFiles();
            toggleAddMore( myDropzone.files.length );
          } );
        }
      }
    } );
  };

  toggleAddMore = ( len ) => {
    const addMore = $( '#add-multiple-files' ).parent();
    if ( len ) {
      addMore.addClass( 'dz-preview' ).removeClass( 'hidden' );
    } else {
      addMore.addClass( 'hidden' ).removeClass( 'dz-preview' );
    }
  }

  submitProblemForm = ( is_draft ) => {
    frappe.call( {
      method: 'contentready_oip.api.add_primary_content',
      args: {
        doctype: 'Problem',
        doc: frappe.web_form.doc,
        is_draft: is_draft
      },
      callback: function ( r ) {
        // console.log(r);
        if ( r.message && r.message.is_published && r.message.route ) {
          window.location.href = r.message.route;
        } else {
          window.location.href = '/dashboard';
        }
      }
    } );
  };

  showAutoSaveAlert = () => {
    $( '#auto-save-alert' ).removeClass( 'hidden' );
  };

  hideAutoSaveAlert = () => {
    $( '#auto-save-alert' ).addClass( 'hidden' );
  };

  autoSaveDraft = () => {
    if ( frappe.web_form.doc.title ) {
      frappe.call( {
        method: 'contentready_oip.api.add_primary_content',
        args: {
          doctype: 'Problem',
          doc: frappe.web_form.doc,
          is_draft: true
        },
        callback: function ( r ) {
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
          keysToCopy.map( key => {
            frappe.web_form.doc[ key ] = r.message[ key ];
          } );

          // update delete btn vue instance
          deleteBtnInstance.btnText = deleteBtnInstance.getBtnText();

          // Replace state if exists
          const currQueryParam = window.location[ 'search' ];

          if ( currQueryParam.includes( "new=1" ) ) {
            window.history.replaceState( {}, null, `?name=${ r.message[ 'name' ] }` );
          }

          showAutoSaveAlert();
          setTimeout( hideAutoSaveAlert, 1000 );
        }
      } );
    }
  };

  saveAsDraft = ( event ) => {
    frappe.web_form.doc.is_published = false;
    const is_draft = true;
    submitProblemForm( is_draft );
  };

  publishProblem = ( event ) => {
    frappe.web_form.doc.is_published = true;
    const is_draft = false;
    submitProblemForm( is_draft );
  };

  addActionButtons = () => {
    const saveAsDraftBtn = `<button class="btn ml-2 btn-outline-primary outline-primary-btn" onclick="saveAsDraft()">Save as Draft</button>`;
    const publishBtn = `<button 
      class="btn btn-primary ml-2 solid-primary-btn" 
      onclick="publishProblem()"
      >
        Publish
      </button>`;
    const deleteBtnPlaceholder = `
      <div id="deleteBtn"></div>
    `
    const alert = `<span class="alert alert-primary fade show hidden" role="alert" id="auto-save-alert">Saved</span>`;
    $( '.page-header-actions-block' ).append( alert );
    $( '.page-header-actions-block' )
      // .append(saveAsDraftBtn)
      .append( deleteBtnPlaceholder )
      .append( publishBtn );
  };

  const problemDetails = () => {
    $( '.form-layout' ).prepend(
      `<h2 class="form-layout-problem-details">1. Problem Details</h2>`
    );
  };

  const controlLabels = () => {
    $( '.control-label' ).addClass( 'label-styles' );
  };

  const styleFields = () => {
    $( '.input-with-feedback' ).addClass( 'field-styles' );
  };

  const styleFormHeadings = () => {
    $( '.form-section-heading' ).prepend( '<hr/>' );
    $( '.form-section-heading' ).addClass( 'problem-details-page-subheadings' );
  };

  const pageHeadingSection = () => {
    // $('button:contains("Save as Draft")')
    //   .removeClass('btn-sm')
    //   .addClass('btn-outline-primary outline-primary-btn');

    // $('button:contains("Publish")')
    //   .removeClass('')
    //   .addClass('solid-primary-btn');

    $( '#auto-save-alert' ).addClass( 'auto-saved' );
    $( '.page-header-actions-block' ).addClass( 'd-flex align-items-center' );
    $( '.page-header' )
      .addClass( 'd-flex align-items-center' )
      .css( { 'width': '70%' } )
      .prepend(
        '<img src="/files/problem_dark.svg" class="add-problem-icon" />'
      );

    const problemTitle = $( '.page-header h2' ).text();
    $( '.page-header h2' )
      .addClass( 'text-truncate' )
      .attr( 'title', problemTitle )
      .css( { 'margin-bottom': '0px' } );

    $( '#introduction' ).addClass( 'd-none' );
  };

  const appendAttachLink = () => {
    let btn = `
    <div class="attach-links-section pattern1">
      <button class="btn btn-primary solid-primary-btn mb-3" >Attach video link</button>
      <ul class="list-group"></ul>
    </div>`;

    $( 'h6:contains("Media")' )
      .parent()
      .append( btn );

    // if media attachment already exist
    displayAttachedLinks();

    $( '.attach-links-section button' ).click( function () {
      let links = prompt( 'Please enter links from Youtube or Vimeo. Separate multiple links with commas.' );
      if ( links ) {
        if ( !frappe.web_form.doc.media ) {
          frappe.web_form.doc.media = []
        }

        let media = frappe.web_form.doc.media;
        let linkArr = links.split( ',' );

        linkArr.forEach( link => {
          // check if link exist
          let idxExist = media.findIndex( mediaObj => {
            return mediaObj[ 'attachment' ] === link;
          } )


          if ( checkMedialUrl( link ) && idxExist < 0 ) {
            media.push( { attachment: link, type: 'link' } );
          } else if ( idxExist > -1 ) {
            alert( 'Provided link already exists.' )
          } else {
            alert( "Please enter links from Youtube or Vimeo only." );
          }
        } );

        displayAttachedLinks();
      }
    } );
  };


  const checkMedialUrl = function ( url ) {
    const regex = /(youtube|youtu|vimeo)\.(com|be)\/((watch\?v=([-\w]+))|(video\/([-\w]+))|(projects\/([-\w]+)\/([-\w]+))|([-\w]+))/;

    if ( url.match( regex ) ) {
      return true
    }
    else {
      return false
    }
  }

  const displayAttachedLinks = () => {
    if ( !frappe.web_form.doc.media ) {
      return;
    }
    let media = frappe.web_form.doc.media;

    let linkArr = [];
    $( '.attach-links-section ul' ).empty();
    if ( media && media.length ) {
      linkArr = media.filter( mediaObj => mediaObj[ 'type' ] === 'link' );
    }

    for ( const [ index, link ] of linkArr.entries() ) {
      let unorderedList = `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        ${link[ 'attachment' ] }
        <button type="button" class="close" id="removeBtn-${index + 1 }" data-attachment="${ link.attachment }" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
      </li>`;


      $( '.attach-links-section ul' ).append( unorderedList );
      let btnId = `#removeBtn-${ index + 1 }`;

      // remove button event listener
      $( btnId )
        .click( function () {
          let linkText = $( this ).attr( 'data-attachment' );

          if ( media ) {
            let foundIndex = media.findIndex( ( linkObj ) => {
              return linkObj[ 'attachment' ] === linkText;
            } )

            if ( foundIndex > -1 ) {
              media.splice( foundIndex, 1 );
              displayAttachedLinks();
            }
          }
        } );
    }
  };

  const addSection = function () {
    // For Sectors
    $( '*[data-fieldname="sectors"]' ).before(
      '<label class="control-label" style="padding-right: 0px;">Sectors</label><br/><div id="sectorsComp"></div>'
    );
  }

  function hideAttachmentsSection () {
    $( '.attachments' ).hide();
  }

  // End Helpers

  // Delay until page is fully rendered
  while ( !frappe.web_form.fields ) {
    await sleep( 1000 );
  }

  // Start UI Fixes
  $( '*[data-doctype="Web Form"]' ).wrap( '<div class="container pt-5"></div>' );
  // We hide the default form buttons (using css) and add our own
  addActionButtons();
  moveDivs();
  createOrgOptions();
  // createSectorOptions();
  addSection();
  problemDetails();
  controlLabels();
  styleFields();
  styleFormHeadings();
  pageHeadingSection();
  appendAttachLink();
  hideAttachmentsSection();
  // End UI Fixes


  const getAvailableSectors = function () {
    frappe.call( {
      method: 'contentready_oip.api.get_sector_list',
      args: {},
      callback: function ( r ) {
        let problem_sectors;
        if ( frappe.web_form && frappe.web_form.doc && frappe.web_form.doc.sectors ) {
          problem_sectors = frappe.web_form.doc.sectors.map( s => s.sector );
        }

        sectorsComp.problem_sectors = problem_sectors || [];
        sectorsComp.avail_sectors = r.message
      }
    } );
  }

  const sectorsComp = new Vue( {
    el: '#sectorsComp',
    data: function () {
      return {
        avail_sectors: [],
        problem_sectors: []
      }
    },
    beforeCreate: function () {
      // https://vuejs.org/v2/api/#created
      getAvailableSectors();
    },
    methods: {
      updateSectorToDoc: function ( sectorClicked ) {
        if ( !frappe.web_form.doc.sectors ) {
          frappe.web_form.doc.sectors = [];
        }

        let index = frappe.web_form.doc.sectors.findIndex( s => s.sector === sectorClicked );

        if ( index > 0 ) {
          frappe.web_form.doc.sectors.splice( index, 1 )
        } else {
          frappe.web_form.doc.sectors.push( { sector: sectorClicked } );
        }

        getAvailableSectors();
      },
      toggleClass: function ( sector ) {
        let is_present = this.problem_sectors.find( s => sector === s );
        if ( is_present ) {
          return true
        } else {
          return false;
        }
      }
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
    `
  } );

  const deleteBtnInstance = new Vue( {
    el: '#deleteBtn',
    delimiters: [ '[[', ']]' ],
    data: function () {
      return {
        btnText: this.getBtnText()
      }
    },
    methods: {
      deleteDocument: async function () {
        const vm = this;
        if ( frappe.web_form.doc.name ) {
          frappe.confirm( 'Are you sure you want to delete this problem?',
            async function () {
              // delete document
              await frappe.web_form.delete( frappe.web_form.doc.name );
              clearInterval( autoSave );
              $( window ).off( "beforeunload" );
              // window.history.back();
              vm.show_progress_bar();
              return true;
            },
            function () {
              // do nothing
              return false;
            } );
        } else {
          window.history.back();
        }
      },
      getBtnText: function () {
        if ( frappe.web_form.doc.name ) {
          return 'Delete';
        } else {
          return 'Cancel';
        }
      },
      show_progress_bar: function () {
        let i = 0;
        let loader;
        const id = setInterval( frame, 20 );

        function frame () {
          if ( i >= 100 ) {
            clearInterval( id );
            i = 0;
            loader.hide();
            window.history.back();
          } else {
            i++;
            loader = frappe.show_progress( 'Deleting..', i, 100, 'Please wait' );
            loader.$body.find( '.description' ).css( { "font-size": "1.6rem", "padding-top": ".5rem" } );
          }
        }
      }
    },
    template: `<button 
      v-if="frappe.web_form.doc.is_published !== 1"
      class="btn ml-2 solid-primary-btn btn-danger bg-danger" 
      title="delete" 
      style="border-color: var(--danger);" 
      v-on:click="deleteDocument"
      >
        [[btnText]]
      </button>`
  } );

  // Start Google Maps Autocomplete
  const gScriptUrl =
    'https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places';
  $.getScript( gScriptUrl, initAutocomplete );
  // End Google Maps Autocomplete

  // Start dropzone.js integration
  const dScriptUrl = 'assets/contentready_oip/js/dropzone.js';
  $.getScript( dScriptUrl, addDropzone );
  // End dropzone.js integration

  // Start Events
  // Look for similar problems when title is entered
  $( '*[data-fieldname="title"]:text' ).on( 'keyup', e => {
    const value = e.target.value.trim();
    if ( value.length && value.length % 3 === 0 ) {
      lookForSimilarProblems();
    } else if ( value.length === 0 ) {
      $( '#similar-problems' ).empty();
    }
  } );
  // Set org link field when org title is selected
  $( '*[data-fieldname="org"]' ).on( 'change', e => {
    frappe.web_form.doc.org = e.target.value;
  } );

  const autoSave = setInterval( autoSaveDraft, 5000 );
  $( window ).on( "beforeunload", function ( e ) {
    e.preventDefault();
    autoSaveDraft();
    return;
  } );

  // End Events
} );
