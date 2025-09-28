<template>
  <div class="bg-black grid grid-cols-12 items-center border-[0px] rounded-[6px] border-gray-700">
    <div class="col-span-4 relative">
      <img src="./../../assets/images/BESS3.jpg" alt="center image" class="h-[260px] object-contain" />
      <div class="absolute top-[50px] right-[130px] flex flex-col items-center ">
        <p class="text-xl font-bold text-cyan-400">Battery SoC</p>
        <p class="text-4xl font-bold text-center text-cyan-400">
          {{ soc/100 }}<span class="text-sm">%</span>
        </p>
        <CircleProgress 
          :value1="0"
          :value2="soc/100"
          :max="100"
          imagePath="../../src/assets/images/battery.png"
        />
      </div>
    </div>

    <div class="col-span-8 grid grid-cols-12 gap-4 ">
      <div class="col-span-3 flex flex-col justify-around">
        <div class="flex flex-row gap-5 text-center justify-center items-center border-b pb-3 border-gray-700">
          <div>
            <p class="text-cyan-200">Bat Voltage</p>
            <p>{{ batteryPackVoltage }} <span class="text-sm">V</span></p>
          </div>
          <div>
            <p class="text-cyan-200">Bat Current</p>
            <p>{{ batteryPackCurrent }} <span class="text-sm">A</span></p>
          </div>
          <div>
            <p class="text-cyan-200">Bat Capacity</p>
            <p>{{ capacity }} <span class="text-sm">Ah</span></p>
          </div>
        </div>
        <div class="flex flex-row gap-8 text-center justify-center items-center border-b pb-3 border-gray-700">
          <div>
            <p class="text-cyan-200">Max Cell Temp</p>
            <p>{{ maxCellTemperature }} <span class="text-sm">°C</span></p>
          </div>
          <div>
            <p class="text-cyan-200">Min Cell Temp</p>
            <p>{{ minCellTemperature }} <span class="text-sm">°C</span></p>
          </div>
        </div>
        <div class="flex flex-row gap-8 text-center justify-center items-center">
          <div>
            <p class="text-cyan-200">Max Cell Voltage</p>
            <p>{{ maxCellVoltage/1000 }} <span class="text-sm">V</span></p>
          </div>
          <div>
            <p class="text-cyan-200">Min Cell Voltage</p>
            <p>{{ minCellVoltage/1000 }} <span class="text-sm">V</span></p>
          </div>
        </div>
      </div>

      <div class="card col-span-6 h-full">
        <div class="flex flex-row gap-3 justify-around text-center border-b pb-6 border-gray-700">
          <div>
            <p class="text-xl text-cyan-200">Active Power</p>
            <p>{{ activePower }} <span class="text-sm">kW</span></p>
          </div>
          <div>
            <p class="text-xl text-cyan-200">Reactive Power</p>
            <p>{{ reactivePower }} <span class="text-sm">kVAR</span></p>
          </div>
          <div>
            <p class="text-xl text-cyan-200">Power Factor</p>
            <p>{{ powerFactor/100 }}</p>
          </div>
          <div>
            <p class="text-xl text-cyan-200">Frequency</p>
            <p>{{ frequency/10 }} <span class="text-sm">Hz</span></p>
          </div>
        </div>
        <div class="flex flex-row gap-6 justify-around text-center pt-5">
          <div>
            <p class="text-xl text-cyan-200">L1</p>
            <p>{{ activePowerL1 }} <span class="text-sm">kW</span></p>
          </div>
          <div>
            <p class="text-xl text-cyan-200">L2</p>
            <p>{{ activePowerL2 }} <span class="text-sm">kW</span></p>
          </div>
          <div>
            <p class="text-xl text-cyan-200">L3</p>
            <p>{{ activePowerL3 }} <span class="text-sm">kW</span></p>
          </div>
        </div>
      </div>

      <div class="card col-span-3 mr-2">
        <div class="flex flex-row gap-10 justify-around text-center border-b pb-6 h-fit border-cyan-900">
          <div>
            <p class="text-xl text-cyan-200">Voltage</p>
            <p>{{ Voltage }}</p>
          </div>
          <div>
            <p class="text-xl text-cyan-200">Current</p>
            <p>{{ Current }}</p>
          </div>
        </div>
        <div class="flex flex-row gap-6 pt-2 justify-around text-center">
          <div>
            <p class="text-m text-cyan-200">L1</p>
            <p>{{ VoltageL1 }}<span class="text-sm">V</span></p>
            <p>{{ CurrentL1 }}<span class="text-sm">A</span></p>
          </div>
          <div>
            <p class="text-m text-cyan-200">L2</p>
            <p>{{ VoltageL2 }}<span class="text-sm">V</span></p>
            <p>{{ CurrentL2 }}<span class="text-sm">A</span></p>
          </div>
          <div>
            <p class="text-m text-cyan-200">L3</p>
            <p>{{ VoltageL3 }}<span class="text-sm">V</span></p>
            <p>{{ CurrentL3 }}<span class="text-sm">A</span></p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- set points -->
  <div class="grid grid-cols-12 my-2">
    <hr class="col-span-5 border-b border-gray-700">
    <p class="col-span-2 text-center text-2xl font-bold">
      BESS Set points
    </p>
    <hr class="col-span-5 border-b border-gray-700">
  </div>
  <div class="grid grid-cols-11 gap-0 mb-3 pb-3 text-center justify-around border-b border-gray-700">
    <div class="col-span-3 flex flex-row justify-around gap-4 my-0 border-r border-gray-700">
      <div>
        <p class="text-1xl font-bold text-cyan-200">Requested Active Power</p>
        <p class="text-2xl">{{ requestedActivePower }} <span>kWh</span></p>
      </div>
      <div>
        <p class="text-1xl font-bold text-cyan-200">Requested Reactive Power</p>
        <p class="text-2xl">{{ requestedReactivePower }} <span>kWh</span></p>
      </div>
    </div>
    <div class="col-span-3 flex flex-row justify-around gap-4 my-0 border-r border-gray-700">
      <div>
        <p class="text-1xl font-bold text-cyan-200">Max Charging Power</p>
        <p class="text-2xl">{{ maxChargingPower }} <span>kWh</span></p>
      </div>
      <div>
        <p class="text-1xl font-bold text-cyan-200">Max Discharging Power</p>
        <p class="text-2xl">{{ maxDischargingPower }} <span>kWh</span></p>
      </div>
    </div>
    <div class="col-span-3 flex flex-row justify-around gap-4 my-0 border-r border-gray-700">
      <div>
        <p class="text-1xl font-bold text-cyan-200">Global Max SoC</p>
        <p class="text-2xl">{{ globalMaxSoc }} <span>%</span></p>
      </div>
      <div>
        <p class="text-1xl font-bold text-cyan-200">Global Min Soc</p>
        <p class="text-2xl">{{ globalMinSoc }} <span>%</span></p>
      </div>
    </div>
    <div class="col-span-2 flex flex-row justify-around gap-4 my-0">
      <div>
        <p class="text-1xl font-bold text-cyan-200">Ramp Rate</p>
        <p class="text-2xl">{{ rampRate }} <span>kWh/s</span></p>
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref, computed, inject, onMounted, onBeforeUnmount } from 'vue'
import CircleProgress from '@/the_components/charts/CircleProgress.vue'

