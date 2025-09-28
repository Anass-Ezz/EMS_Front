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
        <div class="flex items-baseline mb-4">
          <i class="bi bi-bar-chart text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Gas Consumption History</h3>
            <p class="text-sm text-gray-400">Gas consumption in kilograms over time</p>
          </div>
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

    <!-- Bottom Row -->
    <div class="grid grid-cols-12 gap-6">
      <!-- Gas Metrics History -->
      <div class="col-span-8 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-graph-up text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Gas Metrics Over Time</h3>
            <p class="text-sm text-gray-400">Flow rate, temperature and pressure trends</p>
          </div>
        </div>
        <div class="h-64">
          <GasMetricsHistory 
            :edge-id="'edge0'"
            :channels="[`${channelPrefix}FlowRate`, `${channelPrefix}Temperature`, `${channelPrefix}Pressure`]"
            :chart-type="'metrics'"
          />
        </div>
      </div>

      <!-- Gas Meter Alerts -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
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
import GasMeterAlerts from '@/components/gas/GasMeterAlerts.vue'
import GasMeterReadingsTable from '@/components/gas/GasMeterReadingsTable.vue'
import GasMeterSelector from '@/components/gas/GasMeterSelector.vue'
import GasMetricsHistory from '@/components/gas/GasMetricsHistory.vue'
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
    // Handle cases like "120.5 kg/s" or "2.5 bar"
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
