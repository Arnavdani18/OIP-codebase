$('*[data-fieldname="sectors"]').before(
    '<div id="sectorsComp"></div>'
);

const sectorsComp = new Vue({
    name: 'Sectors',
    el: '#sectorsComp',
    delimiters: ["[[", "]]"],
    data: function () {
        return {
            available_sectors: [],
            selected_sectors: [],
        };
    },
    created: function () {
        // https://vuejs.org/v2/api/#created
        this.getAvailableSectors();
    },
    methods: {
        getAvailableSectors: function () {
            frappe.call({
                method: 'contentready_oip.api.get_sector_list',
                args: {},
                callback: function (r) {
                    let selected_sectors;
                    if (
                        frappe.web_form &&
                        frappe.web_form.doc &&
                        frappe.web_form.doc.sectors
                    ) {
                        selected_sectors = frappe.web_form.doc.sectors.map((s) => s.sector);
                    }

                    sectorsComp.selected_sectors = selected_sectors || [];
                    sectorsComp.available_sectors = [...r.message.sort(sortAlphabetically)];
                    if (['Problem', 'Enrichment'].includes(doctype)) {
                        add_beneficiary_options(selected_sectors ?? []);
                    }
                },
            });
        },

        updateSectorToDoc: function (sectorClicked) {
            if (!frappe.web_form.doc.sectors) {
                frappe.web_form.doc.sectors = [];
            }

            let index = frappe.web_form.doc.sectors.findIndex(
                (s) => s.sector === sectorClicked
            );

            if (index > -1) {
                frappe.web_form.doc.sectors.splice(index, 1);
            } else {
                frappe.web_form.doc.sectors.push({
                    sector: sectorClicked
                });
            }

            this.getAvailableSectors();
        },

        toggleClass: function (sector) {
            let is_present = this.selected_sectors.find((s) => sector === s);
            if (is_present) {
                return true;
            } else {
                return false;
            }
        },

        showHelp: function() {
            frappe.call({
                method: "contentready_oip.api.get_sectors_help",
                args: {},
                callback: function ( r ) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Description'),
                            indicator: 'blue',
                            message: r.message,
                        })
                    }
                }
            });
        }
    },
    template: `
      <div class="pb-2">
            <div class="clearfix">
                <label class="control-label label-styles" style="padding-right: 0px;">
                    Sectors
                    <i class="pl-1 octicon octicon-question text-muted actions" @click="showHelp"></i>
                </label>
            </div>
            
            <div class="row">
            <div class="col d-flex flex-wrap">
            <button 
            v-for="sector in available_sectors"
            class="btn btn-lg btnHover" 
            :title="sector['label']"
            :class="{
                'btn-primary': toggleClass(sector['value']),
                'text-white': toggleClass(sector['value']),
                'btn-outline-primary' :!toggleClass(sector['value']) 
            }"
            v-on:click="updateSectorToDoc(sector['value'])"
            >
            [[sector.label]]
            </button>
            </div>
            </div>
        </div>
    `,
});