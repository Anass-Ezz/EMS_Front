<template>
  <div class="border border-gray-600 rounded-lg p-6 grid grid-cols-12 mb-6">
    <!-- Fuel Meter Selection -->
    <div class="col-span-2">
      <img 
        :src="meterImage" 
        alt="Fuel Meter Model" 
        class="w-60 h-60 object-contain"
        @error="fallbackToDefaultImage"
      />
    </div>
    <div class="col-span-10">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-baseline">
          <i class="bi bi-droplet text-orange-500 text-xl mr-3"></i>
          <h1 class="text-xl font-semibold">Fuel Meter Selection</h1>
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
            placeholder="Select Fuel Meter"
            class="bg-orange-600 border-orange-600"
            @change="onMeterChange"
          >
            <template #value="slotProps">
              <span class="text-white">
                {{ slotProps.value ? slotProps.value.name : 'Select Fuel Meter' }}
              </span>
            </template>
          </Dropdown>
        </div>
      </div>

      <!-- Fuel Meter Info -->
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

// Fuel meters (only 1 meter)
const meters = ref([
  { id: 'fm-0', name: 'Fuel Meter 0 - Chaudière' }
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
      location: 'Building A - Fuel Distribution',
      type: 'Fuel Flow Meter'
    }
  }

  return {
    name: 'Select a Fuel Meter',
    code: '—',
    location: '—',
    type: '—'
  }
})

// Import fuel meter images
const meterImages = {
  'SSM.png': new URL('@/assets/images/SSM.png', import.meta.url).href
}

// Return correct image URL based on meter ID
const meterImage = computed(() => {
  return meterImages['SSM.png'] // All fuel meters use SSM.png
})

// Fallback if image fails
function fallbackToDefaultImage(e) {
  console.warn(`[FuelMeterSelector] Image failed to load:`, e.target.src)
  e.target.src = meterImages['SSM.png']
}

// Preload images on mount
onMounted(() => {
  Object.values(meterImages).forEach(src => {
    const img = new Image()
    img.src = src
    img.onload = () => console.log(`[FuelMeterSelector] Preloaded: ${src}`)
    img.onerror = () => console.error(`[FuelMeterSelector] Failed to preload: ${src}`)
  })
})

// Alert counts for fuel meters
const alertMap = {
  'fm-0': [
    { severity: 'warning', title: 'FLOW_RATE_HIGH', detail: 'Flow: 0.5 L/s', timeAgo: '2 mins ago' },
    { severity: 'info', title: 'PRESSURE_HIGH', detail: 'Pressure: 2.5 bar', timeAgo: '6 mins ago' },
    { severity: 'info', title: 'TEMPERATURE_HIGH', detail: 'Temp: 38.5°C', timeAgo: '10 mins ago' }
  ],
  'default': [
    { severity: 'info', title: 'FUEL_METER_OK', detail: 'All systems normal', timeAgo: '10 mins ago' }
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
      path: '/fuel-meters',
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
