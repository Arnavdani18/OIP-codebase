const add_media_to_doc = (file) => {
    if (file.xhr) {
        const response = JSON.parse(file.xhr.response);
        const file_url = response.message.file_url;
        if (!frappe.web_form.doc.media) {
            frappe.web_form.doc.media = [];
        }
        const m = {
            attachment: file_url,
            size: file.size,
            type: file.type
        };
        frappe.web_form.doc.media.push(m);
        show_feature_button(file);
    }
};

const remove_media_from_doc = (file) => {
    if (frappe.web_form.doc.media) {
        frappe.web_form.doc.media = frappe.web_form.doc.media.filter(
            (i) => !i.attachment.endsWith(file.name)
        );
    }
};

const show_feature_button = (file) => {
    $(file['previewElement']).append(`<div id="featureBtn"></div>`);
    {% include 'public/custom_templates/featureBtn.js' %}
};

const toggle_add_more = (len) => {
    const addMore = $('#add-multiple-files').parent();
    if (len) {
      addMore.addClass('dz-preview').removeClass('hidden');
    } else {
      addMore.addClass('hidden').removeClass('dz-preview');
    }
};

const addDropzone = () => {
    // d-flex align-items-center justify-content-center flex-wrap
    // disable autoDiscover as we are manually binding the dropzone to a form element
    Dropzone.autoDiscover = false;
    const el = `{% include "public/custom_templates/dz.html" %}`;
    $('*[data-fieldname="media"]*[data-fieldtype="Table"]').parent().after(el);
    $('#dropzone').dropzone({
        url: '/api/method/contentready_oip.api.upload_file',
        autoDiscover: false,
        addRemoveLinks: true,
        acceptedFiles: 'image/*,video/*',
        clickable: ['#dropzone', '#add-multiple-files'],
        headers: {
            Accept: 'application/json',
            'X-Frappe-CSRF-Token': frappe.csrf_token,
        },
        init: function () {
            let myDropzone = this;
            // use this event to add to child table
            this.on('complete', (file) => {
                const response = JSON.parse(file.xhr.response);
                if (response.message === false) {
                    this.removeFile(file);
                    frappe.msgprint('Explicit content detected. This file will not be uploaded.');
                } else {
                    add_media_to_doc(file);
                }
            });
            // use this event to remove from child table
            this.on('removedfile', function (file) {
                toggle_add_more(myDropzone.files.length);
                remove_media_from_doc(file);
            });

            if (frappe.web_form.doc.media) {
                toggle_add_more(frappe.web_form.doc.media.length);
                frappe.web_form.doc.media.map((a) => {
                    let mockFile = {
                        name: a.attachment,
                        size: a.size
                    };
                    myDropzone.displayExistingFile(mockFile, a.attachment);
                });
            }

            this.on('sending', function () {
                toggle_add_more(myDropzone.files.length);
            });

            const addMutipleFilesBtn = document.querySelector(
                '#add-multiple-files'
            );
            if (addMutipleFilesBtn) {
                addMutipleFilesBtn.onclick = function (e) {
                    e.preventDefault();
                };
            }

            const clearDzBtn = document.querySelector('button#clear-dropzone');
            if (clearDzBtn) {
                clearDzBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    myDropzone.removeAllFiles();
                    toggle_add_more(myDropzone.files.length);
                });
            }
        },
    });
};

