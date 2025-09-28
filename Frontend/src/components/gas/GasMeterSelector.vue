<template>
  <div class="border border-gray-600 rounded-lg p-6 grid grid-cols-12 mb-6">
    <!-- Gas Meter Selection -->
    <div class="col-span-2">
      <img 
        :src="meterImage" 
        alt="Gas Meter Model" 
        class="w-60 h-60 object-contain"
        @error="fallbackToDefaultImage"
      />
    </div>
    <div class="col-span-10">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-baseline">
          <i class="bi bi-wind text-orange-500 text-xl mr-3"></i>
          <h1 class="text-xl font-semibold">Gas Meter Selection</h1>
        </div>
        <div class="flex items-center space-x-4">
          <!-- Alert indicators -->
          <span class="text-red-500 text-sm flex items-center">
            <i class="bi bi-exclamation-circle text-red-500 mr-1"></i>
            {{ alertCounts.critical }}
          </span>
          <span class="text-yellow-500 text-sm flex items-center">
            <i class="bi bi-exclamation-triangle text-yellow-500 mr-1"></i>
            {{ alertCounts.warning }}
          </span>
          <span class="text-blue-500 text-sm flex items-center">
            <i class="bi bi-info-circle text-blue-500 mr-1"></i>
            {{ alertCounts.info }}
          </span>
          <Dropdown 
            v-model="selectedMeter" 
            :options="meters" 
            optionLabel="name" 
            placeholder="Select Gas Meter"
            class="bg-orange-600 border-orange-600"
            @change="onMeterChange"
          >
            <template #value="slotProps">
              <span class="text-white">
                {{ slotProps.value ? slotProps.value.name : 'Select Gas Meter' }}
              </span>
            </template>
          </Dropdown>
        </div>
      </div>

      <!-- Gas Meter Info -->
      <div class="flex items-center justify-between bg-gray-800 bg-opacity-30 rounded p-4 border border-gray-700">
        <div class="flex items-center">
          <div>
            <h3 class="font-medium">{{ meterInfo.name }} <i class="bi bi-check2-circle text-green-500 text-xl mr-3"></i></h3>
            <p class="text-sm text-gray-400">{{ meterInfo.code }} • {{ meterInfo.location }} • {{ meterInfo.type }}</p>
          </div>
        </div>
        <div class="flex items-center space-x-8">
          <div class="text-right">
            <div class="text-green-500 font-bold">ONLINE</div>
            <div class="text-xs text-gray-400">Status</div>
          </div>
          <div class="text-right">
            <div class="text-white font-bold">Just now</div>
            <div class="text-xs text-gray-400">Last Reading</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Dropdown from 'primevue/dropdown'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Gas meters (2 meters)
const meters = ref([
  { id: 'gm-0', name: 'Gas Meter 0 - Industrial Oven' },
  { id: 'gm-1', name: 'Gas Meter 1 - Industrial Oven' }
])

const selectedMeter = ref(null)

// Meter info computed from route
const meterInfo = computed(() => {
  const meterId = route.query.meterId
  const meterName = route.query.meterName

  if (meterId && meterName) {
    return {
      name: meterName,
      code: meterId.toUpperCase(),
      location: 'Building A - Gas Distribution',
      type: 'Gas Flow Meter'
    }
  }

  return {
    name: 'Select a Gas Meter',
    code: '—',
    location: '—',
    type: '—'
  }
})

// Import gas meter images
const meterImages = {
  'ION9000.png': new URL('@/assets/images/ION9000.png', import.meta.url).href
}

// Return correct image URL based on meter ID
const meterImage = computed(() => {
  return meterImages['ION9000.png'] // All gas meters use ION9000.png
})

// Fallback if image fails
function fallbackToDefaultImage(e) {
  console.warn(`[GasMeterSelector] Image failed to load:`, e.target.src)
  e.target.src = meterImages['ION9000.png']
}

// Preload images on mount
onMounted(() => {
  Object.values(meterImages).forEach(src => {
    const img = new Image()
    img.src = src
    img.onload = () => console.log(`[GasMeterSelector] Preloaded: ${src}`)
    img.onerror = () => console.error(`[GasMeterSelector] Failed to preload: ${src}`)
  })
})

// Alert counts for gas meters
const alertMap = {
  'gm-0': [
    { severity: 'warning', title: 'FLOW_RATE_HIGH', detail: 'Flow: 0.015 kg/s', timeAgo: '3 mins ago' },
    { severity: 'info', title: 'PRESSURE_DROP', detail: 'Pressure: 0.25 bar', timeAgo: '7 mins ago' },
    { severity: 'info', title: 'TEMPERATURE_DRIFT', detail: 'Temp: 24.5°C', timeAgo: '12 mins ago' }
  ],
  'gm-1': [
    { severity: 'warning', title: 'FLOW_RATE_LOW', detail: 'Flow: 0.008 kg/s', timeAgo: '5 mins ago' },
    { severity: 'info', title: 'PRESSURE_STABLE', detail: 'Pressure: 0.32 bar', timeAgo: '8 mins ago' },
    { severity: 'info', title: 'TEMPERATURE_NORMAL', detail: 'Temp: 22.1°C', timeAgo: '15 mins ago' }
  ],
  'default': [
    { severity: 'info', title: 'GAS_METER_OK', detail: 'All systems normal', timeAgo: '10 mins ago' }
  ]
}

// Computed alert counts
const alertCounts = computed(() => {
  const meterId = route.query.meterId || 'default'
  const alerts = alertMap[meterId] || alertMap['default']

  return {
    critical: 0,
    warning: alerts.filter(a => a.severity === 'warning').length,
    info: alerts.filter(a => a.severity === 'info').length
  }
})

// Sync selected meter with route
watch(() => route.query, (newQuery) => {
  if (newQuery.meterId && newQuery.meterName) {
    const matched = meters.value.find(m => m.id === newQuery.meterId)
    if (matched) {
      selectedMeter.value = matched
    }
  }
}, { immediate: true })

// Handle dropdown change
function onMeterChange() {
  if (selectedMeter.value) {
    router.push({
      path: '/gas-meters',
      query: { 
        meterId: selectedMeter.value.id,
        meterName: selectedMeter.value.name
      }
    })
  }
}
</script>

<style scoped>
/* Inherits parent styles */
</style>
