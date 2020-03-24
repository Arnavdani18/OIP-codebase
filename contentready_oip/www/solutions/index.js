frappe.ready(() => {
    goToPage = (page) => {
        const filter_query = loadFilters();
        const existing_query = frappe.utils.get_query_params();
        const page_query = {page: page};
        let qp;
        if (Object.keys(filter_query).length) {
            const combined_query = {...existing_query, ...filter_query, ...page_query };
            // console.log(combined_query, filter_query);
            qp = frappe.utils.make_query_string(combined_query);
            console.log(qp);
        }
        if (qp) {
            const clean_url = window.location.href.split('?')[0]; 
            window.location.href = clean_url+qp;
        }
    }
    
})