new Vue({
  el: `#featureBtn`,
  name: 'featureBtn',
  data() {
    return {
      featured: false,
      media: frappe.web_form.doc.media,
    };
  },
  methods: {
    handleClick() {
      this.media.find((m) => {
        if (m.attachment.endsWith(file.name)) {
          m['is_featured'] = Number(!m['is_featured']);
        } else {
          m['is_featured'] = 0;
        }
      });

      this.setDefaultFeatured();
      autoSaveDraft();
    },

    setDefaultFeatured() {
      let is_featured = this.media.some((m) => m['is_featured'] === 1);

      if (!is_featured) {
        this.media[0]['is_featured'] = 1;
        autoSaveDraft();
      }
    },
  },
  created() {
    if (!this.media) {
      frappe.web_form.doc.media = [];
    }

    this.media.forEach((m) => {
      if (m.attachment.endsWith(file.name)) {
        this.featured = m['is_featured'];
      }
    });

    this.setDefaultFeatured();
  },
  watch: {
    media: {
      handler: function (currentVal) {
        currentVal.forEach((m) => {
          if (m.attachment.endsWith(file.name)) {
            this.featured = m['is_featured'];
          }
        });
      },
      deep: true,
    },
  },
  template: `
    <div class="d-flex justify-content-center">
      <button class="close" title="featured photo" @click.prevent="handleClick">
        <i class="bookmark" v-if="featured">
          {% include 'public/svg/bookmark.svg'%}
        </i>
        <i class="bookmark" v-if="!featured">
          {% include 'public/svg/bookmark-outline.svg'%}
        </i>
      </button>
    </div>
    `,
});
