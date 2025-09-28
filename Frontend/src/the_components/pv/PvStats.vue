<template>
  <div
    class="bg-black grid grid-cols-12 items-center border-[0px] rounded-[6px] border-gray-700"
  >
    <div class="col-span-4">
      <img
        src="./../../assets/images/solar_pannel.jpg"
        alt="center image"
        class="rounded-xl h-[260px] object-contain"
      />
    </div>

    <div class="col-span-8 grid grid-cols-12 gap-4">
      <div class="col-span-3 flex flex-col gap-5 justify-around">
        <div
          class="flex flex-row gap-5 text-center justify-center items-center"
        >
          <div>
            <p class="text-xl text-orange-300">Irridance (GHI)</p>
            <p class="text-lg font-bold">
              {{ currentValues.irradiance }}
              <span class="text-sm">W/m²</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Temperature</p>
            <p class="text-lg font-bold">
              {{ currentValues.temperature }}
              <span class="text-sm">°C</span>
            </p>
          </div>
        </div>

        <div
          class="flex flex-row gap-8 text-center justify-center items-center"
        >
          <div>
            <p class="text-xl text-orange-300">DC Voltage</p>
            <p>
              {{ dcPvVoltage }}
              <span class="text-sm">V</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">DC Current</p>
            <p>
              {{ dcPvCurrent }}
              <span class="text-sm">A</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">DC Power</p>
            <p>
              {{ dcPvPower }}
              <span class="text-sm">kW</span>
            </p>
          </div>
        </div>
      </div>

      <!-- ░░░░░░░  Three-phase power section  ░░░░░░░ -->
      <div class="card col-span-6 h-full">
        <div
          class="flex flex-row gap-3 justify-around text-center border-b pb-6 border-gray-700"
        >
          <div>
            <p class="text-xl text-orange-300">Active Power</p>
            <p>
              {{ activePower }}
              <span class="text-sm">kW</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Reactive Power</p>
            <p>
              {{ reactivePower }}
              <span class="text-sm">kVAR</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Power Factor</p>
            <p>{{ powerFactor / 100 }}</p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Frequency</p>
            <p>
              {{ frequency }}
              <span class="text-sm">Hz</span>
            </p>
          </div>
        </div>

        <div
          class="flex flex-row gap-6 justify-around text-center pt-5"
        >
          <div>
            <p class="text-xl text-orange-300">L1</p>
            <p>
              {{ activePowerL1 }}
              <span class="text-sm">kW</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">L2</p>
            <p>
              {{ activePowerL2 }}
              <span class="text-sm">kW</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">L3</p>
            <p>
              {{ activePowerL3 }}
              <span class="text-sm">kW</span>
            </p>
          </div>
        </div>
      </div>

      <!-- ░░░░░░░  Line voltage/current section  ░░░░░░░ -->
      <div class="card col-span-3 mr-2">
        <div
          class="flex flex-row gap-10 justify-around text-center border-b pb-6 h-fit border-cyan-900"
        >
          <div>
            <p class="text-xl text-orange-300">Voltage</p>
            <p>{{ Voltage }}</p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Current</p>
            <p>{{ Current }}</p>
          </div>
        </div>
        <div
          class="flex flex-row gap-6 pt-2 justify-around text-center"
        >
          <div>
            <p class="text-m text-orange-300">L1</p>
            <p>
              198<span class="text-sm">V</span>
            </p>
            <p>
              198<span class="text-sm">A</span>
            </p>
          </div>
          <div>
            <p class="text-m text-orange-300">L2</p>
            <p>
              198<span class="text-sm">V</span>
            </p>
            <p>
              198<span class="text-sm">A</span>
            </p>
          </div>
          <div>
            <p class="text-m text-orange-300">L3</p>
            <p>
              198<span class="text-sm">V</span>
            </p>
            <p>
              198<span class="text-sm">A</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, onBeforeUnmount } from 'vue'
import CircleProgress from '@/the_components/charts/CircleProgress.vue'

