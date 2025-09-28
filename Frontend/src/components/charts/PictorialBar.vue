<template>
  <div ref="chartEl" class="w-[150%] h-[100%]" :style="{ height, width }"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts/core'
import { PictorialBarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([PictorialBarChart, TooltipComponent, GridComponent, CanvasRenderer])

const props = defineProps({
  // [{ name, value, symbolKey?, symbolSize? }]
  seriesData: {
    type: Array,
    default: () => ([
      { name: 'electricity', value: 10, symbolKey: 'reindeer', symbolSize: [60, 60] },
      { name: 'gas', value: 60,  symbolKey: 'rocket',   symbolSize: [50, 60] },
      { name: 'fuel', value: 25,  symbolKey: 'plane',    symbolSize: [65, 35] },
    ])
  },
  height: { type: String, default: '100%' },
  width:  { type: String, default: '150%' },

  // style controls
  primaryColor: { type: String, default: '#e54035' },
  backgroundColor: { type: String, default: 'transparent' },

  // layout
  gridTop: { type: [String, Number], default: 0 },
  gridRight: { type: [String, Number], default: 0 },
  gridBottom: { type: [String, Number], default: 0 },
  gridLeft: { type: [String, Number], default: 0 },

  // axis visibility
  showXAxis: { type: Boolean, default: true },
  showYAxis: { type: Boolean, default: false },

  // pictorial bar tuning
  hillOpacity: { type: Number, default: 0.5 },
  hillGap: { type: String, default: '-20%' },
  glyphGap: { type: String, default: '-50%' },
  glyphSymbolDefaultSize: { type: [Number, Array], default: 50 },

  // custom symbol path overrides (optional)
  customSymbols: { type: Object, default: () => ({}) },
})

// default path symbols (can be overridden via customSymbols prop)
const pathSymbols = {
  electricity: 'path://M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09zM4.157 8.5H7a.5.5 0 0 1 .478.647L6.11 13.59l5.732-6.09H9a.5.5 0 0 1-.478-.647L9.89 2.41z',
  gas: 'path://M8 16c3.314 0 6-2 6-5.5 0-1.5-.5-4-2.5-6 .25 1.5-1.25 2-1.25 2C11 4 9 .5 6 0c.357 2 .5 4-2 6-1.25 1-2 2.729-2 4.5C2 14 4.686 16 8 16m0-1c-1.657 0-3-1-3-2.75 0-.75.25-2 1.25-3C6.125 10 7 10.5 7 10.5c-.375-1.25.5-3.25 2-3.5-.179 1-.25 2 1 3 .625.5 1 1.364 1 2.25C11 14 9.657 15 8 15',
  fuel: 'path://M8 16a6 6 0 0 0 6-6c0-1.655-1.122-2.904-2.432-4.362C10.254 4.176 8.75 2.503 8 0c0 0-6 5.686-6 10a6 6 0 0 0 6 6M6.646 4.646l.708.708c-.29.29-1.128 1.311-1.907 2.87l-.894-.448c.82-1.641 1.717-2.753 2.093-3.13',
}

const chartEl = ref(null)
let chart = null
let resizeHandler = null

function buildOption() {
  const labels = props.seriesData.map(d => d.name)
  const values = props.seriesData.map(d => d.value)

  const glyphData = props.seriesData.map(d => ({
    value: d.value,
    symbol: (props.customSymbols[d.symbolKey] || pathSymbols[d.symbolKey]) ?? null,
    symbolSize: d.symbolSize ?? props.glyphSymbolDefaultSize
  }))

  return {
    backgroundColor: props.backgroundColor,
    color: [props.primaryColor],
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      formatter: params => `${params[0].name}: ${params[0].value}`
    },
    grid: {
      left: props.gridLeft, right: props.gridRight, top: props.gridTop, bottom: props.gridBottom, containLabel: false
    },
    xAxis: {
      data: labels,
      axisTick: { show: false },
      axisLine: { show: props.showXAxis },
      axisLabel: { show: props.showXAxis, color: props.primaryColor }
    },
    yAxis: {
      splitLine: { show: false },
      axisTick: { show: false },
      axisLine: { show: props.showYAxis },
      axisLabel: { show: props.showYAxis }
    },
    series: [
      {
        name: 'hill',
        type: 'pictorialBar',
        data: values,
        barCategoryGap: props.hillGap,
        symbol: 'path://M0,10 L10,10 C5.5,10 5.5,5 5,0 C4.5,5 4.5,10 0,10 z',
        itemStyle: { opacity: props.hillOpacity },
        emphasis: { itemStyle: { opacity: 1 } },
        z: 10
      },
      {
        name: 'glyph',
        type: 'pictorialBar',
        barGap: props.glyphGap,
        symbolPosition: 'end',
        symbolOffset: [-10, '-10%'],
        data: glyphData
      }
    ]
  }
}

function render() {
  if (!chartEl.value) return
  if (!chart) chart = echarts.init(chartEl.value)
  chart.setOption(buildOption(), true)
}

onMounted(() => {
  render()
  resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler)
  chart?.dispose()
  chart = null
})

watch(
  () => ({
    seriesData: props.seriesData,
    primaryColor: props.primaryColor,
    backgroundColor: props.backgroundColor,
    gridTop: props.gridTop, gridRight: props.gridRight, gridBottom: props.gridBottom, gridLeft: props.gridLeft,
    showXAxis: props.showXAxis, showYAxis: props.showYAxis,
    hillOpacity: props.hillOpacity, hillGap: props.hillGap, glyphGap: props.glyphGap,
    glyphSymbolDefaultSize: props.glyphSymbolDefaultSize,
    customSymbols: props.customSymbols
  }),
  () => render(),
  { deep: true }
)
</script>
