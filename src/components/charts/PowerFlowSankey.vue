<template>
  <div class="w-full h-full rounded-lg shadow-lg p-2">
    <div ref="chartContainer" class="w-full" :style="{ height: chartHeight + 'px' }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  height: { type: Number, default: 800 },
  autoRefresh: { type: Boolean, default: true },
  refreshInterval: { type: Number, default: 5000 }
})

const chartContainer = ref(null)
const chart = ref(null)
const refreshTimer = ref(null)
const chartHeight = computed(() => props.height)

// Current power values that will be updated (kW) - starting near max ratings
const powerData = ref({
  // Workshop A equipment (LV + HV)
  stampingPress: 450,    // Max 500kW
  inductionHeater: 420,  // Max 500kW
  feederMotor: 22,       // Max 25kW
  roboticArms: 85,       // Max 100kW
  largeWelder: 42,       // Max 50kW
  plcSensors: 9,         // Max 10kW (part of controlA)
  lightingDoors: 18,     // Max 20kW (part of utilitiesA)

  // Workshop B equipment (LV)
  chassisMounting: 90,   // Max 100kW
  roboticArmsB: 72,      // Max 80kW
  wiringBenches: 22,     // Part of utilitiesB
  lightingVentilation: 20, // Part of utilitiesB
  plcSensorsB: 4.5,      // Max 5kW (part of controlB)
  relaysB: 4.8,          // Part of controlB

  // Solar
  centralInverter: 120   // Max 150kW
})

// Helper functions for small, realistic fluctuations
function fluctuatePower(currentValue, maxValue, variation = 0.03) {
  // Small fluctuations +/- 3% around current value
  const variationFactor = 1 + (Math.random() - 0.5) * variation
  const newValue = currentValue * variationFactor
  // Keep within reasonable bounds near max rating
  const minVal = maxValue * 0.7  // 70% of max
  const maxVal = maxValue * 1.05 // 105% of max (slight buffer)
  return Math.max(minVal, Math.min(maxVal, newValue))
}

// Base helper sums (keeping your original structure)
const aHV = computed(() =>
  powerData.value.stampingPress + powerData.value.inductionHeater
)
const aLV = computed(() =>
  powerData.value.feederMotor +
  powerData.value.roboticArms +
  powerData.value.largeWelder +
  powerData.value.plcSensors +
  powerData.value.lightingDoors
)
const bLV = computed(() =>
  powerData.value.chassisMounting +
  powerData.value.roboticArmsB +
  powerData.value.wiringBenches +
  powerData.value.lightingVentilation +
  powerData.value.plcSensorsB +
  powerData.value.relaysB
)

// New grouping sums (keeping your original structure)
const aControl = computed(() => powerData.value.plcSensors) // A: PLC/Sensors
const aUtilities = computed(() => powerData.value.lightingDoors) // A: Lighting/Doors

const bControl = computed(() => powerData.value.plcSensorsB + powerData.value.relaysB) // B: PLC/Sensors/Relays
const bUtilities = computed(() => powerData.value.lightingVentilation) // B: Lighting/Vent

// PV routing logic: PV meets A-LV first
const pvToALV = computed(() => Math.min(powerData.value.centralInverter, aLV.value))
const gridToALV = computed(() => Math.max(0, aLV.value - pvToALV.value))

// Grid-side transformer loads
const transformerAFromGrid = computed(() => aHV.value + gridToALV.value)
const transformerBFromGrid = computed(() => bLV.value)

// What the MV grid actually supplies
const mvGridSupply = computed(() => transformerAFromGrid.value + transformerBFromGrid.value)

const totalPower = computed(() => aHV.value + aLV.value + bLV.value)

