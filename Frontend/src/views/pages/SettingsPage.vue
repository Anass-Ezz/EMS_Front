<template>
  <div class="w-full h-full p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-white mb-2">Settings</h1>
      <p class="text-gray-400">Configure your application preferences and system connections</p>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-6">
      <!-- Time & Units Section -->
      <div class="bg-transparent rounded-lg p-6 border border-gray-600/50">
        <div class="flex items-center gap-3 mb-6">
          <i class="pi pi-clock text-orange-500 text-xl"></i>
          <h2 class="text-xl font-semibold text-white">Time & Units</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Time Format -->
          <div class="space-y-3">
            <label class="block text-sm font-medium text-gray-300">Time Format</label>
            <div class="flex gap-2">
              <button 
                @click="settings.timeFormat = '12h'"
                :class="[
                  'px-4 py-2 rounded-lg border transition-colors',
                  settings.timeFormat === '12h' 
                    ? 'bg-orange-500 border-orange-500 text-white' 
                    : 'bg-transparent border-gray-600 text-gray-300 hover:border-gray-500'
                ]"
              >
                12 Hour
              </button>
              <button 
                @click="settings.timeFormat = '24h'"
                :class="[
                  'px-4 py-2 rounded-lg border transition-colors',
                  settings.timeFormat === '24h' 
                    ? 'bg-orange-500 border-orange-500 text-white' 
                    : 'bg-transparent border-gray-600 text-gray-300 hover:border-gray-500'
                ]"
              >
                24 Hour
              </button>
            </div>
          </div>

          <!-- Weight Units -->
          <div class="space-y-3">
            <label class="block text-sm font-medium text-gray-300">Weight Units</label>
            <div class="flex gap-2">
              <button 
                @click="settings.weightUnit = 'kg'"
                :class="[
                  'px-4 py-2 rounded-lg border transition-colors',
                  settings.weightUnit === 'kg' 
                    ? 'bg-orange-500 border-orange-500 text-white' 
                    : 'bg-transparent border-gray-600 text-gray-300 hover:border-gray-500'
                ]"
              >
                Kilogram
              </button>
              <button 
                @click="settings.weightUnit = 'lb'"
                :class="[
                  'px-4 py-2 rounded-lg border transition-colors',
                  settings.weightUnit === 'lb' 
                    ? 'bg-orange-500 border-orange-500 text-white' 
                    : 'bg-transparent border-gray-600 text-gray-300 hover:border-gray-500'
                ]"
              >
                Pound
              </button>
            </div>
          </div>

          <!-- Volume Units -->
          <div class="space-y-3">
            <label class="block text-sm font-medium text-gray-300">Volume Units</label>
            <div class="flex gap-2">
              <button 
                @click="settings.volumeUnit = 'L'"
                :class="[
                  'px-4 py-2 rounded-lg border transition-colors',
                  settings.volumeUnit === 'L' 
                    ? 'bg-orange-500 border-orange-500 text-white' 
                    : 'bg-transparent border-gray-600 text-gray-300 hover:border-gray-500'
                ]"
              >
                Liter
              </button>
              <button 
                @click="settings.volumeUnit = 'gal'"
                :class="[
                  'px-4 py-2 rounded-lg border transition-colors',
                  settings.volumeUnit === 'gal' 
                    ? 'bg-orange-500 border-orange-500 text-white' 
                    : 'bg-transparent border-gray-600 text-gray-300 hover:border-gray-500'
                ]"
              >
                Gallon
              </button>
            </div>
          </div>
        </div>

        <!-- Currency -->
        <div class="mt-6">
          <label class="block text-sm font-medium text-gray-300 mb-3">Currency</label>
          <div class="flex gap-2 flex-wrap">
            <button 
              v-for="currency in currencies"
              :key="currency.code"
              @click="settings.currency = currency.code"
              :class="[
                'px-4 py-2 rounded-lg border transition-colors',
                settings.currency === currency.code 
                  ? 'bg-orange-500 border-orange-500 text-white' 
                  : 'bg-transparent border-gray-600 text-gray-300 hover:border-gray-500'
              ]"
            >
              {{ currency.symbol }} {{ currency.code }}
            </button>
          </div>
        </div>
      </div>

      <!-- Edge Connections Section -->
      <div class="bg-transparent rounded-lg p-6 border border-gray-600/50">
        <div class="flex items-center gap-3 mb-6">
          <i class="pi pi-sitemap text-orange-500 text-xl"></i>
          <h2 class="text-xl font-semibold text-white">Edge Connections</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div 
            v-for="(edge, index) in edges"
            :key="edge.id"
            class="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
          >
             <div class="flex items-center justify-between mb-3">
               <h3 class="font-medium text-white">{{ edge.name }}</h3>
               <div class="flex items-center gap-2">
                 <div 
                   :class="[
                     'w-3 h-3 rounded-full',
                     edgeStates[index] ? 'bg-red-500' : 'bg-green-500'
                   ]"
                 ></div>
                 <span class="text-xs text-gray-400">
                   {{ edgeStates[index] ? 'Offline' : 'Online' }}
                 </span>
               </div>
             </div>
             <div class="flex items-center justify-between">
               <span class="text-sm text-gray-400">Status</span>
               <button
                 @click="toggleEdge(index)"
                 :class="[
                   'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                   tempEdgeStates[index] ? 'bg-red-600' : 'bg-green-600'
                 ]"
               >
                 <span
                   :class="[
                     'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                     tempEdgeStates[index] ? 'translate-x-6' : 'translate-x-1'
                   ]"
                 ></span>
               </button>
             </div>
          </div>
        </div>
      </div>

      <!-- Smart Meters Section -->
      <div class="bg-transparent rounded-lg p-6 border border-gray-600/50">
        <div class="flex items-center gap-3 mb-6">
          <i class="pi pi-bolt text-orange-500 text-xl"></i>
          <h2 class="text-xl font-semibold text-white">Smart Meters</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="(meter, id) in smartMeters"
            :key="id"
            class="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
          >
             <div class="flex items-center justify-between mb-3">
               <h3 class="font-medium text-white text-sm">{{ meter.name }}</h3>
               <div class="flex items-center gap-2">
                 <div 
                   :class="[
                     'w-3 h-3 rounded-full',
                     meterStates[id] ? 'bg-red-500' : 'bg-green-500'
                   ]"
                 ></div>
                 <span class="text-xs text-gray-400">
                   {{ meterStates[id] ? 'Disconnected' : 'Connected' }}
                 </span>
               </div>
             </div>
             <div class="flex items-center justify-between">
               <span class="text-sm text-gray-400">Connection</span>
               <button
                 @click="toggleMeter(id)"
                 :class="[
                   'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                   tempMeterStates[id] ? 'bg-red-600' : 'bg-green-600'
                 ]"
               >
                 <span
                   :class="[
                     'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                     tempMeterStates[id] ? 'translate-x-6' : 'translate-x-1'
                   ]"
                 ></span>
               </button>
             </div>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="flex justify-end">
        <button 
          @click="saveSettings"
          class="px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg transition-colors font-medium"
        >
          Save Settings
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

