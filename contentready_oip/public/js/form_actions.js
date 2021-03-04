const submit_form = (is_draft) => {
    let error_message = 'The following fields are mandatory: ';
    let is_incomplete = false;
    mandatory_fields.map(fieldname => {
        if (!frappe.web_form.doc[fieldname] || !frappe.web_form.doc[fieldname].length) {
            error_message += fieldname + ', ';
            is_incomplete = true;
        }
    });
    if (is_incomplete) {
        if (error_message.endsWith(', ')) {
            error_message = error_message.slice(0, error_message.length - 2);
        }
        frappe.msgprint(error_message);
        return false;
    }


    frappe.call({
        method: 'contentready_oip.api.add_primary_content',
        args: {
            doctype: doctype,
            doc: frappe.web_form.doc,
            is_draft: is_draft,
        },
        callback: function (r) {
            // console.log( r );
            $(window).off('beforeunload');
            clearInterval(autoSave);

            if (r.message && r.message.is_published && r.message.route) {
                window.location.href = r.message.route;
            } else {
                window.location.href = '/dashboard';
            }
        },
    });
};


const auto_save_draft = () => {
    console.log('auto save draft: ');
    formatMultiSelectValues();

    if (frappe.web_form.doc.title) {
        frappe.call({
            method: 'contentready_oip.api.add_primary_content',
            args: {
                doctype: doctype,
                doc: frappe.web_form.doc,
                is_draft: true,
            },
            callback: function (r) {
                // console.log(r);
                // update local form technical fields so that they are up to date with server values
                // Important: do no update fields on the UI as that will interfere with user experience.
                const keysToCopy = [
                    'creation',
                    'modified',
                    'docstatus',
                    'doctype',
                    'idx',
                    'owner',
                    'modified_by',
                    'name',
                ];
                keysToCopy.map((key) => {
                    frappe.web_form.doc[key] = r.message[key];
                });

                // update delete btn vue instance
                vue_delete_button.btnText = vue_delete_button.getBtnText();

                // Replace state if exists
                const currQueryParam = window.location['search'];

                if (currQueryParam.includes('new=1')) {
                    window.history.replaceState({}, null, `?name=${r.message['name']}`);
                }

                showAutoSaveAlert();
                setTimeout(hideAutoSaveAlert, 1000);
            },
        });
    }
};

save_as_draft = (event) => {
    frappe.web_form.doc.is_published = false;
    const is_draft = true;
    submit_form(is_draft);
};

publish_content = (event) => {
    frappe.web_form.doc.is_published = true;
    const is_draft = false;
    submit_form(is_draft);
};

add_action_buttons = () => {
    const save_as_draftBtn = `<button class="btn ml-2 btn-outline-primary outline-primary-btn" onclick="save_as_draft()">Save as Draft</button>`;
    const publishBtn = `<button 
      class="btn btn-primary ml-2 solid-primary-btn" 
      onclick="publish_content()"
      >
        Publish
      </button>`;
    const deleteBtnPlaceholder = `
      <div id="deleteBtn"></div>
    `;
    const alert = `<span class="alert alert-primary fade show hidden" role="alert" id="auto-save-alert">Saved</span>`;
    $('.page-header-actions-block').append(alert);
    $('.page-header-actions-block')
        // .append(save_as_draftBtn)
        .append(deleteBtnPlaceholder)
        .append(publishBtn);
};

const vue_delete_button = new Vue({
    name: 'DeleteBtn',
    el: '#deleteBtn',
    delimiters: ['[[', ']]'],
    data: function () {
        return {
            btnText: this.getBtnText(),
        };
    },
    methods: {
        deleteDocument: async function () {
            const vm = this;
            if (frappe.web_form.doc.name) {
                frappe.confirm(
                    `Are you sure you want to delete this ${doctype.toLowerCase()}?`,
                    async function () {
                            // delete document
                            await frappe.web_form.delete(frappe.web_form.doc.name);
                            clearInterval(autoSave);
                            $(window).off('beforeunload');
                            // window.history.back();
                            vm.show_progress_bar();
                            return true;
                        },
                        function () {
                            // do nothing
                            return false;
                        }
                );
            } else {
                window.history.back();
            }
        },
        getBtnText: function () {
            if (frappe.web_form.doc.name) {
                return 'Delete';
            } else {
                return 'Cancel';
            }
        },
        show_progress_bar: function () {
            let i = 0;
            let loader;
            const id = setInterval(frame, 20);

            function frame() {
                if (i >= 100) {
                    clearInterval(id);
                    i = 0;
                    loader.hide();
                    window.history.back();
                } else {
                    i++;
                    loader = frappe.show_progress('Deleting..', i, 100, 'Please wait');
                    loader.$body
                        .find('.description')
                        .css({
                            'font-size': '1.6rem',
                            'padding-top': '.5rem'
                        });
                }
            }
        },
    },
    template: `<button 
      v-if="frappe.web_form.doc.is_published !== 1"
      class="btn ml-2 solid-primary-btn btn-danger bg-danger" 
      title="delete" 
      style="border-color: var(--danger);" 
      v-on:click="deleteDocument"
      >
        [[btnText]]
      </button>`,
});