let copy_vue_filter;

frappe.ready(() => {
  const vue_filter = new Vue({
    el: '#filter-component',
    delimiters: ['[[', ']]'],
    template: '#filter-script',
    data: function () {
      return {
        selected_sector: 'all',
        show_range_filter: true,
        selected_range: 25,
        searched_location: localStorage.getItem('filter_location_name') || '',
        found_location: null,
        qp_page: '',
      };
    },
    created() {
      const existing_sectors = frappe.utils.get_query_params();
      let sectors = localStorage.getItem('filter_sectors');
      let rng = localStorage.getItem('filter_location_range');

      this.selected_range = rng;
      [this.selected_sector] = JSON.parse(sectors) || 'all';

      // check if existing sector is from available_sectors
      if (!this.available_sectors.includes(this.selected_sector)) {
        this.selected_sector = 'all';
      }

      if (existing_sectors && existing_sectors['page']) {
        this.qp_page = existing_sectors['page'];
      }

      const filter_sectors = [this.selected_sector];
      if (localStorage) {
        localStorage.setItem('filter_sectors', JSON.stringify(filter_sectors));
        this.setQueryParam();
      }

      if (!Object.keys(existing_sectors).length) {
        setTimeout(() => window.location.reload(), 500);
      }

      this.showDistanceSelect();
    },
    async mounted() {
      const inputBox = this.$refs.location;
      this.found_location = new google.maps.places.Autocomplete(inputBox, {
        types: ['(cities)'],
        componentRestrictions: { country: 'in' },
      });

      this.found_location.setFields(['address_component', 'geometry']);
      this.found_location.addListener(
        'place_changed',
        this.storeLocationFilter
      );
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
    },
    methods: {
      showDistanceSelect() {
        if (this.searched_location) {
          this.show_range_filter = true;
        } else {
          this.show_range_filter = false;
        }
      },

      storeSectorFilter() {
        const filter_sectors = [this.selected_sector];
        if (localStorage) {
          localStorage.setItem(
            'filter_sectors',
            JSON.stringify(filter_sectors)
          );
          this.setQueryParam();
        }
        window.location.reload();
      },

      clearLocationIfEmpty() {
        if (this.searched_location) {
          return false; // don't do anything
        }
        if (localStorage) {
          localStorage.setItem('filter_location_name', '');
          localStorage.setItem('filter_location_lat', '');
          localStorage.setItem('filter_location_lng', '');
          localStorage.setItem('filter_location_range', '');
          this.setQueryParam();
          window.location.reload();
        }
      },

      storeRangeFilter() {
        console.log(this.selected_range, typeof this.selected_range);
        const filter_location_range = Number(this.selected_range); // Read range from the select dropdown
        if (localStorage) {
          localStorage.setItem('filter_location_range', filter_location_range);
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
        const filter_location_name = name_components.join(', ');
        const filter_location_lat = selectedLocation.latitude;
        const filter_location_lng = selectedLocation.longitude;
        const filter_location_range = Number(this.selected_range); // Read range from the select dropdown
        this.searched_location = filter_location_name;

        if (localStorage) {
          localStorage.setItem('filter_location_name', filter_location_name);
          localStorage.setItem('filter_location_lat', filter_location_lat);
          localStorage.setItem('filter_location_lng', filter_location_lng);
          localStorage.setItem('filter_location_range', filter_location_range);
          this.setQueryParam();
          window.location.reload();
        }
      },

      getLocation() {
        const place = this.found_location.getPlace();
        console.log('place: ', place);

        const addressMapping = {
          locality: {
            long_name: 'city',
          },
          administrative_area_level_1: {
            short_name: 'state_code',
            long_name: 'state',
          },
          country: {
            short_name: 'country_code',
            long_name: 'country',
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
            if (addressMapping[address_type]['short_name']) {
              selectedLocation[addressMapping[address_type]['short_name']] =
                place.address_components[i]['short_name'];
            }
            if (addressMapping[address_type]['long_name']) {
              selectedLocation[addressMapping[address_type]['long_name']] =
                place.address_components[i]['long_name'];
            }
          }
        }
        selectedLocation['latitude'] = place.geometry.location.lat();
        selectedLocation['longitude'] = place.geometry.location.lng();
        return selectedLocation;
      },

      loadFilters() {
        if (localStorage) {
          // guest user so we don't have filters stored on the server.
          // retrieve from localStorage and get our content
          let query_obj = {};
          const lat = localStorage.getItem('filter_location_lat');
          if (lat) {
            query_obj['lat'] = Number(lat);
          }
          const lng = localStorage.getItem('filter_location_lng');
          if (lng) {
            query_obj['lng'] = Number(lng);
          }
          let rng = localStorage.getItem('filter_location_range');
          if (rng) {
            rng = Number(rng);
            query_obj['rng'] = rng;
            this.selected_range = rng;
          }

          let search_str = localStorage.getItem('search_query');
          if (search_str && window.location.pathname.includes('search')) {
            query_obj['key'] = search_str;
          }

          let sectors = localStorage.getItem('filter_sectors');
          if (!sectors) {
            sectors = JSON.stringify(['all']);
          }
          if (sectors) {
            sectors = JSON.parse(sectors); // since we stringify while storing
            query_obj['sectors'] = sectors;
            this.selected_sector = sectors[0];
          }
          return query_obj;
        }
      },
    },
  });

  function passFilterContext() {
    copy_vue_filter = vue_filter;
  }

  passFilterContext();
});
