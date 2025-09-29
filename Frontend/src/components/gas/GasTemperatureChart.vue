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
import { LineChart } from 'echarts/charts'
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
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// Props
const props = defineProps({
  edgeId: {
    type: String,
    default: 'edge0'
  },
  channels: {
    type: Array,
    required: true
  }
})

// Inject required contexts
const ws = inject('ws')
const auth = inject('auth')
const dateRangeContext = inject('dateRange')
const resolutionContext = inject('resolution')
const refreshContext = inject('refresh')

// Reactive data
const loading = ref(false)
const chartData = ref({
  timestamps: [],
  series: []
})
const chartOption = shallowRef(null)

// Computed properties for date range and resolution
const fromDate = computed(() => {
  if (!dateRangeContext.value.value[0]) return null
  const date = new Date(dateRangeContext.value.value[0])
  return date.toISOString().split('T')[0] // Format as YYYY-MM-DD
})

const toDate = computed(() => {
  if (!dateRangeContext.value.value[1]) return null
  const date = new Date(dateRangeContext.value.value[1])
  return date.toISOString().split('T')[0] // Format as YYYY-MM-DD
})

const resolution = computed(() => resolutionContext.value.value)

// Temperature formatting function
function formatTemperatureWithUnit(value) {
  if (value === null || value === undefined || isNaN(value)) return 'N/A'
  const num = parseFloat(value)
  if (isNaN(num)) return 'N/A'
  return `${num.toFixed(1)}°C`
}

// Wait for WebSocket to be open
function waitForSocketOpen(ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// Fetch data from API
async function fetchData() {
  if (!fromDate.value || !toDate.value || !auth.ready || !ws) return
  
  loading.value = true
  
  try {
    await waitForSocketOpen(ws)
    
    const OUTER = crypto.randomUUID()
    const INNER = crypto.randomUUID()
    
    // Use queryHistoricTimeseriesData for gas temperature data
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER,
      method: 'edgeRpc',
      params: {
        edgeId: props.edgeId,
        payload: {
          jsonrpc: '2.0',
          id: INNER,
          method: 'queryHistoricTimeseriesData',
          params: {
            channels: props.channels,
            fromDate: fromDate.value,
            toDate: toDate.value,
            resolution: {
              value: resolution.value.value,
              unit: resolution.value.unit
            },
            timezone: 'Africa/Casablanca'
          }
        }
      }
    }))
    
    // Handle response
    const handleMessage = ({ data }) => {
      const msg = JSON.parse(data)
      if (msg.id === OUTER && msg.result) {
        const result = msg.result.payload?.result ?? msg.result
        
        if (result && result.timestamps && result.data) {
          processChartData(result)
          updateChartOption()
        } else {
          console.warn('Unexpected data structure in API response:', result)
        }
        
        loading.value = false
        ws.removeEventListener('message', handleMessage)
      }
    }
    
    ws.addEventListener('message', handleMessage)
    
  } catch (error) {
    console.error('Error fetching gas temperature data:', error)
    loading.value = false
  }
}

// Process chart data
function processChartData(result) {
  // Format timestamps for temperature chart
  const formattedTimestamps = result.timestamps.map(ts => {
    const date = new Date(ts)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  
  // Extract series data with scaling applied
  const seriesData = props.channels.map(channelId => {
    const rawValues = result.data[channelId] || []
    let scaledValues = rawValues
    
    // Apply temperature scaling: deci-°C ÷ 10 = °C
    scaledValues = rawValues.map(value => {
      if (value === null || value === undefined) return value
      return value / 10
    })
    
    return {
      name: channelId,
      values: scaledValues,
      rawTimestamps: result.timestamps // Store raw timestamps for tooltip
    }
  })
  
  chartData.value = {
    timestamps: formattedTimestamps,
    series: seriesData
  }
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
        if (!params || params.length === 0) return ''
        
        const firstParam = params[0]
        const rawTimestamp = chartData.value.series[0]?.rawTimestamps?.[firstParam.dataIndex]
        
        if (!rawTimestamp) {
          return 'No timestamp available'
        }
        
        const date = new Date(rawTimestamp)
        const formattedDate = date.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
        
        let tooltipText = `${formattedDate}<br/>`
        params.forEach(param => {
          const formattedValue = formatTemperatureWithUnit(param.value)
          tooltipText += `${param.marker} Temperature: ${formattedValue}<br/>`
        })
        return tooltipText
      }
    },
    legend: {
      show: false
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
      data: chartData.value.timestamps,
      axisLine: {
        lineStyle: {
          color: '#4b5563'
        }
      },
      axisLabel: {
        color: '#9ca3af'
      }
    },
    yAxis: {
      type: 'value',
      name: 'Temperature (°C)',
      axisLine: {
        lineStyle: {
          color: '#ef4444'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        formatter: '{value}°C'
      },
      splitLine: {
        lineStyle: {
          color: '#374151'
        }
      }
    },
    series: chartData.value.series.map((series, index) => {
      return {
        name: 'Temperature (°C)',
        type: 'line',
        data: series.values,
        smooth: true,
        lineStyle: {
          color: '#ef4444',
          width: 2
        },
        itemStyle: {
          color: '#ef4444'
        }
      }
    })
  }
}

// Watch for changes
watch(
  () => [fromDate.value, toDate.value, resolution.value, refreshContext?.count, props.channels], 
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

<style scoped>
/* Chart container styles */
</style>
