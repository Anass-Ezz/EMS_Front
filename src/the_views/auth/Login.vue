<script setup>
import FloatingConfigurator from '@/components/FloatingConfigurator.vue';
import { ref, inject } from 'vue';
import { useRouter, useRoute } from 'vue-router'; // MODIFIED: Added useRoute
import { useToast } from 'primevue/usetoast'; // Added toast import

const email = ref('');
const password = ref('');
const checked = ref(false);
const router = useRouter();
const route = useRoute(); // NEW: Get route access
const ws = inject('ws');
const auth = inject('auth');
const loading = ref(false);
const errorMsg = ref('');
const toast = useToast(); // Initialized toast

const login = async () => {
    loading.value = true;
    errorMsg.value = '';

    if (ws.readyState !== WebSocket.OPEN) {
        errorMsg.value = 'Connection not ready. Please try again.';
        toast.add({
            severity: 'error',
            summary: 'Connection Error',
            detail: 'Connection not ready. Please try again.',
            life: 3000
        });
        loading.value = false;
        return;
    }

    const id = crypto.randomUUID();

    // Set up a one-time event listener for this request
    const handleMessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id === id) {
            ws.removeEventListener('message', handleMessage);

            if (msg.result) {
                const token = msg.result.token;
                if (checked.value) {
                    localStorage.setItem('token', token);
                } else {
                    sessionStorage.setItem('token', token);
                }
                auth.token = token;
                auth.ready = true;
                
                // Show success toast
                toast.add({
                    severity: 'success',
                    summary: 'Login Successful',
                    detail: 'You have been authenticated.',
                    life: 3000
                });

                // MODIFIED: Redirect to original URL or home
                const redirectPath = route.query.redirect || '/';
                router.push(redirectPath);
            } else {
                const message = msg.error?.message || 'Authentication failed';
                errorMsg.value = message;
                toast.add({
                    severity: 'error',
                    summary: 'Authentication Failed',
                    detail: message,
                    life: 3000
                });
            }
            loading.value = false;
        }
    };

    ws.addEventListener('message', handleMessage);

    ws.send(JSON.stringify({
        jsonrpc: '2.0',
        id: id,
        method: 'authenticateWithPassword',
        params: {
            username: email.value,
            password: password.value
        }
    }));
};
</script>

<template>
    <!-- <FloatingConfigurator /> -->
    <form class="bg-surface-50 dark:bg-surface-950 flex items-center justify-center min-h-screen min-w-[100vw] overflow-hidden">
        <div class="flex flex-col items-center justify-center">
            <div style="border-radius: 56px; padding: 0.3rem; background: linear-gradient(180deg, var(--primary-color) 10%, rgba(33, 150, 243, 0) 30%)">
                <div class="w-full bg-surface-0 dark:bg-surface-900 py-20 px-8 sm:px-20" style="border-radius: 53px">
                    <div class="text-center mb-8">
                        
                        <img 
                            src="@/assets/images/innovx2.png" 
                            alt="InnovX logo" 
                            class="mb-10 w-[250px] shrink-0 mx-auto"
                        >
                        <div class="text-surface-900 dark:text-surface-0 text-3xl font-medium mb-4">Welcome to INNOVX EMS</div>
                        <span class="text-muted-color font-medium">Sign in to continue</span>
                    </div>

                    <div>
                        <label for="email1" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Email</label>
                        <InputText id="email1" type="text" placeholder="Email address" class="w-full md:w-[30rem] mb-8" v-model="email" />

                        <label for="password1" class="block text-surface-900 dark:text-surface-0 font-medium text-xl mb-2">Password</label>
                        <Password id="password1" v-model="password" placeholder="Password" :toggleMask="true" class="mb-4" fluid :feedback="false"></Password>

                        <div class="flex items-center justify-between mt-2 mb-8 gap-8">
                            <!-- <div class="flex items-center">
                                <Checkbox v-model="checked" id="rememberme1" binary class="mr-2"></Checkbox>
                                <label for="rememberme1">Remember me</label>
                            </div> -->
                            <!-- <span class="font-medium no-underline ml-2 text-right cursor-pointer text-primary">Forgot password?</span> -->
                        </div>
                        <div v-if="errorMsg" class="text-red-500 mb-4">{{ errorMsg }}</div>
                        <Button 
                        type="submit"
                          label="Sign In" 
                          class="w-full" 
                          @click="login"
                          :disabled="loading"
                        >
                          <span v-if="loading" class="pi pi-spin pi-spinner mr-2"></span>
                          <span v-else>Sign In</span>
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    </form>
</template>

<style scoped>
.pi-eye {
    transform: scale(1.6);
    margin-right: 1rem;
}

.pi-eye-slash {
    transform: scale(1.6);
    margin-right: 1rem;
}
</style>
