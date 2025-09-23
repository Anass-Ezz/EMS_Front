<!-- src/components/charts/PhasorChart.vue -->
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue'
import * as echarts from 'echarts/core'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { LineChart, ScatterChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([GridComponent, TooltipComponent, LegendComponent, LineChart, ScatterChart, CanvasRenderer])

type LeadLag = 'lead' | 'lag'

// ✅ REMOVED `currentScale` from props — now computed internally
const props = withDefaults(defineProps<{
  vMag: [number, number, number]
  iMag: [number, number, number]
  pf: [number, number, number]
  pfSign?: [LeadLag, LeadLag, LeadLag]
  voltageIsLineToLine?: boolean
  voltageAngles?: [number, number, number]
}>(), {
  pfSign: () => ['lag','lag','lag'],
  voltageIsLineToLine: false
})

const deg2rad = (d: number) => d * Math.PI / 180
const vAnglesDeg = computed<[number, number, number]>(() =>
  props.voltageAngles ?? [0, -120, 120]
)

function pfToAngleDeg(pf: number, sign: LeadLag): number {
  const clamped = Math.max(0, Math.min(1, pf))
  const phi = Math.acos(clamped) * 180 / Math.PI
  return sign === 'lag' ? -phi : +phi
}

function phasorXY(mag: number, angleDeg: number) {
  const th = deg2rad(angleDeg)
  return [mag * Math.cos(th), mag * Math.sin(th)]
}

function buildOption() {
  const vPhaseMag = (props.voltageIsLineToLine
    ? props.vMag.map(v => v / Math.sqrt(3))
    : props.vMag) as [number, number, number]

  const iAnglesDeg = vAnglesDeg.value.map((va, i) => va + pfToAngleDeg(props.pf[i], props.pfSign![i]))

  const maxV = Math.max(...vPhaseMag)
  const maxI = Math.max(...props.iMag)

  // ✅ DYNAMIC CURRENT SCALE — auto-adjust so current arrows are ~70% length of voltage arrows
  const TARGET_RATIO = 0.7 // You can tweak this (e.g., 0.5 for smaller, 0.9 for larger)
  const IScale = maxI > 0 ? (maxV * TARGET_RATIO) / maxI : 1

  const maxLen = Math.max(maxV, maxI * IScale) || 1
  const pad = 1.1 // Slight padding for labels

  const vNames = ['Va', 'Vb', 'Vc']
  const iNames = ['Ia', 'Ib', 'Ic']

  // Use same colors for voltage and corresponding current
  const vColors = ['#f43f5e', '#60a5fa', '#34d399'] // rose-500, blue-400, emerald-400

  // Enhanced arrowhead with proper tooltip
  const arrowHead = (
    name: string,
    x: number,
    y: number,
    color: string,
    angleDeg: number,
    magnitude: number,
    isVoltage: boolean
  ) => ({
    name: `${name}_arrow`,
    type: 'scatter',
    data: [[x, y]],
    symbol: 'path://M0,0 L10,5 L0,10 Z',
    symbolSize: 13,
    symbolRotate: angleDeg,
    itemStyle: { color },
    tooltip: {
      show: true,
      trigger: 'item',
      backgroundColor: 'rgba(31,41,55,0.95)',
      borderColor: '#374151',
      borderWidth: 1,
      textStyle: { color: '#e5e7eb', fontSize: 12 },
      formatter: () => {
        const unit = isVoltage ? 'V' : 'A'
        return `<b>${name}</b><br/>|M| = ${magnitude.toFixed(2)} ${unit}<br/>∠ = ${angleDeg.toFixed(1)}°`
      }
    },
    z: 5
  })

  const series: any[] = []

  // Reference ring (very faint)
  series.push({
    name: 'Reference Circle',
    type: 'line',
    data: Array.from({ length: 361 }, (_, d) => {
      const r = maxLen
      return [r * Math.cos(deg2rad(d)), r * Math.sin(deg2rad(d))]
    }),
    lineStyle: { width: 1, color: 'rgba(148,163,184,0.15)' },
    showSymbol: false,
    tooltip: { show: false },
    z: 0
  })

  // Origin dot
  series.push({
    name: 'Origin',
    type: 'scatter',
    data: [[0, 0]],
    symbol: 'circle',
    symbolSize: 6,
    itemStyle: { color: '#94a3b8' },
    tooltip: { show: false },
    z: 6
  })

  // Voltage vectors + arrowheads
  vPhaseMag.forEach((vm, i) => {
    const ang = vAnglesDeg.value[i]
    const [x, y] = phasorXY(vm, ang)
    
    // Voltage line
    series.push({
      name: vNames[i],
      type: 'line',
      data: [[0, 0], [x, y]],
      showSymbol: false,
      lineStyle: { width: 3, color: vColors[i] },
      tooltip: {
        show: true,
        trigger: 'item',
        backgroundColor: 'rgba(31,41,55,0.95)',
        borderColor: '#374151',
        borderWidth: 1,
        textStyle: { color: '#e5e7eb', fontSize: 12 },
        formatter: () => {
          return `<b>${vNames[i]}</b><br/>|M| = ${vm.toFixed(2)} V<br/>∠ = ${ang.toFixed(1)}°`
        }
      },
      z: 3
    })
    
    // Voltage arrowhead
    series.push(arrowHead(vNames[i], x, y, vColors[i], ang, vm, true))
  })

  // Current vectors (dashed) + arrowheads — SCALED VISUALLY
  props.iMag.forEach((im, i) => {
    const ang = iAnglesDeg[i]
    // ✅ Apply dynamic scale for visual only — tooltip still shows real value
    const [x, y] = phasorXY(im * IScale, ang)
    
    // Current line (dashed)
    series.push({
      name: iNames[i],
      type: 'line',
      data: [[0, 0], [x, y]],
      showSymbol: false,
      lineStyle: { width: 2, type: 'dashed', color: vColors[i] },
      tooltip: {
        show: true,
        trigger: 'item',
        backgroundColor: 'rgba(31,41,55,0.95)',
        borderColor: '#374151',
        borderWidth: 1,
        textStyle: { color: '#e5e7eb', fontSize: 12 },
        formatter: () => {
          // ✅ Tooltip shows REAL current (unscaled)
          return `<b>${iNames[i]}</b><br/>|M| = ${im.toFixed(2)} A<br/>∠ = ${ang.toFixed(1)}°`
        }
      },
      z: 2
    })
    
    // Current arrowhead — tooltip uses real value
    series.push(arrowHead(iNames[i], x, y, vColors[i], ang, im, false))
  })

  const option = {
    backgroundColor: 'transparent',
    animation: false,
    textStyle: { color: '#e5e7eb' },
    tooltip: {
      show: true,
      trigger: 'item',
      confine: true
    },
    legend: {
      bottom: 10,
      left: 'center',
      orient: 'horizontal',
      itemWidth: 20,
      itemHeight: 4,
      itemGap: 15,
      textStyle: { color: '#cbd5e1', fontSize: 11 },
      data: [
        { name: 'Va', icon: 'roundRect', lineStyle: { type: 'solid' } },
        { name: 'Vb', icon: 'roundRect', lineStyle: { type: 'solid' } },
        { name: 'Vc', icon: 'roundRect', lineStyle: { type: 'solid' } },
        { name: 'Ia', icon: 'roundRect', lineStyle: { type: 'dashed' } },
        { name: 'Ib', icon: 'roundRect', lineStyle: { type: 'dashed' } },
        { name: 'Ic', icon: 'roundRect', lineStyle: { type: 'dashed' } }
      ]
    },
    grid: {
      left: 20,
      right: 20,
      top: 20,
      bottom: 60,
      containLabel: false
    },

    xAxis: {
      type: 'value',
      show: true,
      min: -pad * maxLen,
      max: pad * maxLen,
      axisLine: {
        show: true,
        lineStyle: { color: '#475569', width: 1.5 }
      },
      axisTick: { show: false },
      axisLabel: { show: false },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      show: true,
      min: -pad * maxLen,
      max: pad * maxLen,
      axisLine: {
        show: true,
        lineStyle: { color: '#475569', width: 1.5 }
      },
      axisTick: { show: false },
      axisLabel: { show: false },
      splitLine: { show: false }
    },

    series
  }

  return option
}

/* ECharts lifecycle */
const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let ro: ResizeObserver | null = null

onMounted(() => {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(buildOption())
  ro = new ResizeObserver(() => chart?.resize())
  ro.observe(chartEl.value)
})

onBeforeUnmount(() => {
  ro?.disconnect()
  chart?.dispose()
})

watch(
  () => [props.vMag, props.iMag, props.pf, props.pfSign, props.voltageAngles, props.voltageIsLineToLine],
  () => chart?.setOption(buildOption(), true),
  { deep: true }
)
</script>

<template>
  <div class="w-full aspect-square flex items-start justify-center">
    <div
      ref="chartEl"
      class="w-[305px] h-[335px] rounded-2xl shadow-inner"
    />
  </div>
</template>

<style scoped>
/* Optional: Add subtle loading or error states later */
</style>