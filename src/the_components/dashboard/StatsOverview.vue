<!-- StatsOverview.vue -->
<template>
  <!-- 1 ▸ TOTAL GENERATION ------------------------------------------------- -->
  <div class="col-span-12 lg:col-span-6 xl:col-span-2">
    <span class="block text-secondary-color font-bold mb-3 text-[15px]">Total Generation</span>
    <div class="card mb-0">
      <div class="flex justify-between">
        <div>

          <div class="text-green-700 text-lg">Available Power</div>
          <span class="text-green-500 text-xl font-bold">
            {{ availableGeneration }} Kw
            <!-- {{ formatPower(availableGeneration) }} -->
          </span>

          <div class="text-orange-700 text-lg">Current Power</div>
          <span class="text-orange-500 text-xl font-bold">
            {{ currentGeneration}} kW
            <!-- {{ formatPower(currentGeneration) }} -->
          </span>
        </div>

        <CircleProgress
          :value1="availableGeneration"
          :value2="currentGeneration"
          :max="4000"
          imagePath="../../src/assets/images/electricity.png"
        />
      </div>
    </div>
  </div>

  <!-- 2 ▸ SOLAR GENERATION ------------------------------------------------- -->
  <div class="col-span-12 lg:col-span-6 xl:col-span-2">
    <span class="block text-secondary-color font-bold mb-3 text-[15px]">Solar Generation</span>
    <div class="card mb-0">
      <div class="flex justify-between">
        <div>

          <div class="text-green-700 text-lg">Available Power</div>
          <span class="text-green-500 text-xl font-bold">
            {{ solarCapacity }} kW
            <!-- {{ formatPower(solarCapacity) }} -->
          </span>

          <div class="text-orange-700 text-lg">Current Power</div>
          <span class="text-orange-500 text-xl font-bold">
            {{ solarActual }} kW
            <!-- {{ formatPower(solarActual) }} -->
          </span>
        </div>

        <CircleProgress
          :value1="solarCapacity"
          :value2="solarActual"
          :max="solarMax"
          imagePath="../../src/assets/images/solar.png"
        />
      </div>
    </div>
  </div>

  <!-- 3 ▸ WIND GENERATION -------------------------------------------------- -->
  <div class="col-span-12 lg:col-span-6 xl:col-span-2">
    <span class="block text-secondary-color font-bold mb-3 text-[15px]">Wind Generation</span>
    <div class="card mb-0">
      <div class="flex justify-between">
        <div>
          <div class="text-green-700 text-lg">Available Power</div>
          <span class="text-green-500 text-xl font-bold">
            {{ windCapacity }} kW
            <!-- {{ formatPower(windCapacity) }} -->
          </span>

          <div class="text-orange-700 text-lg">Current Power</div>
          <span class="text-orange-500 text-xl font-bold">
            {{ windActual }} kW
            <!-- {{ formatPower(windActual) }} -->
          </span>
        </div>

        <CircleProgress
          :value1="windCapacity"
          :value2="windActual"
          :max="windMax"
          imagePath="../../src/assets/images/wind.png"
        />
      </div>
    </div>
  </div>

  <!-- 4 ▸ BATTERY ---------------------------------------------------------- -->
  <div class="col-span-12 lg:col-span-6 xl:col-span-3">
    <span class="block text-secondary-color font-bold mb-3 text-[15px]">Battery</span>
    <div class="card mb-0">
      <div class="flex justify-between">
          <div class="flex gap-10 my-5">
            <div>
              <div class="text-green-700 font-medium text-2xl mb-3">Power</div>
              <div class="text-green-500 font-bold text-xl">
                {{ batteryPower}} kW
                <!-- {{ formatPower(batteryPower) }} -->
              </div>
            </div>
            <div>
              <div class="text-orange-700 text-2xl mb-3">SoC</div>
              <span class="text-orange-500 font-bold text-xl">
                {{ batterySoC.toFixed(0) }} %
              </span>
            </div>
          </div>

        <CircleProgress
          :value1="0"
          :value2="batterySoC"
          :max="100"
          imagePath="../../src/assets/images/battery.png"
        />
      </div>
    </div>
  </div>

  <!-- 5 ▸ CONSUMPTION ------------------------------------------------------ -->
  <div class="col-span-12 lg:col-span-6 xl:col-span-3">
    <span class="block text-secondary-color font-bold mb-3 text-[15px]">Export</span>
    <div class="card mb-0">
      <div class="flex justify-between">
        <div>

          <div class="flex gap-5 mt-5 mb-6">
            <div>
              <div class="text-green-700 font-medium text-xl mb-3">
                Active Power
              </div>
              <div class="text-green-500 font-bold text-xl">
                <!-- {{ formatPower(consumptionActive) }} -->
                {{ consumptionActive}} kW
              </div>
            </div>
            <div>
              <div class="text-orange-700 text-xl mb-3">
                Reactive Power
              </div>
              <span class="text-orange-500 font-bold text-xl">
                {{ consumptionReactive }} kVAR
                <!-- {{ formatReactivePower(consumptionReactive) }} -->
                
              </span>
            </div>
          </div>
        </div>
        <a href="/consumption">

          <CircleProgress
            :value1="0"
            :value2="0"
            :max="1"
            imagePath="../../src/assets/images/grid.png"
          />
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import CircleProgress from '@/the_components/charts/CircleProgress.vue'
import { computed, defineEmits, inject, onBeforeUnmount, onMounted, ref } from 'vue'

