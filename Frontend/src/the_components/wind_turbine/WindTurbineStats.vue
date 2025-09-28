<template>
  <div
    class="bg-black grid grid-cols-12 items-center border-[0px] rounded-[6px] border-gray-700"
  >
    <div class="col-span-4">
      <img
        src="./../../assets/images/windturbine.png"
        alt="center image"
        class="rounded-xl h-[260px] object-contain"
      />
    </div>
    <div class="col-span-8 grid grid-cols-12 gap-4 ">
      <div class="col-span-3 flex flex-col gap-5 justify-around">
        <div class="flex flex-row gap-5 text-center justify-center items-center">
          <div>
            <p class="text-xl text-green-300">Wind Speed</p>
            <p class="text-lg font-bold">{{ windSpeed }} <span class="text-sm">m/s</span></p>
          </div>
          <div>
            <p class="text-xl text-green-300">Pitch Angle</p>
            <p class="text-lg font-bold">{{ pitchAngle }} <span class="text-sm">°</span></p>
          </div>
        </div>
        <div class="flex flex-row gap-8 text-center justify-center items-center">
          <div>
            <p class="text-xl text-green-300">Wind Power</p>
            <p>{{ maxWindPower }} <span class="text-sm">kW</span></p>
          </div>
        </div>
      </div>
      <div class="card col-span-6 h-full">
        <div class="flex flex-row gap-3 justify-around text-center border-b pb-6 border-gray-700">
          <div>
            <p class="text-xl text-green-300">Active Power</p>
            <p>{{ activePower }} <span class="text-sm">kW</span></p>
          </div>
          <div>
            <p class="text-xl text-green-300">Reactive Power</p>
            <p>{{ reactivePower }} <span class="text-sm">kVAR</span></p>
          </div>
          <div>
            <p class="text-xl text-green-300">Power Factor</p>
            <p>{{ powerFactor/100 }}</p>
          </div>
          <div>
            <p class="text-xl text-green-300">Frequency</p>
            <p>{{ frequency/10 }} <span class="text-sm">Hz</span></p>
          </div>
        </div>
        <div class="flex flex-row gap-6 justify-around text-center pt-5">
          <div>
            <p class="text-xl text-green-300">L1</p>
            <p>{{ activePowerL1 }} <span class="text-sm">kW</span></p>
          </div>
          <div>
            <p class="text-xl text-green-300">L2</p>
            <p>{{ activePowerL2 }} <span class="text-sm">kW</span></p>
          </div>
          <div>
            <p class="text-xl text-green-300">L3</p>
            <p>{{ activePowerL3 }} <span class="text-sm">kW</span></p>
          </div>
        </div>
      </div>
      <div class="card col-span-3 mr-2">
        <div class="flex flex-row gap-10 justify-around text-center border-b pb-6 h-fit border-cyan-900">
          <div>
            <p class="text-xl text-green-300">Voltage</p>
            <p>{{ Voltage }}</p>
          </div>
          <div>
            <p class="text-xl text-green-300">Current</p>
            <p>{{ Current }}</p>
          </div>
        </div>
        <div class="flex flex-row gap-6 pt-2 justify-around text-center">
          <div>
            <p class="text-m text-green-300">L1</p>
            <p>198<span class="text-sm">V</span></p>
            <p>198<span class="text-sm">A</span></p>
          </div>
          <div>
            <p class="text-m text-green-300">L2</p>
            <p>198<span class="text-sm">V</span></p>
            <p>198<span class="text-sm">A</span></p>
          </div>
          <div>
            <p class="text-m text-green-300">L3</p>
            <p>198<span class="text-sm">V</span></p>
            <p>198<span class="text-sm">A</span></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, onBeforeUnmount } from 'vue'
import CircleProgress from '@/the_components/charts/CircleProgress.vue'

