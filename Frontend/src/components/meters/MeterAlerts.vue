<!-- src/components/meters/MeterAlerts.vue -->
<template>
    <div class="flex flex-col h-full">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-baseline">
          <i class="bi bi-exclamation-triangle text-orange-500 text-xl mr-3"></i>
          <h3 class="font-semibold">Meter Alerts</h3>
        </div>
        <div class="flex items-center">
          <span v-if="criticalCount > 0" class="bg-red-600 text-white px-2 py-1 rounded text-xs mr-2">
            {{ criticalCount }} Critical
          </span>
          <span v-else-if="warningCount > 0" class="bg-yellow-600 text-white px-2 py-1 rounded text-xs mr-2">
            {{ warningCount }} Warning{{ warningCount > 1 ? 's' : '' }}
          </span>
          <span class="text-gray-400 text-sm">{{ meterId?.toUpperCase() || 'MTR-001' }}</span>
        </div>
      </div>
  
      <div class="space-y-3 mb-4 flex-1">
        <div 
          v-for="(alert, index) in alerts" 
          :key="index"
          class="flex items-center p-3 rounded"
          :class="{
            'bg-red-900 bg-opacity-50 border border-red-600': alert.severity === 'critical',
            'bg-yellow-900 bg-opacity-50 border border-yellow-600': alert.severity === 'warning',
            'bg-blue-900 bg-opacity-50 border border-blue-600': alert.severity === 'info'
          }"
        >
          <div 
            class="w-2 h-2 rounded-full mr-3"
            :class="{
              'bg-red-500': alert.severity === 'critical',
              'bg-yellow-500': alert.severity === 'warning',
              'bg-blue-500': alert.severity === 'info'
            }"
          ></div>
          <div class="flex-1">
            <div 
              class="text-sm font-medium"
              :class="{
                'text-red-400': alert.severity === 'critical',
                'text-yellow-400': alert.severity === 'warning',
                'text-blue-400': alert.severity === 'info'
              }"
            >
              {{ alert.title }}
            </div>
            <div class="text-xs text-gray-400">{{ alert.detail }}</div>
          </div>
          <div class="text-xs text-gray-400">{{ alert.timeAgo }}</div>
        </div>
  
        <div v-if="alerts.length === 0" class="text-gray-500 text-sm italic py-4 text-center">
          No active alerts
        </div>
      </div>
  
      <div class="flex justify-between text-sm pt-2 border-t border-gray-700 mt-auto">
        <div class="text-center">
          <div class="text-red-500 font-bold text-lg">{{ criticalCount }}</div>
          <div class="text-gray-400">Critical</div>
        </div>
        <div class="text-center">
          <div class="text-yellow-500 font-bold text-lg">{{ warningCount }}</div>
          <div class="text-gray-400">Warning</div>
        </div>
        <div class="text-center">
          <div class="text-blue-500 font-bold text-lg">{{ infoCount }}</div>
          <div class="text-gray-400">Info</div>
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
  
  const timeAgo = () => {
    const base = Math.floor(Math.random() * 30) + 1
    const jitter = Math.floor((Math.random() - 0.5) * 6)
    const mins = Math.max(1, base + jitter)
    return mins === 1 ? '1 min ago' : `${mins} mins ago`
  }
  
  const alertMap = {
    'sm-a-0': [
      { severity: 'warning', title: 'MODBUS_CYCLE_SLOW', detail: 'Cycle: 1.8s (threshold: 1.0s)', timeAgo: timeAgo() },
      { severity: 'info', title: 'POWER_FACTOR_LOW', detail: 'PF: 0.87 for 92s', timeAgo: timeAgo() },
      { severity: 'info', title: 'THD_HIGH_MINOR', detail: 'Voltage THD: 6.3%', timeAgo: timeAgo() }
    ],
    'sm-a-1': [
      { severity: 'warning', title: 'READ_TIMEOUT', detail: 'Register 40001 timeout', timeAgo: timeAgo() },
      { severity: 'info', title: 'FREQUENCY_DRIFT_MINOR', detail: '50.32 Hz for 18s', timeAgo: timeAgo() },
      { severity: 'info', title: 'CLOCK_DRIFT_MINOR', detail: 'Drift: +2m 17s vs NTP', timeAgo: timeAgo() }
    ],
    'sm-a-2': [
      { severity: 'warning', title: 'PHASE_IMBALANCE_MINOR', detail: 'L1-L3 Δ: 7.1%', timeAgo: timeAgo() },
      { severity: 'info', title: 'VOLTAGE_SAG_MINOR', detail: '216.3V (90.1% of 240V)', timeAgo: timeAgo() }
    ],
    'sm-a-3': [
      { severity: 'warning', title: 'CRC_CHECK_FAIL', detail: '3 CRC errors last 5min', timeAgo: timeAgo() },
      { severity: 'info', title: 'MISSING_INTERVAL_DATA', detail: 'Interval 14:05 missing', timeAgo: timeAgo() }
    ],
    'sm-a-4': [
      { severity: 'info', title: 'VOLTAGE_SWELL_MINOR', detail: '248.7V (108% of 230V)', timeAgo: timeAgo() },
      { severity: 'info', title: 'SENSOR_CAL_NOTICE', detail: 'Current sensor calibration recommended', timeAgo: timeAgo() }
    ],
    'sm-a-5': [
      { severity: 'warning', title: 'PACKET_LOSS_ELEVATED', detail: 'Loss: 4.2% last 2min', timeAgo: timeAgo() },
      { severity: 'info', title: 'CONFIG_CHANGE_DETECTED', detail: 'Register 3001 modified', timeAgo: timeAgo() }
    ],
    'sm-b-0': [
      { severity: 'warning', title: 'MODBUS_CONN_LOST', detail: 'Last seen 4min ago', timeAgo: timeAgo() },
      { severity: 'info', title: 'MODBUS_CONN_RESTORED', detail: 'Recovered after 27s', timeAgo: timeAgo() }
    ],
    'sm-b-1': [
      { severity: 'info', title: 'FIRMWARE_UPDATE_AVAILABLE', detail: 'v2.1.4 ready', timeAgo: timeAgo() },
      { severity: 'info', title: 'NTP_UNSYNCED', detail: 'Last sync: 38min ago', timeAgo: timeAgo() }
    ],
    'sm-b-2': [
      { severity: 'warning', title: 'OUT_OF_ORDER_SAMPLES', detail: 'Non-monotonic timestamps in window', timeAgo: timeAgo() },
      { severity: 'info', title: 'REVERSE_ENERGY_DETECTED_MINOR', detail: '0.8 kWh backfeed (PV)', timeAgo: timeAgo() }
    ],
    'sm-b-3': [
      { severity: 'info', title: 'TAMPER_SUSPECT_MINOR', detail: 'Cover opened briefly', timeAgo: timeAgo() },
      { severity: 'info', title: 'METER_REBOOTED_MINOR', detail: 'Auto-reboot after comms glitch', timeAgo: timeAgo() }
    ],
    'sm-b-4': [
      { severity: 'warning', title: 'POWER_FACTOR_LOW', detail: 'PF: 0.85 for 110s', timeAgo: timeAgo() },
      { severity: 'info', title: 'FREQUENCY_DRIFT_MINOR', detail: '50.41 Hz for 22s', timeAgo: timeAgo() }
    ],
    'default': [
      { severity: 'info', title: 'OTHER_MINOR', detail: 'Meter self-test passed', timeAgo: timeAgo() }
    ]
  }
  
  const alerts = computed(() => {
    const key = props.meterId && alertMap[props.meterId] ? props.meterId : 'default'
    return alertMap[key] || []
  })
  
  const criticalCount = computed(() => 0)
  const warningCount = computed(() => alerts.value.filter(a => a.severity === 'warning').length)
  const infoCount = computed(() => alerts.value.filter(a => a.severity === 'info').length)
  </script>
  
  <style scoped></style>