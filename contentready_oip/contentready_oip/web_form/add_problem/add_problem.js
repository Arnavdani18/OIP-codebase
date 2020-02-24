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
		$(".web-form-wrapper").prepend('<div class="row"><div class="col-md-6" id="add-problem-form"></div><div class="col-md-6" id="similar-problems"><h3>Similar Problems</h3></div></div>');
		$('#add-problem-form').append($('.form-layout'));
		$('#similar-problems').append('<div></div>');
	}

	initAutocomplete = () => {
		$('*[data-fieldname="city"]:text').attr("id", "autocomplete").attr('placeholder', 'Search here');
		// Create the autocomplete object, restricting the search predictions to
		// geographical location types.
		autocomplete = new google.maps.places.Autocomplete(
			document.getElementById('autocomplete'),
			{ types: ['(cities)'], componentRestrictions: {country: 'in'} }
			// TODO: Use domain settings to retrieve country list
		);
		// Avoid paying for data that you don't need by restricting the set of
		// place fields that are returned to just the address components.
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

	lookForSimilarProblems = async () => {
		await sleep(500);
		// Look up title again - user could have typed something since the event was triggered.
		const text = $('*[data-fieldname="title"]:text').val().trim();
		frappe.call({
            method: 'contentready_oip.contentready_oip.web_form.add_problem.add_problem.get_similar_problems',
            args: {
                text: text,
            },
            callback: function(r) {
				console.log(r.message);
				// Add similar problems to div
				$('#similar-problems').empty();
				r.message.map(el => {
					$('#similar-problems').append(el);
				});

            }
        });
		
	}
	// End Helpers
	
	// Delay until page is fully rendered
	await sleep(500);

	// Start UI Fixes
	moveDivs();
	// End UI Fixes

	// Start Google Maps Autocomplete
	const scriptUrl = "https://maps.googleapis.com/maps/api/js?key=AIzaSyAxSPvgric8Zn54pYneG9NondiINqdvb-w&libraries=places";
	$.getScript(scriptUrl, initAutocomplete);
	// End Google Maps Autocomplete

	// Events
	// $('*[data-fieldname="title"]:text').on('change', lookForSimilarProblems);
	$('*[data-fieldname="title"]:text').on('keyup', (e) => {
		const value = e.target.value.trim();
		if (value.length && value.length % 3 === 0) {
			lookForSimilarProblems();
		}
	});
	
})