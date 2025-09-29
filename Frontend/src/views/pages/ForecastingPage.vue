<template>
  <div class="min-h-screen text-white p-6">
    <!-- Time Range Selector -->
    <div class="mb-6">
      <ForecastingTimeSelector 
        v-model="timeRange" 
        :current-offset="currentOffset"
        @offset-change="handleOffsetChange"
      />
    </div>

    <!-- Consumption Section -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold mb-4 flex items-center">
        <i class="bi bi-lightning-charge text-orange-500 text-xl mr-3"></i>
        Energy Consumption Forecast
      </h2>
      <div class="grid grid-cols-12 gap-6">
        <!-- Electricity Consumption -->
        <div class="col-span-4 border border-gray-600 rounded-lg p-6">
          <div class="flex items-baseline mb-4">
            <i class="bi bi-lightning-charge text-blue-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Electricity Consumption</h3>
              <p class="text-sm text-gray-400">Forecast vs Actual (kWh)</p>
            </div>
          </div>
          
          <!-- Statistics at the top -->
          <div class="mb-4 grid grid-cols-3 gap-2 text-sm">
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Actual</div>
              <div class="text-white font-semibold text-sm">{{ electricityStats.actualAvg }} kWh</div>
            </div>
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Forecast</div>
              <div class="text-white font-semibold text-sm">{{ electricityStats.forecastAvg }} kWh</div>
            </div>
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Error</div>
              <div class="text-white font-semibold text-sm" :class="electricityStats.error >= 0 ? 'text-red-400' : 'text-green-400'">
                {{ electricityStats.error >= 0 ? '+' : '' }}{{ electricityStats.error }}%
              </div>
            </div>
          </div>
          
          <div class="h-80">
            <ElectricityConsumptionChart 
              :time-range="timeRange"
              :offset="currentOffset"
              @update-stats="updateElectricityStats"
            />
          </div>
        </div>

        <!-- Gas Consumption -->
        <div class="col-span-4 border border-gray-600 rounded-lg p-6">
          <div class="flex items-baseline mb-4">
            <i class="bi bi-fire text-orange-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Gas Consumption</h3>
              <p class="text-sm text-gray-400">Forecast vs Actual (kg)</p>
            </div>
          </div>
          
          <!-- Statistics at the top -->
          <div class="mb-4 grid grid-cols-3 gap-2 text-sm">
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Actual</div>
              <div class="text-white font-semibold text-sm">{{ gasStats.actualAvg }} kg</div>
            </div>
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Forecast</div>
              <div class="text-white font-semibold text-sm">{{ gasStats.forecastAvg }} kg</div>
            </div>
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Error</div>
              <div class="text-white font-semibold text-sm" :class="gasStats.error >= 0 ? 'text-red-400' : 'text-green-400'">
                {{ gasStats.error >= 0 ? '+' : '' }}{{ gasStats.error }}%
              </div>
            </div>
          </div>
          
          <div class="h-80">
            <GasConsumptionChart 
              :time-range="timeRange"
              :offset="currentOffset"
              @update-stats="updateGasStats"
            />
          </div>
        </div>

        <!-- Fuel Consumption -->
        <div class="col-span-4 border border-gray-600 rounded-lg p-6">
          <div class="flex items-baseline mb-4">
            <i class="bi bi-droplet text-red-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Fuel Consumption</h3>
              <p class="text-sm text-gray-400">Forecast vs Actual (L)</p>
            </div>
          </div>
          
          <!-- Statistics at the top -->
          <div class="mb-4 grid grid-cols-3 gap-2 text-sm">
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Actual</div>
              <div class="text-white font-semibold text-sm">{{ fuelStats.actualAvg }} L</div>
            </div>
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Forecast</div>
              <div class="text-white font-semibold text-sm">{{ fuelStats.forecastAvg }} L</div>
            </div>
            <div class="bg-gray-800 p-2 rounded text-center">
              <div class="text-gray-400 text-xs">Error</div>
              <div class="text-white font-semibold text-sm" :class="fuelStats.error >= 0 ? 'text-red-400' : 'text-green-400'">
                {{ fuelStats.error >= 0 ? '+' : '' }}{{ fuelStats.error }}%
              </div>
            </div>
          </div>
          
          <div class="h-80">
            <FuelConsumptionChart 
              :time-range="timeRange"
              :offset="currentOffset"
              @update-stats="updateFuelStats"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Generation and Emissions Section -->
    <div class="grid grid-cols-12 gap-6">
      <!-- Solar Generation -->
      <div class="col-span-6 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-sun text-yellow-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Solar Generation Forecast</h3>
            <p class="text-sm text-gray-400">Power generation throughout the day (kW)</p>
          </div>
        </div>
        
        <!-- Statistics at the top -->
        <div class="mb-4 grid grid-cols-3 gap-2 text-sm">
          <div class="bg-gray-800 p-2 rounded text-center">
            <div class="text-gray-400 text-xs">Actual</div>
            <div class="text-white font-semibold text-sm">{{ solarStats.actualAvg }} kW</div>
          </div>
          <div class="bg-gray-800 p-2 rounded text-center">
            <div class="text-gray-400 text-xs">Forecast</div>
            <div class="text-white font-semibold text-sm">{{ solarStats.forecastAvg }} kW</div>
          </div>
          <div class="bg-gray-800 p-2 rounded text-center">
            <div class="text-gray-400 text-xs">Error</div>
            <div class="text-white font-semibold text-sm" :class="solarStats.error >= 0 ? 'text-red-400' : 'text-green-400'">
              {{ solarStats.error >= 0 ? '+' : '' }}{{ solarStats.error }}%
            </div>
          </div>
        </div>
        
        <div class="h-80">
          <SolarGenerationChart 
            :time-range="timeRange"
            :offset="currentOffset"
            @update-stats="updateSolarStats"
          />
        </div>
      </div>

      <!-- Emissions -->
      <div class="col-span-6 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <p class="text-gray-400 text-xl mr-3">CO₂</p>
          <div>
            <h3 class="font-semibold">Emissions Forecast</h3>
            <p class="text-sm text-gray-400">CO₂ emissions from energy consumption (kg)</p>
          </div>
        </div>
        
        <!-- Statistics at the top -->
        <div class="mb-4 grid grid-cols-3 gap-2 text-sm">
          <div class="bg-gray-800 p-2 rounded text-center">
            <div class="text-gray-400 text-xs">Electricity</div>
            <div class="text-white font-semibold text-sm">{{ emissionsStats.electricityAvg }} kg</div>
          </div>
          <div class="bg-gray-800 p-2 rounded text-center">
            <div class="text-gray-400 text-xs">Gas</div>
            <div class="text-white font-semibold text-sm">{{ emissionsStats.gasAvg }} kg</div>
          </div>
          <div class="bg-gray-800 p-2 rounded text-center">
            <div class="text-gray-400 text-xs">Fuel</div>
            <div class="text-white font-semibold text-sm">{{ emissionsStats.fuelAvg }} kg</div>
          </div>
        </div>
        
        <div class="h-80">
          <EmissionsChart 
            :time-range="timeRange"
            :offset="currentOffset"
            @update-stats="updateEmissionsStats"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ElectricityConsumptionChart from '@/components/forecasting/ElectricityConsumptionChart.vue'
