<template>
  <div class="min-h-screen text-white p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">Reports</h1>
      <p class="text-gray-400">Generate comprehensive energy consumption and performance reports</p>
    </div>

    <!-- Report Generator Card -->
    <div class="bg-transparent rounded-lg p-6 border border-gray-500 backdrop-blur-sm">
      <!-- Card Header -->
      <div class="flex items-center gap-2 mb-6">
        <i class="pi pi-file-text text-orange-500 text-lg"></i>
        <h2 class="text-xl font-semibold">Report Generator</h2>
      </div>

      <!-- Form Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        <!-- Time Range -->
        <div class="space-y-2">
          <label class="flex items-center gap-2 text-sm font-medium text-gray-300">
            <i class="pi pi-calendar text-white"></i>
            Time Range
          </label>
          <Dropdown
            v-model="selectedTimeRange"
            :options="timeRangeOptions"
            optionLabel="label"
            placeholder="Last 7 Days"
            class="w-full bg-transparent border-gray-600/50"
            panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
          />
        </div>

        <!-- Report Type -->
        <div class="space-y-2">
          <label class="flex items-center gap-2 text-sm font-medium text-gray-300">
            <i class="pi pi-filter text-white"></i>
            Report Type
          </label>
          <Dropdown
            v-model="selectedReportType"
            :options="reportTypeOptions"
            optionLabel="label"
            placeholder="Select a report..."
            class="w-full bg-transparent border-gray-600/50"
            panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
          />
          <p class="text-xs text-gray-400 mt-1">
            Select a report type to generate.</p>
        </div>

        <!-- From Date (Custom only) -->
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-300">From Date (Custom)</label>
          <Calendar
            v-model="fromDate"
            :disabled="selectedTimeRange?.value !== 'custom'"
            placeholder="mm/dd/yyyy"
            class="w-full"
            inputClass="bg-transparent border-gray-600/50 text-white placeholder-gray-400 disabled:opacity-50"
            panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
          />
        </div>

        <!-- To Date (Custom only) -->
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-300">To Date (Custom)</label>
          <Calendar
            v-model="toDate"
            :disabled="selectedTimeRange?.value !== 'custom'"
            placeholder="mm/dd/yyyy"
            class="w-full"
            inputClass="bg-transparent border-gray-600/50 text-white placeholder-gray-400 disabled:opacity-50"
            panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
          />
        </div>
      </div>

      <!-- Meters (Info only; we ignore selection for general reports) -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-2">
          <label class="flex items-center gap-2 text-sm font-medium text-gray-300">
            <i class="pi pi-bolt text-white"></i>
            Meters
          </label>
          <!-- <span class="text-xs text-amber-400">Ignored for this demo — reports are general to the site & period</span> -->
        </div>
        <MultiSelect
          v-model="selectedMeters"
          :options="availableMeters"
          optionLabel="name"
          placeholder="(Ignored) Select meters..."
          class="w-full bg-transparent border-gray-600/50 opacity-60"
          panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
          :disabled="true"
        >
          <template #value>
            <div class="flex items-center gap-2 text-orange-500">
              <i class="pi pi-bolt"></i>
              General site report
            </div>
          </template>
        </MultiSelect>
      </div>

      <!-- Bottom Actions -->
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-400">
          Choose a time range. From/To only apply when <span class="text-white font-medium">Custom</span> is selected.
        </p>

        <div class="flex gap-3">
          <Button
            label="Generate Report"
            icon="pi pi-file-text"
            class="bg-orange-600 hover:bg-orange-700 border-orange-600 text-white px-6 py-2"
            :disabled="!selectedReportType"
            @click="onGenerate"
          />
          <Button
            label="Export"
            icon="pi pi-download"
            class="p-button-outlined border-gray-600/50 text-gray-300 hover:bg-white/5 px-6 py-2"
            @click="onExport"
          />
        </div>
      </div>
    </div>

    <!-- ========= DYNAMIC REPORT RENDERING ========= -->
    <div v-if="showReport" class="max-w-[1600px] mx-auto border border-gray-500 p-6 mt-10 rounded-lg bg-transparent backdrop-blur-sm">
        <!-- Render the Consumption report -->
        <ConsumptionReport
          v-if="selectedReportType?.value === 'energy_consumption'"
          :selectedTimeRange="selectedTimeRange"
          :fromDate="selectedTimeRange?.value === 'custom' ? fromDate : null"
          :toDate="selectedTimeRange?.value === 'custom' ? toDate : null"
        />

        <!-- Render the Emissions report -->
        <EmissionsReport
          v-else-if="selectedReportType?.value === 'emissions'"
          :selectedTimeRange="selectedTimeRange"
          :fromDate="selectedTimeRange?.value === 'custom' ? fromDate : null"
          :toDate="selectedTimeRange?.value === 'custom' ? toDate : null"
        />

        <!-- Placeholder for future reports -->
        <div v-else class="mt-6 text-center text-gray-400">
            Report type '{{ selectedReportType?.label }}' is not yet implemented.
        </div>
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import { ref, watch } from 'vue'

import ConsumptionReport from '@/components/reports/ConsumptionReport.vue'
import EmissionsReport from '@/components/reports/EmissionsReport.vue'

const selectedTimeRange = ref({ label: 'Last 7 Days', value: '7d' })
const selectedReportType = ref({ label: 'Emissions Report', value: 'emissions' })
const fromDate = ref(null)
const toDate = ref(null)
const selectedMeters = ref([]) // ignored

const timeRangeOptions = [
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' },
  { label: 'Last 3 Months', value: '3m' },
  { label: 'Last 6 Months', value: '6m' },
  { label: 'Last Year', value: '1y' },
  { label: 'Custom Range', value: 'custom' }
]

const reportTypeOptions = [
  { label: 'Energy Consumption Report', value: 'energy_consumption' },
  { label: 'Emissions Report', value: 'emissions' },
  { label: 'Cost Analysis Report', value: 'cost_analysis' }
]

const availableMeters = [
  { name: 'Main Building Meter', id: 'meter_1', location: 'Building A' },
  { name: 'Production Line Meter', id: 'meter_2', location: 'Factory Floor' }
]

const showReport = ref(false)
watch(selectedReportType, () => { showReport.value = false })
function onGenerate() { showReport.value = true }
function onExport() { console.log(`Exporting ${selectedReportType.value.label} (placeholder)...`) }
</script>
