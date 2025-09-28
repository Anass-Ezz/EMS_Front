<template>
  <div class="bg-black border-[0px] rounded-[6px] border-gray-700">
    <!-- Manual/Automatic Mode Controls -->
    <div class="flex items-center justify-between p-4 border-b border-gray-700">
      <div class="flex items-center gap-4">
        <label class="flex items-center gap-2 text-orange-300">
          <input 
            type="checkbox" 
            v-model="isManualMode"
            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
          />
          Manual Time Mode
        </label>
        
        <div v-if="isManualMode" class="flex items-center gap-3 text-orange-300">
          <label class="text-sm">Time:</label>
          <input 
            type="number" 
            v-model="manualHour"
            min="0" 
            max="23"
            class="w-16 px-2 py-1 text-black bg-gray-200 rounded text-center"
            placeholder="HH"
          />
          <span>:</span>
          <input 
            type="number" 
            v-model="manualMinute"
            min="0" 
            max="59"
            class="w-16 px-2 py-1 text-black bg-gray-200 rounded text-center"
            placeholder="MM"
          />
        </div>
      </div>
      
      <div class="text-sm text-gray-400">
        {{ isManualMode ? `Manual: ${manualHour.toString().padStart(2, '0')}:${manualMinute.toString().padStart(2, '0')}` : 'Automatic Mode' }}
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-12 items-center p-4">
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
              {{ simulatedData.irradiance }}
              <span class="text-sm">W/m²</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Temperature</p>
            <p class="text-lg font-bold">
              {{ simulatedData.temperature }}
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
              {{ simulatedData.dcPvVoltage }}
              <span class="text-sm">V</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">DC Current</p>
            <p>
              {{ simulatedData.dcPvCurrent }}
              <span class="text-sm">A</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">DC Power</p>
            <p>
              {{ simulatedData.dcPvPower }}
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
              {{ simulatedData.activePower }}
              <span class="text-sm">kW</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Reactive Power</p>
            <p>
              {{ simulatedData.reactivePower }}
              <span class="text-sm">kVAR</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Power Factor</p>
            <p>{{ simulatedData.powerFactor }}</p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Frequency</p>
            <p>
              {{ simulatedData.frequency }}
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
              {{ simulatedData.activePowerL1 }}
              <span class="text-sm">kW</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">L2</p>
            <p>
              {{ simulatedData.activePowerL2 }}
              <span class="text-sm">kW</span>
            </p>
          </div>
          <div>
            <p class="text-xl text-orange-300">L3</p>
            <p>
              {{ simulatedData.activePowerL3 }}
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
            <p>{{ simulatedData.Voltage }}</p>
          </div>
          <div>
            <p class="text-xl text-orange-300">Current</p>
            <p>{{ simulatedData.Current }}</p>
          </div>
        </div>
        <div
          class="flex flex-row gap-6 pt-2 justify-around text-center"
        >
          <div>
            <p class="text-m text-orange-300">L1</p>
            <p>
              {{ simulatedData.VoltageL1 }}<span class="text-sm">V</span>
            </p>
            <p>
              {{ simulatedData.CurrentL1 }}<span class="text-sm">A</span>
            </p>
          </div>
          <div>
            <p class="text-m text-orange-300">L2</p>
            <p>
              {{ simulatedData.VoltageL2 }}<span class="text-sm">V</span>
            </p>
            <p>
              {{ simulatedData.CurrentL2 }}<span class="text-sm">A</span>
            </p>
          </div>
          <div>
            <p class="text-m text-orange-300">L3</p>
            <p>
              {{ simulatedData.VoltageL3 }}<span class="text-sm">V</span>
            </p>
            <p>
              {{ simulatedData.CurrentL3 }}<span class="text-sm">A</span>
            </p>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue';

// Constants from Python script
const AC_P_RATED_KW = 20.0;
const GRID_FREQ_HZ = 50.0;
const AC_V_LL_NOM = 480.0;
const PF_MIN = 0.975;
const PF_MAX = 0.995;
const INV_EFF_MIN = 0.965;
const INV_EFF_MAX = 0.985;
const V_PHASE_NOM = AC_V_LL_NOM / Math.sqrt(3);

// Reactive power sign flip chance
const REACTIVE_SIGN_FLIP_CHANCE = 0.5;

// Simulated data container
const simulatedData = ref({
  irradiance: 0,
  temperature: 25,
  dcPvVoltage: 0,
  dcPvCurrent: 0,
  dcPvPower: 0,
  activePower: 0,
  activePowerL1: 0,
  activePowerL2: 0,
  activePowerL3: 0,
  reactivePower: 0,
  powerFactor: 0,
  frequency: GRID_FREQ_HZ,
  Voltage: AC_V_LL_NOM,
  VoltageL1: V_PHASE_NOM,
  VoltageL2: V_PHASE_NOM,
  VoltageL3: V_PHASE_NOM,
  Current: 0,
  CurrentL1: 0,
  CurrentL2: 0,
  CurrentL3: 0
});

