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
  electricityForecast: [],
  electricityActual: [],
  gasForecast: [],
  gasActual: [],
  fuelForecast: [],
  fuelActual: []
})
const chartOption = shallowRef(null)

// Emission factors (kg CO₂ per unit)
const EMISSION_FACTORS = {
  electricity: 0.4, // kg CO₂ per kWh
  gas: 0.2, // kg CO₂ per kg
  fuel: 2.7 // kg CO₂ per L
}

// Generate forecast data based on consumption patterns
const generateForecastData = () => {
  const dataPoints = props.timeRange === 'day' ? 24 : props.timeRange === 'week' ? 7 : 30
  const timestamps = []
  const electricityForecast = []
  const electricityActual = []
  const gasForecast = []
  const gasActual = []
  const fuelForecast = []
  const fuelActual = []
  
  // Base consumption patterns
  const baseElectricity = 120 // kWh
  const baseGas = 45 // kg
  const baseFuel = 30 // L
  
  for (let i = 0; i < dataPoints; i++) {
    let timestamp
    
    if (props.timeRange === 'day') {
      const hour = i
      timestamp = `${hour.toString().padStart(2, '0')}:00`
    } else if (props.timeRange === 'week') {
      const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      timestamp = dayNames[i]
    } else {
      const day = i + 1
      timestamp = `Day ${day}`
    }
    
    // Generate consumption data (similar to consumption charts)
    let electricityConsumption, gasConsumption, fuelConsumption
    
    if (props.timeRange === 'day') {
      const hour = i
      const isPeakHour = hour >= 8 && hour <= 18
      const peakFactor = isPeakHour ? 1.4 : 0.7
      
      electricityConsumption = baseElectricity * peakFactor * (0.8 + Math.random() * 0.4)
      gasConsumption = baseGas * (0.8 + Math.random() * 0.4)
      fuelConsumption = baseFuel * (0.8 + Math.random() * 0.4)
    } else {
      const isWeekend = i >= 5
      const weekendFactor = isWeekend ? 0.8 : 1.0
      
      electricityConsumption = baseElectricity * 24 * weekendFactor * (0.8 + Math.random() * 0.4)
      gasConsumption = baseGas * 24 * (0.8 + Math.random() * 0.4)
      fuelConsumption = baseFuel * 24 * (isWeekend ? 1.2 : 0.9) * (0.8 + Math.random() * 0.4)
    }
    
    // Calculate emissions
    const electricityEmissions = electricityConsumption * EMISSION_FACTORS.electricity
    const gasEmissions = gasConsumption * EMISSION_FACTORS.gas
    const fuelEmissions = fuelConsumption * EMISSION_FACTORS.fuel
    
    timestamps.push(timestamp)
    electricityForecast.push(electricityEmissions)
    gasForecast.push(gasEmissions)
    fuelForecast.push(fuelEmissions)
    
    // For current period, show actual data if available
    if (props.currentOffset === 0 && (
      (props.timeRange === 'day' && i <= new Date().getHours()) ||
      (props.timeRange === 'week' && i <= new Date().getDay()) ||
      (props.timeRange === 'month' && i < new Date().getDate())
    )) {
      electricityActual.push(electricityEmissions * (0.9 + Math.random() * 0.2))
      gasActual.push(gasEmissions * (0.9 + Math.random() * 0.2))
      fuelActual.push(fuelEmissions * (0.9 + Math.random() * 0.2))
    } else {
      electricityActual.push(null)
      gasActual.push(null)
      fuelActual.push(null)
    }
  }
  
  return {
    timestamps,
    electricityForecast,
    electricityActual,
    gasForecast,
    gasActual,
    fuelForecast,
    fuelActual
  }
}

// Update chart option
const updateChartOption = () => {
  const data = generateForecastData()
  
  chartData.value = data
  
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
          tooltipText += `${param.marker} ${param.seriesName}: ${value} kg CO₂<br/>`
        })
        return tooltipText
      }
    },
    legend: {
      data: [
        'Electricity Forecast', 'Electricity Actual',
        'Gas Forecast', 'Gas Actual',
        'Fuel Forecast', 'Fuel Actual'
      ],
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
      data: data.timestamps,
      axisLine: {
        lineStyle: {
          color: '#6b7280'
        }
      },
      axisLabel: {
        color: '#9ca3af',
        rotate: data.timestamps.length > 20 ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: 'Emissions (kg CO₂)',
      axisLine: {
        lineStyle: {
          color: '#6b7280'
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
        name: 'Electricity Forecast',
        type: 'line',
        data: data.electricityForecast,
        itemStyle: {
          color: '#3b82f6'
        },
        lineStyle: {
          color: '#3b82f6',
          width: 2
        },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Electricity Actual',
        type: 'line',
        data: data.electricityActual,
        itemStyle: {
          color: '#60a5fa'
        },
        lineStyle: {
          color: '#60a5fa',
          width: 2,
          type: 'dashed'
        },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Gas Forecast',
        type: 'line',
        data: data.gasForecast,
        itemStyle: {
          color: '#ea580c'
        },
        lineStyle: {
          color: '#ea580c',
          width: 2
        },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Gas Actual',
        type: 'line',
        data: data.gasActual,
        itemStyle: {
          color: '#fb923c'
        },
        lineStyle: {
          color: '#fb923c',
          width: 2,
          type: 'dashed'
        },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Fuel Forecast',
        type: 'line',
        data: data.fuelForecast,
        itemStyle: {
          color: '#ef4444'
        },
        lineStyle: {
          color: '#ef4444',
          width: 2
        },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Fuel Actual',
        type: 'line',
        data: data.fuelActual,
        itemStyle: {
          color: '#f87171'
        },
        lineStyle: {
          color: '#f87171',
          width: 2,
          type: 'dashed'
        },
        symbol: 'circle',
        symbolSize: 4,
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
