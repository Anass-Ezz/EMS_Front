<!-- Dashboard.vue -->
<template>
  <!-- 1 ▸ POWER MEASUREMENTS ------------------------------------------------- -->
  <div class="col-span-12 lg:col-span-6 xl:col-span-6">
    <div class="flex items-center gap-3">
      <div class="font-semibold text-xl mb-4">Power Measurements</div>
      <button class="button font-semibold text-m px-2 py-1 mb-3" @click="openPowerModal">
        See All
      </button>
    </div>
    <div class="card mb-0 flex flex-col gap-2">
      <div class="flex flex-row gap-3 justify-around border-b pb-3 border-gray-700">
        <div class="flex flex-col text-center justify-center">
          <p class="text-xl p-0 m-0 text-blue-300">Active Power</p>
          <h1 class="text-2xl p-0 m-0 text-blue-300">{{ formatPower(activePower) }}</h1> 
        </div>
        <div class="flex flex-col text-center justify-center">
          <p class="text-xl p-0 m-0 text-red-400">Reactive Power</p>
          <h1 class="text-2xl p-0 m-0 text-red-400">{{ formatReactivePower(reactivePower) }}</h1>
        </div>
        <div class="flex flex-col text-center justify-center">
          <p class="text-xl p-0 m-0 text-cyan-300">Power Factor</p>
           <h1 class="text-2xl p-0 m-0 text-cyan-300">{{ formatUnitless(powerFactor) }}</h1>
        </div>
        <div class="flex flex-col text-center justify-center">
          <p class="text-xl p-0 m-0 text-teal-300">Frequency</p>
          <h1 class="text-2xl p-0 m-0 text-teal-300">{{ formatUnitless(frequency) }} Hz</h1>
        </div>
      </div>
      <div class="general flex flex-row gap-3 justify-around">
        <div class="flex flex-col text-center justify-center">
          <p class="text-xl p-0 m-0">L1</p>
          <h1 class="text-2xl p-0 m-0">{{ formatPower(activePowerL1) }}</h1>
        </div>
        <div class="flex flex-col text-center justify-center">
          <p class="text-xl p-0 m-0">L2</p>
          <h1 class="text-2xl p-0 m-0">{{ formatPower(activePowerL2) }}</h1>
        </div>
        <div class="flex flex-col text-center justify-center">
          <p class="text-xl p-0 m-0">L3</p>
          <h1 class="text-2xl p-0 m-0">{{ formatPower(activePowerL3) }}</h1>
        </div>
      </div>
    </div>
  </div>

  <!-- 2 ▸ VOLTAGE MEASUREMENTS ------------------------------------------------- -->
  <div class="col-span-12 lg:col-span-6 xl:col-span-3">
    <div class="flex items-center gap-3">
      <div class="font-semibold text-xl mb-4">RMS Voltage Measurements</div>
      <button class="button font-semibold text-m px-2 py-1 mb-3" @click="openVoltageModal">
        See All
      </button>
    </div>
    <div class="card mb-0 flex flex-col gap-2">
      <div class="general flex flex-row gap-3 justify-around border-b pb-3 border-gray-700">
        <div class="flex flex-col text-center justify-center">
          <h1 class="text-xl p-0 m-0 text-purple-300">Voltage</h1>
          <h1 class="text-2xl p-0 m-0 text-purple-300">{{ formatUnitless(Voltage) }} V</h1>
        </div>
      </div>
      <div class="general flex flex-row gap-3 justify-around">
        <div class="flex flex-col text-center justify-center">
          <h1 class="text-xl p-0 m-0">L1</h1>
          <h1 class="text-2xl p-0 m-0">{{ formatUnitless(VoltageL1) }} V</h1>
        </div>
        <div class="flex flex-col text-center justify-center">
          <h1 class="text-xl p-0 m-0">L2</h1>
          <h1 class="text-2xl p-0 m-0">{{ formatUnitless(VoltageL2) }} V</h1>
        </div>
        <div class="flex flex-col text-center justify-center">
          <h1 class="text-xl p-0 m-0">L3</h1>
          <h1 class="text-2xl p-0 m-0">{{ formatUnitless(VoltageL3) }} V</h1>
        </div>
      </div>
    </div>
  </div>

  <!-- 3 ▸ CURRENT MEASUREMENTS ------------------------------------------------- -->
  <div class="col-span-12 lg:col-span-6 xl:col-span-3">
    <div class="font-semibold text-xl mb-4">RMS Current Measurements</div>
    <div class="card mb-0 flex flex-col gap-2">
      <div class="general flex flex-row gap-3 justify-around border-b pb-3 border-gray-700">
        <div class="flex flex-col text-center justify-center">
          <h1 class="text-xl p-0 m-0 text-orange-300">Current</h1>
          <h1 class="text-2xl p-0 m-0 text-orange-300">{{ formatUnitless(Current) }} A</h1>
        </div>
      </div>
      <div class="general flex flex-row gap-3 justify-around">
        <div class="flex flex-col text-center justify-center">
          <h1 class="text-xl p-0 m-0">L1</h1>
          <h1 class="text-2xl p-0 m-0">{{ formatUnitless(CurrentL1) }} A</h1>
        </div>
        <div class="flex flex-col text-center justify-center">
          <h1 class="text-xl p-0 m-0">L2</h1>
          <h1 class="text-2xl p-0 m-0">{{ formatUnitless(CurrentL2) }} A</h1>
        </div>
        <div class="flex flex-col text-center justify-center">
          <h1 class="text-xl p-0 m-0">L3</h1>
          <h1 class="text-2xl p-0 m-0">{{ formatUnitless(CurrentL3) }} A</h1>
        </div>
      </div>
    </div>
  </div>

  <!-- DYNAMIC MODAL COMPONENT -->
  <MeasurementsModal
    v-model:visible="isModalVisible"
    :title="modalTitle"
    :data="modalData"
  />
