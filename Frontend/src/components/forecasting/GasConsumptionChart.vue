<template>
  <div class="w-full h-full">
    <div v-if="loading" class="flex items-center justify-center h-full">
      <div class="text-gray-500">Loading gas data...</div>
    </div>
    <v-chart 
      v-else-if="chartOption"
      :option="chartOption" 
      class="w-full h-full"
    />
    <div v-else class="flex items-center justify-center h-full">
      <div class="text-gray-500">No data available</div>
    </div>
  </div>
</template>

<script setup>
import { BarChart } from 'echarts/charts'
import {
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent
} from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { computed, inject, onMounted, ref, shallowRef, watch } from 'vue'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  BarChart,
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
  offset: {
    type: Number,
    default: 0
  }
})

// Emit events
const emit = defineEmits(['update-stats'])

// Inject required contexts
const ws = inject('ws')
const auth = inject('auth')

// Reactive data
const loading = ref(false)
const chartData = ref({
  timestamps: [],
  actualData: [],
  forecastData: []
})
const chartOption = shallowRef(null)

// Calculate date range based on time range and offset
const dateRange = computed(() => {
  const now = new Date()
  const offset = props.offset
  
  let startDate, endDate
  
  switch (props.timeRange) {
    case 'day':
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + offset)
      endDate = new Date(startDate)
      endDate.setDate(endDate.getDate() + 1)
      break
    case 'week':
      const startOfWeek = new Date(now)
      startOfWeek.setDate(now.getDate() - now.getDay() + 1 + (offset * 7)) // Monday
      startDate = new Date(startOfWeek.getFullYear(), startOfWeek.getMonth(), startOfWeek.getDate())
      endDate = new Date(startDate)
      endDate.setDate(endDate.getDate() + 7)
      break
    case 'month':
      startDate = new Date(now.getFullYear(), now.getMonth() + offset, 1)
      endDate = new Date(now.getFullYear(), now.getMonth() + offset + 1, 1)
      break
    default:
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + offset)
      endDate = new Date(startDate)
      endDate.setDate(endDate.getDate() + 1)
  }
  
  return {
    from: startDate.toISOString().split('T')[0],
    to: endDate.toISOString().split('T')[0]
  }
})

// Wait for WebSocket to be open
function waitForSocketOpen(ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// Fetch actual data from API
async function fetchActualData() {
  if (!auth.ready || !ws) return null
  
  try {
    await waitForSocketOpen(ws)
    
    const OUTER = crypto.randomUUID()
    const INNER = crypto.randomUUID()
    
    // Use the same method as the gas meter pages
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER,
      method: 'edgeRpc',
      params: {
        edgeId: 'edge0',
        payload: {
          jsonrpc: '2.0',
          id: INNER,
          method: 'queryHistoricTimeseriesEnergyPerPeriod',
          params: {
            channels: ['gasmeter0/Consumption'],
            fromDate: dateRange.value.from,
            toDate: dateRange.value.to,
            resolution: {
              value: props.timeRange === 'day' ? 1 : props.timeRange === 'week' ? 1 : 1,
              unit: props.timeRange === 'day' ? 'HOURS' : props.timeRange === 'week' ? 'DAYS' : 'DAYS'
            },
            timezone: 'Africa/Casablanca'
          }
        }
      }
    }))
    
    return new Promise((resolve) => {
      const handleMessage = ({ data }) => {
        const msg = JSON.parse(data)
        if (msg.id === OUTER && msg.result) {
          const result = msg.result.payload?.result ?? msg.result
          ws.removeEventListener('message', handleMessage)
          resolve(result)
        }
      }
      ws.addEventListener('message', handleMessage)
    })
  } catch (error) {
    console.error('Error fetching actual gas data:', error)
    return null
  }
}

