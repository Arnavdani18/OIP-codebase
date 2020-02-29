// console.log('actions js');

frappe.ready(() => {
    actionsMap = {
        like: {
            api: 'add_like',
        }
    }
    
    processAction = (action, doctype, name, successCallback) => {
        console.log(action, doctype, name, successCallback);
        frappe.call({
            method: 'contentready_oip.api.'+actionsMap[action].api,
            args: {doctype: doctype, name: name},
            callback: (r) => {
                const success = r.message[0];
                const msg = r.message[1];
                if (success) {
                    successCallback();
                    // actionsMap[action].success();
                    // console.log(msg);
                    // frappe.call({
                    //     method: 'contentready_oip.api.get_doc_by_type_name',
                    //     args: {doctype: doctype, name: name},
                    //     callback: (r) => {
                    //         console.log(r);
                    //     }
                    // });
                } else {
                    if (actionsMap[action].error) {
                        actionsMap[action].error(); 
                    } else {
                        frappe.throw(msg);
                        // actionsMap[action].success(); 
                        successCallback();
                    }
                    // actionsMap[action].error();
                    // frappe.call({
                    //     method: 'contentready_oip.api.get_doc_by_type_name',
                    //     args: {doctype: doctype, name: name},
                    //     callback: (r) => {
                    //         console.log(r);
                    //     }
                    // });
                }
            }
        });
    }
})