</template>

<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import MeasurementsModal from './SeeAllModal.vue'; // Adjust path if necessary

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen(ws) {
  return new Promise((resolve) => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// HELPER FUNCTIONS
const placeholder = '---'
function formatPower(value) {
  if (value === null || typeof value === 'undefined') return placeholder
  const absValue = Math.abs(value)
  if (absValue < 1000) return value.toFixed(0) + ' W'
  if (absValue < 1000000) return (value / 1000).toFixed(2) + ' kW'
  return (value / 1000000).toFixed(2) + ' MW'
}
function formatReactivePower(value) {
  if (value === null || typeof value === 'undefined') return placeholder
  const absValue = Math.abs(value)
  if (absValue < 1000) return value.toFixed(0) + ' var'
  if (absValue < 1000000) return (value / 1000).toFixed(2) + ' kVAR'
  return (value / 1000000).toFixed(2) + ' MVAR'
}
function formatUnitless(value) {
  if (value === null || typeof value === 'undefined') return placeholder
  return value.toFixed(2)
}

/* ────────────────────────── Reactive state ────────────────────────── */
const activeModalType = ref(null) // Can be 'power', 'voltage', or null

const activePower = ref(null), activePowerL1 = ref(null), activePowerL2 = ref(null), activePowerL3 = ref(null)
const reactivePower = ref(null), reactivePowerL1 = ref(null), reactivePowerL2 = ref(null), reactivePowerL3 = ref(null)
const apparentPower = ref(null), apparentPowerL1 = ref(null), apparentPowerL2 = ref(null), apparentPowerL3 = ref(null)
const powerFactor = ref(null), powerFactorL1 = ref(null), powerFactorL2 = ref(null), powerFactorL3 = ref(null)
const frequency = ref(null)
const Voltage = ref(null), VoltageL1 = ref(null), VoltageL2 = ref(null), VoltageL3 = ref(null)
const voltageL1L2 = ref(null), voltageL2L3 = ref(null), voltageL3L1 = ref(null), voltageLLAverage = ref(null)
const Current = ref(null), CurrentL1 = ref(null), CurrentL2 = ref(null), CurrentL3 = ref(null)

/* ─────────────────── Computed properties for tables and modal control ─────────────────── */
const powerTableData = computed(() => [
  { parameter: 'Active Power (Total)', value: formatPower(activePower.value) },
  { parameter: 'Active Power (L1)', value: formatPower(activePowerL1.value) },
  { parameter: 'Active Power (L2)', value: formatPower(activePowerL2.value) },
  { parameter: 'Active Power (L3)', value: formatPower(activePowerL3.value) },
  { parameter: 'Reactive Power (Total)', value: formatReactivePower(reactivePower.value) },
  { parameter: 'Reactive Power (L1)', value: formatReactivePower(reactivePowerL1.value) },
  { parameter: 'Reactive Power (L2)', value: formatReactivePower(reactivePowerL2.value) },
  { parameter: 'Reactive Power (L3)', value: formatReactivePower(reactivePowerL3.value) },
  { parameter: 'Apparent Power (Total)', value: formatPower(apparentPower.value) },
  { parameter: 'Apparent Power (L1)', value: formatPower(apparentPowerL1.value) },
  { parameter: 'Apparent Power (L2)', value: formatPower(apparentPowerL2.value) },
  { parameter: 'Apparent Power (L3)', value: formatPower(apparentPowerL3.value) },
  { parameter: 'Power Factor (Total)', value: formatUnitless(powerFactor.value) },
  { parameter: 'Power Factor (L1)', value: formatUnitless(powerFactorL1.value) },
  { parameter: 'Power Factor (L2)', value: formatUnitless(powerFactorL2.value) },
  { parameter: 'Power Factor (L3)', value: formatUnitless(powerFactorL3.value) },
])
const voltageTableData = computed(() => [
  { parameter: 'Voltage (L1-N)', value: formatUnitless(VoltageL1.value) + ' V' },
  { parameter: 'Voltage (L2-N)', value: formatUnitless(VoltageL2.value) + ' V' },
  { parameter: 'Voltage (L3-N)', value: formatUnitless(VoltageL3.value) + ' V' },
  { parameter: 'Voltage Average (L-N)', value: formatUnitless(Voltage.value) + ' V' },
  { parameter: 'Voltage (L1-L2)', value: formatUnitless(voltageL1L2.value) + ' V' },
  { parameter: 'Voltage (L2-L3)', value: formatUnitless(voltageL2L3.value) + ' V' },
  { parameter: 'Voltage (L3-L1)', value: formatUnitless(voltageL3L1.value) + ' V' },
  { parameter: 'Voltage Average (L-L)', value: formatUnitless(voltageLLAverage.value) + ' V' }
])

const modalData = computed(() => {
  if (activeModalType.value === 'power') return powerTableData.value
  if (activeModalType.value === 'voltage') return voltageTableData.value
  return []
})

const modalTitle = computed(() => {
  if (activeModalType.value === 'power') return 'All Power Measurements'
  if (activeModalType.value === 'voltage') return 'All RMS Voltage Measurements'
  return ''
})

const isModalVisible = computed({
  get: () => activeModalType.value !== null,
  set: (value) => { if (!value) activeModalType.value = null }
})

/* ─────────────────── Modal Control Functions ──────────────────── */
function openPowerModal() { activeModalType.value = 'power' }
function openVoltageModal() { activeModalType.value = 'voltage' }

/* ─────────────────────── WebSocket subscription ───────────────────── */
const ws = inject('ws')
const auth = inject('auth')
let onMessage

const baseChannels = [
  'meter0/ActivePower', 'meter0/ActivePowerL1', 'meter0/ActivePowerL2', 'meter0/ActivePowerL3',
  'meter0/ReactivePower', 'meter0/PowerFactor', 'meter0/Frequency',
  'meter0/Voltage', 'meter0/VoltageL1', 'meter0/VoltageL2', 'meter0/VoltageL3',
  'meter0/Current', 'meter0/CurrentL1', 'meter0/CurrentL2', 'meter0/CurrentL3',
]
const powerModalChannels = [
  'meter0/ReactivePowerL1', 'meter0/ReactivePowerL2', 'meter0/ReactivePowerL3',
  'meter0/ApparentPower', 'meter0/ApparentPowerL1', 'meter0/ApparentPowerL2', 'meter0/ApparentPowerL3',
  'meter0/PowerFactorL1', 'meter0/PowerFactorL2', 'meter0/PowerFactorL3',
]
const voltageModalChannels = [
  'meter0/VoltageL1L2', 'meter0/VoltageL2L3', 'meter0/VoltageL3L1', 'meter0/VoltageLLAverage',
]

async function subscribeChannels() {
  const edgeId = 'edge0'
  await waitForSocketOpen(ws)

  ws.send(JSON.stringify({
    jsonrpc: '2.0',
    id: crypto.randomUUID(),
    method: 'subscribeEdges',
    params: { edges: ['edge0'] }
  }))
  
  let channelsToSubscribe = [...baseChannels]
  if (activeModalType.value === 'power') {
    channelsToSubscribe.push(...powerModalChannels)
  } else if (activeModalType.value === 'voltage') {
    channelsToSubscribe.push(...voltageModalChannels)
  }
  const uniqueChannels = [...new Set(channelsToSubscribe)]
  ws.send(JSON.stringify({
    jsonrpc: '2.0', id: crypto.randomUUID(), method: 'edgeRpc',
    params: {
      edgeId,
      payload: {
        jsonrpc: '2.0', id: crypto.randomUUID(), method: 'subscribeChannels',
        params: { count: 0, ids: [edgeId], channels: uniqueChannels }
      }
    }
  }))
  console.log(`[Dashboard] Subscribed to ${uniqueChannels.length} channels.`)
}

/* Handle every incoming WebSocket message */
function handleMessage({ data }) {
  const msg = JSON.parse(data)
  if (msg.method === 'edgeRpc' && msg.params?.payload?.method === 'currentData') {
    console.log(`[Dashboard] Processing currentData message.` + msg)
    const pd = msg.params.payload.params || {}
    pd['meter0/ActivePower'] != null && (activePower.value = pd['meter0/ActivePower'])
    pd['meter0/ActivePowerL1'] != null && (activePowerL1.value = pd['meter0/ActivePowerL1'])
    pd['meter0/ActivePowerL2'] != null && (activePowerL2.value = pd['meter0/ActivePowerL2'])
    pd['meter0/ActivePowerL3'] != null && (activePowerL3.value = pd['meter0/ActivePowerL3'])
    pd['meter0/ReactivePower'] != null && (reactivePower.value = pd['meter0/ReactivePower'])
    pd['meter0/ReactivePowerL1'] != null && (reactivePowerL1.value = pd['meter0/ReactivePowerL1'])
    pd['meter0/ReactivePowerL2'] != null && (reactivePowerL2.value = pd['meter0/ReactivePowerL2'])
    pd['meter0/ReactivePowerL3'] != null && (reactivePowerL3.value = pd['meter0/ReactivePowerL3'])
    pd['meter0/ApparentPower'] != null && (apparentPower.value = pd['meter0/ApparentPower'])
    pd['meter0/ApparentPowerL1'] != null && (apparentPowerL1.value = pd['meter0/ApparentPowerL1'])
    pd['meter0/ApparentPowerL2'] != null && (apparentPowerL2.value = pd['meter0/ApparentPowerL2'])
    pd['meter0/ApparentPowerL3'] != null && (apparentPowerL3.value = pd['meter0/ApparentPowerL3'])
    pd['meter0/PowerFactor'] != null && (powerFactor.value = pd['meter0/PowerFactor'])
    pd['meter0/PowerFactorL1'] != null && (powerFactorL1.value = pd['meter0/PowerFactorL1'])
    pd['meter0/PowerFactorL2'] != null && (powerFactorL2.value = pd['meter0/PowerFactorL2'])
    pd['meter0/PowerFactorL3'] != null && (powerFactorL3.value = pd['meter0/PowerFactorL3'])
    pd['meter0/Frequency'] != null && (frequency.value = pd['meter0/Frequency'])
    pd['meter0/Voltage'] != null && (Voltage.value = pd['meter0/Voltage'])
    pd['meter0/VoltageL1'] != null && (VoltageL1.value = pd['meter0/VoltageL1'])
    pd['meter0/VoltageL2'] != null && (VoltageL2.value = pd['meter0/VoltageL2'])
    pd['meter0/VoltageL3'] != null && (VoltageL3.value = pd['meter0/VoltageL3'])
    pd['meter0/VoltageL1L2'] != null && (voltageL1L2.value = pd['meter0/VoltageL1L2'])
    pd['meter0/VoltageL2L3'] != null && (voltageL2L3.value = pd['meter0/VoltageL2L3'])
    pd['meter0/VoltageL3L1'] != null && (voltageL3L1.value = pd['meter0/VoltageL3L1'])
    pd['meter0/VoltageLLAverage'] != null && (voltageLLAverage.value = pd['meter0/VoltageLLAverage'])
    pd['meter0/Current'] != null && (Current.value = pd['meter0/Current'])
    pd['meter0/CurrentL1'] != null && (CurrentL1.value = pd['meter0/CurrentL1'])
    pd['meter0/CurrentL2'] != null && (CurrentL2.value = pd['meter0/CurrentL2'])
    pd['meter0/CurrentL3'] != null && (CurrentL3.value = pd['meter0/CurrentL3'])
  }
}

// Watch for changes in modal visibility and re-subscribe
watch(isModalVisible, () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    subscribeChannels()
  }
})

onMounted(() => {
  if (!ws) {
    console.error('[Dashboard] WebSocket not available.')
    return
  }
  if (auth?.ready) {
    subscribeChannels()
  } else {
    watch(() => auth?.ready, (ready) => {
      if (ready) subscribeChannels()
    }, { once: true })
  }
  onMessage = handleMessage.bind(null)
  ws.addEventListener('message', onMessage)
})

onBeforeUnmount(() => {
  ws?.removeEventListener('message', onMessage)
})
</script>

<style scoped>
.button {
  border: 1px solid #0e91e9;
  border-radius: 6px;
  color: #0e91e9;
  cursor: pointer;
  transition: all 0.3s ease;
}
.button:hover {
  background-color: #07314d;
}
</style>