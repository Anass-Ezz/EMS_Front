<template>
  <div class="h-full flex flex-col justify-center space-y-6">
    <!-- Average Flow Rate -->
    <div class="text-center">
      <div class="text-gray-400 text-sm mb-2">AVERAGE FLOW RATE</div>
      <div class="text-2xl font-bold text-blue-500">
        {{ displayFlowRate }}
        <span class="text-gray-400 text-sm ml-1">{{ unitFlowRate }}</span>
      </div>
    </div>

    <!-- Average Temperature -->
    <div class="text-center">
      <div class="text-gray-400 text-sm mb-2">AVERAGE TEMPERATURE</div>
      <div class="text-2xl font-bold text-red-500">
        {{ displayTemperature }}
        <span class="text-gray-400 text-sm ml-1">{{ unitTemperature }}</span>
      </div>
    </div>

    <!-- Average Pressure -->
    <div class="text-center">
      <div class="text-gray-400 text-sm mb-2">AVERAGE PRESSURE</div>
      <div class="text-2xl font-bold text-green-500">
        {{ displayPressure }}
        <span class="text-gray-400 text-sm ml-1">{{ unitPressure }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

// Formatting functions
const placeholder = '---'

function formatFlowRate(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  const absValue = Math.abs(value)
  if (absValue < 0.001) return { value: (value * 1000).toFixed(3), unit: 'g/h' }
  if (absValue < 1) return { value: value.toFixed(4), unit: 'm³/h' }
  return { value: value.toFixed(2), unit: 'm³/h' }
}

function formatTemperature(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  return { value: value.toFixed(1), unit: '°C' }
}

function formatPressure(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  return { value: value.toFixed(2), unit: 'bar' }
}

// Reactive state
const avgFlowRate = ref(null)
const avgTemperature = ref(null)
const avgPressure = ref(null)

// Display values + units (computed separately for styling)
const displayFlowRate = computed(() => {
  const formatted = formatFlowRate(avgFlowRate.value)
  return formatted.value
})
const unitFlowRate = computed(() => {
  const formatted = formatFlowRate(avgFlowRate.value)
  return formatted.unit
})

const displayTemperature = computed(() => {
  const formatted = formatTemperature(avgTemperature.value)
  return formatted.value
})
const unitTemperature = computed(() => {
  const formatted = formatTemperature(avgTemperature.value)
  return formatted.unit
})

const displayPressure = computed(() => {
  const formatted = formatPressure(avgPressure.value)
  return formatted.value
})
const unitPressure = computed(() => {
  const formatted = formatPressure(avgPressure.value)
  return formatted.unit
})

// Generate average values
function generateAverageValues() {
  // Generate realistic average values for gas meters
  const baseFlow = 0.010 + (Math.random() * 0.005) // 0.010-0.015 m³/h
  const baseTemp = 22 + (Math.random() * 6) // 22-28°C
  const basePressure = 0.3 + (Math.random() * 0.1) // 0.3-0.4 bar

  avgFlowRate.value = baseFlow
  avgTemperature.value = baseTemp
  avgPressure.value = basePressure
}

// Start on mount
onMounted(() => {
  generateAverageValues()
})
</script>

<style scoped>
/* Inherits parent styles */
</style>
