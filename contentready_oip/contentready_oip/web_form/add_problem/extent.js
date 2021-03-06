new Vue({
    name: "extentComponent",
    el: '[data-fieldtype="Table"][data-fieldname="extent"]',
    delimiters: ["[[", "]]"],
    data() {
      return {
        searchedLocation: "",
        googleMap: null,
      };
    },
    methods: {
      handleSubmit() {
        this.searchedLocation = "";
      },
      removeLocation(idx) {
        frappe.web_form.doc.extent.splice(idx, 1);
        this.$forceUpdate();
      },
      formatAddress() {
        const formattedAddress = {};
        const place = this.googleMap.getPlace();
  
        const addressMapping = {
          locality: {
            long_name: "city",
          },
          administrative_area_level_1: {
            short_name: "state_code",
            long_name: "state",
          },
          country: {
            short_name: "country_code",
            long_name: "country",
          },
        };
  
        for (let i = 0; i < place.address_components.length; i++) {
          const address_type = place.address_components[i].types[0];
          if (addressMapping[address_type]) {
            if (addressMapping[address_type]["short_name"]) {
              formattedAddress[addressMapping[address_type]["short_name"]] =
                place.address_components[i]["short_name"];
            }
            if (addressMapping[address_type]["long_name"]) {
              formattedAddress[addressMapping[address_type]["long_name"]] =
                place.address_components[i]["long_name"];
            }
          }
        }
  
        formattedAddress["latitude"] = place.geometry.location.lat();
        formattedAddress["longitude"] = place.geometry.location.lng();
  
        this.addNewLocation(formattedAddress);
      },
      addNewLocation(location) {
        const currLocations = frappe.web_form.doc.extent ?? [];
        currLocations.push(location);
        frappe.web_form.doc.extent = [...currLocations];
        this.$forceUpdate();
      },
    },
    mounted() {
      const { inputRef } = this.$refs;
      const options = {
        types: ["(cities)"],
        componentRestrictions: { country: "in" },
      };
      this.googleMap = new window.google.maps.places.Autocomplete(
        inputRef,
        options
      );
      this.googleMap.setFields(["address_component", "geometry"]);
      this.googleMap.addListener("place_changed", this.formatAddress);
    },
    template: `
        <div class="form-group">
            <div class="clearfix">
                <label class="control-label label-styles" style="padding-right: 0px;">
                    Extent
                </label>
            </div>
            <form @submit.prevent="handleSubmit">
                <div class="control-input-wrapper">
                    <div class="control-input">
                        <input type="text" autocomplete="off" class="input-with-feedback form-control bold field-styles"
                            maxlength="140" data-fieldtype="Data" ref="inputRef" v-model.trim="searchedLocation" data-fieldname="extent_lookup" placeholder="Search here"
                            data-doctype="Problem" />
                    </div>
                </div>
            </form>
    
            <div class="tags">
            <div class="tag" v-for="loc,idx in frappe.web_form.doc.extent">
                <span class="text-capitalize">[[loc.city]], [[loc.state]], [[loc.country]]</span>
                <button type="button" @click="removeLocation(idx)" style="font-size:1.9rem;" class="close ml-2" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            </div>
        </div> 
        `,
  });
  