<template>
  <div class="w-full h-full">
    <div v-if="loading" class="flex items-center justify-center h-full">
      <div class="text-gray-500">Loading emissions data...</div>
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

const props = defineProps({
  timeRange: { type: String, default: 'day' },
  offset: { type: Number, default: 0 }
})

const emit = defineEmits(['update-stats'])

const ws = inject('ws')
const auth = inject('auth')

const loading = ref(false)
const chartData = ref({
  timestamps: [],
  electricityActual: [],
  electricityForecast: [],
  gasActual: [],
  gasForecast: [],
  fuelActual: [],
  fuelForecast: []
})
const chartOption = shallowRef(null)

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
      startOfWeek.setDate(now.getDate() - now.getDay() + 1 + (offset * 7))
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

function waitForSocketOpen(ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

async function fetchConsumptionData() {
  if (!auth.ready || !ws) return null
  
  try {
    await waitForSocketOpen(ws)
    
    const OUTER = crypto.randomUUID()
    const INNER = crypto.randomUUID()
    
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
            channels: [
              'meter0/ActiveEnergy',
              'gasmeter0/Consumption', 
              'fuelmeter0/Consumption'
            ],
            fromDate: dateRange.value.from,
            toDate: dateRange.value.to,
            resolution: {
              value: props.timeRange === 'day' ? 1 : 1,
              unit: props.timeRange === 'day' ? 'HOURS' : 'DAYS'
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
    console.error('Error fetching consumption data:', error)
    return null
  }
}

function calculateEmissions(consumptionData) {
  if (!consumptionData || !consumptionData.timestamps || !consumptionData.data) {
    return null
  }
  
  const electricityData = consumptionData.data['meter0/ActiveEnergy'] || []
  const gasData = consumptionData.data['gasmeter0/Consumption'] || []
  const fuelData = consumptionData.data['fuelmeter0/Consumption'] || []
  
  const ELECTRICITY_EMISSION_FACTOR = 0.5
  const GAS_EMISSION_FACTOR = 0.2
  const FUEL_EMISSION_FACTOR = 2.3
  
  const electricityEmissions = electricityData.map(value => {
    if (value === null || value === undefined) return value
    return (value / 1000) * ELECTRICITY_EMISSION_FACTOR
  })
  
  const gasEmissions = gasData.map(value => {
    if (value === null || value === undefined) return value
    return (value / 1000) * GAS_EMISSION_FACTOR
  })
  
  const fuelEmissions = fuelData.map(value => {
    if (value === null || value === undefined) return value
    return (value / 1000) * FUEL_EMISSION_FACTOR
  })
  
  return {
    timestamps: consumptionData.timestamps,
    electricity: electricityEmissions,
    gas: gasEmissions,
    fuel: fuelEmissions
  }
}

function generateForecastEmissions(actualEmissions) {
  if (!actualEmissions) return null
  
  const forecastElectricity = actualEmissions.electricity.map(value => {
    if (value === null || value === undefined) return value
    const variation = (Math.random() - 0.5) * 0.2 + 0.1
    return value * (1 + variation)
  })
  
  const forecastGas = actualEmissions.gas.map(value => {
    if (value === null || value === undefined) return value
    const variation = (Math.random() - 0.5) * 0.2 + 0.1
    return value * (1 + variation)
  })
  
  const forecastFuel = actualEmissions.fuel.map(value => {
    if (value === null || value === undefined) return value
    const variation = (Math.random() - 0.5) * 0.2 + 0.1
    return value * (1 + variation)
  })
  
  return {
    timestamps: actualEmissions.timestamps,
    electricity: forecastElectricity,
    gas: forecastGas,
    fuel: forecastFuel
  }
}

async function fetchData() {
  if (!auth.ready || !ws) return
  
  loading.value = true
  
  try {
    const consumptionData = await fetchConsumptionData()
    
    if (consumptionData && consumptionData.timestamps && consumptionData.data) {
      const actualEmissions = calculateEmissions(consumptionData)
      
      if (actualEmissions) {
        const forecastEmissions = generateForecastEmissions(actualEmissions)
        
        processChartData(actualEmissions, forecastEmissions)
        updateChartOption()
        
        calculateAndEmitStats(actualEmissions, forecastEmissions)
      }
    }
  } catch (error) {
    console.error('Error fetching emissions data:', error)
  } finally {
    loading.value = false
  }
}

function processChartData(actualEmissions, forecastEmissions) {
  let timestamps = actualEmissions.timestamps || []
  let electricityActual = actualEmissions.electricity || []
  let gasActual = actualEmissions.gas || []
  let fuelActual = actualEmissions.fuel || []
  let electricityForecast = forecastEmissions ? forecastEmissions.electricity : []
  let gasForecast = forecastEmissions ? forecastEmissions.gas : []
  let fuelForecast = forecastEmissions ? forecastEmissions.fuel : []
  
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
    electricityActual = electricityActual.slice(0, cutoffIndex)
    gasActual = gasActual.slice(0, cutoffIndex)
    fuelActual = fuelActual.slice(0, cutoffIndex)
    electricityForecast = electricityForecast.slice(0, cutoffIndex)
    gasForecast = gasForecast.slice(0, cutoffIndex)
    fuelForecast = fuelForecast.slice(0, cutoffIndex)
  }
  
  // Get current time for filtering future data
  const now = new Date()
  
  // Filter out future actual data - only show actual data up to current time
  const filteredElectricityActual = electricityActual.map((value, index) => {
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
  
  const filteredGasActual = gasActual.map((value, index) => {
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
  
  const filteredFuelActual = fuelActual.map((value, index) => {
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
    electricityActual: filteredElectricityActual,
    electricityForecast: electricityForecast,
    gasActual: filteredGasActual,
    gasForecast: gasForecast,
    fuelActual: filteredFuelActual,
    fuelForecast: fuelForecast
  }
}

function calculateAndEmitStats(actualEmissions, forecastEmissions) {
  let timestamps = actualEmissions.timestamps || []
  let electricityActual = actualEmissions.electricity || []
  let gasActual = actualEmissions.gas || []
  let fuelActual = actualEmissions.fuel || []
  
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
    electricityActual = electricityActual.slice(0, cutoffIndex)
    gasActual = gasActual.slice(0, cutoffIndex)
    fuelActual = fuelActual.slice(0, cutoffIndex)
  }
  
  // Get current time for filtering future data
  const now = new Date()
  
  // Filter actual values to only include data up to current time
  const filteredElectricityActual = electricityActual.filter((value, index) => {
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
  
  const filteredGasActual = gasActual.filter((value, index) => {
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
  
  const filteredFuelActual = fuelActual.filter((value, index) => {
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
  
  const electricityAvg = filteredElectricityActual.length > 0 ? 
    filteredElectricityActual.reduce((sum, val) => sum + (val || 0), 0) / filteredElectricityActual.length : 0
  
  const gasAvg = filteredGasActual.length > 0 ? 
    filteredGasActual.reduce((sum, val) => sum + (val || 0), 0) / filteredGasActual.length : 0
  
  const fuelAvg = filteredFuelActual.length > 0 ? 
    filteredFuelActual.reduce((sum, val) => sum + (val || 0), 0) / filteredFuelActual.length : 0
  
  emit('update-stats', {
    electricityAvg: electricityAvg.toFixed(2),
    gasAvg: gasAvg.toFixed(2),
    fuelAvg: fuelAvg.toFixed(2)
  })
}

function updateChartOption() {
  chartOption.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#4b5563',
      textStyle: { color: '#ffffff' },
      formatter: (params) => {
        let tooltipText = `${params[0].axisValue}<br/>`
        params.forEach(param => {
          const value = param.value
          const formattedValue = value !== null && value !== undefined ? 
            `${value.toFixed(2)} kg CO₂` : 'N/A'
          tooltipText += `${param.marker} ${param.seriesName}: ${formattedValue}<br/>`
        })
        return tooltipText
      }
    },
    legend: {
      data: [
        'Electricity Actual', 'Electricity Forecast',
        'Gas Actual', 'Gas Forecast', 
        'Fuel Actual', 'Fuel Forecast'
      ],
      textStyle: { color: '#d1d5db' },
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
      data: chartData.value.timestamps,
      axisLine: { lineStyle: { color: '#4b5563' } },
      axisLabel: {
        color: '#9ca3af',
        rotate: chartData.value.timestamps.length > 20 ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: 'Emissions (kg CO₂)',
      axisLine: { lineStyle: { color: '#4b5563' } },
      axisLabel: { color: '#9ca3af' },
      splitLine: { lineStyle: { color: '#374151' } }
    },
    series: [
      {
        name: 'Electricity Actual',
        type: 'line',
        data: chartData.value.electricityActual,
        itemStyle: { color: '#3b82f6' },
        lineStyle: { color: '#3b82f6', width: 2 },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Electricity Forecast',
        type: 'line',
        data: chartData.value.electricityForecast,
        itemStyle: { color: '#60a5fa' },
        lineStyle: { color: '#60a5fa', width: 2, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Gas Actual',
        type: 'line',
        data: chartData.value.gasActual,
        itemStyle: { color: '#ea580c' },
        lineStyle: { color: '#ea580c', width: 2 },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Gas Forecast',
        type: 'line',
        data: chartData.value.gasForecast,
        itemStyle: { color: '#fb923c' },
        lineStyle: { color: '#fb923c', width: 2, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Fuel Actual',
        type: 'line',
        data: chartData.value.fuelActual,
        itemStyle: { color: '#ef4444' },
        lineStyle: { color: '#ef4444', width: 2 },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      },
      {
        name: 'Fuel Forecast',
        type: 'line',
        data: chartData.value.fuelForecast,
        itemStyle: { color: '#f87171' },
        lineStyle: { color: '#f87171', width: 2, type: 'dashed' },
        symbol: 'circle',
        symbolSize: 4,
        smooth: true
      }
    ]
  }
}

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

onMounted(() => {
  if (auth.ready) {
    fetchData()
  }
})
</script>