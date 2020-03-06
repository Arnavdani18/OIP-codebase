frappe.ready(async function() {
	// Start helpers
	// Simple sleep(ms) function from https://stackoverflow.com/a/48882182
    const sleep = m => new Promise(r => setTimeout(r, m));

    let orgs = {};

    // Fix layout - without this, the entire form occupies col-2 due to custom CSS.
    moveDivs = () => {
        $('.section-body > div').each(function() {
            $(this).parent().before(this);
        });
    }

    createOrgOptions = () => {
        $('*[data-fieldname="org_title"]').attr('list', 'orgs');
        $('*[data-fieldname="org_title"]').after('<datalist id="orgs"></datalist>');
        frappe.call({
            method: 'contentready_oip.api.get_orgs_list',
            args: {},
            callback: function(r) {
                r.message.map(op => {
                    $('#orgs').append($('<option>', {
                        value: op.label,
                    }));
                    orgs[op.label] = op.value;
                })
            }
        });
    }
    
    createPersonaOptions = () => {
        $('*[data-fieldname="personas"]').before('<label class="control-label" style="padding-right: 0px;">Personas</label><br/><div id="persona-options"></div>');
        frappe.call({
            method: 'contentready_oip.api.get_persona_list',
            args: {},
            callback: function(r) {
                r.message.map(op => {
                    const el = `<div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" id="persona-check-${op.value}" value="${op.value}"><label class="form-check-label" for="persona-check-${op.value}">${op.label}</label></div>`;
                    $('#persona-options').append(el);
                })
                $("[id^=persona-check]").on('click', addPersonaToDoc);
            }
        });
    }

    addPersonaToDoc = (event) => {
        if(!frappe.web_form.doc.personas){
            frappe.web_form.doc.personas = [];
        }
        frappe.web_form.doc.personas.push({'persona': event.target.value});
    }

    createSectorOptions = () => {
        $('*[data-fieldname="sectors"]').before('<label class="control-label" style="padding-right: 0px;">Sectors</label><br/><div id="sector-options"></div>');
        frappe.call({
            method: 'contentready_oip.api.get_sector_list',
            args: {},
            callback: function(r) {
                r.message.map(op => {
                    const el = `<div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" id="sector-check-${op.value}" value="${op.value}"><label class="form-check-label" for="sector-check-${op.value}">${op.label}</label></div>`;
                    $('#sector-options').append(el);
                });
                $("[id^=sector-check]").on('click', addSectorToDoc);
            }
        });
    }

    addSectorToDoc = (event) => {
        if(!frappe.web_form.doc.sectors){
            frappe.web_form.doc.sectors = [];
        }
        frappe.web_form.doc.sectors.push({'sector': event.target.value});
    }
    
    addFileToDoc = (file) => {
        const response = JSON.parse(file.xhr.response);
        frappe.web_form.doc.photo = response.message.file_url;
    }

    removeFileFromDoc = (file) => {
        // console.log('removed', file);
        frappe.web_form.doc.photo = '';
    }

	addDropzone = () => {
        // disable autoDiscover as we are manually binding the dropzone to a form element
        Dropzone.autoDiscover = false;
        const el = `<form class="dropzone dz-clickable" id='dropzone'><div class="dz-default dz-message"><button class="dz-button" type="button">Drop files here to upload</button></div></form>`;
        $('*[data-fieldname="photo"]').after(el);
        $('#dropzone').dropzone({
            url: "/api/method/upload_file",
            autoDiscover: false,
            maxFiles: 1,
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
            }
        });
    }

    addActionButtons = () => {
        const publishBtn = `<button class="btn btn-sm btn-primary ml-2" onclick="publishProfile()">Update</button>`;
        $('.page-header-actions-block').append(publishBtn);
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

    publishProfile = () => {
        frappe.call({
            method: "contentready_oip.api.add_primary_content",
			args: {
				doctype: 'User Profile',
				doc: frappe.web_form.doc,
			},
            callback: function(r) {
                // console.log(r.message);
                if (r.message && r.message.route){
                    window.location.href = r.message.route;    
                } else {
                    window.location.href = '/dashboard';
                }
            }
        });
    }

	// End Helpers
	// Delay until page is fully rendered
    await sleep(500);

    // Start UI Fixes
    // We hide the default form buttons (using css) and add our own
    addActionButtons();
    moveDivs();
    createOrgOptions();
    createPersonaOptions();
    createSectorOptions();

    // Start Google Maps Autocomplete
    const gScriptUrl = "https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places";
    $.getScript(gScriptUrl, initAutocomplete);
    // End Google Maps Autocomplete

	// Start dropzone.js integration
    // const scriptPath = "public/js/dropzone.js";
    const dScriptUrl = '/files/dropzone.js';
    $.getScript(dScriptUrl, addDropzone);
    // End dropzone.js integration
	
	// set email field
	frappe.web_form.set_df_property('user', 'read_only', 1);
	frappe.web_form.set_value('user', frappe.session.user)
	// frappe.web_form.doc.user = frappe.session.user;
})