// Settings state
const settings = reactive({
  timeFormat: '24h',
  weightUnit: 'kg',
  volumeUnit: 'L',
  currency: 'MAD'
})

// Currency options
const currencies = [
  { code: 'USD', symbol: '', name: 'US Dollar' },
  { code: 'EUR', symbol: '', name: 'Euro' },
  { code: 'MAD', symbol: '', name: 'British Pound' },

]

// Edge connections (from DiagramPage.vue)
const edges = [
  { id: 'edge-0', name: 'Edge 0' },
  { id: 'edge-1', name: 'Edge 1' },
  { id: 'edge-2', name: 'Edge 2' },
  { id: 'edge-3', name: 'Edge 3' }
]

// Edge states (true = offline, false = online)
const edgeStates = ref([false, false, false, false])

// Smart meters (from DiagramPage.vue)
const smartMeters = {
  'sm-a-0': { name: 'WS-A Stamping Press' },
  'sm-a-1': { name: 'WS-A Induction Heater' },
  'sm-a-2': { name: 'WS-A Coil Feeder' },
  'sm-a-3': { name: 'WS-A Large Welder' },
  'sm-a-4': { name: 'WS-A Controls' },
  'sm-a-5': { name: 'WS-A Utilities' },
  'sm-b-0': { name: 'WS-B Chassis Mounting' },
  'sm-b-1': { name: 'WS-B Robotic Arms' },
  'sm-b-2': { name: 'WS-B Wiring Benches' },
  'sm-b-3': { name: 'WS-B Control' },
  'sm-b-4': { name: 'WS-B Utilities' },
  'gas-0': { name: 'Gas Meter 1' },
  'gas-1': { name: 'Gas Meter 2' },
  'fuel-0': { name: 'Fuel Oil Meter' }
}

// Meter states (true = disconnected/ERROR, false = connected/OK)
const meterStates = ref({
  'sm-a-0': false,
  'sm-a-1': false,
  'sm-a-2': false,
  'sm-a-3': false,
  'sm-a-4': false,
  'sm-a-5': false,
  'sm-b-0': false,
  'sm-b-1': false,
  'sm-b-2': false,
  'sm-b-3': false,
  'sm-b-4': false,
  'gas-0': false,
  'gas-1': false,
  'fuel-0': false,
})

// Temporary states for pending changes (don't update labels until save)
const tempEdgeStates = ref([false, false, false, false])
const tempMeterStates = ref({
  'sm-a-0': false,
  'sm-a-1': false,
  'sm-a-2': false,
  'sm-a-3': false,
  'sm-a-4': false,
  'sm-a-5': false,
  'sm-b-0': false,
  'sm-b-1': false,
  'sm-b-2': false,
  'sm-b-3': false,
  'sm-b-4': false,
  'gas-0': false,
  'gas-1': false,
  'fuel-0': false,
})

// Toggle functions (use temporary states)
const toggleEdge = (index) => {
  tempEdgeStates.value[index] = !tempEdgeStates.value[index]
}

const toggleMeter = (id) => {
  tempMeterStates.value[id] = !tempMeterStates.value[id]
}

// Save settings (demo function)
const saveSettings = () => {
  // Apply temporary changes to actual states
  edgeStates.value = [...tempEdgeStates.value]
  meterStates.value = { ...tempMeterStates.value }
  
  console.log('Settings saved:', {
    settings,
    edgeStates: edgeStates.value,
    meterStates: meterStates.value
  })
  
  // Show success message (you could use a toast notification here)
  alert('Settings saved successfully!')
}
</script>
