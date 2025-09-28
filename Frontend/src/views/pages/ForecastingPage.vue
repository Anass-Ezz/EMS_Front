<template>
  <div class="min-h-screen text-white p-6">
    <!-- Time Range Selector -->
    <div class="mb-6">
      <RangeToggle v-model="timeRange" class="mb-4"/>
    </div>

    <!-- Navigation Controls -->
    <div class="mb-6 flex justify-between items-center">
      <div class="flex items-center gap-4">
        <button 
          @click="navigateTime(-1)"
          class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          :disabled="loading"
        >
          <i class="bi bi-chevron-left mr-2"></i>
          Previous {{ timeRangeLabel }}
        </button>
        
        <div class="text-lg font-semibold">
          {{ currentPeriodLabel }}
        </div>
        
        <button 
          @click="navigateTime(1)"
          class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          :disabled="loading"
        >
          Next {{ timeRangeLabel }}
          <i class="bi bi-chevron-right ml-2"></i>
        </button>
      </div>
      
      <div class="text-sm text-gray-400">
        Showing forecast vs actual data
      </div>
    </div>

    <!-- Consumption Section -->
    <div class="mb-8">
      <h2 class="text-2xl font-bold mb-6 flex items-center">
        <i class="bi bi-lightning-charge text-blue-500 text-2xl mr-3"></i>
        Energy Consumption Forecast
      </h2>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Electricity Consumption -->
        <div class="border border-gray-600 rounded-lg p-6">
          <div class="flex items-baseline mb-4">
            <i class="bi bi-lightning text-blue-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Electricity Consumption</h3>
              <p class="text-sm text-gray-400">kWh consumption forecast</p>
            </div>
          </div>
          
          <!-- Average Metrics -->
          <div class="mb-4 grid grid-cols-2 gap-4 text-sm">
            <div class="bg-gray-800 p-3 rounded">
              <div class="text-gray-400">Forecast Avg</div>
              <div class="text-blue-400 font-semibold">{{ electricityForecastAvg }} kWh</div>
            </div>
            <div class="bg-gray-800 p-3 rounded">
              <div class="text-gray-400">Actual Avg</div>
              <div class="text-green-400 font-semibold">{{ electricityActualAvg }} kWh</div>
            </div>
          </div>
          
          <div class="h-64">
            <ElectricityConsumptionChart 
              :time-range="timeRange"
              :current-offset="currentOffset"
              :loading="loading"
            />
          </div>
        </div>

        <!-- Gas Consumption -->
        <div class="border border-gray-600 rounded-lg p-6">
          <div class="flex items-baseline mb-4">
            <i class="bi bi-fire text-orange-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Gas Consumption</h3>
              <p class="text-sm text-gray-400">kg consumption forecast</p>
            </div>
          </div>
          
          <!-- Average Metrics -->
          <div class="mb-4 grid grid-cols-2 gap-4 text-sm">
            <div class="bg-gray-800 p-3 rounded">
              <div class="text-gray-400">Forecast Avg</div>
              <div class="text-orange-400 font-semibold">{{ gasForecastAvg }} kg</div>
            </div>
            <div class="bg-gray-800 p-3 rounded">
              <div class="text-gray-400">Actual Avg</div>
              <div class="text-green-400 font-semibold">{{ gasActualAvg }} kg</div>
            </div>
          </div>
          
          <div class="h-64">
            <GasConsumptionChart 
              :time-range="timeRange"
              :current-offset="currentOffset"
              :loading="loading"
            />
          </div>
        </div>

        <!-- Fuel Consumption -->
        <div class="border border-gray-600 rounded-lg p-6">
          <div class="flex items-baseline mb-4">
            <i class="bi bi-droplet text-red-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Fuel Consumption</h3>
              <p class="text-sm text-gray-400">L consumption forecast</p>
            </div>
          </div>
          
          <!-- Average Metrics -->
          <div class="mb-4 grid grid-cols-2 gap-4 text-sm">
            <div class="bg-gray-800 p-3 rounded">
              <div class="text-gray-400">Forecast Avg</div>
              <div class="text-red-400 font-semibold">{{ fuelForecastAvg }} L</div>
            </div>
            <div class="bg-gray-800 p-3 rounded">
              <div class="text-gray-400">Actual Avg</div>
              <div class="text-green-400 font-semibold">{{ fuelActualAvg }} L</div>
            </div>
          </div>
          
          <div class="h-64">
            <FuelConsumptionChart 
              :time-range="timeRange"
              :current-offset="currentOffset"
              :loading="loading"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Generation and Emissions Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Solar Generation -->
      <div class="border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-sun text-yellow-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Solar Generation Forecast</h3>
            <p class="text-sm text-gray-400">kW generation forecast</p>
          </div>
        </div>
        
        <!-- Average Metrics -->
        <div class="mb-4 grid grid-cols-2 gap-4 text-sm">
          <div class="bg-gray-800 p-3 rounded">
            <div class="text-gray-400">Forecast Avg</div>
            <div class="text-yellow-400 font-semibold">{{ solarForecastAvg }} kW</div>
          </div>
          <div class="bg-gray-800 p-3 rounded">
            <div class="text-gray-400">Actual Avg</div>
            <div class="text-green-400 font-semibold">{{ solarActualAvg }} kW</div>
          </div>
        </div>
        
        <div class="h-80">
          <SolarGenerationChart 
            :time-range="timeRange"
            :current-offset="currentOffset"
            :loading="loading"
          />
        </div>
      </div>

      <!-- Emissions -->
      <div class="border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-cloud text-gray-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Emissions Forecast</h3>
            <p class="text-sm text-gray-400">CO₂ emissions forecast</p>
          </div>
        </div>
        
        <!-- Average Metrics -->
        <div class="mb-4 grid grid-cols-2 gap-4 text-sm">
          <div class="bg-gray-800 p-3 rounded">
            <div class="text-gray-400">Forecast Avg</div>
            <div class="text-gray-400 font-semibold">{{ emissionsForecastAvg }} kg CO₂</div>
          </div>
          <div class="bg-gray-800 p-3 rounded">
            <div class="text-gray-400">Actual Avg</div>
            <div class="text-green-400 font-semibold">{{ emissionsActualAvg }} kg CO₂</div>
          </div>
        </div>
        
        <div class="h-80">
          <EmissionsChart 
            :time-range="timeRange"
            :current-offset="currentOffset"
            :loading="loading"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import RangeToggle from '@/components/dashboard/RangeToggle.vue'
