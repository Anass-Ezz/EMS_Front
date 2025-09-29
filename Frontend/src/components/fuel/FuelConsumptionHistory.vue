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
import { computed, inject, onMounted, ref, shallowRef, watch } from 'vue'
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
    default: 'fuel' // 'fuel' or 'metrics'
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

// Fuel consumption formatting function
function formatFuelConsumptionWithUnit(value) {
  if (value === null || value === undefined) return 'N/A'
  
  const num = parseFloat(value)
  
  if (Math.abs(num) < 1000) {
    return `${num.toFixed(1)} kg`
  } else if (Math.abs(num) < 1000000) {
    return `${(num / 1000).toFixed(1)} t`
  } else {
    return `${(num / 1000000).toFixed(1)} kt`
  }
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
    
    // Use queryHistoricTimeseriesEnergyPerPeriod for consumption data
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER,
      method: 'edgeRpc',
      params: {
        edgeId: props.edgeId,
        payload: {
          jsonrpc: '2.0',
          id: INNER,
          method: 'queryHistoricTimeseriesEnergyPerPeriod',
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
    console.error('Error fetching fuel data:', error)
    loading.value = false
  }
}

// Process chart data
function processChartData(result) {
  // Format timestamps based on chart type
  const formattedTimestamps = result.timestamps.map(ts => {
    const date = new Date(ts)
    if (props.chartType === 'fuel') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    } else {
      // For metrics chart — store full timestamp for tooltip
      return ts // Keep ISO string for accurate tooltip
    }
  })
  
  // Extract series data with scaling applied
  const seriesData = props.channels.map(channelId => {
    const rawValues = result.data[channelId] || []
    // Apply scaling: grams ÷ 1000 = kg for consumption data
    const scaledValues = rawValues.map(value => {
      if (value === null || value === undefined) return value
      return value / 1000  // Convert grams to kg
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
  if (props.chartType === 'fuel') {
    // Fuel consumption chart (bar)
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
            const formattedValue = formatFuelConsumptionWithUnit(param.value)
            tooltipText += `${param.marker} ${param.seriesName}: ${formattedValue}<br/>`
          })
          return tooltipText
        }
      },
      legend: {
        data: ['Fuel Consumption'],
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
            color: '#ea580c'
          }
        },
        axisLabel: {
          color: '#9ca3af',
          rotate: chartData.value.timestamps.length > 20 ? 45 : 0
        }
      },
      yAxis: {
        type: 'value',
        name: 'Consumption (kg)',
        axisLine: {
          lineStyle: {
            color: '#ea580c'
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
          name: 'Fuel Consumption',
          type: 'bar',
          data: chartData.value.series[0]?.values || [],
          itemStyle: {
            color: '#ea580c'
          },
          barWidth: '60%'
        }
      ]
    }
  } else {
    // Fuel metrics chart (line)
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
              formattedValue = formatFuelFlowWithUnit(param.value)
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
        data: chartData.value.timestamps.map(ts => {
          const date = new Date(ts)
          return date.toLocaleDateString('en-US', { weekday: 'short' })
        }),
        axisLine: {
          lineStyle: {
            color: '#ea580c'
          }
        },
        axisLabel: {
          color: '#9ca3af'
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#ea580c'
          }
        },
        axisLabel: {
          color: '#9ca3af'
        },
        splitLine: {
          lineStyle: {
            color: '#374151'
          }
        }
      },
      series: chartData.value.series.map((series, index) => {
        const colors = ['#ea580c', '#ef4444', '#10b981'] // Orange, Red, Green
        const isFlowRate = series.name.includes('FlowRate')
        const isTemperature = series.name.includes('Temperature')
        const isPressure = series.name.includes('Pressure')
        
        return {
          name: isFlowRate ? 'Flow Rate' : isTemperature ? 'Temperature' : isPressure ? 'Pressure' : series.name,
          type: 'line',
          data: series.values,
          itemStyle: {
            color: colors[index % colors.length]
          },
          lineStyle: {
            color: colors[index % colors.length],
            width: 2
          },
          symbol: 'circle',
          symbolSize: 6,
          smooth: true
        }
      })
    }
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