// Generate forecast data based on actual data with small variations
function generateForecastData(actualData) {
  if (!actualData || !actualData.timestamps || !actualData.data) {
    return null
  }
  
  const actualValues = actualData.data['gasmeter0/Consumption'] || []
  const forecastValues = actualValues.map(value => {
    if (value === null || value === undefined) return value
    
    // Add small random variation (±5% to ±15%)
    const variation = (Math.random() - 0.5) * 0.2 + 0.1 // 10% ± 10%
    const multiplier = 1 + variation
    return value * multiplier
  })
  
  return {
    timestamps: actualData.timestamps,
    data: {
      'gasmeter0/Consumption': forecastValues
    }
  }
}

// Fetch data and update chart
async function fetchData() {
  if (!auth.ready || !ws) return
  
  loading.value = true
  
  try {
    // Fetch actual data
    const actualData = await fetchActualData()
    
    if (actualData && actualData.timestamps && actualData.data) {
      // Generate forecast data
      const forecastData = generateForecastData(actualData)
      
      // Process and update chart
      processChartData(actualData, forecastData)
      updateChartOption()
      
      // Calculate and emit stats
      calculateAndEmitStats(actualData, forecastData)
    } else {
      console.warn('No actual gas data received')
    }
  } catch (error) {
    console.error('Error fetching gas data:', error)
  } finally {
    loading.value = false
  }
}

// Process chart data
function processChartData(actualData, forecastData) {
  let actualValues = actualData.data['gasmeter0/Consumption'] || []
  let forecastValues = forecastData ? forecastData.data['gasmeter0/Consumption'] || [] : []
  let timestamps = actualData.timestamps || []
  
  // Filter day data to only show first day (midnight to 11:59 PM)
  if (props.timeRange === 'day') {
    const startOfDay = new Date(timestamps[0])
    startOfDay.setHours(0, 0, 0, 0) // Set to midnight
    const endOfDay = new Date(startOfDay)
    endOfDay.setHours(23, 59, 59, 999) // Set to 11:59:59 PM
    
    // Find the cutoff index for the first day
    let cutoffIndex = timestamps.length
    for (let i = 0; i < timestamps.length; i++) {
      const dataTime = new Date(timestamps[i])
      if (dataTime > endOfDay) {
        cutoffIndex = i
        break
      }
    }
    
    // Slice arrays to only include first day data
    timestamps = timestamps.slice(0, cutoffIndex)
    actualValues = actualValues.slice(0, cutoffIndex)
    forecastValues = forecastValues.slice(0, cutoffIndex)
  }
  
  // Get current time for filtering future data
  const now = new Date()
  
  // Filter out future actual data - only show actual data up to current time
  const filteredActualValues = actualValues.map((value, index) => {
    const timestamp = timestamps[index]
    const dataTime = new Date(timestamp)
    
    // For future dates (offset > 0), hide ALL actual data
    if (props.offset > 0) {
      return null // No actual data for future dates
    }
    
    // If this is today (offset = 0) and the data time is in the future, set to null
    if (props.offset === 0) {
      // For day resolution, compare at hour level
      if (props.timeRange === 'day') {
        const dataHour = dataTime.getHours()
        const currentHour = now.getHours()
        if (dataHour > currentHour) {
          return null // Hide actual data for future hours
        }
      } else {
        // For other time ranges, compare at full time level
        if (dataTime > now) {
          return null // Hide actual data for future time periods
        }
      }
    }
    
    return value
  })
  
  // Format timestamps based on time range
  const formattedTimestamps = timestamps.map(ts => {
    const date = new Date(ts)
    if (props.timeRange === 'day') {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    } else if (props.timeRange === 'week') {
      return date.toLocaleDateString('en-US', { weekday: 'short' })
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }
  })
  
  chartData.value = {
    timestamps: formattedTimestamps,
    actualData: filteredActualValues,
    forecastData: forecastValues
  }
}