// Inject WebSocket, auth, and manager
const ws = inject('ws')
const auth = inject('auth')
const manager = inject('currentDataManager')

// Reactive state
const activePower = ref(0)
const activePowerL1 = ref(0)
const activePowerL2 = ref(0)
const activePowerL3 = ref(0)
const reactivePower = ref(0)
const powerFactor = ref(0)
const frequency = ref(0)
const Voltage = ref(0)
const VoltageL1 = ref(0)
const VoltageL2 = ref(0)
const VoltageL3 = ref(0)
const Current = ref(0)
const CurrentL1 = ref(0)
const CurrentL2 = ref(0)
const CurrentL3 = ref(0)
const batteryPackVoltage = ref(0)
const batteryPackCurrent = ref(0)
const capacity = ref(0)
const maxCellVoltage = ref(0)
const minCellVoltage = ref(0)
const maxCellTemperature = ref(0)
const minCellTemperature = ref(0)
const soc = ref(0)
const requestedActivePower = ref(0)
const requestedReactivePower = ref(0)
const maxChargingPower = ref(0)
const maxDischargingPower = ref(0)
const globalMaxSoc = ref(0)
const globalMinSoc = ref(0)
const rampRate = ref(0)

// Computed totals
const currentGeneration = computed(() => activePower.value)

