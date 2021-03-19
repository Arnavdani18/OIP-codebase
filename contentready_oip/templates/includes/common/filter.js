let copy_vue_filter;

frappe.ready(() => {
  const vue_filter = new Vue({
    name: "filters",
    el: "#filter-component",
    delimiters: ["[[", "]]"],
    template: "#filter-script",
    data: function () {
      return {
        key: "",
        qp_page: "",
        selected_service_category: "",
        selected_range: null,
        show_beneficiary: true,
        searched_location: "",
        google_map_instance: null,
        sdg_multiselect_instance: null,
        sector_multiselect_instance: null,
        beneficiary_multiselect_instance: null,
        persona_multiselect_instance: null,
        selected_range: 25,
        range_options: [0, 25, 50, 100, 200],
        suggested_titles: [],
        scope: {},
        selected_sectors: [],
      };
    },
    created() {
      this.selected_range = localStorage.getItem("filter_location_range");
      this.searched_location = localStorage.getItem("filter_location_name");
    },
    mounted() {
      // Sector, SDG, Beneficiary, Persona multiselect initialization
      this.initializeMultiselect();

      const { location } = this.$refs;
      const options = {
        types: ["(cities)"],
        componentRestrictions: { country: "in" },
      };
      this.google_map_instance = new google.maps.places.Autocomplete(
        location,
        options
      );
      this.google_map_instance.setFields(["address_component", "geometry"]);
      this.google_map_instance.addListener(
        "place_changed",
        this.storeLocationFilter
      );

      const query_params = frappe.utils.get_query_params();

      const { key, sectors , sdgs, beneficiaries, personas, service_category } = query_params;
      
      this.key = key;

      if (sectors) {
        const parsed_sectors = JSON.parse(sectors);
        this.prefillMultiselect(parsed_sectors, this.sector_multiselect_instance);
      }
      
      if (sdgs) {
        const parsed_sdgs = JSON.parse(sdgs);
        this.prefillMultiselect(parsed_sdgs,this.sdg_multiselect_instance);
      }
      
      if (beneficiaries) {
        const parsed_beneficiaries = JSON.parse(beneficiaries);
        this.prefillMultiselect(parsed_beneficiaries, this.beneficiary_multiselect_instance);
      }

      if (personas) {
        const parsed_personas = JSON.parse(personas);
        this.prefillMultiselect(parsed_personas, this.persona_multiselect_instance);
      }

      this.selected_service_category = service_category;

    },
    computed: {
      available_sectors() {
        return JSON.parse(`{{ available_sectors | json }}`) || [];
      },
      available_sdg() {
        return JSON.parse(`{{ available_sdg | json }}`) || [];
      },
      available_beneficiaries() {
        return JSON.parse(`{{ available_beneficiaries | json }}`) || [];
      },
      available_personas() {
        return JSON.parse(`{{ available_personas | json }}`) || [];
      },
      available_service_categories() {
        return JSON.parse(`{{ available_service_categories | json }}`) || [];
      },
    },
    methods: {

      get_search_suggestions() {
        if (this.key) {
          this.storeSectorFilter();
          this.storeBeneficiaryFilter();
          this.storePersonaFilter();
          this.storeSdgFilter();
          frappe.call({
            method: "contentready_oip.api.get_suggested_titles",
            args: { text: this.key, scope: this.loadFilters() },
            callback: function ( r ) {
              this.suggested_titles = r.message;
              this.$forceUpdate();
            }.bind(this)
          });
        } else {
          return [];
        }

      },

      initializeMultiselect() {
        // init Sector
        this.sector_multiselect_instance = document.multiselect("#sector-sel");
        // init SDG
        this.sdg_multiselect_instance = document.multiselect("#sdg-sel");
        // init Beneficiary
        this.beneficiary_multiselect_instance = document.multiselect(
          "#beneficiary-sel"
        );
        // init Personas
        this.persona_multiselect_instance = document.multiselect(
          "#persona-sel"
        );

        $("#sector-sel_input, #sdg-sel_input, #beneficiary-sel_input, #persona-sel_input")
          .addClass("filter-select m-0 filter-input");

        $("#sector-sel_input")
          .attr("placeholder", "Sector Filter");
        $("#sdg-sel_input")
          .attr("placeholder", "SDG Filter");
        $("#beneficiary-sel_input")
          .attr("placeholder", "Beneficiary Filter");

        $("#persona-sel_input")
          .attr("placeholder", "Persona Filter");

        $(".multiselect-dropdown-arrow").attr(
          "style",
          "display:none !important;"
        );
      },

      prefillMultiselect(values, instance) {
        if (!values || !instance) {
          return;
        }

        values.forEach((val) => instance.select(val));
      },

      storeSdgFilter(){
        const sdg_list = $("#sdg-sel").val() ?? [];
        if(typeof sdg_list === 'string'){
          localStorage.setItem("filter_sdgs", sdg_list);
        }
        localStorage.setItem("filter_sdgs", JSON.stringify(sdg_list));
      },
      
      storeBeneficiaryFilter(){
        const beneficiary_list = $("#beneficiary-sel").val() ?? [];
        if (typeof beneficiary_list === 'string') {
          localStorage.setItem("filter_beneficiaries", beneficiary_list);
        }
        localStorage.setItem("filter_beneficiaries", JSON.stringify(beneficiary_list));
      },

      storePersonaFilter(){
        const persona_list = $("#persona-sel").val() ?? [];
        if (typeof persona_list === 'string') {
          localStorage.setItem("filter_personas", persona_list);
        }
        localStorage.setItem("filter_personas", JSON.stringify(persona_list));
      },

      storeSectorFilter() {
        const sectors_list = $("#sector-sel").val() ?? [];
        if(typeof sectors_list === 'string'){
          localStorage.setItem("filter_sectors", sectors_list);
        }
        localStorage.setItem("filter_sectors", JSON.stringify(sectors_list));
      },

      storeServiceCategoryFilter() {
        const service_category = $("#service-category-sel").val() ?? '';
        localStorage.setItem("filter_service_category", service_category);
      },

      clearLocationIfEmpty() {
        if (this.searched_location) {
          return false; // don't do anything
        }
        if (localStorage) {
          localStorage.setItem("filter_location_name", "");
          localStorage.setItem("filter_location_lat", "");
          localStorage.setItem("filter_location_lng", "");
          localStorage.setItem("filter_location_range", "");
        }
      },

      storeRangeFilter() {
        const filter_location_range = Number(this.selected_range); // Read range from the select dropdown
        if (localStorage) {
          localStorage.setItem("filter_location_range", filter_location_range);
        }
      },

      setQueryParam() {
        const filter_query = this.loadFilters();
        let page_query = {};
        if (this.qp_page) {
          page_query = { page: this.qp_page };
        }

        let qp;
        if (Object.keys(filter_query).length) {
          const combined_query = { ...filter_query, ...page_query };

          qp = frappe.utils.make_query_string(combined_query);
          window.history.replaceState({}, null, qp);
        }
      },

      storeLocationFilter() {
        let selectedLocation;
        try {
          selectedLocation = this.getLocation(); // Read location from the autocomplete field
          if (!Object.keys(selectedLocation).length) {
            return false;
          }
        } catch (e) {
          console.trace(e);
          return false;
        }
        
        let name_components = [
          selectedLocation.city,
          selectedLocation.state,
          selectedLocation.country,
        ];
        name_components = name_components.filter((c) => c); // remove falsy values
        const filter_location_name = name_components.join(", ");
        const filter_location_lat = selectedLocation.latitude;
        const filter_location_lng = selectedLocation.longitude;
        const filter_location_range = Number(this.selected_range); // Read range from the select dropdown
        this.searched_location = filter_location_name;

        if (localStorage) {
          localStorage.setItem("filter_location_name", filter_location_name);
          localStorage.setItem("filter_location_lat", filter_location_lat);
          localStorage.setItem("filter_location_lng", filter_location_lng);
          localStorage.setItem("filter_location_range", filter_location_range);
        }
      },

      getLocation() {
        const place = this.google_map_instance.getPlace();

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
        // Get each component of the address from the place details,
        // and then fill-in the corresponding field on the form.
        const selectedLocation = {};

        if (place && !place.address_components) {
          return selectedLocation;
        }

        for (let i = 0; i < place.address_components.length; i++) {
          const address_type = place.address_components[i].types[0];
          if (addressMapping[address_type]) {
            if (addressMapping[address_type]["short_name"]) {
              selectedLocation[addressMapping[address_type]["short_name"]] =
                place.address_components[i]["short_name"];
            }
            if (addressMapping[address_type]["long_name"]) {
              selectedLocation[addressMapping[address_type]["long_name"]] =
                place.address_components[i]["long_name"];
            }
          }
        }
        selectedLocation["latitude"] = place.geometry.location.lat();
        selectedLocation["longitude"] = place.geometry.location.lng();
        return selectedLocation;
      },

      loadFilters() {
        if (localStorage) {
          // guest user so we don't have filters stored on the server.
          // retrieve from localStorage and get our content
          let query_obj = {};
          const lat = localStorage.getItem("filter_location_lat");
          if (lat) {
            query_obj["lat"] = Number(lat);
          }
          const lng = localStorage.getItem("filter_location_lng");
          if (lng) {
            query_obj["lng"] = Number(lng);
          }
          let rng = localStorage.getItem("filter_location_range");
          if (rng) {
            rng = Number(rng);
            query_obj["rng"] = rng;
            this.selected_range = rng;
          }
          let loc_name = localStorage.getItem("filter_location_name");
          if (loc_name) {
            query_obj["loc_name"] = loc_name;
          }

          if (this.key && window.location.pathname.includes("search")) {
            query_obj["key"] = this.key;
          }

          let sectors = localStorage.getItem("filter_sectors");
          if (sectors) {
            query_obj["sectors"] = JSON.parse(sectors);
          }

          let sdgs = localStorage.getItem("filter_sdgs");
          if (sdgs) {
            query_obj['sdgs'] = JSON.parse(sdgs);
          }
          
          let beneficiaries = localStorage.getItem("filter_beneficiaries");
          if (beneficiaries) {
            query_obj['beneficiaries'] = JSON.parse(beneficiaries);
          }

          let personas = localStorage.getItem("filter_personas");
          if (personas) {
            query_obj['personas'] = JSON.parse(personas);
          }

          let service_category = localStorage.getItem("filter_service_category");
          query_obj['service_category'] = service_category;
          
          return query_obj;
        }
      },
      
      searchWithFilters() {
        this.storeSectorFilter();
        this.storeBeneficiaryFilter();
        this.storePersonaFilter();
        this.storeSdgFilter();
        this.storeServiceCategoryFilter();
        this.setQueryParam();
        window.location.reload();
      },

      resetFilter() {
        localStorage.setItem("filter_location_name", "");
        localStorage.setItem("filter_location_lat", "");
        localStorage.setItem("filter_location_lng", "");
        localStorage.setItem("filter_location_range", "");
        localStorage.setItem("filter_beneficiaries", "");
        localStorage.setItem("filter_personas", "");
        localStorage.setItem("filter_sdgs", "");
        localStorage.setItem("filter_sectors", "");
        localStorage.setItem("filter_service_category", "");
        this.selected_service_category = '';

        this.setQueryParam();
        window.location.reload();
      },
    },
  });

  function passFilterContext() {
    copy_vue_filter = vue_filter;
  }

  passFilterContext();
});
