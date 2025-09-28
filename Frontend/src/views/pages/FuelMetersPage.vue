<template>
  <div class="min-h-screen text-white p-6">
    <!-- Fuel Meter Selection -->
    <FuelMeterSelector />

    <!-- Stats Cards Row -->
    <div class="mb-6">
      <RealTimeFuelMeterData />
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-12 gap-6 mb-6">
      <!-- Fuel Consumption History Chart -->
      <div class="col-span-8 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-bar-chart text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Fuel Consumption History</h3>
            <p class="text-sm text-gray-400">Fuel consumption in liters over time</p>
          </div>
        </div>
        <div class="h-80">
          <FuelConsumptionHistory 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}Consumption`]"
            :chart-type="'fuel'"
          />
        </div>
      </div>

      <!-- Fuel Average Values -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-calculator text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Average Values</h3>
          </div>
        </div>
        <div class="h-80">
          <FuelAverageValues />
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="grid grid-cols-12 gap-6">
      <!-- Fuel Metrics History -->
      <div class="col-span-8 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-graph-up text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Fuel Metrics Over Time</h3>
            <p class="text-sm text-gray-400">Flow rate, temperature and pressure trends</p>
          </div>
        </div>
        <div class="h-64">
          <FuelMetricsHistory 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}FlowRate`, `${channelPrefix}Temperature`, `${channelPrefix}Pressure`]"
            :chart-type="'metrics'"
          />
        </div>
      </div>

      <!-- Fuel Meter Alerts -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <FuelMeterAlerts :meter-id="route.query.meterId" />
      </div>
    </div>

    <!-- Live Fuel Meter Readings Table -->
    <div class="mt-6">
      <FuelMeterReadingsTable @update:latestReading="latestReading = $event" />
    </div>
  </div>
</template>

<script setup>
import FuelAverageValues from '@/components/fuel/FuelAverageValues.vue'
import FuelConsumptionHistory from '@/components/fuel/FuelConsumptionHistory.vue'
import FuelMeterAlerts from '@/components/fuel/FuelMeterAlerts.vue'
import FuelMeterReadingsTable from '@/components/fuel/FuelMeterReadingsTable.vue'
import FuelMeterSelector from '@/components/fuel/FuelMeterSelector.vue'
import FuelMetricsHistory from '@/components/fuel/FuelMetricsHistory.vue'
import RealTimeFuelMeterData from '@/components/fuel/RealTimeFuelMeterData.vue'
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

// Hold latest fuel meter reading
const latestReading = ref(null)

// Helper to safely convert string to number, fallback to 0
const safeNumber = (val) => {
  if (typeof val === 'string' && val.includes(' ')) {
    // Handle cases like "8.5 L/s" or "4.2 bar"
    val = val.split(' ')[0]
  }
  const num = Number(val)
  return isNaN(num) ? 0 : num
}

// Fuel Meter ID → Index Map (only one fuel meter)
const fuelMeterIdToIndex = {
  'fm-0': 0
}

// Compute fuel meter index based on route query
const meterIndex = computed(() => {
  const id = route.query.meterId
  return fuelMeterIdToIndex[id] !== undefined ? fuelMeterIdToIndex[id] : 0
})

// Compute channel prefix dynamically
const channelPrefix = computed(() => `fuelmeter${meterIndex.value}/`)
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