// =================================================================================
// HELPER FUNCTIONS FOR POWER UNIT SCALING
// =================================================================================
/**
 * Formats an active power value with appropriate units for display (W, kW, MW).
 * Assumes the input value is in Watts.
 * @param {number | null} value - The power value in Watts.
 * @returns {string} The formatted string.
 */
function formatPower(value) {
  if (value === null || typeof value === 'undefined') {
    return '---'
  }
  const absValue = Math.abs(value)

  if (absValue < 1000) {
    return value.toFixed(0) + ' W'
  } else if (absValue < 1000000) {
    return (value / 1000).toFixed(2) + ' kW'
  } else {
    return (value / 1000000).toFixed(2) + ' MW'
  }
}

/**
 * Formats a reactive power value with appropriate units for display (var, kVAR, MVAR).
 * Assumes the input value is in Volt-Amperes Reactive.
 * @param {number | null} value - The power value in var.
 * @returns {string} The formatted string.
 */
function formatReactivePower(value) {
  if (value === null || typeof value === 'undefined') {
    return '---'
  }
  const absValue = Math.abs(value)

  if (absValue < 1000) {
    return value.toFixed(0) + ' var'
  } else if (absValue < 1000000) {
    return (value / 1000).toFixed(2) + ' kVAR'
  } else {
    return (value / 1000000).toFixed(2) + ' MVAR'
  }
}
// =================================================================================

/* ────────────────────────── Reactive state ────────────────────────── */
const solarActual = ref(0)
const solarCapacity = ref(0)
const solarMax = ref(0)
const windActual = ref(0)
const windCapacity = ref(0)
const windMax = ref(0)
const batterySoC = ref(0)
const batteryPower = ref(0)
const consumptionActive = ref(0)
const consumptionReactive = ref(0)

/* Derived totals */
const currentGeneration = computed(() => solarActual.value + windActual.value + batteryPower.value)
const availableGeneration = computed(() => solarCapacity.value + windCapacity.value)

/* ─────────────────────── Subscription via manager ───────────────────── */
const manager = inject('currentDataManager')
const subscriberId = crypto.randomUUID()
const edges = ['edge0']
const channels = [
  'pvinverter0/ActivePower',
  'pvinverter0/MaxActivePower',
  'pvinverter0/DcPvPower',
  'windturbine0/ActivePower',
  'windturbine0/MaxPower',
  'windturbine0/MaxWindPower',
  'ess0/Soc',
  'ess0/ActivePower',
  'meter0/ActivePower',
  'meter0/ReactivePower'
]

// Define the custom event that this component can emit
const emit = defineEmits(['update:flowData'])

function handleData(update) {
  if (update['pvinverter0/DcPvPower'] != null) solarCapacity.value = update['pvinverter0/DcPvPower']
  if (update['pvinverter0/ActivePower'] != null) solarActual.value = update['pvinverter0/ActivePower']
  if (update['pvinverter0/MaxActivePower'] != null) solarMax.value = update['pvinverter0/MaxActivePower']
  if (update['windturbine0/ActivePower'] != null) windActual.value = update['windturbine0/ActivePower']
  if (update['windturbine0/MaxWindPower'] != null) windCapacity.value = update['windturbine0/MaxWindPower']
  if (update['windturbine0/MaxPower'] != null) windMax.value = update['windturbine0/MaxPower']
  if (update['ess0/Soc'] != null) batterySoC.value = update['ess0/Soc'] / 100
  if (update['ess0/ActivePower'] != null) batteryPower.value = update['ess0/ActivePower']
  if (update['meter0/ActivePower'] != null) consumptionActive.value = update['meter0/ActivePower']
  if (update['meter0/ReactivePower'] != null) consumptionReactive.value = update['meter0/ReactivePower']

  // Emit the data up to the parent AFTER all relevant reactive variables are updated
  emit('update:flowData', {
    solarPower: solarActual.value,
    windPower: windActual.value,
    batteryPower: batteryPower.value,
    consumptionPower: consumptionActive.value,
  })
}

onMounted(() => {
  manager.register(subscriberId, edges, channels, handleData)
})

onBeforeUnmount(() => {
  manager.unregister(subscriberId)
})
</script>

<style scoped>
/* The Tailwind/PrimeVue classes in your HTML handle styling */
</style>