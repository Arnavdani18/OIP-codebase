let copy_vue_filter;

frappe.ready(() => {
  const vue_filter = new Vue({
    name: "filters",
    el: "#filter-component",
    delimiters: ["[[", "]]"],
    template: "#filter-script",
    data: function () {
      return {
        selected_sector: ["all"],
        show_range_filter: false,
        selected_range: 25,
        searched_location: localStorage.getItem("filter_location_name") || "",
        found_location: null,
        qp_page: "",
        sdg_multiselect_instance: null,
        sector_multiselect_instance: null,
        beneficiary_multiselect_instance: null,
      };
    },
    created() {
      this.showDistanceSelect();
      let rng = localStorage.getItem("filter_location_range");
      this.selected_range = rng;
    },
    mounted() {
      // Sector, SDG, Beneficiary multiselect initialization
      this.initializeMultiselect();

      const { location } = this.$refs;
      const options = {
        types: ["(cities)"],
        componentRestrictions: { country: "in" },
      };
      this.found_location = new google.maps.places.Autocomplete(
        location,
        options
      );
      this.found_location.setFields(["address_component", "geometry"]);
      this.found_location.addListener(
        "place_changed",
        this.storeLocationFilter
      );

      const query_params = frappe.utils.get_query_params();
      const { sectors } = query_params;

      const parsed_sectors = JSON.parse(sectors) ?? ["all"];
      this.prefillMultiselect(parsed_sectors, this.sector_multiselect_instance);
    },
    watch: {
      searched_location(currentVal, oldVal) {
        if (currentVal) {
          this.show_range_filter = true;
        } else {
          this.show_range_filter = false;
        }
      },
    },
    computed: {
      available_sectors() {
        return JSON.parse(`{{available_sectors | json}}`) || [];
      },
      available_sdg() {
        return JSON.parse(`{{available_sdg | json}}`) || [];
      },
      available_beneficiaries() {
        return JSON.parse(`{{available_beneficiaries | json}}`) || [];
      },
    },
    methods: {
      initializeMultiselect() {
        this.sector_multiselect_instance = document.multiselect("#sector-sel");
        this.sdg_multiselect_instance = document.multiselect("#sdg-sel");
        this.beneficiary_multiselect_instance = document.multiselect(
          "#beneficiary-sel"
        );

        $("#sector-sel_input, #sdg-sel_input, #beneficiary-sel_input")
          .addClass("filter-select m-0 filter-input")
          .attr("placeholder", "Sector Filter");

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
      showDistanceSelect() {
        if (this.searched_location) {
          this.show_range_filter = true;
        } else {
          this.show_range_filter = false;
        }
      },

      storeSectorFilter() {
        const sectors_list = $("#sector-sel").val() ?? [];

        // sectors filter cannot be null, set to default
        if (!sectors_list.length) {
          document.multiselect("#sector-sel").select("all");
          sectors_list.push("all");
        }

        const filter_sectors = JSON.stringify(sectors_list);
        localStorage.setItem("filter_sectors", filter_sectors);
        this.setQueryParam();
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
          this.setQueryParam();
          window.location.reload();
        }
      },

      storeRangeFilter() {
        console.log(this.selected_range, typeof this.selected_range);
        const filter_location_range = Number(this.selected_range); // Read range from the select dropdown
        if (localStorage) {
          localStorage.setItem("filter_location_range", filter_location_range);
          this.setQueryParam();
          window.location.reload();
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
        console.log(selectedLocation);
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
          this.setQueryParam();
          window.location.reload();
        }
      },

      getLocation() {
        const place = this.found_location.getPlace();
        console.log("place: ", place);

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

          let search_str = localStorage.getItem("search_query");
          if (search_str && window.location.pathname.includes("search")) {
            query_obj["key"] = search_str;
          }

          let sectors = localStorage.getItem("filter_sectors");
          if (!sectors) {
            sectors = JSON.stringify(["all"]);
          }
          if (sectors) {
            sectors = JSON.parse(sectors); // since we stringify while storing
            query_obj["sectors"] = sectors;
            this.selected_sector = sectors;
          }
          return query_obj;
        }
      },
      applyFilter() {
        console.log("apply filters");
        this.storeSectorFilter();
        window.location.reload();
      },
      resetFilter() {
        console.log("reset filters");
      },
    },
  });

  function passFilterContext() {
    copy_vue_filter = vue_filter;
  }

  passFilterContext();
});
