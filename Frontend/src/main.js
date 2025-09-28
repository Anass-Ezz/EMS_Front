import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import Aura from '@primeuix/themes/aura';
import PrimeVue from 'primevue/config';
import DialogService from 'primevue/dialogservice' 
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';

import '@/assets/styles.scss';




import '@vue-flow/controls/dist/style.css';
import '@vue-flow/core/dist/style.css';
import '@vue-flow/minimap/dist/style.css';



const app = createApp(App);

app.use(router);
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            // darkModeSelector: '.app-dark'
        }
    }
});
app.use(DialogService)  
app.use(ToastService);
app.use(ConfirmationService);

app.mount('#app');
