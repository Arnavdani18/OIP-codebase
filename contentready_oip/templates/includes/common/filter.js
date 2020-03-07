frappe.ready(() => {
    // Start helpers
    showDistanceSelect = () => {
        $('#sector-sel-div').removeClass('offset-md-8').addClass('offset-md-6');
        $('#range-sel-div').show();
    }
    hideDistanceSelect = () => {
        $('#range-sel-div').hide();
    }
    // End helpers

    // Start Initialisation - Values are set from session into context if available
    // We can use Jinja2 templates with context here as the JS is compiled server-side.
    {% if (filter_location_name and filter_location_range) %}
        // console.log(`{{selectedLocation}}`);
        showDistanceSelect();
        $('#autocomplete').val('{{filter_location_name}}');
        $('#range-sel').val(`{{filter_location_range}}`);
    {% else %}
        if (localStorage) {
            const filter_location_name = localStorage.getItem('filter_location_name');
            let filter_location_range = 25;
            const stored_location_range = localStorage.getItem('filter_location_range');
            // will be null if never set
            if (stored_location_range != null) {
                filter_location_range = Number(stored_location_range);
            }
            if (filter_location_name) {
                showDistanceSelect();
                $('#autocomplete').val(`${filter_location_name}`);
                $('#range-sel').val(`${filter_location_range}`);
            }
        }
    {% endif %}

    {% if (filter_sectors) %}
        // console.log(`{{filter_sectors}}`);
        $('#sector-sel').val('{{filter_sectors[0]}}');
    {% else %}
    console.log('reading from localstorage');
        if (localStorage) {
            console.log('reading from localstorage');
            let filter_sectors = JSON.parse(localStorage.getItem('filter_sectors'));
            console.log(filter_sectors);
            if (!filter_sectors) {
                filter_sectors = ['all']
            }
            $('#sector-sel').val(`${filter_sectors[0]}`);
        }
    {% endif %}
    // End Inititialisation

    // Start Location Filter
    getLocation = () => {
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
        const selectedLocation = {};
        for (let i = 0; i < place.address_components.length; i++) {
            const address_type = place.address_components[i].types[0];
            if (addressMapping[address_type]) {
                if (addressMapping[address_type]['short_name']) {
                    selectedLocation[
                        addressMapping[address_type]['short_name']
                    ] = place.address_components[i]['short_name'];
                }
                if (addressMapping[address_type]['long_name']) {
                    selectedLocation[
                        addressMapping[address_type]['long_name']
                    ] = place.address_components[i]['long_name'];
                }
            }
        }
        // selectedLocation['name'] = place.name;
        selectedLocation['latitude'] = place.geometry.location.lat();
        selectedLocation['longitude'] = place.geometry.location.lng();
        showDistanceSelect();
        return selectedLocation;
    }
    storeLocationFilter = () => {
        let selectedLocation;
        try {
            selectedLocation = getLocation(); // Read location from the autocomplete field
        } catch(e) {
            console.trace(e);
            return false;
        }
        // console.log(selectedLocation);
        let name_components = [selectedLocation.city, selectedLocation.state, selectedLocation.country];
        name_components = name_components.filter(c => c); // remove falsy values
        const filter_location_name = name_components.join(', ');
        const filter_location_lat = selectedLocation.latitude;
        const filter_location_lng = selectedLocation.longitude;
        const filter_location_range = Number($('#range-sel').val()); // Read range from the select dropdown
        if (frappe.session.user !== 'Guest') {
            // Send this information to backend to store in session
            frappe.call({
                method: 'contentready_oip.api.set_location_filter',
                args: {
                    filter_location_name: filter_location_name,
                    filter_location_lat: filter_location_lat,
                    filter_location_lng: filter_location_lng,
                    filter_location_range: filter_location_range,
                },
                callback: function(r) {
                    // console.log(r.message);
                    // Reload as index.py will use the session variables to filter problems/solutions shown.
                    window.location.reload();
                }
            });
        } else if (localStorage) {
            localStorage.setItem('filter_location_name', filter_location_name);
            localStorage.setItem('filter_location_lat', filter_location_lat);
            localStorage.setItem('filter_location_lng', filter_location_lng);
            localStorage.setItem('filter_location_range', filter_location_range);
            window.location.reload();
        }
    }
    const autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'),
        // { types: ['(cities)'], componentRestrictions: {country: 'in'} }
        { types: ['(cities)'] }
        // TODO: Use domain settings to retrieve country list
    );
    // Specify fields to retrieve from the Google Maps API - cost implications.
    autocomplete.setFields(['address_component', 'geometry']);
    // Specify callback to run everytime location is changed by user.
    autocomplete.addListener('place_changed', storeLocationFilter);
    // Select all text on click so that it's easier to edit.
    $('#autocomplete').on('click', () => {
        $('#autocomplete').select();
    });
    // End Location Filter

    // Start Sector filter
    storeSectorFilter = (evt) => {
        const filter_sectors = [evt.target.value];
        if (frappe.session.user !== 'Guest') {
            frappe.call({
                method: 'contentready_oip.api.set_sector_filter',
                args: {
                    filter_sectors: filter_sectors, // TODO: Replace with evt.target.value once multiselect sector is implemented.
                },
                callback: function(r) {
                    // console.log(r.message);
                    // Reload as index.py will use the session variables to filter problems/solutions shown.
                    window.location.reload();
                }
            });
        } else if (localStorage) {
            localStorage.setItem('filter_sectors', JSON.stringify(filter_sectors));
            window.location.reload();
        }
    }
    // End Sector Filter
});