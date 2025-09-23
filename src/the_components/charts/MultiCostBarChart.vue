<template>
  <v-chart
    v-if="chartOptions"
    :option="chartOptions"
    autoresize
    class="w-full h-full"
  />
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// Register the necessary ECharts components
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

/* ─── props ─────────────────────────────────────────────── */
const props = defineProps({
  response: { type: Object, required: true }
})

/* ─── helpers ───────────────────────────────────────────── */
function toDateLabel (iso) {
  return iso.slice(0, iso.length >= 13 ? 10 : 7)
}

function randomRGBA () {
  const r = 100 + ~~(Math.random() * 120)
  const g = 100 + ~~(Math.random() * 120)
  const b = 100 + ~~(Math.random() * 120)
  return `rgba(${r},${g},${b},1)`
}

/* ─── ECharts options ───────────────────────────────────── */
const chartOptions = computed(() => {
  const core = props.response.payload?.result ?? props.response
  const { timestamps = [], data = {} } = core

  if (!timestamps.length || !Object.keys(data).length) {
    return null
  }

  const labels = timestamps.map(toDateLabel)
  const numberOfSeries = Object.keys(data).length
  const showDataLabels = numberOfSeries === 1

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        let tooltipText = `${params[0].axisValueLabel}<br/>`
        params.forEach(param => {
          const price = (param.data.value ?? 0).toLocaleString('en-US')
          const energy = (param.data.energy ?? 0).toLocaleString('en-US')
          tooltipText += `${param.marker}${param.seriesName}: ${price} MAD • ${energy} kWh<br/>`
        })
        return tooltipText
      }
    },

    // <<< MODIFIED: Hide the legend to remove the bottom margin it creates.
    legend: {
      show: false
    },
    
    // <<< MODIFIED: Adjust grid to remove padding.
    grid: {
      top: '25px',       // Minimal space for top data labels when shown.
      left: '1%',        // Minimal space on the left.
      right: '1%',       // Minimal space on the right.
      bottom: '1%',      // Minimal space on the bottom.
      containLabel: true // CRITICAL: This ensures axis labels are not cut off.
    },
    
    xAxis: {
      type: 'category',
      data: labels,
      axisTick: { alignWithLabel: true },
      axisLabel: { color: '#ccc' }
    },
    
    yAxis: {
      type: 'value',
      // <<< MODIFIED: Removed the name to save space.
      name: '',
      min: 0,
      axisLabel: {
        color: '#ccc',
        formatter: '{value}'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255,255,255,0.1)'
        }
      }
    },

    series: Object.entries(data).map(([key, arr]) => {
      const color = randomRGBA()
      return {
        name: key,
        type: 'bar',
        barGap: '10%',
        itemStyle: {
          color: color
        },
        data: arr.map(o => ({
          value: o?.price ?? 0,
          energy: o?.energy ?? 0
        })),
        
        label: {
          show: showDataLabels,
          position: 'top',
          color: color,
          fontWeight: 'bold',
          fontSize: 10,
          formatter: (params) => {
            return (params.value ?? 0).toLocaleString('en-US')
          }
        }
      }
    })
  }
})
</script>