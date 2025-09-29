<template>
  <div class="min-h-screen text-white p-6">
    <!-- Meter Selection -->
    <MeterSelector />

    <!-- Stats Cards Row -->
    <div class="mb-6">
      <RealTimeMeterData />
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-12 gap-6 mb-6">
      <!-- Monthly Energy Chart -->
      <div class="col-span-8 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-bar-chart text-orange-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Energy Consumption</h3>
              <p class="text-sm text-gray-400">Detailed energy Wh and VAR usage over periods</p>
            </div>
          </div>
          <button 
            @click="downloadCSV('energy-consumption')"
            class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
          >
            <i class="bi bi-download text-xs"></i>
            Save CSV
          </button>
        </div>
        <div class="h-80">
          <EnergyConsumptionHistory 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}ActiveEnergy`, `${channelPrefix}ReactiveEnergy`]"
            :chart-type="'energy'"
          />
        </div>
      </div>

      <!-- Load Distribution -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline">
          <i class="bi bi-pie-chart text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Load Distribution</h3>
          </div>
        </div>
        <div class="h-80 ">
          <!-- <LoadDistributionPie /> -->
          <!-- ✅ DYNAMIC PHASOR DIAGRAM -->
          <PhasorDiagram
            v-if="latestReading"
            :vMag="[latestReading.vL1, latestReading.vL2, latestReading.vL3].map(safeNumber)"
            :iMag="[latestReading.aL1, latestReading.aL2, latestReading.aL3].map(safeNumber)"
            :pf="[latestReading.pf, latestReading.pf, latestReading.pf].map(safeNumber)"
            :pfSign="['lag','lag','lag']"
            :voltageIsLineToLine="false"
          />
          <!-- Show placeholder if no data -->
          <div v-else class="flex items-center justify-center h-full text-gray-500">
            Loading phasor data...
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="grid grid-cols-12 gap-6">
      <!-- Power Fluctuation -->
      <div class="col-span-8 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-lightning text-orange-500 text-xl mr-3"></i>
            <div>
              <h3 class="font-semibold">Power Fluctuation Over Time</h3>
              <p class="text-sm text-gray-400">Detailed power kW demand over time</p>
            </div>
          </div>
          <button 
            @click="downloadCSV('power-fluctuation')"
            class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
          >
            <i class="bi bi-download text-xs"></i>
            Save CSV
          </button>
        </div>
        <div class="h-64">
          <EnergyConsumptionHistory 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}ActivePower`]"
            :chart-type="'power'"
          />
        </div>
      </div>

      <!-- Meter Alerts -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <MeterAlerts :meter-id="route.query.meterId" />
      </div>
    </div>

    <!-- ✅ Live Meter Readings Table - Extracted -->
    <div class="mt-6">
      <MeterReadingsTable @update:latestReading="latestReading = $event" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import EnergyConsumptionHistory from '@/components/meters/MeterEnergyHistroy.vue'
import RealTimeMeterData from '@/components/meters/RealTimeMeterData.vue'
import LoadDistributionPie from '@/components/meters/LoadDistributionPie.vue'
import MeterAlerts from '@/components/meters/MeterAlerts.vue'
import MeterSelector from '@/components/meters/MeterSelector.vue'
// ✅ Import new component
import MeterReadingsTable from '@/components/meters/MeterReadingsTable.vue'
import PhasorDiagram from '@/components/charts/PhasorChart.vue'

use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const route = useRoute()

// ✅ Hold latest meter reading
const latestReading = ref(null)

// ✅ Helper to safely convert string to number, fallback to 0
const safeNumber = (val) => {
  if (typeof val === 'string' && val.includes(' ')) {
    // Handle cases like "120.5 A" or "2.5 kW"
    val = val.split(' ')[0]
  }
  const num = Number(val)
  return isNaN(num) ? 0 : num
}

// ✅ Meter ID → Index Map (copied from RealTimeMeterData.vue)
const meterIdToIndex = {
  'sm-a-0': 0,
  'sm-a-1': 1,
  'sm-a-2': 2,
  'sm-a-3': 3,
  'sm-a-4': 4,
  'sm-a-5': 5,
  'sm-b-0': 6,
  'sm-b-1': 7,
  'sm-b-2': 8,
  'sm-b-3': 9,
  'sm-b-4': 10
}

// ✅ Compute meter index based on route query
const meterIndex = computed(() => {
  const id = route.query.meterId
  return meterIdToIndex[id] !== undefined ? meterIdToIndex[id] : 0
})

// ✅ Compute channel prefix dynamically
const channelPrefix = computed(() => `meter${meterIndex.value}/`)

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