// Animation state
let animationFrameId = null;
let lastUpdateTime = 0;
let currentPower = 0;
let activeEnergy = 0;
let reactiveEnergy = 0;

// Manual/Automatic mode toggle
const isManualMode = ref(false);
const manualHour = ref(12);
const manualMinute = ref(0);

// Helper functions
function getRandom(min, max) {
  return Math.random() * (max - min) + min;
}

function getLocalTime() {
  // Use manual time if in manual mode
  if (isManualMode.value) {
    return {
      hour: manualHour.value,
      minute: manualMinute.value,
      dayOfYear: Math.floor((new Date() - new Date(new Date().getFullYear(), 0, 0)) / 86400000)
    };
  }
  
  // Casablanca timezone offset (UTC+1 during standard time, UTC+0 during DST)
  // For simplicity, we'll use UTC+1 as an approximation
  const now = new Date();
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
  const localTime = new Date(utc + (3600000 * 1)); // UTC+1
  
  return {
    hour: localTime.getHours(),
    minute: localTime.getMinutes(),
    dayOfYear: Math.floor((localTime - new Date(localTime.getFullYear(), 0, 0)) / 86400000)
  };
}

function calculateSolarIrradiance(hour, minute) {
  // Convert to minutes since midnight
  const minutes = hour * 60 + minute;
  
  // Casablanca sunrise/sunset times (approximate for Aug-Oct)
  const sunrise = getRandom(6*60 + 15, 7*60 + 30); // 6:15-7:30
  const sunset = getRandom(18*60 + 15, 19*60 + 30); // 18:15-19:30
  
  if (minutes < sunrise || minutes > sunset) {
    return 0;
  }
  
  // Calculate position in day (0-1)
  const dayProgress = (minutes - sunrise) / (sunset - sunrise);
  
  // Smooth bell curve using cosine
  const irradiance = Math.max(0, Math.sin(Math.PI * dayProgress));
  
  // Apply cloud dips (20% chance of a dip)
  let finalIrradiance = irradiance;
  if (Math.random() < 0.2) {
    const dipDepth = getRandom(0.1, 0.4);
    const dipWidth = getRandom(0.1, 0.3);
    const dipCenter = getRandom(0.3, 0.7);
    
    if (Math.abs(dayProgress - dipCenter) < dipWidth/2) {
      const attenuation = 1 - dipDepth * (1 - Math.abs(dayProgress - dipCenter) / (dipWidth/2));
      finalIrradiance *= attenuation;
    }
  }
  
  // Scale to realistic irradiance (max ~1000 W/m²)
  return Math.round(finalIrradiance * 1000);
}

function calculateTemperature(irradiance) {
  // Base temperature with daily variation
  const baseTemp = 20 + Math.sin(getLocalTime().hour / 24 * Math.PI * 2) * 10;
  
  // Add irradiance effect (more sun = hotter)
  const tempEffect = irradiance * 0.02;
  
  // Add small random variation
  const randomVariation = getRandom(-2, 2);
  
  return Math.round(baseTemp + tempEffect + randomVariation);
}

function calculatePowerTarget(irradiance) {
  // Convert irradiance to theoretical power (20kW system)
  const theoreticalPower = (irradiance / 1000) * AC_P_RATED_KW;
  
  // Apply system efficiency and cloud effects
  const efficiency = getRandom(INV_EFF_MIN, INV_EFF_MAX);
  const cloudFactor = irradiance > 0 ? getRandom(0.7, 1.0) : 0;
  
  return Math.min(AC_P_RATED_KW, theoreticalPower * efficiency * cloudFactor);
}

function splitThreePhases(totalPower) {
  // Add small imbalance between phases
  const imbalance = 0.03;
  const a = getRandom(-imbalance, imbalance);
  const b = getRandom(-imbalance, imbalance);
  const c = -(a + b);
  
  let l1 = Math.max(totalPower * (1/3 + a), 0);
  let l2 = Math.max(totalPower * (1/3 + b), 0);
  let l3 = Math.max(totalPower * (1/3 + c), 0);
  
  // Normalize to maintain total power
  const total = l1 + l2 + l3;
  if (total > 0) {
    l1 = (l1 / total) * totalPower;
    l2 = (l2 / total) * totalPower;
    l3 = (l3 / total) * totalPower;
  }
  
  return [l1, l2, l3];
}

function calculateDcValues(acPower) {
  if (acPower <= 0) {
    // Night values
    return {
      voltage: getRandom(350, 450),
      current: 0,
      power: 0
    };
  }
  
  // Calculate efficiency
  const efficiency = getRandom(INV_EFF_MIN, INV_EFF_MAX);
  const dcPower = acPower / efficiency;
  
  // DC voltage varies with power level
  const midVoltage = 670 + getRandom(-40, 40);
  const spread = 120;
  const normalizedPower = Math.min(acPower / AC_P_RATED_KW, 1.0);
  const voltage = midVoltage + (1 - Math.abs(normalizedPower * 2 - 1)) * spread * 0.3 + getRandom(-10, 10);
  const clampedVoltage = Math.max(520, Math.min(voltage, 760));
  
  const current = dcPower * 1000 / clampedVoltage; // Convert kW to W
  
  return {
    voltage: clampedVoltage,
    current: current,
    power: dcPower
  };
}

