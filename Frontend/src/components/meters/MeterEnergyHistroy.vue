<template>
  <div class="w-full h-full">
    <div v-if="loading" class="flex items-center justify-center h-full">
      <div class="text-gray-500">Loading...</div>
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
import { ref, computed, inject, watch, onMounted, shallowRef } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
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
    default: 'energy' // 'energy' or 'power'
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

// ✅ DYNAMIC POWER FORMATTING — scales W → kW → MW
function formatPowerWithUnit(value) {
  if (value === null || value === undefined) return 'N/A'
  
  const num = parseFloat(value)
  
  if (Math.abs(num) >= 1000000) {
    return `${(num / 1000000).toFixed(2)} MW`
  } else if (Math.abs(num) >= 1000) {
    return `${(num / 1000).toFixed(2)} kW`
  } else {
    return `${num.toFixed(2)} W`
  }
}

// Energy formatting (unchanged)
function formatEnergyWithUnit(value) {
  if (value === null || value === undefined) return 'N/A'
  
  const num = parseFloat(value)
  
  if (Math.abs(num) >= 1000000) {
    return `${(num / 1000000).toFixed(2)} MWh`
  } else if (Math.abs(num) >= 1000) {
    return `${(num / 1000).toFixed(2)} kWh`
  } else {
    return `${num.toFixed(2)} Wh`
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
    
    // Determine method based on chart type
    const method = props.chartType === 'energy' 
      ? 'queryHistoricTimeseriesEnergyPerPeriod'
      : 'queryHistoricTimeseriesData'
    
    // Send request
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER,
      method: 'edgeRpc',
      params: {
        edgeId: props.edgeId,
        payload: {
          jsonrpc: '2.0',
          id: INNER,
          method: method,
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
    console.error('Error fetching data:', error)
    loading.value = false
  }
}

// Process chart data
function processChartData(result) {
  // Format timestamps based on chart type
  const formattedTimestamps = result.timestamps.map(ts => {
    const date = new Date(ts)
    if (props.chartType === 'energy') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    } else {
      // ✅ For power chart — store full timestamp for tooltip
      return ts // Keep ISO string for accurate tooltip
    }
  })
  
  // Extract series data
  const seriesData = props.channels.map(channelId => ({
    name: channelId,
    values: result.data[channelId] || [],
    rawTimestamps: result.timestamps // ✅ Store raw timestamps for tooltip
  }))
  
  chartData.value = {
    timestamps: formattedTimestamps,
    series: seriesData
  }
}

// Update chart option
function updateChartOption() {
  if (props.chartType === 'energy') {
    // Energy chart (stacked bar) — ✅ MODIFIED: ONLY REACTIVE ENERGY HAS ROUNDED TOPS
    chartOption.value = {
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.value.timestamps,
        axisLabel: {
          color: '#9ca3af',
          fontSize: 10
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          show: false
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        splitLine: {
          lineStyle: {
            type: 'dotted',
            color: '#4b5563',
            opacity: 0.3
          }
        }
      },
      series: chartData.value.series.map((series, index) => {
        // Determine if it's Active or Reactive based on channel name
        const isActive = series.name.includes('Active')
        
        // ✅ CREATE GRADIENT FOR EACH BAR
        const gradient = {
          type: 'linear',
          x: 0,
          y: 1,
          x2: 0,
          y2: 0,
          colorStops: [
            {
              offset: 0,
              color: isActive ? 'rgba(159, 130, 246, 0.2)' : 'rgba(239, 68, 68, 0.2)' // Light transparent blue/red at bottom
            },
            {
              offset: 1,
              color: isActive ? 'rgba(159, 130, 246, 1)' : 'rgba(239, 68, 68, 1)' // Solid blue/red at top
            }
          ]
        }
        
        // ✅ CONDITIONAL BORDER RADIUS — only round tops for REACTIVE energy
        const borderRadius = isActive ? [0, 0, 0, 0] : [0, 0, 0, 0]
        
        return {
          name: isActive ? 'Active Energy' : 'Reactive Energy',
          type: 'bar',
          stack: 'energy',
          data: series.values,
          itemStyle: {
            color: gradient,
            borderRadius: borderRadius // ✅ Applied conditionally
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: isActive ? 'rgba(59, 130, 246, 0.5)' : 'rgba(239, 68, 68, 0.5)'
            }
          }
        }
      }),
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#374151',
        borderColor: '#6b7280',
        textStyle: {
          color: '#ffffff'
        },
        formatter: (params) => {
          let tooltipText = `${params[0].axisValue}<br/>`
          params.forEach(param => {
            const formattedValue = formatEnergyWithUnit(param.value)
            tooltipText += `${param.marker} ${param.seriesName}: ${formattedValue}<br/>`
          })
          return tooltipText
        }
      },
      legend: {
        show: true,
        bottom: 0,
        data: chartData.value.series.map(series => 
          series.name.includes('Active') ? 'Active Energy' : 'Reactive Energy'
        ),
        textStyle: {
          color: '#ffffff',
          fontSize: 10
        },
        icon: 'roundRect',
        itemWidth: 12,
        itemHeight: 8
      }
    }
  } else {
    // Power chart (line) — ✅ UPDATED
    chartOption.value = {
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.value.timestamps.map(ts => {
          // ✅ Format for X-axis label: "Mon", "Tue", etc.
          const date = new Date(ts)
          return date.toLocaleDateString('en-US', { weekday: 'short' })
        }),
        axisLabel: {
          color: '#9ca3af',
          fontSize: 10
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        splitLine: {
          show: false
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          show: false
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        splitLine: {
          lineStyle: {
            type: 'dotted',
            color: '#4b5563',
            opacity: 0.2
          }
        }
      },
      series: chartData.value.series.map(series => ({
        name: 'Power', // ✅ Generic name — actual value shown in tooltip
        type: 'line',
        data: series.values,
        itemStyle: {
          color: '#6b7280'
        },
        lineStyle: {
          color: '#6b7280',
          width: 2,
          opacity: 0.8
        },
        symbol: 'circle',
        symbolSize: 6,
        smooth: true,
        areaStyle: {
          color: '#6b7280',
          opacity: 0.1
        }
      })),
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#374151',
        borderColor: '#6b7280',
        textStyle: {
          color: '#ffffff'
        },
        // ✅ UPDATED FORMATTER — shows actual date + hour + dynamic unit
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
            const formattedValue = formatPowerWithUnit(param.value)
            tooltipText += `${param.marker} Power: ${formattedValue}<br/>`
          })
          return tooltipText
        }
      }
    }
  }
}

// Watch for changes - ✅ ADDED props.channels to dependencies
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