import ElectricityConsumptionChart from '@/components/forecasting/ElectricityConsumptionChart.vue'
import EmissionsChart from '@/components/forecasting/EmissionsChart.vue'
import FuelConsumptionChart from '@/components/forecasting/FuelConsumptionChart.vue'
import GasConsumptionChart from '@/components/forecasting/GasConsumptionChart.vue'
import SolarGenerationChart from '@/components/forecasting/SolarGenerationChart.vue'
import { computed, ref, watch } from 'vue'

// Reactive state
const timeRange = ref('day') // 'day' | 'week' | 'month'
const currentOffset = ref(0) // 0 = current period, 1 = next period, -1 = previous period
const loading = ref(false)

// Computed properties
const timeRangeLabel = computed(() => {
  switch(timeRange.value) {
    case 'day': return 'Day'
    case 'week': return 'Week'
    case 'month': return 'Month'
    default: return 'Day'
  }
})

const currentPeriodLabel = computed(() => {
  const now = new Date()
  const offset = currentOffset.value
  
  if (timeRange.value === 'day') {
    const targetDate = new Date(now)
    targetDate.setDate(now.getDate() + offset)
    return targetDate.toLocaleDateString('en-US', { 
      weekday: 'long', 
      month: 'long', 
      day: 'numeric' 
    })
  } else if (timeRange.value === 'week') {
    const targetDate = new Date(now)
    targetDate.setDate(now.getDate() + (offset * 7))
    const weekStart = new Date(targetDate)
    weekStart.setDate(targetDate.getDate() - targetDate.getDay())
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 6)
    
    return `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
  } else if (timeRange.value === 'month') {
    const targetDate = new Date(now)
    targetDate.setMonth(now.getMonth() + offset)
    return targetDate.toLocaleDateString('en-US', { 
      month: 'long', 
      year: 'numeric' 
    })
  }
  return 'Current Period'
})

// Mock data for averages (will be replaced with real data)
const electricityForecastAvg = ref('125.4')
const electricityActualAvg = ref('118.7')
const gasForecastAvg = ref('45.2')
const gasActualAvg = ref('42.8')
const fuelForecastAvg = ref('28.9')
const fuelActualAvg = ref('26.3')
const solarForecastAvg = ref('85.6')
const solarActualAvg = ref('78.2')
const emissionsForecastAvg = ref('156.8')
const emissionsActualAvg = ref('142.3')

// Navigation functions
const navigateTime = (direction) => {
  loading.value = true
  currentOffset.value += direction
  
  // Simulate loading delay
  setTimeout(() => {
    loading.value = false
  }, 500)
}

// Watch for time range changes
watch(timeRange, () => {
  currentOffset.value = 0
  loading.value = true
  
  setTimeout(() => {
    loading.value = false
  }, 500)
})
</script>

<style scoped>
/* Custom styles for the forecasting page */
</style>