function calculateReactivePower(acPower, pf) {
  const phi = Math.acos(Math.max(Math.min(pf, 0.999999), 1e-6));
  let kvar = acPower * Math.tan(phi);
  
  // Randomly flip sign
  if (Math.random() < REACTIVE_SIGN_FLIP_CHANCE) {
    kvar *= -1;
  }
  
  return kvar;
}

function calculateVoltage() {
  const baseVoltage = V_PHASE_NOM * (1 + getRandom(-0.005, 0.005));
  
  // Add occasional sags/swells
  const r = Math.random();
  if (r < 0.0006) {
    return baseVoltage * getRandom(0.96, 0.985); // Sag
  } else if (r < 0.0012) {
    return baseVoltage * getRandom(1.015, 1.04); // Swell
  }
  
  return baseVoltage;
}

function calculateCurrent(power, voltage, pf) {
  if (pf <= 1e-9 || voltage <= 1e-9) return 0;
  return (power * 1000) / (voltage * pf); // kW to W
}

// Animation loop
function animate(timestamp) {
  if (!lastUpdateTime) lastUpdateTime = timestamp;
  const deltaTime = timestamp - lastUpdateTime;
  
  // Update every 1000ms (1 second)
  if (deltaTime >= 1000) {
    updateSimulatedData();
    lastUpdateTime = timestamp;
  }
  
  animationFrameId = requestAnimationFrame(animate);
}

function updateSimulatedData() {
  const { hour, minute } = getLocalTime();
  
  // Calculate irradiance and temperature
  const irradiance = calculateSolarIrradiance(hour, minute);
  const temperature = calculateTemperature(irradiance);
  
  // Calculate power target
  const powerTarget = calculatePowerTarget(irradiance);
  
  // Smooth transition to target power
  const smoothFactor = 0.15;
  currentPower = currentPower + (powerTarget - currentPower) * smoothFactor + getRandom(-0.01, 0.01) * Math.max(powerTarget, 1);
  currentPower = Math.max(0, Math.min(currentPower, AC_P_RATED_KW));
  
  // Split into phases
  const [l1, l2, l3] = splitThreePhases(currentPower);
  
  // Calculate DC values
  const dcValues = calculateDcValues(currentPower);
  
  // Calculate power factor
  let pf = Math.max(PF_MIN, Math.min(PF_MAX, 0.99 + getRandom(-0.007, 0.007)));
  
  // Calculate reactive power
  const reactivePower = calculateReactivePower(currentPower, pf);
  
  // Calculate frequency
  const frequency = GRID_FREQ_HZ + getRandom(-0.02, 0.02);
  
  // Calculate voltages
  const v1 = calculateVoltage();
  const v2 = calculateVoltage();
  const v3 = calculateVoltage();
  const vLL = (v1 + v2 + v3) / 3 * Math.sqrt(3);
  
  // Calculate currents
  const i1 = calculateCurrent(l1, v1, pf);
  const i2 = calculateCurrent(l2, v2, pf);
  const i3 = calculateCurrent(l3, v3, pf);
  const iTotal = i1 + i2 + i3;
  
  // Update energy counters (for completeness, though not displayed)
  activeEnergy += currentPower * 1000 / 60; // Wh per minute
  reactiveEnergy += Math.abs(reactivePower) * 1000 / 60; // varh per minute
  
  // Update simulated data
  simulatedData.value = {
    irradiance,
    temperature,
    dcPvVoltage: Math.round(dcValues.voltage * 10) / 10,
    dcPvCurrent: Math.round(dcValues.current * 100) / 100,
    dcPvPower: Math.round(dcValues.power * 100) / 100,
    activePower: Math.round(currentPower * 100) / 100,
    activePowerL1: Math.round(l1 * 100) / 100,
    activePowerL2: Math.round(l2 * 100) / 100,
    activePowerL3: Math.round(l3 * 100) / 100,
    reactivePower: Math.round(reactivePower * 100) / 100,
    powerFactor: Math.round(pf * 1000) / 1000,
    frequency: Math.round(frequency * 100) / 100,
    Voltage: Math.round(vLL * 10) / 10,
    VoltageL1: Math.round(v1 * 10) / 10,
    VoltageL2: Math.round(v2 * 10) / 10,
    VoltageL3: Math.round(v3 * 10) / 10,
    Current: Math.round(iTotal * 100) / 100,
    CurrentL1: Math.round(i1 * 100) / 100,
    CurrentL2: Math.round(i2 * 100) / 100,
    CurrentL3: Math.round(i3 * 100) / 100
  };
}

// Lifecycle
onMounted(() => {
  // Initial update
  updateSimulatedData();
  
  // Start animation loop
  animationFrameId = requestAnimationFrame(animate);
});

onBeforeUnmount(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
});
</script>

<style scoped>
/* The Tailwind/PrimeVue classes in your HTML handle styling */
</style>