const generateChartData = () => {
  // Node names
  const nMV = `MV Grid Supply ${mvGridSupply.value.toFixed(1)} kW`
  const nTraA = `MV/MV Transformer ${(transformerAFromGrid.value).toFixed(1)} kW`
  const nTraB = `MV/LV Transformer ${(transformerBFromGrid.value).toFixed(1)} kW`
  const nPV = `Central Inverter ${powerData.value.centralInverter.toFixed(1)} kW`

  const nAHV = `Workshop A HV ${aHV.value.toFixed(1)} kW`
  const nALV = `Workshop A LV ${aLV.value.toFixed(1)} kW`
  const nBLV = `Workshop B LV ${bLV.value.toFixed(1)} kW`

  // Equipment leaves that remain explicit
  const nStamp = `Stamping Press ${powerData.value.stampingPress.toFixed(1)} kW`
  const nInd = `Induction Heater ${powerData.value.inductionHeater.toFixed(1)} kW`
  const nFeed = `Feeder Motor ${powerData.value.feederMotor.toFixed(1)} kW`
  const nArmsA = `Robotic Arms A ${powerData.value.roboticArms.toFixed(1)} kW`
  const nChas = `Chassis Mounting ${powerData.value.chassisMounting.toFixed(1)} kW`
  const nArmsB = `Robotic Arms B ${powerData.value.roboticArmsB.toFixed(1)} kW`
  const nWire = `Wiring Benches ${powerData.value.wiringBenches.toFixed(1)} kW`

  // NEW grouped category nodes
  const nControlA = `Control A ${aControl.value.toFixed(1)} kW`
  const nUtilitiesA = `Utilities A ${aUtilities.value.toFixed(1)} kW`
  const nControlB = `Control B ${bControl.value.toFixed(1)} kW`
  const nUtilitiesB = `Utilities B ${bUtilities.value.toFixed(1)} kW`

  const nodes = [
    { name: nMV, depth: 0 },
    { name: nPV, depth: 1 },
    { name: nTraA, depth: 1 },
    { name: nTraB, depth: 1 },

    { name: nAHV, depth: 2 },
    { name: nALV, depth: 2 },
    { name: nBLV, depth: 2 },

    // Workshop A leaves
    { name: nStamp, depth: 3 },
    { name: nInd, depth: 3 },
    { name: nFeed, depth: 3 },
    { name: nArmsA, depth: 3 },
    { name: nControlA, depth: 3 },
    { name: nUtilitiesA, depth: 3 },

    // Workshop B leaves
    { name: nChas, depth: 3 },
    { name: nArmsB, depth: 3 },
    { name: nWire, depth: 3 },
    { name: nControlB, depth: 3 },
    { name: nUtilitiesB, depth: 3 }
  ]

  const links = [
    // MV grid into transformers
    { source: nMV, target: nTraA, value: transformerAFromGrid.value },
    { source: nMV, target: nTraB, value: transformerBFromGrid.value },

    // Transformer A to A sections
    { source: nTraA, target: nAHV, value: aHV.value },
    { source: nTraA, target: nALV, value: gridToALV.value },

    // PV to A-LV
    { source: nPV, target: nALV, value: pvToALV.value },

    // Transformer B to B-LV
    { source: nTraB, target: nBLV, value: bLV.value },

    // A-LV breakdown
    { source: nALV, target: nFeed, value: powerData.value.feederMotor },
    { source: nALV, target: nArmsA, value: powerData.value.roboticArms },
    { source: nALV, target: nControlA, value: aControl.value },
    { source: nALV, target: nUtilitiesA, value: aUtilities.value },

    // A-HV breakdown
    { source: nAHV, target: nStamp, value: powerData.value.stampingPress },
    { source: nAHV, target: nInd, value: powerData.value.inductionHeater },

    // B-LV breakdown
    { source: nBLV, target: nChas, value: powerData.value.chassisMounting },
    { source: nBLV, target: nArmsB, value: powerData.value.roboticArmsB },
    { source: nBLV, target: nWire, value: powerData.value.wiringBenches },
    { source: nBLV, target: nControlB, value: bControl.value },
    { source: nBLV, target: nUtilitiesB, value: bUtilities.value }
  ]

  return { nodes, links }
}

