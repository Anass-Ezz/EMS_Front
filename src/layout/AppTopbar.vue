<script setup>
import { useLayout } from '@/layout/composables/layout';
import DatePicker from '@/components/common/DatePicker.vue';
import RefreshButton from '@/components/common/RefreshButton.vue';
import AlertsTable from '@/components/dashboard/AlertsTable.vue';

import { ref } from 'vue'
import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
const visibleRight = ref(false)



const { toggleMenu, toggleDarkMode, isDarkTheme } = useLayout();

/* ─── simple logout: clear token(s) & reload ─── */
function signOut() {
  localStorage.removeItem('token');
  sessionStorage.removeItem('token');
  location.reload();                 // auth-guard will redirect

  
  
}
</script>

<template>
    <div class="layout-topbar">
        <div class="layout-topbar-logo-container">
            <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">
                <i class="pi pi-bars"></i>
            </button>
            <router-link to="/" class="layout-topbar-logo">
                <!-- (long SVG/logo block preserved) -->

                <span class="flex flex-row gap-2 font-bold items-center"> <img src="@/assets/images/innovx2.png" alt="InnovX logo" class=" w-[110px] shrink-0 mx-auto"> EMS</span>
            </router-link>
        </div>
        
        <div class="layout-topbar-actions">
            <div class="layout-config-menu">
                <!-- (dark-mode & palette buttons commented out) -->
            </div>
            
            <div style="display: flex; gap: 8px; align-items: center;">

                <Drawer :pt="{ root: { style: 'width:500px;' } }" v-model:visible="visibleRight" position="right" class="w-[700px]">
                    <AlertsTable/>
                </Drawer>
                 <div role="Button" class="border border-red-600 p-2 mr-4 w-[40px] h-[40px] rounded-full flex justify-center items-center cursor-pointer" @click="visibleRight = true">
                    <i class="bi bi-bell text-[25px] text-red-600"></i>

                 </div>

                <DatePicker/>
                <RefreshButton/>
            </div>

            <!-- <button
                class="layout-topbar-menu-button layout-topbar-action"
                v-styleclass="{ selector: '@next', enterFromClass: 'hidden', enterActiveClass: 'animate-scalein', leaveToClass: 'hidden', leaveActiveClass: 'animate-fadeout', hideOnOutsideClick: true }"
            >
                <i class="pi pi-sign-out text-red-400"></i>
            </button> -->

            <button class="logout-button h-[45px] flex flex-row gap-2 items-center"  @click="signOut">
                <p class="mt-3  text-red-400 pt-1 text-lg"> Logout</p>
                <i class="pi pi-sign-out pt-1 text-red-400"></i>
            </button>

            <!-- <div class="layout-topbar-menu hidden lg:block">
                <div class="layout-topbar-menu-content mx-6">
                    <button type="button" class=" layout-topbar-action flex mt-2 flex-row gap-2 items-center" @click="signOut">
                        <p class="mt-3  text-red-400 text-lg"> Logout</p>
                        <i class="pi pi-sign-out text-red-400"></i>
                    </button>
                </div>
            </div> -->
        </div>
    </div>
</template>

<style scoped>

.logout-button {
  background: #0f172a;
  border: 1px solid #e90e20;
  border-radius: 6px;
  color: #e2e8f0;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}
</style>
