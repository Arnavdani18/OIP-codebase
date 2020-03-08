frappe.ready(async () => {
    // Start Helpers
    let autocomplete;
    // Simple sleep(ms) function from https://stackoverflow.com/a/48882182
    const sleep = m => new Promise(r => setTimeout(r, m));

    // Fix layout - without this, the entire form occupies col-2 due to custom CSS.
    moveDivs = () => {
        $('.section-body > div').each(function() {
            $(this).parent().before(this);
        });
        $(".web-form-wrapper").prepend('<div class="row"><div class="col-md-6" id="add-problem-form"></div><div class="col-md-6" id="parent-problem"></div></div>');
        $('#add-problem-form').append($('.form-layout'));
    }

    createOrgOptions = () => {
        frappe.call({
            method: 'contentready_oip.api.get_orgs_list',
            args: {},
            callback: function(r) {
                frappe.web_form.set_df_property('org', 'options', r.message);
            }
        });
	}
	
	getProblemCard = () => {
		frappe.call({
            method: 'contentready_oip.api.get_problem_card',
            args: {name: frappe.web_form.doc.problem},
            callback: function(r) {
                // r.message[0] is the html
                // r.message[1] is the doc_name in case we need to do any processing client side
                $('#parent-problem').append(r.message[0]);
            }
        });
	}

    hideTables = () => {
        $('*[data-fieldtype="Table"]').hide();
    }

    initAutocomplete = () => {
        // TODO: Use domain settings to retrieve country list
        $('*[data-fieldname="city"]:text').attr("id", "autocomplete").attr('placeholder', 'Search here');
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
    }

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
                if (addressMapping[address_type]['short_name']){
                    frappe.web_form.set_value(addressMapping[address_type]['short_name'], place.address_components[i]['short_name'])
                }
                if (addressMapping[address_type]['long_name']){
                    frappe.web_form.set_value(addressMapping[address_type]['long_name'], place.address_components[i]['long_name'])
                }
            }
        }
        frappe.web_form.set_value('latitude', place.geometry.location.lat());
        frappe.web_form.set_value('longitude', place.geometry.location.lng());
    }

    addFileToDoc = (file) => {
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
            })
        }
    }

    removeFileFromDoc = (file) => {
        frappe.web_form.doc.media = frappe.web_form.doc.media.filter(i => !i.attachment.endsWith(file.name));
    } 

    addDropzone = () => {
        // TODO: Allow user to select an image as featured image
        // disable autoDiscover as we are manually binding the dropzone to a form element
        Dropzone.autoDiscover = false;
        const el = `<form class="dropzone dz-clickable" id='dropzone'><div class="dz-default dz-message"><button class="dz-button" type="button">Drop files here to upload</button></div></form>`;
        $('*[data-fieldname="media"]*[data-fieldtype="Table"]').parent().after(el);
        $('#dropzone').dropzone({
            url: "/api/method/upload_file",
            autoDiscover: false,
            addRemoveLinks: true,
            acceptedFiles: 'image/*',
            headers: {
                'Accept': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token
            },
            init: function() {
                // use this event to add to child table
                this.on("complete", addFileToDoc);
                // use this event to remove from child table
                this.on('removedfile', removeFileFromDoc);
                let myDropzone = this;
                frappe.web_form.doc.media.map(a => {
                    let mockFile = { name: a.attachment, size: a.size };
                    myDropzone.emit("addedfile", mockFile);
                    myDropzone.options.thumbnail.call(myDropzone, mockFile, a.attachment);
                    myDropzone.emit("complete", mockFile);
                });
            }
        });
    }

    submitEnrichmentForm = (is_draft) => {
        frappe.web_form.doc.doctype = 'Enrichment';
        frappe.web_form.doc.user = frappe.session.user;
        frappe.call({
            // method: "frappe.website.doctype.web_form.web_form.accept",
            method: "contentready_oip.api.add_enrichment",
			args: {
                doc: frappe.web_form.doc,
                is_draft: is_draft
			},
            callback: function(r) {
                if (r.message & r.message[1]){
                    window.location.href = r.message[1];    
                } else {
                    window.location.href = '/dashboard';
                }
            }
        });
    }

    showAutoSaveAlert = () => {
        $('#auto-save-alert').removeClass('hidden');
    }

    hideAutoSaveAlert = () => {
        $('#auto-save-alert').addClass('hidden');
    }

    autoSaveDraft = () => {
        frappe.web_form.doc.user = frappe.session.user;
        frappe.call({
            method: "contentready_oip.api.add_enrichment",
			args: {
                doc: frappe.web_form.doc,
                is_draft: true
			},
            callback: function(r) {
                // update local form technical fields so that they are up to date with server values
                // Important: do no update fields on the UI as that will interfere with user experience.
                const keysToCopy = ['creation', 'modified', 'docstatus', 'doctype', 'idx', 'owner', 'modified_by', 'name', 'problem'];
                keysToCopy.map(key => {
                    frappe.web_form.doc[key] = r.message[0][key];
                })
                showAutoSaveAlert();
                setTimeout(hideAutoSaveAlert, 1000);
            }
        });
    }
    
    saveAsDraft = (event) => {
        const is_draft = true;
        submitEnrichmentForm(is_draft);
    }

    publishEnrichment = (event) => {
        const is_draft = false;
        frappe.web_form.doc.is_published = true;
        submitEnrichmentForm(is_draft);
    }

    addActionButtons = () => {
        const saveAsDraftBtn = `<button class="btn btn-sm ml-2" onclick="saveAsDraft()">Save as Draft</button>`;
        const publishBtn = `<button class="btn btn-sm btn-primary ml-2" onclick="publishEnrichment()">Publish</button>`;
        const alert = `<span class="alert alert-primary fade show hidden" role="alert" id="auto-save-alert">Saved</span>`;
        $('.page-header-actions-block').append(alert);
        $('.page-header-actions-block').append(saveAsDraftBtn).append(publishBtn);
    }
    // End Helpers

    // Delay until page is fully rendered
    await sleep(500);

    // Start UI Fixes
    // We hide the default form buttons (using css) and add our own
    addActionButtons();
    moveDivs();
	createOrgOptions();
	getProblemCard();
    // End UI Fixes

    // Start Google Maps Autocomplete
    const gScriptUrl = "https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places";
    $.getScript(gScriptUrl, initAutocomplete);
    // End Google Maps Autocomplete

    // Start dropzone.js integration
    // const scriptPath = "public/js/dropzone.js";
    const dScriptUrl = '/files/dropzone.js';
    $.getScript(dScriptUrl, addDropzone);
    // End dropzone.js integration

    // Start Events
    // Set org link field when org title is selected
    $('*[data-fieldname="org"]').on('change', (e) => {
        frappe.web_form.doc.org = e.target.value;
    });

    setInterval(autoSaveDraft, 10000);

    // End Events

})
