<template>
  <div class="w-full h-full rounded-lg shadow-lg">
    <div ref="pieContainer" class="w-full" :style="{ height: height + '%' }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  height: { type: Number, default: 100 },
  range: { type: String, default: 'day' }
})

const pieContainer = ref(null)
let pie = null

// Base power ratings in kW with realistic variations by range
const getPowerRatings = (range) => {
  const base = {
    stampingPress: 125.3,
    inductionHeater: 89.7,
    feederMotor: 15.2,
    roboticArmsA: 42.8,
    plcSensorsA: 8.5,
    lightingDoorsA: 12.1,
    chassisMounting: 78.9,
    roboticArmsB: 65.4,
    wiringBenches: 34.7,
    lightingVentB: 28.3,
    plcSensorsB: 9.8,
    relaysB: 6.2
  }
  
  // Apply small proportional variations based on range
  switch(range) {
    case 'week':
      // Slightly different usage patterns for week (e.g., maintenance days, reduced weekends)
      return {
        ...base,
        stampingPress: base.stampingPress * 0.95,  // Slightly less intensive
        inductionHeater: base.inductionHeater * 0.98,
        roboticArmsA: base.roboticArmsA * 1.02,    // Slightly more usage
        chassisMounting: base.chassisMounting * 0.97,
        wiringBenches: base.wiringBenches * 1.03    // More weekend work
      }
    case 'month':
      // Monthly patterns with more variation (e.g., production cycles, maintenance)
      return {
        ...base,
        stampingPress: base.stampingPress * 1.05,  // Peak production periods
        inductionHeater: base.inductionHeater * 0.95,
        feederMotor: base.feederMotor * 1.03,
        roboticArmsB: base.roboticArmsB * 0.98,
        wiringBenches: base.wiringBenches * 0.95,  // Some maintenance downtime
        lightingVentB: base.lightingVentB * 1.02
      }
    default: // day
      return base
  }
}

// Calculate hours based on range
const getHoursForRange = (range) => {
  switch(range) {
    case 'day': return 16  // operating hours per day
    case 'week': return 16 * 7  // 7 days
    case 'month': return 16 * 30  // 30 days
    default: return 16
  }
}

const calculateEnergyData = (range) => {
  const P = getPowerRatings(range)
  const H = getHoursForRange(range)
  
  const E = {
    'Stamping Press': P.stampingPress * H,
    'Induction Heater': P.inductionHeater * H,
    'Feeder Motor': P.feederMotor * H,
    'Robotic Arms A': P.roboticArmsA * H,
    'Chassis Mounting': P.chassisMounting * H,
    'Robotic Arms B': P.roboticArmsB * H,
    'Wiring Benches': P.wiringBenches * H,
    'Control': (P.plcSensorsA + P.plcSensorsB + P.relaysB) * H,
    'Utilities': (P.lightingDoorsA + P.lightingVentB) * H
  }
  
  // Round values to 2 decimal places
  return Object.entries(E).map(([name, value]) => ({ 
    name, 
    value: Math.round(value * 100) / 100 
  }))
}

const data = ref(calculateEnergyData(props.range))
const total = ref(data.value.reduce((s, d) => s + d.value, 0))
const centerTxt = ref(`${(Math.round(total.value * 100) / 100).toFixed(2)}\nkWh`)

const option = {
  backgroundColor: 'transparent',
  color: [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
  ],
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(17,24,39,0.9)',
    borderColor: '#374151',
    textStyle: { color: '#f9fafb' },
    formatter: (p) => `${p.name}<br/><b>${p.value.toFixed(2)} kWh</b> (${p.percent?.toFixed(1)}%)`
  },
  series: [{
    name: 'Energy',
    type: 'pie',
    radius: ['45%', '75%'],
    center: ['50%', '50%'],
    avoidLabelOverlap: true,
    padAngle: 1,
    itemStyle: { 
      borderWidth: 1,
      borderColor: '#1f2937',
      borderRadius: 5
    },
    label: {
      show: true,
      color: '#e5e7eb',
      formatter: '{b|{b}}\n{v|{c} kWh}  {p|({d}%)}',
      rich: {
        b: { fontSize: 11, lineHeight: 16, color: '#e5e7eb' },
        v: { fontSize: 10, color: '#cbd5e1' },
        p: { fontSize: 10, color: '#94a3b8' }
      }
    },
    labelLine: { show: true, length: 8, length2: 8 },
    data: data.value
  }],
  graphic: [{
    type: 'text',
    left: '50%',
    top: '55%',
    style: {
      text: centerTxt.value,
      textAlign: 'center',
      fill: '#e5e7eb',
      fontSize: 14,
      fontWeight: 600
    }
  }]
}

const updateChart = () => {
  data.value = calculateEnergyData(props.range)
  total.value = data.value.reduce((s, d) => s + d.value, 0)
  centerTxt.value = `${(Math.round(total.value * 100) / 100).toFixed(2)}\nkWh`
  
  if (pie) {
    option.series[0].data = data.value
    option.graphic[0].style.text = centerTxt.value
    pie.setOption(option, true)
  }
}

onMounted(() => {
  if (!pieContainer.value) return
  pie = echarts.init(pieContainer.value, 'dark')
  pie.setOption(option)
})

watch(() => props.range, () => {
  updateChart()
})
</script>