import EmissionsChart from '@/components/forecasting/EmissionsChart.vue'
import ForecastingTimeSelector from '@/components/forecasting/ForecastingTimeSelector.vue'
import FuelConsumptionChart from '@/components/forecasting/FuelConsumptionChart.vue'
import GasConsumptionChart from '@/components/forecasting/GasConsumptionChart.vue'
import SolarGenerationChart from '@/components/forecasting/SolarGenerationChart.vue'
import { reactive, ref } from 'vue'

// Time range selector
const timeRange = ref('day')
const currentOffset = ref(0)

// Stats for each chart
const electricityStats = reactive({
  actualAvg: 0,
  forecastAvg: 0,
  error: 0
})

const gasStats = reactive({
  actualAvg: 0,
  forecastAvg: 0,
  error: 0
})

const fuelStats = reactive({
  actualAvg: 0,
  forecastAvg: 0,
  error: 0
})

const solarStats = reactive({
  actualAvg: 0,
  forecastAvg: 0,
  error: 0
})

const emissionsStats = reactive({
  electricityAvg: 0,
  gasAvg: 0,
  fuelAvg: 0
})

// Handle offset changes from time selector
const handleOffsetChange = (offset) => {
  currentOffset.value = offset
}

// Update stats from child components
const updateElectricityStats = (stats) => {
  Object.assign(electricityStats, stats)
}

const updateGasStats = (stats) => {
  Object.assign(gasStats, stats)
}

const updateFuelStats = (stats) => {
  Object.assign(fuelStats, stats)
}

const updateSolarStats = (stats) => {
  Object.assign(solarStats, stats)
}

const updateEmissionsStats = (stats) => {
  Object.assign(emissionsStats, stats)
}
</script>

<style scoped>
/* Custom styles for the forecasting page */
</style>