<template>
  <div class="min-h-screen text-white p-6">
    <!-- Gas Meter Selection -->
    <GasMeterSelector />

    <!-- Stats Cards Row -->
    <div class="mb-6">
      <RealTimeGasMeterData />
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-12 gap-6 mb-6">
      <!-- Gas Consumption History Chart -->
      <div class="col-span-8 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-bar-chart text-orange-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Gas Consumption History</h3>
              <p class="text-sm text-gray-400">Gas consumption in cubic meters over time</p>
            </div>
          </div>
          <button 
            @click="downloadCSV('gas-consumption')"
            class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
          >
            <i class="bi bi-download text-xs"></i>
            Save CSV
          </button>
        </div>
        <div class="h-80">
          <GasConsumptionHistory 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}Consumption`]"
            :chart-type="'gas'"
          />
        </div>
      </div>

      <!-- Gas Average Values -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-calculator text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Average Values</h3>
          </div>
        </div>
        <div class="h-80">
          <GasAverageValues />
        </div>
      </div>
    </div>

    <!-- Bottom Row - Three Separate Charts -->
    <div class="grid grid-cols-12 gap-6 mb-6">
      <!-- Gas Flow Rate Chart -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-speedometer2 text-blue-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Flow Rate</h3>
              <p class="text-sm text-gray-400">Gas flow rate in m³/h</p>
            </div>
          </div>
          <button 
            @click="downloadCSV('gas-flow-rate')"
            class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
          >
            <i class="bi bi-download text-xs"></i>
            Save CSV
          </button>
        </div>
        <div class="h-64">
          <GasFlowRateChart 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}FlowRate`]"
          />
        </div>
      </div>

      <!-- Gas Temperature Chart -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-thermometer text-red-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Temperature</h3>
              <p class="text-sm text-gray-400">Gas temperature in °C</p>
            </div>
          </div>
          <button 
            @click="downloadCSV('gas-temperature')"
            class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
          >
            <i class="bi bi-download text-xs"></i>
            Save CSV
          </button>
        </div>
        <div class="h-64">
          <GasTemperatureChart 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}Temperature`]"
          />
        </div>
      </div>

      <!-- Gas Pressure Chart -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-speedometer text-green-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Pressure</h3>
              <p class="text-sm text-gray-400">Gas pressure in bar</p>
            </div>
          </div>
          <button 
            @click="downloadCSV('gas-pressure')"
            class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
          >
            <i class="bi bi-download text-xs"></i>
            Save CSV
          </button>
        </div>
        <div class="h-64">
          <GasPressureChart 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}Pressure`]"
          />
        </div>
      </div>
    </div>

    <!-- Gas Meter Alerts -->
    <div class="grid grid-cols-12 gap-6">
      <div class="col-span-12 border border-gray-600 rounded-lg p-6">
        <GasMeterAlerts :meter-id="route.query.meterId" />
      </div>
    </div>

    <!-- Live Gas Meter Readings Table -->
    <div class="mt-6">
      <GasMeterReadingsTable @update:latestReading="latestReading = $event" />
    </div>
  </div>
</template>

<script setup>
import GasAverageValues from '@/components/gas/GasAverageValues.vue'
import GasConsumptionHistory from '@/components/gas/GasConsumptionHistory.vue'
import GasFlowRateChart from '@/components/gas/GasFlowRateChart.vue'
import GasMeterAlerts from '@/components/gas/GasMeterAlerts.vue'
import GasMeterReadingsTable from '@/components/gas/GasMeterReadingsTable.vue'
import GasMeterSelector from '@/components/gas/GasMeterSelector.vue'
import GasPressureChart from '@/components/gas/GasPressureChart.vue'
import GasTemperatureChart from '@/components/gas/GasTemperatureChart.vue'
import RealTimeGasMeterData from '@/components/gas/RealTimeGasMeterData.vue'
import { PieChart } from 'echarts/charts'
import {
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent
} from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const route = useRoute()

// Hold latest gas meter reading
const latestReading = ref(null)

// Helper to safely convert string to number, fallback to 0
const safeNumber = (val) => {
  if (typeof val === 'string' && val.includes(' ')) {
    // Handle cases like "120.5 m³/s" or "2.5 bar"
    val = val.split(' ')[0]
  }
  const num = Number(val)
  return isNaN(num) ? 0 : num
}

// Gas Meter ID → Index Map
const gasMeterIdToIndex = {
  'gm-0': 0,
  'gm-1': 1
}

// Compute gas meter index based on route query
const meterIndex = computed(() => {
  const id = route.query.meterId
  return gasMeterIdToIndex[id] !== undefined ? gasMeterIdToIndex[id] : 0
})

// Compute channel prefix dynamically
const channelPrefix = computed(() => `gasmeter${meterIndex.value}/`)

// CSV download function
const downloadCSV = (type) => {
  const csvContent = 'Timestamp,Value\n' + 
    new Date().toISOString() + ',0\n' + 
    new Date(Date.now() - 3600000).toISOString() + ',0\n'
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${type}-data.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
</script>

<style>
.custom-table {
  background: transparent;
}

.custom-table .p-datatable-table {
  background: transparent;
}

.custom-table .p-datatable-thead > tr > th {
  background: #374151;
  color: #9ca3af;
  border: 1px solid #4b5563;
}

.custom-table .p-datatable-tbody > tr > td {
  background: transparent;
  color: #d1d5db;
  border: 1px solid #4b5563;
}

.custom-table .p-datatable-tbody > tr:hover {
  background: #374151;
}

.p-dropdown {
  background: #ea580c !important;
  border: 1px solid #ea580c !important;
}

.p-dropdown .p-dropdown-label {
  color: white !important;
}
</style>