// Calculate and emit statistics
function calculateAndEmitStats(actualData, forecastData) {
  let actualValues = actualData.data['gasmeter0/Consumption'] || []
  let forecastValues = forecastData ? forecastData.data['gasmeter0/Consumption'] || [] : []
  let timestamps = actualData.timestamps || []
  
  // Filter day data to only show first day (midnight to 11:59 PM)
  if (props.timeRange === 'day') {
    const startOfDay = new Date(timestamps[0])
    startOfDay.setHours(0, 0, 0, 0) // Set to midnight
    const endOfDay = new Date(startOfDay)
    endOfDay.setHours(23, 59, 59, 999) // Set to 11:59:59 PM
    
    // Find the cutoff index for the first day
    let cutoffIndex = timestamps.length
    for (let i = 0; i < timestamps.length; i++) {
      const dataTime = new Date(timestamps[i])
      if (dataTime > endOfDay) {
        cutoffIndex = i
        break
      }
    }
    
    // Slice arrays to only include first day data
    timestamps = timestamps.slice(0, cutoffIndex)
    actualValues = actualValues.slice(0, cutoffIndex)
    forecastValues = forecastValues.slice(0, cutoffIndex)
  }
  
  // Get current time for filtering future data
  const now = new Date()
  
  // Filter actual values to only include data up to current time
  const filteredActualValues = actualValues.filter((value, index) => {
    const timestamp = timestamps[index]
    const dataTime = new Date(timestamp)
    
    // For future dates (offset > 0), exclude ALL actual data from stats
    if (props.offset > 0) {
      return false
    }
    
    // If this is today (offset = 0) and the data time is in the future, exclude from stats
    if (props.offset === 0) {
      // For day resolution, compare at hour level
      if (props.timeRange === 'day') {
        const dataHour = dataTime.getHours()
        const currentHour = now.getHours()
        if (dataHour > currentHour) {
          return false // Exclude future hours from stats
        }
      } else {
        // For other time ranges, compare at full time level
        if (dataTime > now) {
          return false
        }
      }
    }
    
    return value !== null && value !== undefined
  })
  
  const actualAvg = filteredActualValues.length > 0 ? 
    filteredActualValues.reduce((sum, val) => sum + (val || 0), 0) / filteredActualValues.length : 0
  
  const forecastAvg = forecastValues.length > 0 ? 
    forecastValues.reduce((sum, val) => sum + (val || 0), 0) / forecastValues.length : 0
  
  const error = actualAvg > 0 ? ((forecastAvg - actualAvg) / actualAvg) * 100 : 0
  
  emit('update-stats', {
    actualAvg: (actualAvg / 1000).toFixed(2), // Convert grams to m³
    forecastAvg: (forecastAvg / 1000).toFixed(2), // Convert grams to m³
    error: error.toFixed(1)
  })
}

// Update chart option
function updateChartOption() {
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
          const value = param.value
          const formattedValue = value !== null && value !== undefined ? 
            `${(value / 1000).toFixed(2)} m³` : 'N/A'
          tooltipText += `${param.marker} ${param.seriesName}: ${formattedValue}<br/>`
        })
        return tooltipText
      }
    },
    legend: {
      data: ['Actual', 'Forecast'],
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
      data: chartData.value.timestamps,
      axisLine: {
        lineStyle: {
          color: '#4b5563'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        rotate: chartData.value.timestamps.length > 20 ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: 'Consumption (m³)',
      axisLine: {
        lineStyle: {
          color: '#4b5563'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        formatter: (value) => (value / 1000).toFixed(1)
      },
      splitLine: {
        lineStyle: {
          color: '#374151'
        }
      }
    },
    series: [
      {
        name: 'Actual',
        type: 'bar',
        data: chartData.value.actualData.map(val => val / 1000), // Convert grams to m³
        itemStyle: {
          color: '#ea580c'
        },
        barWidth: '40%'
      },
      {
        name: 'Forecast',
        type: 'bar',
        data: chartData.value.forecastData.map(val => val / 1000), // Convert grams to m³
        itemStyle: {
          color: '#f59e0b'
        },
        barWidth: '40%'
      }
    ]
  }
}

// Watch for changes
watch(
  () => [props.timeRange, props.offset],
  () => {
    if (auth.ready) {
      fetchData()
    }
  },
  { deep: true }
)

watch(
  () => auth.ready,
  r => {
    if (r) {
      fetchData()
    }
  },
  { immediate: true }
)

// Initial data fetch
onMounted(() => {
  if (auth.ready) {
    fetchData()
  }
})
</script>