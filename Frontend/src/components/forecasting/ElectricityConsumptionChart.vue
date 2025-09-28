<template>
  <div class="h-full">
    <VChart 
      :option="chartOption" 
      class="w-full h-full"
      autoresize
    />
  </div>
</template>

<script setup>
import { BarChart, LineChart } from 'echarts/charts'
import {
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent
} from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { inject, onMounted, ref, shallowRef, watch } from 'vue'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// Props
const props = defineProps({
  timeRange: {
    type: String,
    default: 'day',
    validator: v => ['day', 'week', 'month'].includes(v)
  },
  currentOffset: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Inject required contexts
const ws = inject('ws')
const auth = inject('auth')

// Reactive data
const chartData = ref({
  timestamps: [],
  forecastData: [],
  actualData: []
})
const chartOption = shallowRef(null)

// Generate forecast data based on historical patterns
const generateForecastData = () => {
  const dataPoints = props.timeRange === 'day' ? 24 : props.timeRange === 'week' ? 7 : 30
  const forecastData = []
  const actualData = []
  const timestamps = []
  
  // Base consumption patterns
  const baseConsumption = 120 // kWh base
  const dailyVariation = 0.3 // 30% variation
  const seasonalFactor = 1.0 + (Math.sin(Date.now() / (1000 * 60 * 60 * 24 * 30)) * 0.2) // Seasonal variation
  
  for (let i = 0; i < dataPoints; i++) {
    let timestamp, forecast, actual
    
    if (props.timeRange === 'day') {
      // Hourly data for a day
      const hour = i
      timestamp = `${hour.toString().padStart(2, '0')}:00`
      
      // Peak hours (8-18) have higher consumption
      const isPeakHour = hour >= 8 && hour <= 18
      const peakFactor = isPeakHour ? 1.4 : 0.7
      
      // Add some randomness
      const randomFactor = 0.8 + Math.random() * 0.4
      
      forecast = baseConsumption * peakFactor * seasonalFactor * randomFactor
      
      // For current day, show actual data if available
      if (props.currentOffset === 0 && hour <= new Date().getHours()) {
        actual = forecast * (0.9 + Math.random() * 0.2) // Actual is close to forecast with some variation
      } else {
        actual = null
      }
    } else if (props.timeRange === 'week') {
      // Daily data for a week
      const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      timestamp = dayNames[i]
      
      // Weekend has different consumption pattern
      const isWeekend = i >= 5
      const weekendFactor = isWeekend ? 0.8 : 1.0
      
      const randomFactor = 0.85 + Math.random() * 0.3
      forecast = baseConsumption * 24 * weekendFactor * seasonalFactor * randomFactor
      
      // For current week, show actual data if available
      if (props.currentOffset === 0 && i <= new Date().getDay()) {
        actual = forecast * (0.9 + Math.random() * 0.2)
      } else {
        actual = null
      }
    } else {
      // Daily data for a month
      const day = i + 1
      timestamp = `Day ${day}`
      
      const randomFactor = 0.8 + Math.random() * 0.4
      forecast = baseConsumption * 24 * seasonalFactor * randomFactor
      
      // For current month, show actual data if available
      if (props.currentOffset === 0 && day <= new Date().getDate()) {
        actual = forecast * (0.9 + Math.random() * 0.2)
      } else {
        actual = null
      }
    }
    
    timestamps.push(timestamp)
    forecastData.push(forecast)
    actualData.push(actual)
  }
  
  return { timestamps, forecastData, actualData }
}

// Update chart option
const updateChartOption = () => {
  const { timestamps, forecastData, actualData } = generateForecastData()
  
  chartData.value = { timestamps, forecastData, actualData }
  
  chartOption.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#4b5563',
      textStyle: {
        color: '#ffffff'
      },
      formatter: (params) => {
        let tooltipText = `${params[0].axisValue}<br/>`
        params.forEach(param => {
          const value = param.value !== null ? param.value.toFixed(1) : 'N/A'
          tooltipText += `${param.marker} ${param.seriesName}: ${value} kWh<br/>`
        })
        return tooltipText
      }
    },
    legend: {
      data: ['Forecast', 'Actual'],
      textStyle: {
        color: '#d1d5db'
      },
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: true,
      data: timestamps,
      axisLine: {
        lineStyle: {
          color: '#3b82f6'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        rotate: timestamps.length > 20 ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: 'Consumption (kWh)',
      axisLine: {
        lineStyle: {
          color: '#3b82f6'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        formatter: '{value}'
      },
      splitLine: {
        lineStyle: {
          color: '#374151'
        }
      }
    },
    series: [
      {
        name: 'Forecast',
        type: 'bar',
        data: forecastData,
        itemStyle: {
          color: '#3b82f6'
        },
        barWidth: '60%'
      },
      {
        name: 'Actual',
        type: 'bar',
        data: actualData,
        itemStyle: {
          color: '#10b981'
        },
        barWidth: '60%'
      }
    ]
  }
}

// Watch for changes
watch(
  () => [props.timeRange, props.currentOffset, props.loading],
  () => {
    if (!props.loading) {
      updateChartOption()
    }
  },
  { immediate: true }
)

// Initial data generation
onMounted(() => {
  updateChartOption()
})
</script>

<style scoped>
/* Chart container styles */
</style>