// Inject manager and ws, auth
const manager = inject('currentDataManager')
const ws = inject('ws')
const auth = inject('auth')

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen(ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

/* ────────────────────────── Weather state ────────────────────────── */
const currentValues = ref({ irradiance: '-', temperature: '-' })
let weatherIntervalId = null

async function fetchWeatherData() {
  try {
    const url = new URL('https://api.open-meteo.com/v1/forecast')
    const params = {
      latitude: 33.5731,
      longitude: -7.5898,
      current: 'shortwave_radiation,temperature_2m',
      timezone: 'auto'
    }
    Object.keys(params).forEach(key =>
      url.searchParams.append(key, params[key])
    )

    const response = await fetch(url)
    const data = await response.json()

    if (data.current && data.current.time) {
      currentValues.value.irradiance = Math.round(data.current.shortwave_radiation / 3.6)
      currentValues.value.temperature = data.current.temperature_2m
    }
  } catch (error) {
    console.error('Error fetching weather data:', error)
  }
}

/* ────────────────────────── Inverter state ────────────────────────── */
const activePower = ref(0)
const activePowerL1 = ref(0)
const activePowerL2 = ref(0)
const activePowerL3 = ref(0)
const reactivePower = ref(0)
const powerFactor = ref(0)
const frequency = ref(0)

const dcPvPower = ref(0)
const dcPvVoltage = ref(0)
const dcPvCurrent = ref(0)

const Voltage = ref(0)
const VoltageL1 = ref(0)
const VoltageL2 = ref(0)
const VoltageL3 = ref(0)

const Current = ref(0)
const CurrentL1 = ref(0)
const CurrentL2 = ref(0)
const CurrentL3 = ref(0)

// Subscription setup
const subscriberId = crypto.randomUUID()
const edgeId = 'edge0'
const channels = [
  'pvinverter0/ActivePower',
  'pvinverter0/ActivePowerL1',
  'pvinverter0/ActivePowerL2',
  'pvinverter0/ActivePowerL3',
  'pvinverter0/ReactivePower',
  'pvinverter0/PowerFactor',
  'pvinverter0/Frequency',
  'pvinverter0/DcPvVoltage',
  'pvinverter0/DcPvCurrent',
  'pvinverter0/DcPvPower',
  'pvinverter0/Voltage',
  'pvinverter0/VoltageL1',
  'pvinverter0/VoltageL2',
  'pvinverter0/VoltageL3',
  'pvinverter0/Current',
  'pvinverter0/CurrentL1',
  'pvinverter0/CurrentL2',
  'pvinverter0/CurrentL3'
]

function handleData(update) {
  if (update['pvinverter0/ActivePower'] != null) activePower.value = update['pvinverter0/ActivePower']
  if (update['pvinverter0/ActivePowerL1'] != null) activePowerL1.value = update['pvinverter0/ActivePowerL1']
  if (update['pvinverter0/ActivePowerL2'] != null) activePowerL2.value = update['pvinverter0/ActivePowerL2']
  if (update['pvinverter0/ActivePowerL3'] != null) activePowerL3.value = update['pvinverter0/ActivePowerL3']
  if (update['pvinverter0/ReactivePower'] != null) reactivePower.value = update['pvinverter0/ReactivePower']
  if (update['pvinverter0/PowerFactor'] != null) powerFactor.value = update['pvinverter0/PowerFactor']
  if (update['pvinverter0/Frequency'] != null) frequency.value = update['pvinverter0/Frequency']
  if (update['pvinverter0/DcPvVoltage'] != null) dcPvVoltage.value = update['pvinverter0/DcPvVoltage']
  if (update['pvinverter0/DcPvCurrent'] != null) dcPvCurrent.value = update['pvinverter0/DcPvCurrent']
  if (update['pvinverter0/DcPvPower'] != null) dcPvPower.value = update['pvinverter0/DcPvPower']
  if (update['pvinverter0/Voltage'] != null) Voltage.value = update['pvinverter0/Voltage']
  if (update['pvinverter0/VoltageL1'] != null) VoltageL1.value = update['pvinverter0/VoltageL1']
  if (update['pvinverter0/VoltageL2'] != null) VoltageL2.value = update['pvinverter0/VoltageL2']
  if (update['pvinverter0/VoltageL3'] != null) VoltageL3.value = update['pvinverter0/VoltageL3']
  if (update['pvinverter0/Current'] != null) Current.value = update['pvinverter0/Current']
  if (update['pvinverter0/CurrentL1'] != null) CurrentL1.value = update['pvinverter0/CurrentL1']
  if (update['pvinverter0/CurrentL2'] != null) CurrentL2.value = update['pvinverter0/CurrentL2']
  if (update['pvinverter0/CurrentL3'] != null) CurrentL3.value = update['pvinverter0/CurrentL3']
}

onMounted(() => {
  fetchWeatherData()
  weatherIntervalId = setInterval(fetchWeatherData, 30000)
  manager.register(subscriberId, [edgeId], channels, handleData)
})

onBeforeUnmount(() => {
  manager.unregister(subscriberId)
  if (weatherIntervalId) clearInterval(weatherIntervalId)
})
</script>

<style scoped>
/* The Tailwind/PrimeVue classes in your HTML handle styling */
</style>
