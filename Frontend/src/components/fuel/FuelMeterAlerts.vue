<template>
  <div class="h-full">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-baseline">
        <i class="bi bi-exclamation-triangle text-orange-500 text-xl mr-3"></i>
        <h3 class="font-semibold">Fuel Meter Alerts</h3>
      </div>
    </div>

    <div class="space-y-3 max-h-80 overflow-y-auto">
      <div 
        v-for="alert in alerts" 
        :key="alert.id"
        class="p-3 rounded-lg border"
        :class="getAlertClass(alert.severity)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center mb-1">
              <i :class="getAlertIcon(alert.severity)" class="mr-2"></i>
              <span class="font-medium text-sm">{{ alert.title }}</span>
            </div>
            <p class="text-xs text-gray-400 mb-1">{{ alert.detail }}</p>
            <p class="text-xs text-gray-500">{{ alert.timeAgo }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  meterId: {
    type: String,
    default: ''
  }
})

const route = useRoute()

// Alert data for fuel meters
const alertMap = {
  'fm-0': [
    { id: 1, severity: 'warning', title: 'FLOW_RATE_HIGH', detail: 'Flow: 0.5 L/s', timeAgo: '2 mins ago' },
    { id: 2, severity: 'info', title: 'PRESSURE_HIGH', detail: 'Pressure: 2.5 bar', timeAgo: '6 mins ago' },
    { id: 3, severity: 'info', title: 'TEMPERATURE_HIGH', detail: 'Temp: 38.5°C', timeAgo: '10 mins ago' }
  ],
  'default': [
    { id: 4, severity: 'info', title: 'FUEL_METER_OK', detail: 'All systems normal', timeAgo: '10 mins ago' }
  ]
}

// Get alerts for current meter
const alerts = computed(() => {
  const meterId = props.meterId || route.query.meterId || 'default'
  return alertMap[meterId] || alertMap['default']
})

// Get alert styling based on severity
function getAlertClass(severity) {
  switch (severity) {
    case 'critical':
      return 'bg-red-900 bg-opacity-20 border-red-500'
    case 'warning':
      return 'bg-yellow-900 bg-opacity-20 border-yellow-500'
    case 'info':
      return 'bg-blue-900 bg-opacity-20 border-blue-500'
    default:
      return 'bg-gray-800 bg-opacity-20 border-gray-500'
  }
}

// Get alert icon based on severity
function getAlertIcon(severity) {
  switch (severity) {
    case 'critical':
      return 'bi bi-exclamation-circle text-red-500'
    case 'warning':
      return 'bi bi-exclamation-triangle text-yellow-500'
    case 'info':
      return 'bi bi-info-circle text-blue-500'
    default:
      return 'bi bi-info-circle text-gray-500'
  }
}
</script>

<style scoped>
/* Custom scrollbar for alerts */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #374151;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #6b7280;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
