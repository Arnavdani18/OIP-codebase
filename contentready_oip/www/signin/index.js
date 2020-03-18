{% include "public/js/global.js" %}

frappe.ready(async () => {
    (function () {
        'use strict';
        window.addEventListener('load', function () {
            // Fetch all the forms we want to apply custom Bootstrap validation styles to
            var forms = document.getElementsByClassName('needs-validation');
            // Loop over them and prevent submission
            var validation = Array.prototype.filter.call(forms, function (form) {
                form.addEventListener('submit', function (event) {
                    if (form.checkValidity() === false) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                }, false);
            });
        }, false);
    })();
    const sleep = m => new Promise(r => setTimeout(r, m));

    await sleep(500);
    const login_vue = new Vue({
        el: '#login-form',
        data: {
            email: '',
            password: ''
        },
        methods: {
            validateForm: function(){
                return this.email && this.password;
            },
            login: function(){
                const me = this;
                frappe.call({
                    method: 'login',
                    args: {
                        usr: me.email, 
                        pwd: me.password,
                    },
                    callback: function(r) {
                        console.log(r, frappe.session.user);
                        if (r.message.toLowerCase() == 'logged in'){
                            window.location.href = '/dashboard';
                        } else {
                            frappe.throw('Incorrect email or password. Please try again or click on the forgot password link.');
                        }
                    }
                });
            }
        }
    })
})