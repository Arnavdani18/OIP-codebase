$('*[data-fieldname="personas"]').before(
  '<label class="form-group control-label">Personas</label><br/><div id="personasComp"></div>'
);
const personaVueComp = new Vue({
    name: 'Personas',
    el: '#personasComp',
    data() {
      return {
        available_personas: [],
        selected_personas: [],
      };
    },
    created() {
      this.getAvailablePersonas();
    },
    methods: {
      getAvailablePersonas() {
        frappe.call({
          method: 'contentready_oip.api.get_persona_list',
          args: {},
          callback: function (r) {
            let selected_personas;
            if (frappe.web_form.doc.personas) {
              selected_personas = frappe.web_form.doc.personas.map((p) => p.persona);
            }
    
            personaVueComp.selected_personas = selected_personas;
            personaVueComp.available_personas = r.message;
          },
        });
      },
      toggleClass(persona) {
        let is_present = this.selected_personas.find((p) => persona === p);
        if (is_present) {
          return true;
        }
        return false;
      },
      updatePersonaToDoc(personaClicked) {
        if (!frappe.web_form.doc.personas) {
          frappe.web_form.doc.personas = [];
        }
        const updatedPersonas = [...frappe.web_form.doc.personas];

        let index = updatedPersonas.findIndex(
          (s) => s.persona === personaClicked
        );

        if (index > -1) {
          updatedPersonas.splice(index, 1);
        } else {
          updatedPersonas.push({ persona: personaClicked });
        }

        frappe.web_form.doc.personas = updatedPersonas;
        this.getAvailablePersonas();
      },
    },
    template: `
    {% raw %}
    <div class="row">
      <div class="col d-flex flex-wrap">
          <button 
            v-for="persona in available_personas" 
            class="btn btn-lg mb-3 mr-3" 
            :title="persona['label']"
            :class="{
              'btn-primary': toggleClass(persona['value']),
              'text-white': toggleClass(persona['value']),
              'btn-outline-primary' :!toggleClass(persona['value']) 
            }"
            v-on:click="updatePersonaToDoc(persona['value'])"
            >
            {{persona['label']}}
          </button>
      </div>
    </div>
    {% endraw %}
    `,
  });