// Subscription setup
const subscriberId = crypto.randomUUID()
const edgeId = 'edge0'
const channels = [
  'ess0/BatteryPackVoltage', 'ess0/BatteryPackCurrent', 'ess0/Capacity',
  'ess0/MaxCellVoltage', 'ess0/MinCellVoltage',
  'ess0/MaxCellTemperature', 'ess0/MinCellTemperature',
  'ess0/Soc',
  'ess0/RequestedActivePower', 'ess0/RequestedReactivePower',
  'ess0/MaxChargingPower', 'ess0/MaxDischargingPower',
  'ess0/GlobalMaxSoc', 'ess0/GlobalMinSoc', 'ess0/RampRate',
  'ess0/ActivePower', 'ess0/ActivePowerL1', 'ess0/ActivePowerL2', 'ess0/ActivePowerL3',
  'ess0/ReactivePower', 'ess0/PowerFactor', 'ess0/Frequency',
  'ess0/Voltage', 'ess0/VoltageL1', 'ess0/VoltageL2', 'ess0/VoltageL3',
  'ess0/Current', 'ess0/CurrentL1', 'ess0/CurrentL2', 'ess0/CurrentL3'
]

function handleData(update) {
  if (update['ess0/BatteryPackVoltage'] != null) batteryPackVoltage.value = update['ess0/BatteryPackVoltage']
  if (update['ess0/BatteryPackCurrent'] != null) batteryPackCurrent.value = update['ess0/BatteryPackCurrent']
  if (update['ess0/Capacity'] != null) capacity.value = update['ess0/Capacity']
  if (update['ess0/MaxCellVoltage'] != null) maxCellVoltage.value = update['ess0/MaxCellVoltage']
  if (update['ess0/MinCellVoltage'] != null) minCellVoltage.value = update['ess0/MinCellVoltage']
  if (update['ess0/MaxCellTemperature'] != null) maxCellTemperature.value = update['ess0/MaxCellTemperature']
  if (update['ess0/MinCellTemperature'] != null) minCellTemperature.value = update['ess0/MinCellTemperature']
  if (update['ess0/Soc'] != null) soc.value = update['ess0/Soc']
  if (update['ess0/RequestedActivePower'] != null) requestedActivePower.value = update['ess0/RequestedActivePower']
  if (update['ess0/RequestedReactivePower'] != null) requestedReactivePower.value = update['ess0/RequestedReactivePower']
  if (update['ess0/MaxChargingPower'] != null) maxChargingPower.value = update['ess0/MaxChargingPower']
  if (update['ess0/MaxDischargingPower'] != null) maxDischargingPower.value = update['ess0/MaxDischargingPower']
  if (update['ess0/GlobalMaxSoc'] != null) globalMaxSoc.value = update['ess0/GlobalMaxSoc']
  if (update['ess0/GlobalMinSoc'] != null) globalMinSoc.value = update['ess0/GlobalMinSoc']
  if (update['ess0/RampRate'] != null) rampRate.value = update['ess0/RampRate']
  if (update['ess0/ActivePower'] != null) activePower.value = update['ess0/ActivePower']
  if (update['ess0/ActivePowerL1'] != null) activePowerL1.value = update['ess0/ActivePowerL1']
  if (update['ess0/ActivePowerL2'] != null) activePowerL2.value = update['ess0/ActivePowerL2']
  if (update['ess0/ActivePowerL3'] != null) activePowerL3.value = update['ess0/ActivePowerL3']
  if (update['ess0/ReactivePower'] != null) reactivePower.value = update['ess0/ReactivePower']
  if (update['ess0/PowerFactor'] != null) powerFactor.value = update['ess0/PowerFactor']
  if (update['ess0/Frequency'] != null) frequency.value = update['ess0/Frequency']
  if (update['ess0/Voltage'] != null) Voltage.value = update['ess0/Voltage']
  if (update['ess0/VoltageL1'] != null) VoltageL1.value = update['ess0/VoltageL1']
  if (update['ess0/VoltageL2'] != null) VoltageL2.value = update['ess0/VoltageL2']
  if (update['ess0/VoltageL3'] != null) VoltageL3.value = update['ess0/VoltageL3']
  if (update['ess0/Current'] != null) Current.value = update['ess0/Current']
  if (update['ess0/CurrentL1'] != null) CurrentL1.value = update['ess0/CurrentL1']
  if (update['ess0/CurrentL2'] != null) CurrentL2.value = update['ess0/CurrentL2']
  if (update['ess0/CurrentL3'] != null) CurrentL3.value = update['ess0/CurrentL3']
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
