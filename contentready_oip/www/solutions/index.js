frappe.ready(() => {
    if (frappe.session.user === 'Guest') {
        // guest user so we don't have filters stored on the server.
        // retrieve from localStorage and get our content
        if (localStorage) {
            const filter_sectors = JSON.parse(localStorage.getItem('filter_sectors')); // since we stringify while storing
            const filter_location_lat = Number(localStorage.getItem('filter_location_name'));
            const filter_location_lng = Number(localStorage.getItem('filter_location_lng'));
            const filter_location_range = Number(localStorage.getItem('filter_location_range'));
            frappe.call({
                method: 'contentready_oip.api.get_filtered_content',
                args: {
                    doctype: 'Solution',
                    filter_location_lat: filter_location_lat,
                    filter_location_lng: filter_location_lng,
                    filter_location_range: filter_location_range,
                    filter_sectors: filter_sectors,
                    html: true
                },
                callback: function(r) {
                    r.message.map(el => {
                        el = `<div class="col-md-6">`+el+`</div>`;
                        $('#solutions-container').append(el);
                    })
                    $('#solutions-count').text(r.message.length);
                }
            });
        }
    }
})