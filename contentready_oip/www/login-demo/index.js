new Vue({
    el:`#login-page`,
    template:`#login-template`,
    data:function(){
        return{
            show_eye: true
        }
    },
    methods:{
        toggleEye(){
            this.show_eye = !this.show_eye;
            if (this.show_eye) {
                this.$refs.pwd.setAttribute('type','password');
            } else {
                this.$refs.pwd.setAttribute('type','text');
            }
        }
    }
})