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
  },
  chartType: {
    type: String,
    default: 'metrics'
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

// Gas formatting functions
function formatGasFlowWithUnit(value) {
  if (value === null || value === undefined) return 'N/A'
  
  const num = parseFloat(value)
  
  if (Math.abs(num) < 0.001) {
    return `${(num * 1000).toFixed(3)} g/s`
  } else if (Math.abs(num) < 1) {
    return `${num.toFixed(4)} kg/s`
  } else {
    return `${num.toFixed(2)} kg/s`
  }
}

function formatTemperatureWithUnit(value) {
  if (value === null || value === undefined) return 'N/A'
  return `${parseFloat(value).toFixed(1)}°C`
}

function formatPressureWithUnit(value) {
  if (value === null || value === undefined) return 'N/A'
  return `${parseFloat(value).toFixed(2)} bar`
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
    
    // Use queryHistoricTimeseriesData for gas metrics data
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
    console.error('Error fetching gas metrics data:', error)
    loading.value = false
  }
}

// Process chart data
function processChartData(result) {
  // Format timestamps for metrics chart
  const formattedTimestamps = result.timestamps.map(ts => {
    const date = new Date(ts)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  
  // Extract series data
  const seriesData = props.channels.map(channelId => ({
    name: channelId,
    values: result.data[channelId] || [],
    rawTimestamps: result.timestamps // Store raw timestamps for tooltip
  }))
  
  chartData.value = {
    timestamps: formattedTimestamps,
    series: seriesData
  }
}

// Update chart option
function updateChartOption() {
  // Gas metrics chart (line)
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
          let formattedValue = 'N/A'
          if (param.seriesName.includes('FlowRate')) {
            formattedValue = formatGasFlowWithUnit(param.value)
          } else if (param.seriesName.includes('Temperature')) {
            formattedValue = formatTemperatureWithUnit(param.value)
          } else if (param.seriesName.includes('Pressure')) {
            formattedValue = formatPressureWithUnit(param.value)
          }
          tooltipText += `${param.marker} ${param.seriesName}: ${formattedValue}<br/>`
        })
        return tooltipText
      }
    },
    legend: {
      data: chartData.value.series.map(series => {
        if (series.name.includes('FlowRate')) return 'Flow Rate'
        if (series.name.includes('Temperature')) return 'Temperature'
        if (series.name.includes('Pressure')) return 'Pressure'
        return series.name
      }),
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
    yAxis: [
      {
        type: 'value',
        name: 'Flow Rate (kg/s)',
        position: 'left',
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
      {
        type: 'value',
        name: 'Temperature (°C)',
        position: 'right',
        axisLine: {
          lineStyle: {
            color: '#ef4444'
          }
        },
        axisLabel: {
          color: '#9ca3af',
          formatter: '{value}°C'
        }
      }
    ],
    series: chartData.value.series.map((series, index) => {
      const isFlowRate = series.name.includes('FlowRate')
      const isTemperature = series.name.includes('Temperature')
      const isPressure = series.name.includes('Pressure')
      
      let yAxisIndex = 0 // Default to left axis
      let color = '#22c55e' // Default green for pressure
      
      if (isFlowRate) {
        yAxisIndex = 0
        color = '#3b82f6' // Blue
      } else if (isTemperature) {
        yAxisIndex = 1
        color = '#ef4444' // Red
      } else if (isPressure) {
        yAxisIndex = 0
        color = '#22c55e' // Green
      }
      
      return {
        name: isFlowRate ? 'Flow Rate' : isTemperature ? 'Temperature' : isPressure ? 'Pressure' : series.name,
        type: 'line',
        yAxisIndex: yAxisIndex,
        data: series.values,
        smooth: true,
        lineStyle: {
          color: color,
          width: 2
        },
        itemStyle: {
          color: color
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