const chartOptions = computed(() => {
  const { nodes, links } = generateChartData()
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(17,24,39,0.9)',
      borderColor: '#374151',
      textStyle: { color: '#f9fafb' },
      formatter: (p) =>
        p.dataType === 'edge'
          ? `${p.data.source} → ${p.data.target}<br/>${p.data.value.toFixed(1)} kW`
          : p.data.name
    },
    series: [{
      type: 'sankey',
      orient: 'horizontal',
      nodeAlign: 'left',
      nodeGap: 20,
      nodeWidth: 5,
      layoutIterations: 96,
      data: nodes,
      links: links,
      lineStyle: { color: 'gradient', curveness: 0.25 },
      itemStyle: { borderWidth: 1, borderColor: '#4b5563' },
      label: { color: '#e5e7eb', fontSize: 11 },
      levels: [
        { depth: 0, itemStyle: { color: '#f59e0b' } }, // MV
        { depth: 1, itemStyle: { color: '#60a5fa' } }, // Transformers / PV
        { depth: 2, itemStyle: { color: '#34d399' } }, // Section buses
        { depth: 3, itemStyle: { color: '#a78bfa' } }  // Equipment & grouped nodes
      ]
    }]
  }
})

// Simulate real-time data changes with small, coherent fluctuations
const refreshData = () => {
  // Workshop A equipment (small fluctuations near max ratings)
  powerData.value.stampingPress = fluctuatePower(powerData.value.stampingPress, 500)
  powerData.value.inductionHeater = fluctuatePower(powerData.value.inductionHeater, 500)
  powerData.value.roboticArms = fluctuatePower(powerData.value.roboticArms, 100)
  powerData.value.largeWelder = fluctuatePower(powerData.value.largeWelder, 50)
  powerData.value.feederMotor = fluctuatePower(powerData.value.feederMotor, 25)
  powerData.value.plcSensors = fluctuatePower(powerData.value.plcSensors, 10)
  powerData.value.lightingDoors = fluctuatePower(powerData.value.lightingDoors, 20)

  // Workshop B equipment (small fluctuations near max ratings)
  powerData.value.chassisMounting = fluctuatePower(powerData.value.chassisMounting, 100)
  powerData.value.roboticArmsB = fluctuatePower(powerData.value.roboticArmsB, 80)
  powerData.value.wiringBenches = fluctuatePower(powerData.value.wiringBenches, 25)
  powerData.value.lightingVentilation = fluctuatePower(powerData.value.lightingVentilation, 25)
  powerData.value.plcSensorsB = fluctuatePower(powerData.value.plcSensorsB, 5)
  powerData.value.relaysB = fluctuatePower(powerData.value.relaysB, 5)

  // Solar PV (larger fluctuations but still reasonable)
  const pvVariation = 1 + (Math.random() - 0.5) * 0.1 // +/- 5%
  powerData.value.centralInverter = Math.max(0, Math.min(150, powerData.value.centralInverter * pvVariation))
}

const initChart = () => {
  if (!chartContainer.value) return
  chart.value = echarts.init(chartContainer.value, 'dark')
  chart.value.setOption(chartOptions.value)
}

const updateChart = () => { if (chart.value) chart.value.setOption(chartOptions.value) }

const setupAutoRefresh = () => {
  if (props.autoRefresh) {
    refreshTimer.value = setInterval(() => refreshData(), props.refreshInterval)
  }
}

const clearAutoRefresh = () => {
  if (refreshTimer.value) { clearInterval(refreshTimer.value); refreshTimer.value = null }
}

watch(chartOptions, updateChart, { deep: true })

const handleResize = () => { if (chart.value) chart.value.resize() }

onMounted(() => { initChart(); setupAutoRefresh(); window.addEventListener('resize', handleResize) })
onUnmounted(() => { clearAutoRefresh(); if (chart.value) chart.value.dispose(); window.removeEventListener('resize', handleResize) })
</script>