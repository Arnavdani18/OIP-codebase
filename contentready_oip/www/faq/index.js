frappe.ready(function () {
    const { hash } = window.location

    if (hash) {
        $(hash).collapse('show');
    }else{
        $('.collapse').collapse('show');
    }
})