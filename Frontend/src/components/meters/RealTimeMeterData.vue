<!-- src/components/meters/RealTimeMeterData.vue -->
<template>
  <div class="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-5 gap-6">
    <!-- Current Power Tile — NOW BLUE -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">CURRENT POWER</div>
      <div class="text-3xl font-bold text-blue-500">
        {{ displayActivePower }}
        <span class="text-gray-400 text-[15px] ml-1">{{ unitActivePower }}</span>
      </div>
    </div>

    <!-- Current Reactive Power Tile — NOW RED -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">CURRENT REACTIVE POWER</div>
      <div class="text-3xl font-bold text-red-500">
        {{ displayReactivePower }}
        <span class="text-gray-400 text-[15px] ml-1">{{ unitReactivePower }}</span>
      </div>
    </div>

    <!-- Current Power Factor Tile — DIVIDED BY 1000, 2 DECIMALS -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">CURRENT POWER FACTOR</div>
      <div class="text-3xl font-bold text-green-500">
        {{ displayPowerFactor }}
        <span class="text-gray-400 text-[15px] ml-1"></span>
      </div>
    </div>

    <!-- Energy Today Tile -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">ENERGY TODAY</div>
      <div class="text-3xl font-bold text-yellow-500">
        {{ displayEnergyToday }}
        <span class="text-gray-400 text-[15px] ml-1">{{ unitEnergyToday }}</span>
      </div>
    </div>

    <!-- Cost Today Tile -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">COST TODAY</div>
      <div class="text-3xl font-bold text-purple-500">
        {{ displayCostToday }}
        <span class="text-gray-400 text-[15px] ml-1">{{ unitCostToday }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen(ws) {
  return new Promise((resolve) => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// Formatting functions — UPDATED to return value + unit separately
const placeholder = '---'

function formatPower(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  const absValue = Math.abs(value)
  if (absValue < 1000) return { value: value.toFixed(0), unit: 'W' }
  if (absValue < 1000000) return { value: (value / 1000).toFixed(2), unit: 'kW' }
  return { value: (value / 1000000).toFixed(2), unit: 'MW' }
}

function formatReactivePower(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  const absValue = Math.abs(value)
  if (absValue < 1000) return { value: value.toFixed(0), unit: 'var' }
  if (absValue < 1000000) return { value: (value / 1000).toFixed(2), unit: 'kVAR' }
  return { value: (value / 1000000).toFixed(2), unit: 'MVAR' }
}

function formatUnitless(value) {
  if (value === null || typeof value === 'undefined') return placeholder
  // ✅ DIVIDE BY 1000 and show 2 decimals
  if (!Number.isFinite(value)) return placeholder
  return (value / 1000).toFixed(2)
}

function formatEnergy(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  const absValue = Math.abs(value)
  if (absValue < 1000) return { value: value.toFixed(2), unit: 'Wh' }
  if (absValue < 1000000) return { value: (value / 1000).toFixed(2), unit: 'kWh' }
  return { value: (value / 1000000).toFixed(2), unit: 'MWh' }
}

function formatCurrencyMud(value) {
  if (value === null || typeof value === 'undefined' || !Number.isFinite(value)) return { value: placeholder, unit: '' }
  return { value: value.toFixed(2), unit: 'MAD' }
}

// Reactive state
const activePower = ref(null)
const reactivePower = ref(null)
const powerFactor = ref(null)
const energyToday = ref(null)

// Tariff
const TARIFF_PER_KWH = 0.8

// ✅ Display values + units (computed separately for styling)
const displayActivePower = computed(() => {
  const formatted = formatPower(activePower.value)
  return formatted.value
})
const unitActivePower = computed(() => {
  const formatted = formatPower(activePower.value)
  return formatted.unit
})

const displayReactivePower = computed(() => {
  const formatted = formatReactivePower(reactivePower.value)
  return formatted.value
})
const unitReactivePower = computed(() => {
  const formatted = formatReactivePower(reactivePower.value)
  return formatted.unit
})

// ✅ Power Factor: divided by 1000, 2 decimals
const displayPowerFactor = computed(() => {
  return formatUnitless(powerFactor.value)
})

const displayEnergyToday = computed(() => {
  const formatted = formatEnergy(energyToday.value)
  return formatted.value
})
const unitEnergyToday = computed(() => {
  const formatted = formatEnergy(energyToday.value)
  return formatted.unit
})

const displayCostToday = computed(() => {
  const formatted = formatCurrencyMud(costToday.value)
  return formatted.value
})
const unitCostToday = computed(() => {
  const formatted = formatCurrencyMud(costToday.value)
  return formatted.unit
})

// Cost calculation (unchanged)
const energyTodayKWh = computed(() => {
  if (energyToday.value == null || !Number.isFinite(energyToday.value)) return null
  return energyToday.value / 1000
})

const costToday = computed(() => {
  if (energyTodayKWh.value == null) return null
  return energyTodayKWh.value * TARIFF_PER_KWH
})

// Inject
const ws = inject('ws')
const auth = inject('auth')
const route = useRoute()

// Guard
let historicRequested = false

// Meter ID → Index Map
const meterIdToIndex = {
  'sm-a-0': 0,
  'sm-a-1': 1,
  'sm-a-2': 2,
  'sm-a-3': 3,
  'sm-a-4': 4,
  'sm-a-5': 5,
  'sm-b-0': 6,
  'sm-b-1': 7,
  'sm-b-2': 8,
  'sm-b-3': 9,
  'sm-b-4': 10
}

const meterIndex = computed(() => {
  const id = route.query.meterId
  return meterIdToIndex[id] !== undefined ? meterIdToIndex[id] : 0
})

const channelPrefix = computed(() => `meter${meterIndex.value}/`)

// Function to get today's date
function getTodayDate() {
  const now = new Date()
  return now.toISOString().split('T')[0]
}

// Fetch historic data for dynamic meter
async function queryHistoricDataToday() {
  if (historicRequested) return
  historicRequested = true

  if (!ws) return

  await waitForSocketOpen(ws)

  const today = getTodayDate()
  const OUTER_ID = crypto.randomUUID()
  const INNER_ID = crypto.randomUUID()

  const channels = [
    `${channelPrefix.value}ActiveEnergy`,
    `${channelPrefix.value}ActivePower`,
    `${channelPrefix.value}ReactivePower`,
    `${channelPrefix.value}PowerFactor`
  ]

  ws.send(
    JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER_ID,
      method: 'edgeRpc',
      params: {
        edgeId: 'edge0',
        payload: {
          jsonrpc: '2.0',
          id: INNER_ID,
          method: 'queryHistoricTimeseriesData',
          params: {
            channels,
            fromDate: today,
            toDate: today,
            resolution: {
              value: 5,
              unit: 'Minutes',
            },
            timezone: 'Africa/Casablanca',
          },
        },
      },
    })
  )

  const handler = ({ data }) => {
    const msg = JSON.parse(data)
    if (msg.id === OUTER_ID && msg.result?.payload?.result) {
      processHistoricData(msg.result.payload.result, channels)
      ws.removeEventListener('message', handler)
    }
  }

  ws.addEventListener('message', handler, { once: false })
}

// Process historic data for dynamic meter
function processHistoricData(historic, channels) {
  const timestamps = historic?.timestamps
  if (!Array.isArray(timestamps) || timestamps.length === 0) return

  const nowMs = Date.now()
  const midnight = new Date()
  midnight.setHours(0, 0, 0, 0)
  const midnightMs = midnight.getTime()

  const validIndices = []
  for (let i = 0; i < timestamps.length; i++) {
    const t = new Date(timestamps[i]).getTime()
    if (t >= midnightMs && t <= nowMs) {
      validIndices.push(i)
    }
  }

  if (validIndices.length === 0) return

  const energyKey = `${channelPrefix.value}ActiveEnergy`
  const powerKey = `${channelPrefix.value}ActivePower`
  const reactiveKey = `${channelPrefix.value}ReactivePower`
  const pfKey = `${channelPrefix.value}PowerFactor`

  // Calculate Energy Today - Fixed Algorithm
  const energyValues = historic.data?.[energyKey]
  if (Array.isArray(energyValues) && energyValues.length === timestamps.length && validIndices.length > 0) {
    // Get midnight value (first valid reading of today)
    const midnightIndex = validIndices[0]
    const midnightEnergyValue = energyValues[midnightIndex]
    
    // Get current/latest value (last valid reading)
    const currentIndex = validIndices[validIndices.length - 1]
    const currentEnergyValue = energyValues[currentIndex]
    
    // Debug logging
    console.log('=== ENERGY TODAY CALCULATION DEBUG ===')
    console.log('Midnight timestamp:', timestamps[midnightIndex])
    console.log('Midnight energy value:', midnightEnergyValue)
    console.log('Current timestamp:', timestamps[currentIndex])
    console.log('Current energy value:', currentEnergyValue)
    
    if (midnightEnergyValue != null && currentEnergyValue != null && 
        Number.isFinite(midnightEnergyValue) && Number.isFinite(currentEnergyValue)) {
      
      const energyConsumedToday = currentEnergyValue - midnightEnergyValue
      console.log('Energy consumed today (raw):', energyConsumedToday)
      console.log('Energy consumed today (formatted):', formatEnergy(energyConsumedToday))
      console.log('=======================================')
      
      energyToday.value = Math.max(0, energyConsumedToday) // Ensure non-negative
    } else {
      console.log('Invalid energy values - cannot calculate')
      console.log('=======================================')
    }
  }

  // Extract LAST valid values
  const powerValues = historic.data?.[powerKey]
  const reactiveValues = historic.data?.[reactiveKey]
  const pfValues = historic.data?.[pfKey]

  for (let i = validIndices.length - 1; i >= 0; i--) {
    const idx = validIndices[i]

    if (activePower.value === null && powerValues?.[idx] != null && Number.isFinite(powerValues[idx])) {
      activePower.value = powerValues[idx]
    }

    if (reactivePower.value === null && reactiveValues?.[idx] != null && Number.isFinite(reactiveValues[idx])) {
      reactivePower.value = reactiveValues[idx]
    }

    if (powerFactor.value === null && pfValues?.[idx] != null && Number.isFinite(pfValues[idx])) {
      powerFactor.value = pfValues[idx]
    }

    if (
      activePower.value !== null &&
      reactivePower.value !== null &&
      powerFactor.value !== null
    ) {
      break
    }
  }
}

// Refetch when meter changes
watch(() => route.query.meterId, () => {
  activePower.value = null
  reactivePower.value = null
  powerFactor.value = null
  energyToday.value = null
  historicRequested = false

  if (auth?.ready) {
    queryHistoricDataToday()
  }
}, { immediate: false })

// Fetch on mount
onMounted(() => {
  if (!ws) return

  if (auth?.ready) {
    queryHistoricDataToday()
  } else {
    const unwatchAuth = watch(
      () => auth?.ready,
      (isReady) => {
        if (isReady) {
          queryHistoricDataToday()
          unwatchAuth()
        }
      },
      { immediate: true }
    )
  }
})

onBeforeUnmount(() => {
  // Nothing to clean up
})
</script>

<style scoped>
/* Optional: if you want to fine-tune unit spacing or weight */
</style>