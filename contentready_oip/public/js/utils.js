const sortAlphabetically = (a, b) => {
    var labelA = a.label.toUpperCase(); // ignore upper and lowercase
    var labelB = b.label.toUpperCase(); // ignore upper and lowercase
    if (labelA < labelB) {
        return -1;
    }
    if (labelA > labelB) {
        return 1;
    }

    // for equal case
    return 0;
}

// Simple sleep(ms) function from https://stackoverflow.com/a/48882182
const sleep = (m) => new Promise((r) => setTimeout(r, m));

const hideTables = () => {
    $('*[data-fieldtype="Table"]').hide();
};

const hide_attachments_section = () => {
    $('.attachments').hide();
}

const addAsterisk = function (fieldnameArr) {
    for (const field of fieldnameArr) {
        $(`[data-fieldname="${field}"] label`)
            .append(`<span class="text-danger">*</span>`);
    }
}

const showAutoSaveAlert = () => {
    $('#auto-save-alert').removeClass('hidden');
};

const hideAutoSaveAlert = () => {
    $('#auto-save-alert').addClass('hidden');
};

const control_labels = () => {
    $('.control-label').addClass('label-styles');
};

const style_fields = () => {
    $('.input-with-feedback').addClass('field-styles');
};