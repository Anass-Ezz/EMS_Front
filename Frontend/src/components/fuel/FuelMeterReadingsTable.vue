<template>
  <div class="border border-gray-600 rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-baseline">
        <i class="bi bi-table text-orange-500 text-xl mr-3"></i>
        <h3 class="font-semibold">Live Fuel Meter Readings</h3>
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

// Fuel Meter ID → Index Map (only one fuel meter)
const fuelMeterIdToIndex = {
  'fm-0': 0
}

const meterIndex = computed(() => {
  const id = route.query.meterId
  return fuelMeterIdToIndex[id] !== undefined ? fuelMeterIdToIndex[id] : 0
})

// Timer
let refreshInterval = null

// Generate synthetic fuel meter readings
function generateFuelMeterReadings() {
  const now = new Date()
  const baseFlow = 0.3 + (Math.random() * 0.2) // 0.3-0.5 L/s (realistic boiler)
  const baseTemp = 35 + (Math.random() * 5) // 35-40°C (preheated fuel)
  const basePressure = 2.0 + (Math.random() * 0.5) // 2.0-2.5 bar (realistic boiler pressure)

  // Add realistic fluctuations
  const flowVariation = (Math.random() - 0.5) * 0.1 // ±0.05 L/s (realistic for boiler)
  const tempVariation = (Math.random() - 0.5) * 3 // ±1.5°C
  const pressureVariation = (Math.random() - 0.5) * 0.1 // ±0.05 bar (realistic for boiler)

  const flow = Math.max(0.1, Math.min(0.6, baseFlow + flowVariation))
  const temperature = Math.max(32, Math.min(42, baseTemp + tempVariation))
  const pressure = Math.max(1.5, Math.min(2.8, basePressure + pressureVariation))
  
  // Calculate consumption (simulate hourly consumption)
  const consumption = flow * 3600 // L/s * s/h = L/h

  const reading = {
    timestamp: now.toLocaleTimeString([], { hour12: false }),
    flow: formatValue(flow, 1, 'L/s'),
    temperature: formatValue(temperature, 1, '°C'),
    pressure: formatValue(pressure, 1, 'bar'),
    consumption: formatValue(consumption, 1, 'L/h')
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
  generateFuelMeterReadings()
  
  refreshInterval = setInterval(() => {
    generateFuelMeterReadings()
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
