new Vue({
    name: 'extentComponent',
    el: '[data-fieldtype="Table"][data-fieldname="extent"]',
    delimiters: ['[[', ']]'],
    data(){
        return {
            searchedLocation: '',
            locations : []
        }
    },
    methods: {
        handleSubmit(){
            this.locations.push(this.searchedLocation);
            this.searchedLocation = '';
        },
        removeLocation(idx){
            this.locations.splice(idx,1);
        }
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
                        maxlength="140" data-fieldtype="Data" v-model.trim="searchedLocation" data-fieldname="extent_lookup" placeholder="Search here"
                        data-doctype="Problem" />
                </div>
            </div>
        </form>

        <div class="tags">
        <div class="tag" v-for="location,idx in locations">
            <span>[[location]]</span>
            <button type="button" @click="removeLocation(idx)" class="close ml-2" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
        </div>
    </div> 
    `
})