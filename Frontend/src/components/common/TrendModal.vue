<template>
  <Dialog 
    v-model:visible="visible" 
    :header="`${metricName} Trend`" 
    :modal="true" 
    :closable="true"
    :style="{ width: '80vw', maxWidth: '1200px' }"
    class="trend-modal"
  >
    <div class="trend-content">
      <div v-if="loading" class="loading-state">
        <i class="bi bi-hourglass-split text-orange-500 text-2xl mr-2"></i>
        <span>Loading trend data...</span>
      </div>
      
      <div v-else-if="error" class="error-state">
        <i class="bi bi-exclamation-triangle text-red-500 text-2xl mr-2"></i>
        <span>{{ error }}</span>
      </div>
      
      <div v-else-if="chartData.length === 0" class="no-data-state">
        <i class="bi bi-graph-down text-gray-500 text-2xl mr-2"></i>
        <span>No data available for this metric</span>
      </div>
      
      <div v-else class="chart-container">
        <div class="chart-header">
          <div class="metric-info">
            <h4 class="metric-title">{{ metricName }}</h4>
            <p class="metric-description">{{ metricDescription }}</p>
          </div>
          <div class="time-range">
            <span class="text-sm text-gray-400">
              Last {{ timeRange }} • {{ chartData.length }} data points
            </span>
          </div>
        </div>
        
        <div class="chart-wrapper">
          <v-chart 
            :option="chartOption" 
            :style="{ height: '400px', width: '100%' }"
            autoresize
          />
        </div>
        
        <div class="chart-footer">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">Current</span>
              <span class="stat-value">{{ currentValue }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Average</span>
              <span class="stat-value">{{ averageValue }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Min</span>
              <span class="stat-value">{{ minValue }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Max</span>
              <span class="stat-value">{{ maxValue }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Dialog>
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
import Dialog from 'primevue/dialog'
import { computed, ref, watch } from 'vue'
import VChart from 'vue-echarts'

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen(ws) {
  return new Promise((resolve) => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  metricName: {
    type: String,
    required: true
  },
  metricDescription: {
    type: String,
    default: ''
  },
  channel: {
    type: String,
    required: true
  },
  meterType: {
    type: String,
    required: true // 'electricity', 'gas', 'fuel'
  },
  meterIndex: {
    type: Number,
    required: true
  },
  // Pass dependencies as props instead of inject
  ws: {
    type: Object,
    required: true
  },
  auth: {
    type: Object,
    required: true
  },
  dateRange: {
    type: Object,
    required: true
  },
  resolution: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:visible'])

// Use props instead of inject
const ws = computed(() => props.ws)
const auth = computed(() => props.auth)
const dateRange = computed(() => props.dateRange)
const resolution = computed(() => props.resolution)

const loading = ref(false)
const error = ref(null)
const chartData = ref([])
const timeRange = ref('30 minutes')

const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const channelPrefix = computed(() => {
  switch (props.meterType) {
    case 'electricity':
      return `meter${props.meterIndex}/`
    case 'gas':
      return `gasmeter${props.meterIndex}/`
    case 'fuel':
      return `fuelmeter${props.meterIndex}/`
    default:
      return ''
  }
})

const chartOption = computed(() => {
  if (chartData.value.length === 0) return {}

  const times = chartData.value.map(item => item.time)
  const values = chartData.value.map(item => item.value)

  return {
    title: {
      text: `${props.metricName} Over Time`,
      left: 'center',
      textStyle: {
        color: '#d1d5db',
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#374151',
      borderColor: '#4b5563',
      textStyle: {
        color: '#d1d5db'
      },
      formatter: function(params) {
        const point = params[0]
        return `
          <div>
            <strong>${point.axisValue}</strong><br/>
            ${props.metricName}: <strong>${point.value} ${getUnit()}</strong>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
      backgroundColor: 'transparent'
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: times,
      axisLine: {
        lineStyle: {
          color: '#4b5563'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        fontSize: 10,
        interval: 'auto'
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#4b5563'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        formatter: `{value} ${getUnit()}`
      },
      splitLine: {
        lineStyle: {
          color: '#374151'
        }
      }
    },
    series: [
      {
        name: props.metricName,
        type: 'line',
        data: values,
        smooth: true,
        lineStyle: {
          color: '#ea580c',
          width: 2
        },
        itemStyle: {
          color: '#ea580c'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(234, 88, 12, 0.3)' },
              { offset: 1, color: 'rgba(234, 88, 12, 0.05)' }
            ]
          }
        }
      }
    ]
  }
})

const currentValue = computed(() => {
  if (chartData.value.length === 0) return '—'
  return formatValue(chartData.value[0].value) + ' ' + getUnit()
})

const averageValue = computed(() => {
  if (chartData.value.length === 0) return '—'
  const sum = chartData.value.reduce((acc, item) => acc + item.value, 0)
  const avg = sum / chartData.value.length
  return formatValue(avg) + ' ' + getUnit()
})

const minValue = computed(() => {
  if (chartData.value.length === 0) return '—'
  const min = Math.min(...chartData.value.map(item => item.value))
  return formatValue(min) + ' ' + getUnit()
})

const maxValue = computed(() => {
  if (chartData.value.length === 0) return '—'
  const max = Math.max(...chartData.value.map(item => item.value))
  return formatValue(max) + ' ' + getUnit()
})

function getUnit() {
  const unitMap = {
    'V L1': 'V', 'V L2': 'V', 'V L3': 'V',
    'A L1': 'A', 'A L2': 'A', 'A L3': 'A',
    'kW': 'kW', 'PF': '', 'Hz': 'Hz',
    'Flow Rate': props.meterType === 'gas' ? 'm³/s' : 'kg/s',
    'Temperature': '°C',
    'Pressure': 'bar',
    'Consumption': props.meterType === 'gas' ? 'm³/h' : 'kg/h'
  }
  return unitMap[props.metricName] || ''
}

function formatValue(value, decimals = 2) {
  if (value == null || !Number.isFinite(value)) return '—'
  
  // Apply scaling factors based on meter type and metric
  let scaledValue = value
  
  if (props.meterType === 'gas') {
    if (props.metricName === 'Flow Rate') {
      scaledValue = value / 1000 // g/s → kg/s
    } else if (props.metricName === 'Temperature') {
      scaledValue = value / 10 // deci-°C → °C
    } else if (props.metricName === 'Pressure') {
      scaledValue = value / 1000 // mbar → bar
    } else if (props.metricName === 'Consumption') {
      scaledValue = value / 1000 // g → kg
    }
  } else if (props.meterType === 'fuel') {
    if (props.metricName === 'Flow Rate') {
      scaledValue = value / 1000 // mL/s → L/s
    } else if (props.metricName === 'Temperature') {
      scaledValue = value / 10 // deci-°C → °C
    } else if (props.metricName === 'Pressure') {
      scaledValue = value / 1000 // mbar → bar
    } else if (props.metricName === 'Consumption') {
      scaledValue = value / 1000 // mL → L
    }
  }
  
  // Special formatting for different metrics
  if (props.metricName === 'Flow Rate' && props.meterType === 'gas') {
    return scaledValue.toFixed(4)
  } else if (props.metricName === 'Flow Rate' && props.meterType === 'fuel') {
    return scaledValue.toFixed(1)
  } else if (props.metricName === 'Temperature') {
    return scaledValue.toFixed(1)
  } else if (props.metricName === 'Pressure') {
    return scaledValue.toFixed(props.meterType === 'gas' ? 2 : 1)
  } else if (props.metricName === 'Consumption') {
    return scaledValue.toFixed(props.meterType === 'gas' ? 2 : 1)
  }
  
  return scaledValue.toFixed(decimals)
}

// Watch for modal visibility changes to fetch data
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    fetchTrendData()
  }
})

// Fetch trend data when modal opens
async function fetchTrendData() {
  if (!props.visible) return
  
  loading.value = true
  error.value = null
  chartData.value = []
  
  try {
    // For now, generate sample data to show the trend modal works
    // TODO: Replace with real API call once we fix the WebSocket issues
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay
    
    const now = new Date()
    const sampleData = []
    
    // Generate 30 data points over the last 30 minutes (chronological order: oldest to newest)
    for (let i = 0; i < 30; i++) {
      const time = new Date(now.getTime() - (29 - i) * 60 * 1000)
      const baseValue = getBaseValue()
      const variation = (Math.random() - 0.5) * 0.2
      const value = Math.max(0, baseValue + variation)
      
      sampleData.push({
        time: time.toLocaleTimeString([], { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        value: value
      })
    }
    
    chartData.value = sampleData
    console.log('Generated sample trend data:', chartData.value)
    
  } catch (err) {
    error.value = 'Failed to load trend data'
    console.error('Error fetching trend data:', err)
  } finally {
    loading.value = false
  }
}

// TODO: Implement real API data processing when WebSocket issues are resolved

function getBaseValue() {
  // Return base values based on metric and meter type
  const baseValues = {
    'electricity': {
      'V L1': 220, 'V L2': 220, 'V L3': 220,
      'A L1': 5.5, 'A L2': 5.2, 'A L3': 5.8,
      'kW': 3.2, 'PF': 0.85, 'Hz': 50
    },
    'gas': {
      'Flow Rate': 0.010,
      'Temperature': 22,
      'Pressure': 0.3,
      'Consumption': 36
    },
    'fuel': {
      'Flow Rate': 0.35,
      'Temperature': 37,
      'Pressure': 2.2,
      'Consumption': 1260
    }
  }
  
  return baseValues[props.meterType]?.[props.metricName] || 1
}
</script>

<style scoped>
.trend-modal :deep(.p-dialog) {
  background: #1f2937;
  color: #d1d5db;
  border: 1px solid #4b5563;
}

.trend-modal :deep(.p-dialog-header) {
  background: #374151;
  border-bottom: 1px solid #4b5563;
  color: #d1d5db;
}

.trend-modal :deep(.p-dialog-content) {
  background: #1f2937;
  padding: 1.5rem;
}

.trend-content {
  min-height: 500px;
}

.loading-state,
.error-state,
.no-data-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  font-size: 1.1rem;
  color: #9ca3af;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 1rem;
  border-bottom: 1px solid #374151;
}

.metric-info h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #d1d5db;
  margin: 0 0 0.25rem 0;
}

.metric-description {
  color: #9ca3af;
  margin: 0;
  font-size: 0.875rem;
}

.time-range {
  text-align: right;
}

.chart-wrapper {
  background: #111827;
  border: 1px solid #374151;
  border-radius: 0.5rem;
  padding: 1rem;
}

.chart-footer {
  padding-top: 1rem;
  border-top: 1px solid #374151;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  display: block;
  font-size: 1.125rem;
  font-weight: 600;
  color: #ea580c;
}
</style>
