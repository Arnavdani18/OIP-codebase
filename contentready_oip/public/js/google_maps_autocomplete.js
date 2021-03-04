let autocomplete;

const init_google_maps_autocomplete = () => {
    // TODO: Use domain settings to retrieve country list
    $('*[data-fieldname="city"]:text')
        .attr('id', 'autocomplete')
        .attr('placeholder', 'Search here');
    // Create the autocomplete object, restricting the search predictions to
    // geographical location types.
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'), {
            types: ['(cities)'],
            componentRestrictions: {
                country: 'in'
            }
        }
        // { types: ['(cities)'] }
    );
    // Avoid paying for data that you don't need by restricting the set of
    // place fields that are returned to just the address components.
    // See https://developers.google.com/maps/documentation/javascript/places-autocomplete#add_autocomplete
    autocomplete.setFields(['address_component', 'geometry']);
    // When the user selects an address from the drop-down, populate the
    // address fields in the form.
    autocomplete.addListener('place_changed', fill_address_from_google_maps);
};

const fill_address_from_google_maps = () => {
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