/* ────────────────────────── Reactive state ────────────────────────── */
const activePower     = ref(0)
const activePowerL1   = ref(0)
const activePowerL2   = ref(0)
const activePowerL3   = ref(0)
const reactivePower   = ref(0)
const powerFactor     = ref(0)
const frequency       = ref(0)

const maxWindPower    = ref(0)
const windSpeed       = ref(0)
const pitchAngle      = ref(0)

const Voltage         = ref(0)
const VoltageL1       = ref(0)
const VoltageL2       = ref(0)
const VoltageL3       = ref(0)

const Current         = ref(0)
const CurrentL1       = ref(0)
const CurrentL2       = ref(0)
const CurrentL3       = ref(0)

/* ───────────────── Subscription via manager ───────────────── */
const manager      = inject('currentDataManager')
const edgeId       = 'edge0'
const subscriberId = crypto.randomUUID()
const channels     = [
  'windturbine0/ActivePower',
  'windturbine0/ActivePowerL1',
  'windturbine0/ActivePowerL2',
  'windturbine0/ActivePowerL3',
  'windturbine0/ReactivePower',
  'windturbine0/PowerFactor',
  'windturbine0/Frequency',
  'windturbine0/MaxWindPower',
  'windturbine0/WindSpeed',
  'windturbine0/PitchAngle',
  'windturbine0/Voltage',
  'windturbine0/VoltageL1',
  'windturbine0/VoltageL2',
  'windturbine0/VoltageL3',
  'windturbine0/Current',
  'windturbine0/CurrentL1',
  'windturbine0/CurrentL2',
  'windturbine0/CurrentL3'
]

function handleData(update) {
  if (update['windturbine0/ActivePower']    != null) activePower.value    = update['windturbine0/ActivePower']
  if (update['windturbine0/ActivePowerL1'] != null) activePowerL1.value  = update['windturbine0/ActivePowerL1']
  if (update['windturbine0/ActivePowerL2'] != null) activePowerL2.value  = update['windturbine0/ActivePowerL2']
  if (update['windturbine0/ActivePowerL3'] != null) activePowerL3.value  = update['windturbine0/ActivePowerL3']

  if (update['windturbine0/ReactivePower'] != null) reactivePower.value  = update['windturbine0/ReactivePower']
  if (update['windturbine0/PowerFactor']   != null) powerFactor.value    = update['windturbine0/PowerFactor']
  if (update['windturbine0/Frequency']     != null) frequency.value      = update['windturbine0/Frequency']

  if (update['windturbine0/MaxWindPower']  != null) maxWindPower.value   = update['windturbine0/MaxWindPower']
  if (update['windturbine0/WindSpeed']     != null) windSpeed.value      = update['windturbine0/WindSpeed']
  if (update['windturbine0/PitchAngle']    != null) pitchAngle.value     = update['windturbine0/PitchAngle']

  if (update['windturbine0/Voltage']      != null) Voltage.value        = update['windturbine0/Voltage']
  if (update['windturbine0/VoltageL1']    != null) VoltageL1.value      = update['windturbine0/VoltageL1']
  if (update['windturbine0/VoltageL2']    != null) VoltageL2.value      = update['windturbine0/VoltageL2']
  if (update['windturbine0/VoltageL3']    != null) VoltageL3.value      = update['windturbine0/VoltageL3']

  if (update['windturbine0/Current']      != null) Current.value        = update['windturbine0/Current']
  if (update['windturbine0/CurrentL1']    != null) CurrentL1.value      = update['windturbine0/CurrentL1']
  if (update['windturbine0/CurrentL2']    != null) CurrentL2.value      = update['windturbine0/CurrentL2']
  if (update['windturbine0/CurrentL3']    != null) CurrentL3.value      = update['windturbine0/CurrentL3']
}

onMounted(() => {
  manager.register(subscriberId, [edgeId], channels, handleData)
})

onBeforeUnmount(() => {
  manager.unregister(subscriberId)
})
</script>

<style scoped>
/* The Tailwind/PrimeVue classes in your HTML handle styling */
</style>
