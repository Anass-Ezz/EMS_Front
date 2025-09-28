<template>
  <div class="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-5 gap-6">
    <!-- Current Flow Rate Tile -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">CURRENT FLOW RATE</div>
      <div class="text-3xl font-bold text-blue-500">
        {{ displayFlowRate }}
        <span class="text-gray-400 text-[15px] ml-1">{{ unitFlowRate }}</span>
      </div>
    </div>

    <!-- Current Temperature Tile -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">CURRENT TEMPERATURE</div>
      <div class="text-3xl font-bold text-red-500">
        {{ displayTemperature }}
        <span class="text-gray-400 text-[15px] ml-1">{{ unitTemperature }}</span>
      </div>
    </div>

    <!-- Current Pressure Tile -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">CURRENT PRESSURE</div>
      <div class="text-3xl font-bold text-green-500">
        {{ displayPressure }}
        <span class="text-gray-400 text-[15px] ml-1">{{ unitPressure }}</span>
      </div>
    </div>

    <!-- Gas Consumption Today Tile -->
    <div class="border border-gray-600 rounded-lg p-6">
      <div class="text-gray-400 text-sm mb-2">GAS CONSUMPTION TODAY</div>
      <div class="text-3xl font-bold text-yellow-500">
        {{ displayConsumptionToday }}
        <span class="text-gray-400 text-[15px] ml-1">{{ unitConsumptionToday }}</span>
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
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen(ws) {
  return new Promise((resolve) => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// Formatting functions
const placeholder = '---'

function formatFlowRate(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  const absValue = Math.abs(value)
  if (absValue < 0.001) return { value: (value * 1000).toFixed(3), unit: 'g/s' }
  if (absValue < 1) return { value: value.toFixed(4), unit: 'kg/s' }
  return { value: value.toFixed(2), unit: 'kg/s' }
}

function formatTemperature(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  return { value: value.toFixed(1), unit: '°C' }
}

function formatPressure(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  return { value: value.toFixed(2), unit: 'bar' }
}

function formatConsumption(value) {
  if (value === null || typeof value === 'undefined') return { value: placeholder, unit: '' }
  const absValue = Math.abs(value)
  if (absValue < 1) return { value: value.toFixed(3), unit: 'kg' }
  if (absValue < 1000) return { value: value.toFixed(2), unit: 'kg' }
  return { value: (value / 1000).toFixed(2), unit: 't' }
}

function formatCurrencyMud(value) {
  if (value === null || typeof value === 'undefined' || !Number.isFinite(value)) return { value: placeholder, unit: '' }
  return { value: value.toFixed(2), unit: 'MAD' }
}

// Reactive state
const flowRate = ref(null)
const temperature = ref(null)
const pressure = ref(null)
const consumptionToday = ref(null)

// Gas tariff (MAD per kg)
const GAS_TARIFF_PER_KG = 2.5

// Display values + units (computed separately for styling)
const displayFlowRate = computed(() => {
  const formatted = formatFlowRate(flowRate.value)
  return formatted.value
})
const unitFlowRate = computed(() => {
  const formatted = formatFlowRate(flowRate.value)
  return formatted.unit
})

const displayTemperature = computed(() => {
  const formatted = formatTemperature(temperature.value)
  return formatted.value
})
const unitTemperature = computed(() => {
  const formatted = formatTemperature(temperature.value)
  return formatted.unit
})

const displayPressure = computed(() => {
  const formatted = formatPressure(pressure.value)
  return formatted.value
})
const unitPressure = computed(() => {
  const formatted = formatPressure(pressure.value)
  return formatted.unit
})

const displayConsumptionToday = computed(() => {
  const formatted = formatConsumption(consumptionToday.value)
  return formatted.value
})
const unitConsumptionToday = computed(() => {
  const formatted = formatConsumption(consumptionToday.value)
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

// Cost calculation
const costToday = computed(() => {
  if (consumptionToday.value == null) return null
  return consumptionToday.value * GAS_TARIFF_PER_KG
})

// Inject
const ws = inject('ws')
const auth = inject('auth')
const route = useRoute()

// Guard
let historicRequested = false

// Gas Meter ID → Index Map
const gasMeterIdToIndex = {
  'gm-0': 0,
  'gm-1': 1
}

const meterIndex = computed(() => {
  const id = route.query.meterId
  return gasMeterIdToIndex[id] !== undefined ? gasMeterIdToIndex[id] : 0
})

const channelPrefix = computed(() => `gasmeter${meterIndex.value}/`)

// Function to get today's date
function getTodayDate() {
  const now = new Date()
  return now.toISOString().split('T')[0]
}

// Fetch historic data for dynamic gas meter
async function queryHistoricDataToday() {
  if (historicRequested) return
  historicRequested = true

  if (!ws) return

  await waitForSocketOpen(ws)

  const today = getTodayDate()
  const OUTER_ID = crypto.randomUUID()
  const INNER_ID = crypto.randomUUID()

  const channels = [
    `${channelPrefix.value}FlowRate`,
    `${channelPrefix.value}Temperature`,
    `${channelPrefix.value}Pressure`,
    `${channelPrefix.value}Consumption`
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
    console.log("RealTimeGasMeterData: sdhfkjhsdkjghfsdhgfikhkj", msg)
    if (msg.id === OUTER_ID && msg.result?.payload?.result) {
      processHistoricData(msg.result.payload.result, channels)
      ws.removeEventListener('message', handler)
    }
  }

  ws.addEventListener('message', handler, { once: false })
}

// Process historic data for dynamic gas meter
function processHistoricData(historic, channels) {
  console.log('Gas processHistoricData called with:', historic)
  console.log('Available data keys:', Object.keys(historic?.data || {}))
  
  const timestamps = historic?.timestamps
  if (!Array.isArray(timestamps) || timestamps.length === 0) {
    console.log('No timestamps found')
    return
  }

  const consumptionKey = `${channelPrefix.value}Consumption`
  const flowKey = `${channelPrefix.value}FlowRate`
  const temperatureKey = `${channelPrefix.value}Temperature`
  const pressureKey = `${channelPrefix.value}Pressure`

  // Also try alternative channel names in case the exact names don't match
  const alternativeKeys = [
    `${channelPrefix.value}Flow`,
    `${channelPrefix.value}Temp`,
    `${channelPrefix.value}Pres`,
    `${channelPrefix.value}Energy`,
    `${channelPrefix.value}Power`
  ]

  console.log('Looking for keys:', { consumptionKey, flowKey, temperatureKey, pressureKey })
  console.log('Also checking alternative keys:', alternativeKeys)

  // Get the latest values from the entire dataset (not just today)
  const flowValues = historic.data?.[flowKey]
  const temperatureValues = historic.data?.[temperatureKey]
  const pressureValues = historic.data?.[pressureKey]
  const consumptionValues = historic.data?.[consumptionKey]

  console.log('Data arrays:', {
    flowValues: flowValues?.length,
    temperatureValues: temperatureValues?.length,
    pressureValues: pressureValues?.length,
    consumptionValues: consumptionValues?.length
  })

  // Find the latest valid values (go backwards from the end)
  for (let i = timestamps.length - 1; i >= 0; i--) {
    // Set flow rate if not already set and value is valid
    if (flowRate.value === null && flowValues?.[i] != null && Number.isFinite(flowValues[i])) {
      flowRate.value = flowValues[i]
      console.log('Set flowRate.value to:', flowRate.value)
    }

    // Set temperature if not already set and value is valid
    if (temperature.value === null && temperatureValues?.[i] != null && Number.isFinite(temperatureValues[i])) {
      temperature.value = temperatureValues[i]
      console.log('Set temperature.value to:', temperature.value)
    }

    // Set pressure if not already set and value is valid
    if (pressure.value === null && pressureValues?.[i] != null && Number.isFinite(pressureValues[i])) {
      pressure.value = pressureValues[i]
      console.log('Set pressure.value to:', pressure.value)
    }

    // Set consumption today if not already set and value is valid
    if (consumptionToday.value === null && consumptionValues?.[i] != null && Number.isFinite(consumptionValues[i])) {
      consumptionToday.value = consumptionValues[i]
      console.log('Set consumptionToday.value to:', consumptionToday.value)
    }

    // If we have all values, we can break early
    if (
      flowRate.value !== null &&
      temperature.value !== null &&
      pressure.value !== null &&
      consumptionToday.value !== null
    ) {
      break
    }
  }

  // If we still don't have values, try to find any available data
  if (flowRate.value === null || temperature.value === null || pressure.value === null || consumptionToday.value === null) {
    console.log('Some values are still null, trying to find any available data...')
    
    // Try alternative channel names
    for (const altKey of alternativeKeys) {
      const altValues = historic.data?.[altKey]
      if (altValues && altValues.length > 0) {
        for (let i = altValues.length - 1; i >= 0; i--) {
          if (altValues[i] != null && Number.isFinite(altValues[i])) {
            if (flowRate.value === null) {
              flowRate.value = altValues[i]
              console.log(`Set flowRate from ${altKey}:`, flowRate.value)
            } else if (temperature.value === null) {
              temperature.value = altValues[i]
              console.log(`Set temperature from ${altKey}:`, temperature.value)
            } else if (pressure.value === null) {
              pressure.value = altValues[i]
              console.log(`Set pressure from ${altKey}:`, pressure.value)
            } else if (consumptionToday.value === null) {
              consumptionToday.value = altValues[i]
              console.log(`Set consumption from ${altKey}:`, consumptionToday.value)
            }
            break
          }
        }
      }
    }
  }

  console.log('Final values:', {
    flowRate: flowRate.value,
    temperature: temperature.value,
    pressure: pressure.value,
    consumptionToday: consumptionToday.value
  })
}

// Refetch when meter changes
watch(() => route.query.meterId, () => {
  flowRate.value = null
  temperature.value = null
  pressure.value = null
  consumptionToday.value = null
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
