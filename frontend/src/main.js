import { createApp } from 'vue';
import App from './App.vue';
import  VueGoogleMaps from '@fawmi/vue-google-maps';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap";

const app = createApp(App);
app.use(VueGoogleMaps, {
    load: {
        key: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    },
}).mount('#app');