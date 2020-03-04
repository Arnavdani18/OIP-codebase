frappe.ready(() => {
    if (frappe.session.user === 'Guest') {
        // guest user so we don't have filters stored on the server.
        // retrieve from localStorage and get our content
        if (localStorage) {
            const sectors = JSON.parse(localStorage.getItem('sectors')); // since we stringify while storing
            const location = JSON.parse(localStorage.getItem('location'));
            frappe.call({
                method: 'contentready_oip.api.get_filtered_content',
                args: {
                    doctype: 'Problem', 
                    location: location,
                    sectors: sectors,
                    guest: true,
                    html: true
                },
                callback: function(r) {
                    r.message.map(el => {
                        el = `<div class="col-md-6">`+el+`</div>`;
                        $('#problems-container').append(el);
                    })
                    $('#problems-count').text(r.message.length);
                }
            });
        }
    }
})