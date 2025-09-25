<template>
    <div class="rounded-lg border border-gray-700 bg-gray-900">
      <div class="px-4 py-3 border-b border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-baseline">
            <i class="bi bi-clock-history text-blue-500 text-xl mr-3"></i>
            <h3 class="font-semibold text-white">Alerts History</h3>
          </div>
          <div class="flex items-center space-x-3">
            <!-- Filter dropdown -->
            <select 
              v-model="selectedFilter" 
              class="bg-gray-800 border border-gray-600 text-white text-sm rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical Only</option>
              <option value="warning">Warning Only</option>
              <option value="info">Info Only</option>
            </select>
            
            <!-- Date range selector -->
            <select 
              v-model="selectedTimeRange" 
              class="bg-gray-800 border border-gray-600 text-white text-sm rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>
      </div>
  
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-800 border-b border-gray-700">
            <tr>
              <th class="px-4 py-3 text-left text-gray-300 font-medium">Severity</th>
              <th class="px-4 py-3 text-left text-gray-300 font-medium">Alert</th>
              <th class="px-4 py-3 text-left text-gray-300 font-medium">Details</th>
              <th class="px-4 py-3 text-left text-gray-300 font-medium">Meter ID</th>
              <th class="px-4 py-3 text-left text-gray-300 font-medium">Timestamp</th>
              <th class="px-4 py-3 text-left text-gray-300 font-medium">Duration</th>
              <th class="px-4 py-3 text-left text-gray-300 font-medium">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700">
            <tr 
              v-for="(alert, index) in filteredAlerts" 
              :key="index"
              class="hover:bg-gray-800 transition-colors"
              :class="{
                'bg-red-900 bg-opacity-20': alert.severity === 'critical',
                'bg-yellow-900 bg-opacity-20': alert.severity === 'warning'
              }"
            >
              <!-- Severity -->
              <td class="px-4 py-3">
                <div class="flex items-center">
                  <div 
                    class="w-3 h-3 rounded-full mr-2"
                    :class="{
                      'bg-red-500': alert.severity === 'critical',
                      'bg-yellow-500': alert.severity === 'warning',
                      'bg-blue-500': alert.severity === 'info'
                    }"
                  ></div>
                  <span 
                    class="px-2 py-1 rounded text-xs font-medium"
                    :class="{
                      'bg-red-600 text-white': alert.severity === 'critical',
                      'bg-yellow-600 text-white': alert.severity === 'warning',
                      'bg-blue-600 text-white': alert.severity === 'info'
                    }"
                  >
                    {{ alert.severity.toUpperCase() }}
                  </span>
                </div>
              </td>
  
              <!-- Alert Title -->
              <td class="px-4 py-3">
                <div 
                  class="font-medium"
                  :class="{
                    'text-red-400': alert.severity === 'critical',
                    'text-yellow-400': alert.severity === 'warning',
                    'text-blue-400': alert.severity === 'info'
                  }"
                >
                  {{ alert.title }}
                </div>
              </td>
  
              <!-- Details -->
              <td class="px-4 py-3 text-gray-300 max-w-xs">
                <div class="truncate" :title="alert.detail">
                  {{ alert.detail }}
                </div>
              </td>
  
              <!-- Meter ID -->
              <td class="px-4 py-3">
                <span class="text-gray-400 font-mono text-xs bg-gray-800 px-2 py-1 rounded">
                  {{ alert.meterId }}
                </span>
              </td>
  
              <!-- Timestamp -->
              <td class="px-4 py-3 text-gray-300">
                <div class="text-xs">
                  <div>{{ formatDate(alert.timestamp) }}</div>
                  <div class="text-gray-500">{{ formatTime(alert.timestamp) }}</div>
                </div>
              </td>
  
              <!-- Duration -->
              <td class="px-4 py-3 text-gray-400 text-xs">
                {{ alert.duration || '-' }}
              </td>
  
              <!-- Status -->
              <td class="px-4 py-3">
                <span 
                  class="px-2 py-1 rounded text-xs"
                  :class="{
                    'bg-green-600 text-white': alert.status === 'resolved',
                    'bg-red-600 text-white': alert.status === 'active',
                    'bg-gray-600 text-white': alert.status === 'acknowledged'
                  }"
                >
                  {{ alert.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
  
        <!-- Empty state -->
        <div v-if="filteredAlerts.length === 0" class="text-center py-8 text-gray-500">
          <i class="bi bi-inbox text-3xl mb-2"></i>
          <div>No alerts found for the selected criteria</div>
        </div>
      </div>
  
      <!-- Pagination -->
      <div class="px-4 py-3 border-t border-gray-700 flex items-center justify-between">
        <div class="text-gray-400 text-sm">
          Showing {{ Math.min((currentPage - 1) * itemsPerPage + 1, filteredAlerts.length) }} 
          to {{ Math.min(currentPage * itemsPerPage, filteredAlerts.length) }} 
          of {{ filteredAlerts.length }} alerts
        </div>
        
        <div class="flex items-center space-x-2">
          <button 
            @click="currentPage = Math.max(1, currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-1 text-sm bg-gray-800 border border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 text-white"
          >
            Previous
          </button>
          
          <span class="text-gray-400 text-sm">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          
          <button 
            @click="currentPage = Math.min(totalPages, currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 text-sm bg-gray-800 border border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 text-white"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed, ref } from 'vue'
  
  const props = defineProps({
    meterId: {
      type: String,
      default: null
    }
  })
  
  // Reactive filters
  const selectedFilter = ref('all')
  const selectedTimeRange = ref('24h')
  const currentPage = ref(1)
  const itemsPerPage = 10
  
  // Generate random timestamp within range
  const generateTimestamp = (hoursAgo) => {
    const now = new Date()
    const timestamp = new Date(now.getTime() - (hoursAgo * 60 * 60 * 1000))
    return timestamp
  }
  
  // Generate random duration
  const generateDuration = () => {
    const durations = ['2m 15s', '45s', '1h 23m', '3m 02s', '12s', '5m 41s', '1h 05m', '28s']
    return durations[Math.floor(Math.random() * durations.length)]
  }
  
  // Sample historical alerts data
  const allAlerts = ref([
    // Critical alerts
    { severity: 'critical', title: 'OVERCURRENT_FAULT', detail: 'Current: 125A (limit: 100A)', meterId: 'SM-A-0', timestamp: generateTimestamp(2), duration: '45s', status: 'resolved' },
    { severity: 'critical', title: 'VOLTAGE_OUTAGE', detail: 'All phases lost', meterId: 'SM-B-1', timestamp: generateTimestamp(8), duration: '2m 15s', status: 'resolved' },
    { severity: 'critical', title: 'TEMPERATURE_CRITICAL', detail: 'Internal temp: 85°C', meterId: 'SM-A-2', timestamp: generateTimestamp(12), duration: '1h 23m', status: 'resolved' },
    
    // Warning alerts
    { severity: 'warning', title: 'MODBUS_CYCLE_SLOW', detail: 'Cycle: 1.8s (threshold: 1.0s)', meterId: 'SM-A-0', timestamp: generateTimestamp(1), duration: '3m 02s', status: 'active' },
    { severity: 'warning', title: 'READ_TIMEOUT', detail: 'Register 40001 timeout', meterId: 'SM-A-1', timestamp: generateTimestamp(3), duration: '12s', status: 'acknowledged' },
    { severity: 'warning', title: 'PHASE_IMBALANCE_MINOR', detail: 'L1-L3 Δ: 7.1%', meterId: 'SM-A-2', timestamp: generateTimestamp(4), duration: '5m 41s', status: 'resolved' },
    { severity: 'warning', title: 'CRC_CHECK_FAIL', detail: '3 CRC errors last 5min', meterId: 'SM-A-3', timestamp: generateTimestamp(6), duration: '1h 05m', status: 'resolved' },
    { severity: 'warning', title: 'PACKET_LOSS_ELEVATED', detail: 'Loss: 4.2% last 2min', meterId: 'SM-A-5', timestamp: generateTimestamp(10), duration: '28s', status: 'resolved' },
    { severity: 'warning', title: 'MODBUS_CONN_LOST', detail: 'Last seen 4min ago', meterId: 'SM-B-0', timestamp: generateTimestamp(14), duration: '2m 30s', status: 'resolved' },
    { severity: 'warning', title: 'OUT_OF_ORDER_SAMPLES', detail: 'Non-monotonic timestamps in window', meterId: 'SM-B-2', timestamp: generateTimestamp(18), duration: '1m 15s', status: 'resolved' },
    { severity: 'warning', title: 'POWER_FACTOR_LOW', detail: 'PF: 0.85 for 110s', meterId: 'SM-B-4', timestamp: generateTimestamp(20), duration: '1h 50m', status: 'resolved' },
    
    // Info alerts
    { severity: 'info', title: 'POWER_FACTOR_LOW', detail: 'PF: 0.87 for 92s', meterId: 'SM-A-0', timestamp: generateTimestamp(0.5), duration: '1m 32s', status: 'resolved' },
    { severity: 'info', title: 'THD_HIGH_MINOR', detail: 'Voltage THD: 6.3%', meterId: 'SM-A-0', timestamp: generateTimestamp(1.5), duration: '45s', status: 'resolved' },
    { severity: 'info', title: 'FREQUENCY_DRIFT_MINOR', detail: '50.32 Hz for 18s', meterId: 'SM-A-1', timestamp: generateTimestamp(2.5), duration: '18s', status: 'resolved' },
    { severity: 'info', title: 'CLOCK_DRIFT_MINOR', detail: 'Drift: +2m 17s vs NTP', meterId: 'SM-A-1', timestamp: generateTimestamp(5), duration: '-', status: 'acknowledged' },
    { severity: 'info', title: 'VOLTAGE_SAG_MINOR', detail: '216.3V (90.1% of 240V)', meterId: 'SM-A-2', timestamp: generateTimestamp(7), duration: '3m 15s', status: 'resolved' },
    { severity: 'info', title: 'MISSING_INTERVAL_DATA', detail: 'Interval 14:05 missing', meterId: 'SM-A-3', timestamp: generateTimestamp(9), duration: '-', status: 'acknowledged' },
    { severity: 'info', title: 'VOLTAGE_SWELL_MINOR', detail: '248.7V (108% of 230V)', meterId: 'SM-A-4', timestamp: generateTimestamp(11), duration: '2m 08s', status: 'resolved' },
    { severity: 'info', title: 'SENSOR_CAL_NOTICE', detail: 'Current sensor calibration recommended', meterId: 'SM-A-4', timestamp: generateTimestamp(13), duration: '-', status: 'active' },
    { severity: 'info', title: 'CONFIG_CHANGE_DETECTED', detail: 'Register 3001 modified', meterId: 'SM-A-5', timestamp: generateTimestamp(15), duration: '-', status: 'acknowledged' },
    { severity: 'info', title: 'MODBUS_CONN_RESTORED', detail: 'Recovered after 27s', meterId: 'SM-B-0', timestamp: generateTimestamp(16), duration: '-', status: 'resolved' },
    { severity: 'info', title: 'FIRMWARE_UPDATE_AVAILABLE', detail: 'v2.1.4 ready', meterId: 'SM-B-1', timestamp: generateTimestamp(17), duration: '-', status: 'active' },
    { severity: 'info', title: 'NTP_UNSYNCED', detail: 'Last sync: 38min ago', meterId: 'SM-B-1', timestamp: generateTimestamp(19), duration: '-', status: 'active' },
    { severity: 'info', title: 'REVERSE_ENERGY_DETECTED_MINOR', detail: '0.8 kWh backfeed (PV)', meterId: 'SM-B-2', timestamp: generateTimestamp(21), duration: '15m 30s', status: 'resolved' },
    { severity: 'info', title: 'TAMPER_SUSPECT_MINOR', detail: 'Cover opened briefly', meterId: 'SM-B-3', timestamp: generateTimestamp(22), duration: '5s', status: 'resolved' },
    { severity: 'info', title: 'METER_REBOOTED_MINOR', detail: 'Auto-reboot after comms glitch', meterId: 'SM-B-3', timestamp: generateTimestamp(24), duration: '-', status: 'resolved' }
  ])
  
  // Computed filtered alerts
  const filteredAlerts = computed(() => {
    let filtered = allAlerts.value
  
    // Filter by severity
    if (selectedFilter.value !== 'all') {
      filtered = filtered.filter(alert => alert.severity === selectedFilter.value)
    }
  
    // Filter by time range
    if (selectedTimeRange.value !== 'all') {
      const now = new Date()
      const cutoff = new Date()
      
      switch (selectedTimeRange.value) {
        case '24h':
          cutoff.setHours(cutoff.getHours() - 24)
          break
        case '7d':
          cutoff.setDate(cutoff.getDate() - 7)
          break
        case '30d':
          cutoff.setDate(cutoff.getDate() - 30)
          break
      }
      
      filtered = filtered.filter(alert => alert.timestamp >= cutoff)
    }
  
    // Filter by meter ID if provided
    if (props.meterId) {
      filtered = filtered.filter(alert => alert.meterId.toLowerCase() === props.meterId.toLowerCase())
    }
  
    return filtered.sort((a, b) => b.timestamp - a.timestamp)
  })
  
  // Pagination
  const totalPages = computed(() => Math.ceil(filteredAlerts.value.length / itemsPerPage))
  
  // Format functions
  const formatDate = (timestamp) => {
    return timestamp.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }
  
  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  }
  
  // Reset page when filters change
  import { watch } from 'vue'
  watch([selectedFilter, selectedTimeRange], () => {
    currentPage.value = 1
  })
  </script>
  
  <style scoped>
  /* Additional custom styles if needed */
  </style>