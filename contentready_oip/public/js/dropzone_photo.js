const add_photo_to_doc = (file) => {
    if (file.xhr) {
        const response = JSON.parse(file.xhr.response);
        frappe.web_form.doc.photo = response.message.file_url;
    }
};

const remove_photo_from_doc = (file) => {
    frappe.web_form.doc.photo = '';
};

const addDropzone = () => {
    // disable autoDiscover as we are manually binding the dropzone to a form element
    Dropzone.autoDiscover = false;
    const el = `<form class="dropzone dz-clickable d-flex align-items-center justify-content-center flex-wrap mb-4" style="font-size:var(--f14);" id='dropzone'><div class="dz-default dz-message"><button class="dz-button" type="button">Drop files here to upload</button></div></form>`;
    $('*[data-fieldname="photo"]').after(el);
    $('#dropzone').dropzone({
        url: '/api/method/contentready_oip.api.upload_file',
        autoDiscover: false,
        maxFiles: 1,
        addRemoveLinks: true,
        acceptedFiles: 'image/*',
        headers: {
            Accept: 'application/json',
            'X-Frappe-CSRF-Token': frappe.csrf_token,
        },
        init: function () {
            // use this event to add to child table
            this.on('complete', (file) => {
                const response = JSON.parse(file.xhr.response);
                if (response.message === false) {
                    this.removeFile(file);
                    frappe.msgprint('Explicit content detected. This file will not be uploaded.');
                } else {
                    add_photo_to_doc(file);
                }
            });
            // use this event to remove from child table
            this.on('removedfile', remove_photo_from_doc);
            if (frappe.web_form.doc.photo) {
                const file_url = frappe.web_form.doc.photo;
                let mockFile = {
                    name: file_url,
                    size: null
                };
                this.displayExistingFile(mockFile, file_url);
            }
        },
    });
};