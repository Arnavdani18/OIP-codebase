$('*[data-fieldname="sectors"]').before(
    '<label class="control-label" style="padding-right: 0px;">Sectors</label><br/><div id="sectorsComp"></div>'
);

const sectorsComp = new Vue({
    name: 'Sectors',
    el: '#sectorsComp',
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
        showDescription: function(description) {
            frappe.msgprint({
                title: __('Description'),
                indicator: 'blue',
                message: description
            })
        }
    },
    template: `
      {% raw %}
        <div class="row">
          <div class="col d-flex flex-wrap">
            <div class="btn-group" role="group" v-for="sector in available_sectors">
                <button 
                class="btn btn-lg btnHover" 
                :title="sector['label']"
                :class="{
                    'btn-primary': toggleClass(sector['value']),
                    'text-white': toggleClass(sector['value']),
                    'btn-outline-primary' :!toggleClass(sector['value']) 
                }"
                v-on:click="updateSectorToDoc(sector['value'])"
                >
                {{sector['label']}}
                </button>
                <button type="button" class="btn btn-outline-primary" @click="showDescription(sector['description'])"><i class="octicon octicon-question actions"></i></button>
            </div>
          </div>
        </div>
      {% endraw %}
    `,
});