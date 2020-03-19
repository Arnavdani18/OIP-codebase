frappe.ready(() => {
    // if (frappe.session.user === 'Guest') {
    //     // guest user so we don't have filters stored on the server.
    //     // retrieve from localStorage and get our content
    //     if (localStorage) {
    //         const filter_sectors = JSON.parse(localStorage.getItem('filter_sectors')); // since we stringify while storing
    //         const lat = localStorage.getItem('filter_location_lat');
    //         let filter_location_lat;
    //         if (lat) {
    //             filter_location_lat = Number(lat);
    //         } else {
    //             filter_location_lat = null;
    //         }
    //         const lng = localStorage.getItem('filter_location_lng');
    //         let filter_location_lng;
    //         if (lng) {
    //             filter_location_lng = Number(lng);
    //         } else {
    //             filter_location_lng = null;
    //         }
    //         const l_range = localStorage.getItem('filter_location_range');
    //         let filter_location_range;
    //         if (l_range) {
    //             filter_location_range = Number(l_range);
    //         } else {
    //             filter_location_range = null;
    //         }
    //         console.log(filter_sectors, filter_location_lat, filter_location_lng, filter_location_range);
    //     }
    // }
})