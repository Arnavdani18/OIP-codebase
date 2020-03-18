frappe.ready(() => {
    // Start helpers
    showDistanceSelect = () => {
        $('#range-sel-div').show();
        // $('#sector-sel-div').removeClass('offset-md-8').addClass('offset-md-6');
    }
    hideDistanceSelect = () => {
        $('#range-sel-div').hide();
    }
    loadFilters = () => {
        if (frappe.session.user === 'Guest' && localStorage) {
            // guest user so we don't have filters stored on the server.
            // retrieve from localStorage and get our content
            let query_obj = {};
            let lname = localStorage.getItem('filter_location_name');
            if (lname) {
                $('#autocomplete').val(lname);
                showDistanceSelect();
            }
            const lat = localStorage.getItem('filter_location_lat');
            if (lat) {
                query_obj['lat'] = Number(lat);
            }
            const lng = localStorage.getItem('filter_location_lng');
            if (lng) {
                query_obj['lng'] = Number(lng);
            }
            let rng = localStorage.getItem('filter_location_range');
            if (rng) {
                rng = Number(rng);
                query_obj['rng'] = rng;
                $('#range-sel').val(rng);
            }
            let sectors = localStorage.getItem('filter_sectors'); // since we stringify while storing
            if(sectors){
                sectors = JSON.parse(sectors);
                if (!sectors) {
                    sectors = ['all'];
                }
                query_obj['sectors'] = sectors;
                $('#sector-sel').val(`${sectors[0]}`);
            }
            return frappe.utils.make_query_string(query_obj);
        }
    }

    reloadWithParams = () => {
        const qp = loadFilters();
        const clean_url = window.location.href.split('?')[0]; 
        window.location.href = clean_url+qp;
    }

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
    
    clearLocationIfEmpty = () => {
        const location_name = $('#autocomplete').val();
        if (location_name) {
            return false; // don't do anything
        }
        if (frappe.session.user !== 'Guest') {
            // Send this information to backend to store in session
            frappe.call({
                method: 'contentready_oip.api.clear_location_filter',
                args: {
                },
                callback: function(r) {
                    // console.log(r.message);
                    // Reload as index.py will use the session variables to filter problems/solutions shown.
                    window.location.reload();
                }
            });
        } else if (localStorage) {
            localStorage.setItem('filter_location_name', '');
            localStorage.setItem('filter_location_lat', '');
            localStorage.setItem('filter_location_lng', '');
            localStorage.setItem('filter_location_range', '');
            // window.location.reload();
            reloadWithParams();
        }
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
            // window.location.reload();
            reloadWithParams();
        }
    }

    storeRangeFilter = () => {
        const filter_location_range = Number($('#range-sel').val()); // Read range from the select dropdown
        if (frappe.session.user !== 'Guest') {
            // Send this information to backend to store in session
            frappe.call({
                method: 'contentready_oip.api.set_location_filter',
                args: {
                    filter_location_range: filter_location_range,
                },
                callback: function(r) {
                    // console.log(r.message);
                    // Reload as index.py will use the session variables to filter problems/solutions shown.
                    window.location.reload();
                }
            });
        } else if (localStorage) {
            localStorage.setItem('filter_location_range', filter_location_range);
            reloadWithParams();
        }
    }

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
            reloadWithParams();
        }
    }

    // End helpers

    // Start Initialisation - Values are set from session into context if available
    // We can use Jinja2 templates with context here as the JS is compiled server-side.

    {% if frappe.session.user == 'Guest' %}
        const local_qs = loadFilters();
        const window_qs = frappe.utils.get_query_string(window.location.href);
        if (!window_qs && local_qs){
            reloadWithParams();
        }
    {% else %}
        showDistanceSelect();
        $('#autocomplete').val('{{filter_location_name}}');
        $('#range-sel').val('{{filter_location_range}}');
        {% if filter_sectors %}
            $('#sector-sel').val('{{filter_sectors[0]}}');
        {% endif %}
    {% endif %}
    // End Inititialisation
    // Start location filter
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

});