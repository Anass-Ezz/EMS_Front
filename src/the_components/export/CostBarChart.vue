<template>
  <div class="w-full h-full">
    <v-chart
      v-if="chartOptions"
      :option="chartOptions"
      autoresize
      class="w-full h-full"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

// ECharts imports
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

// Register ECharts components
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// Props remain identical
const props = defineProps({
  costBars: {
    type: Object,
    default: () => ({})
  },
  overlay: { type: Boolean, default: true }
})

const chartOptions = computed(() => {
  if (!props.costBars || Object.keys(props.costBars).length === 0) {
    return null
  }
  
  const categories = Object.keys(props.costBars)

  return {
    grid: {
      left: 0,
      right: 55,
      top: 20,
      bottom: 40,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      // --- START OF CHANGE ---
      // This section controls the appearance and behavior of the x-axis labels
      axisLabel: {
        // interval: 0 tells ECharts to try to display every single label.
        interval: 0,
        // hideOverlap: true will automatically hide labels if they overlap.
        // This is the perfect solution for "hidden on overflow".
        hideOverlap: true
      }
      // --- END OF CHANGE ---
    },
    yAxis: {
      type: 'value',
      name: '',
      nameLocation: 'middle',
      nameGap: 50,
      
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: 'rgba(255,255,255,0.1)'
        }
      }
    },
    legend: {
      bottom: 10,
      data: ['Last Month Price', 'Current Month Price'],
      textStyle: {
        color: '#FFFFFF'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter(params) {
        const category = params[0].name
        const costBarData = props.costBars[category]

        if (!costBarData) return ''

        let tooltipText = `${category}<br/>`
        
        params.sort((a) => (a.seriesName === 'Last Month Price' ? -1 : 1));

        params.forEach(param => {
          const isLast = param.seriesName === 'Last Month Price'
          const dataPoint = isLast ? costBarData.last : costBarData.current
          const price = dataPoint.price
          const energy = dataPoint.energy
          
          tooltipText += `${param.marker}${param.seriesName}: ${price.toLocaleString()} MAD • ${energy.toLocaleString()} kWh<br/>`
        })

        return tooltipText
      }
    },
    series: [
      {
        name: 'Last Month Price',
        type: 'bar',
        stack: props.overlay ? undefined : 'total',
        color: 'rgba(54, 162, 235, 0.9)',
        data: categories.map(c => props.costBars[c].last.price)
      },
      {
        name: 'Current Month Price',
        type: 'bar',
        stack: props.overlay ? undefined : 'total',
        color: 'rgba(54, 162, 235, 0.4)',
        data: categories.map(c => props.costBars[c].current.price)
      }
    ]
  }
})
</script>