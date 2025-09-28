<template>
  <div class="border border-gray-600 rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-baseline">
        <i class="bi bi-table text-orange-500 text-xl mr-3"></i>
        <h3 class="font-semibold">Live Gas Meter Readings</h3>
      </div>
      <div class="text-sm text-gray-400">Updates every 1 minute</div>
    </div>

    <DataTable :value="displayedReadings" class="custom-table">
      <Column field="timestamp" header="Timestamp" class="text-gray-300"></Column>
      <Column field="flow" header="Flow Rate" class="text-gray-300"></Column>
      <Column field="temperature" header="Temperature" class="text-gray-300"></Column>
      <Column field="pressure" header="Pressure" class="text-gray-300"></Column>
      <Column field="consumption" header="Consumption" class="text-gray-300"></Column>
    </DataTable>
  </div>
</template>

<script setup>
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

// Define emit to send latest reading to parent
const emit = defineEmits(['update:latestReading'])

const route = useRoute()

// Reactive state
const rawReadings = ref([]) // All generated records
const displayedReadings = computed(() => {
  // Return last 10 records — most recent first
  return rawReadings.value.slice(0, 10)
})

// Gas Meter ID → Index Map
const gasMeterIdToIndex = {
  'gm-0': 0,
  'gm-1': 1
}

const meterIndex = computed(() => {
  const id = route.query.meterId
  return gasMeterIdToIndex[id] !== undefined ? gasMeterIdToIndex[id] : 0
})

// Timer
let refreshInterval = null

// Generate synthetic gas meter readings
function generateGasMeterReadings() {
  const now = new Date()
  const baseFlow = 0.010 + (meterIndex.value * 0.002) // gm-0: 0.010, gm-1: 0.012
  const baseTemp = 22 + (meterIndex.value * 1) // gm-0: 22°C, gm-1: 23°C
  const basePressure = 0.3 + (meterIndex.value * 0.05) // gm-0: 0.3 bar, gm-1: 0.35 bar

  // Add realistic fluctuations
  const flowVariation = (Math.random() - 0.5) * 0.004 // ±0.002 kg/s
  const tempVariation = (Math.random() - 0.5) * 4 // ±2°C
  const pressureVariation = (Math.random() - 0.5) * 0.1 // ±0.05 bar

  const flow = Math.max(0.005, baseFlow + flowVariation)
  const temperature = Math.max(18, Math.min(30, baseTemp + tempVariation))
  const pressure = Math.max(0.2, Math.min(0.5, basePressure + pressureVariation))
  
  // Calculate consumption (simulate hourly consumption)
  const consumption = flow * 3600 // kg/s * s/h = kg/h

  const reading = {
    timestamp: now.toLocaleTimeString([], { hour12: false }),
    flow: formatValue(flow, 4, 'kg/s'),
    temperature: formatValue(temperature, 1, '°C'),
    pressure: formatValue(pressure, 2, 'bar'),
    consumption: formatValue(consumption, 2, 'kg/h')
  }

  // Add to readings array (most recent first)
  rawReadings.value.unshift(reading)

  // Keep only last 20 readings
  if (rawReadings.value.length > 20) {
    rawReadings.value = rawReadings.value.slice(0, 20)
  }

  // Emit the latest reading to parent
  emit('update:latestReading', reading)
}

// Format value helper
function formatValue(value, decimals = 2, unit = '') {
  if (value == null || !Number.isFinite(value)) return '—'
  return value.toFixed(decimals) + ' ' + unit
}

// Start auto-refresh
function startAutoRefresh() {
  if (refreshInterval) clearInterval(refreshInterval)
  
  // Generate initial reading
  generateGasMeterReadings()
  
  refreshInterval = setInterval(() => {
    generateGasMeterReadings()
  }, 60000) // 1 minute
}

// Stop auto-refresh
function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// Start on mount
onMounted(() => {
  startAutoRefresh()
})

// Cleanup
onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
/* Inherits global table styles */
</style>
