frappe.ready(() => {
    // Start helpers
    showDistanceSelect = () => {
        $('#sector-sel-div').removeClass('offset-md-8').addClass('offset-md-6');
        $('#distance-sel-div').show();
    }
    hideDistanceSelect = () => {
        $('#distance-sel-div').hide();
    }
    // End helpers

    // Start Initialisation - Set values from session if available
    // We can use Jinja2 templates with context here as the JS is compiled server-side.
    {% if (selectedLocation and selectedLocation.center) %}
        // console.log({{selectedLocation}});
        showDistanceSelect();
        $('#autocomplete').val('{{selectedLocation.center.city}}, {{selectedLocation.center.state}}, {{selectedLocation.center.country}}');
        $('#distance-sel').val('{{selectedLocation.distance}}');
    {% endif %}

    {% if selectedSectors %}
        // console.log({{selectedSectors}});
        $('#sector-sel').val('{{selectedSectors[0]}}');
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
        selectedLocation['name'] = place.name;
        selectedLocation['latitude'] = place.geometry.location.lat();
        selectedLocation['longitude'] = place.geometry.location.lng();
        showDistanceSelect();
        return selectedLocation;
    }
    setSessionLocationFilter = () => {
        let selectedLocation = {};
        try {
            selectedLocation = getLocation(); // Read location from the autocomplete field
        } catch(e) {
            console.trace(e);
        }
        const distance = Number($('#distance-sel').val()); // Read distance from the select dropdown
        // Send this information to backend to store in session
        frappe.call({
            method: 'contentready_oip.templates.includes.common.filter.set_location_filter',
            args: {
                selectedLocation: selectedLocation,
                distance: distance,
            },
            callback: function(r) {
                // console.log(r.message);
                window.location.reload();
            }
        });
    }
    const autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'),
        { types: ['(cities)'], componentRestrictions: {country: 'in'} }
        // TODO: Use domain settings to retrieve country list
    );
    // Specify fields to retrieve from the Google Maps API - cost implications.
    autocomplete.setFields(['address_component', 'geometry', 'name']);
    // Specify callback to run everytime location is changed by user.
    autocomplete.addListener('place_changed', setSessionLocationFilter);
    // End Location Filter

    // Start Sector filter
    setSessionSectorFilter = (evt) => {
        frappe.call({
            method: 'contentready_oip.templates.includes.common.filter.set_sector_filter',
            args: {
                sectors: [evt.target.value], // TODO: Replace with evt.target.value once multiselect sector is implemented.
            },
            callback: function(r) {
                // console.log(r.message);
                window.location.reload();
            }
        });
    }
    // End Sector Filter
});