  <template>
    <div class="border border-gray-600 rounded-lg p-6 grid grid-cols-12 mb-6">
      <!-- Meter Selection -->
      <div class="col-span-2">
        <img 
          :src="meterImage" 
          alt="Meter Model" 
          class="w-60 h-60 object-contain"
          @error="fallbackToDefaultImage"
        />
      </div>
      <div class="col-span-10">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-speedometer2 text-orange-500 text-xl mr-3"></i>
            <h1 class="text-xl font-semibold">Meter Selection</h1>
          </div>
          <div class="flex items-center space-x-4">
            <!-- ✅ Replaced dots with Bootstrap Icons -->
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
              placeholder="Select Meter"
              class="bg-orange-600 border-orange-600"
              @change="onMeterChange"
            >
              <template #value="slotProps">
                <span class="text-white">
                  {{ slotProps.value ? slotProps.value.name : 'Select Meter' }}
                </span>
              </template>
            </Dropdown>
          </div>
        </div>

        <!-- Meter Info -->
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
  import { ref, computed, watch, onMounted } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import Dropdown from 'primevue/dropdown'

  const router = useRouter()
  const route = useRoute()

  // All 11 meters
  const meters = ref([
    { id: 'sm-a-0', name: 'WS-A Stamping Press Meter' },
    { id: 'sm-a-1', name: 'WS-A Induction Heater Meter' },
    { id: 'sm-a-2', name: 'WS-A Coil feeder Meter' },
    { id: 'sm-a-3', name: 'WS-A Large Welder Meter' },
    { id: 'sm-a-4', name: 'WS-A Controls Meter' },
    { id: 'sm-a-5', name: 'WS-A Utilities Meter' },
    { id: 'sm-b-0', name: 'WS-B Chassis Mounting Meter' },
    { id: 'sm-b-1', name: 'WS-B Robotic Arms Meter' },
    { id: 'sm-b-2', name: 'WS-B Wiring Benches Meter' },
    { id: 'sm-b-3', name: 'WS-B Control Meter' },
    { id: 'sm-b-4', name: 'WS-B Utilities Meter' }
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
        location: 'Building A - Ground Floor',
        type: '3-Phase Digital'
      }
    }

    return {
      name: 'Select a Meter',
      code: '—',
      location: '—',
      type: '—'
    }
  })

  // ✅ Import all meter images statically — Vite resolves from root @/assets
  const meterImages = {
    'ION9000.png': new URL('@/assets/images/ION9000.png', import.meta.url).href,
    'UMG_800.png': new URL('@/assets/images/UMG_800.png', import.meta.url).href,
    'PMC_350.png': new URL('@/assets/images/PMC_350.png', import.meta.url).href
  }

  // ✅ Return correct image URL based on meter ID
  const meterImage = computed(() => {
    const meterId = route.query.meterId

    if (!meterId) {
      return meterImages['PMC_350.png']
    }

    if (['sm-a-0', 'sm-a-1'].includes(meterId)) {
      return meterImages['ION9000.png']
    } else if (['sm-a-2', 'sm-a-3', 'sm-b-0', 'sm-b-1', 'sm-b-2'].includes(meterId)) {
      return meterImages['UMG_800.png']
    } else {
      return meterImages['PMC_350.png']
    }
  })

  // ✅ Fallback if image fails (should be rare now)
  function fallbackToDefaultImage(e) {
    console.warn(`[MeterSelector] Image failed to load:`, e.target.src)
    e.target.src = meterImages['PMC_350.png']
  }

  // ✅ Preload images on mount
  onMounted(() => {
    Object.values(meterImages).forEach(src => {
      const img = new Image()
      img.src = src
      img.onload = () => console.log(`[MeterSelector] Preloaded: ${src}`)
      img.onerror = () => console.error(`[MeterSelector] Failed to preload: ${src}`)
    })
  })

  // Alert counts — synced with MeterAlerts logic
  const alertMap = {
    'sm-a-0': [
      { severity: 'warning', title: 'MODBUS_CYCLE_SLOW', detail: 'Cycle: 1.8s', timeAgo: '5 mins ago' },
      { severity: 'info', title: 'POWER_FACTOR_LOW', detail: 'PF: 0.87', timeAgo: '8 mins ago' },
      { severity: 'info', title: 'THD_HIGH_MINOR', detail: 'THD: 6.3%', timeAgo: '12 mins ago' }
    ],
    'sm-a-1': [
      { severity: 'warning', title: 'READ_TIMEOUT', detail: 'Register timeout', timeAgo: '3 mins ago' },
      { severity: 'info', title: 'FREQUENCY_DRIFT_MINOR', detail: '50.32 Hz', timeAgo: '7 mins ago' },
      { severity: 'info', title: 'CLOCK_DRIFT_MINOR', detail: '+2m 17s', timeAgo: '15 mins ago' }
    ],
    'sm-a-2': [
      { severity: 'warning', title: 'PHASE_IMBALANCE_MINOR', detail: 'Δ: 7.1%', timeAgo: '6 mins ago' },
      { severity: 'info', title: 'VOLTAGE_SAG_MINOR', detail: '216.3V', timeAgo: '9 mins ago' }
    ],
    'sm-a-3': [
      { severity: 'warning', title: 'CRC_CHECK_FAIL', detail: '3 errors', timeAgo: '4 mins ago' },
      { severity: 'info', title: 'MISSING_INTERVAL_DATA', detail: 'Interval missing', timeAgo: '11 mins ago' }
    ],
    'sm-a-4': [
      { severity: 'info', title: 'VOLTAGE_SWELL_MINOR', detail: '248.7V', timeAgo: '10 mins ago' },
      { severity: 'info', title: 'SENSOR_CAL_NOTICE', detail: 'Calibration', timeAgo: '20 mins ago' }
    ],
    'sm-a-5': [
      { severity: 'warning', title: 'PACKET_LOSS_ELEVATED', detail: '4.2% loss', timeAgo: '5 mins ago' },
      { severity: 'info', title: 'CONFIG_CHANGE_DETECTED', detail: 'Reg 3001', timeAgo: '14 mins ago' }
    ],
    'sm-b-0': [
      { severity: 'warning', title: 'MODBUS_CONN_LOST', detail: '4min ago', timeAgo: '4 mins ago' },
      { severity: 'info', title: 'MODBUS_CONN_RESTORED', detail: 'Recovered', timeAgo: '3 mins ago' }
    ],
    'sm-b-1': [
      { severity: 'info', title: 'FIRMWARE_UPDATE_AVAILABLE', detail: 'v2.1.4', timeAgo: '18 mins ago' },
      { severity: 'info', title: 'NTP_UNSYNCED', detail: '38min ago', timeAgo: '38 mins ago' }
    ],
    'sm-b-2': [
      { severity: 'warning', title: 'OUT_OF_ORDER_SAMPLES', detail: 'Non-monotonic', timeAgo: '7 mins ago' },
      { severity: 'info', title: 'REVERSE_ENERGY_DETECTED_MINOR', detail: '0.8 kWh', timeAgo: '9 mins ago' }
    ],
    'sm-b-3': [
      { severity: 'info', title: 'TAMPER_SUSPECT_MINOR', detail: 'Cover opened', timeAgo: '22 mins ago' },
      { severity: 'info', title: 'METER_REBOOTED_MINOR', detail: 'Auto-reboot', timeAgo: '25 mins ago' }
    ],
    'sm-b-4': [
      { severity: 'warning', title: 'POWER_FACTOR_LOW', detail: 'PF: 0.85', timeAgo: '6 mins ago' },
      { severity: 'info', title: 'FREQUENCY_DRIFT_MINOR', detail: '50.41 Hz', timeAgo: '8 mins ago' }
    ],
    'default': [
      { severity: 'info', title: 'OTHER_MINOR', detail: 'Self-test passed', timeAgo: '10 mins ago' }
    ]
  }

  // Computed alert counts — synced with MeterAlerts
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
        path: '/meters',
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