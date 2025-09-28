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

// Generate forecast data based on solar patterns
const generateForecastData = () => {
  const dataPoints = props.timeRange === 'day' ? 24 : props.timeRange === 'week' ? 7 : 30
  const forecastData = []
  const actualData = []
  const timestamps = []
  
  // Base solar generation patterns
  const maxCapacity = 100 // kW max capacity
  const dailyVariation = 0.3 // 30% variation
  const seasonalFactor = 1.0 + (Math.sin(Date.now() / (1000 * 60 * 60 * 24 * 30)) * 0.4) // Seasonal variation
  
  for (let i = 0; i < dataPoints; i++) {
    let timestamp, forecast, actual
    
    if (props.timeRange === 'day') {
      // Hourly data for a day
      const hour = i
      timestamp = `${hour.toString().padStart(2, '0')}:00`
      
      // Solar generation follows sun pattern
      let solarFactor = 0
      if (hour >= 6 && hour <= 18) {
        // Sun is up, generate power
        const sunAngle = Math.sin((hour - 6) * Math.PI / 12) // Peak at noon
        solarFactor = Math.max(0, sunAngle)
      }
      
      // Add weather variation
      const weatherFactor = 0.7 + Math.random() * 0.6 // 70-130% based on weather
      
      forecast = maxCapacity * solarFactor * seasonalFactor * weatherFactor
      
      // For current day, show actual data if available
      if (props.currentOffset === 0 && hour <= new Date().getHours()) {
        actual = forecast * (0.8 + Math.random() * 0.4) // Actual varies more due to clouds
      } else {
        actual = null
      }
    } else if (props.timeRange === 'week') {
      // Daily data for a week
      const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      timestamp = dayNames[i]
      
      // Daily solar generation (integrated over the day)
      const dailySolarFactor = 0.4 + Math.random() * 0.4 // 40-80% daily average
      const weatherFactor = 0.6 + Math.random() * 0.8 // Weather variation
      
      forecast = maxCapacity * dailySolarFactor * seasonalFactor * weatherFactor
      
      // For current week, show actual data if available
      if (props.currentOffset === 0 && i <= new Date().getDay()) {
        actual = forecast * (0.8 + Math.random() * 0.4)
      } else {
        actual = null
      }
    } else {
      // Daily data for a month
      const day = i + 1
      timestamp = `Day ${day}`
      
      // Monthly variation in solar generation
      const dailySolarFactor = 0.3 + Math.random() * 0.5
      const weatherFactor = 0.5 + Math.random() * 1.0
      
      forecast = maxCapacity * dailySolarFactor * seasonalFactor * weatherFactor
      
      // For current month, show actual data if available
      if (props.currentOffset === 0 && day <= new Date().getDate()) {
        actual = forecast * (0.8 + Math.random() * 0.4)
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
          tooltipText += `${param.marker} ${param.seriesName}: ${value} kW<br/>`
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
      boundaryGap: false,
      data: timestamps,
      axisLine: {
        lineStyle: {
          color: '#f59e0b'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        rotate: timestamps.length > 20 ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: 'Generation (kW)',
      axisLine: {
        lineStyle: {
          color: '#f59e0b'
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
        type: 'line',
        data: forecastData,
        itemStyle: {
          color: '#f59e0b'
        },
        lineStyle: {
          color: '#f59e0b',
          width: 3
        },
        symbol: 'circle',
        symbolSize: 6,
        smooth: true,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(245, 158, 11, 0.3)'
            }, {
              offset: 1, color: 'rgba(245, 158, 11, 0.05)'
            }]
          }
        }
      },
      {
        name: 'Actual',
        type: 'line',
        data: actualData,
        itemStyle: {
          color: '#10b981'
        },
        lineStyle: {
          color: '#10b981',
          width: 3
        },
        symbol: 'circle',
        symbolSize: 6,
        smooth: true
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
