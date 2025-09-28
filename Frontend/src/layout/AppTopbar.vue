<script setup>
import { useLayout } from '@/layout/composables/layout';
import DatePicker from '@/components/common/DatePicker.vue';
import RefreshButton from '@/components/common/RefreshButton.vue';
import AlertsTable from '@/components/dashboard/AlertsTable.vue';
import AlertsHistory from '@/components/dashboard/AlertsHistory.vue';

import { ref } from 'vue'
import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
const visibleRight = ref(false)

// Track global system state (0: OK, 1: INFO, 2: WARNING, 3: FAULT)
const globalState = ref(0);

const { toggleMenu, toggleDarkMode, isDarkTheme } = useLayout();

/* ─── simple logout: clear token(s) & reload ─── */
function signOut() {
  localStorage.removeItem('token');
  sessionStorage.removeItem('token');
  location.reload();                 // auth-guard will redirect
}

// Helper to get bell color class based on state
function getBellColorClass() {
  return {
    0: 'text-green-500',
    1: 'text-blue-500',
    2: 'text-yellow-500',
    3: 'text-red-600'
  }[globalState.value] || 'text-gray-500';
}

// Helper to get border color class based on state
function getBellBorderClass() {
  return {
    0: 'border-green-500',
    1: 'border-blue-500',
    2: 'border-yellow-500',
    3: 'border-red-600'
  }[globalState.value] || 'border-gray-500';
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

                <Drawer :pt="{ root: { style: 'width:1010px;' } }" v-model:visible="visibleRight" position="right" class="w-[700px]">
                    <p class="text-2xl text-bold flex items-center gap-3">Current System State And Alerts 
                        <img 
                        src="@/assets/images/RedDot.gif" 
                        alt="Background image"
                        class="h-[13px] mt-2"
                        />
                    </p>
                    <!-- Listen for global state updates from AlertsTable -->
                    <AlertsTable @update:global-state="globalState = $event"/>
                    <p class="text-2xl text-bold mt-10">Alerts History</p>
                    <AlertsHistory/>
                </Drawer>
                 <div 
                    role="Button" 
                    class="p-2 mr-4 w-[40px] h-[40px] rounded-full flex justify-center items-center cursor-pointer"
                    :class="getBellBorderClass()"
                    @click="visibleRight = true"
                 >
                    <i class="bi bi-bell text-[25px]" :class="getBellColorClass()"></i>
                 </div>

                <DatePicker/>
                <RefreshButton/>
            </div>

            <button class="logout-button h-[45px] flex flex-row gap-2 items-center"  @click="signOut">
                <p class="mt-3  text-red-400 pt-1 text-lg"> Logout</p>
                <i class="pi pi-sign-out pt-1 text-red-400"></i>
            </button>
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