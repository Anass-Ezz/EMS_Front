<template>
    <div class="min-h-screen text-white p-6">
      <!-- Header Section -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white mb-2">Reports</h1>
        <p class="text-gray-400">Generate comprehensive energy consumption and performance reports</p>
      </div>
  
      <!-- Report Generator Card -->
      <div class="bg-transparent rounded-lg p-6 border border-gray-500 backdrop-blur-sm">
        <!-- Card Header -->
        <div class="flex items-center gap-2 mb-6">
          <i class="pi pi-file-text text-orange-500 text-lg"></i>
          <h2 class="text-xl font-semibold text-white">Report Generator</h2>
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
              placeholder="Energy Consumption..."
              class="w-full bg-transparent border-gray-600/50"
              panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
            />
          </div>
  
          <!-- From Date -->
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-300">From Date (Optional)</label>
            <Calendar 
              v-model="fromDate" 
              placeholder="mm/dd/yyyy"
              class="w-full"
              inputClass="bg-transparent border-gray-600/50 text-white placeholder-gray-400"
              panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
            />
          </div>
  
          <!-- To Date -->
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-300">To Date (Optional)</label>
            <Calendar 
              v-model="toDate" 
              placeholder="mm/dd/yyyy"
              class="w-full"
              inputClass="bg-transparent border-gray-600/50 text-white placeholder-gray-400"
              panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
            />
          </div>
        </div>
  
        <!-- Select Meters Section -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-4">
            <label class="flex items-center gap-2 text-sm font-medium text-gray-300">
              <i class="pi pi-bolt text-white"></i>
              Select Meters (2 available)
            </label>
            <Button 
              label="Select All" 
              class="p-button-text p-button-sm text-orange-500 hover:text-orange-400"
              @click="selectAllMeters"
            />
          </div>
          
          <MultiSelect 
            v-model="selectedMeters" 
            :options="availableMeters" 
            optionLabel="name"
            placeholder="Select meters..."
            class="w-full bg-transparent border-gray-600/50"
            panelClass="bg-gray-800/95 border-gray-600/50 backdrop-blur-md"
          >
            <template #value="slotProps">
              <div v-if="!slotProps.value || slotProps.value.length === 0" class="flex items-center gap-2 text-orange-500">
                <i class="pi pi-bolt"></i>
                Select meters...
              </div>
              <div v-else class="flex items-center gap-2">
                <i class="pi pi-bolt text-orange-500"></i>
                <span>{{ slotProps.value.length }} meter(s) selected</span>
              </div>
            </template>
          </MultiSelect>
        </div>
  
        <!-- Bottom Section -->
        <div class="flex items-center justify-between">
          <p class="text-sm text-gray-400">Select at least one meter to generate report</p>
          
          <div class="flex gap-3">
            <Button 
              label="Generate Report" 
              icon="pi pi-file-text"
              class="bg-orange-600 hover:bg-orange-700 border-orange-600 text-white px-6 py-2"
              :disabled="!selectedMeters || selectedMeters.length === 0"
              @click="generateReport"
            />
            <Button 
              label="Export" 
              icon="pi pi-download"
              class="p-button-outlined border-gray-600/50 text-gray-300 hover:bg-white/5 px-6 py-2"
              @click="exportReport"
            />
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import Dropdown from 'primevue/dropdown'
  import Calendar from 'primevue/calendar'
  import MultiSelect from 'primevue/multiselect'
  import Button from 'primevue/button'
  
  // Reactive data
  const selectedTimeRange = ref(null)
  const selectedReportType = ref(null)
  const fromDate = ref(null)
  const toDate = ref(null)
  const selectedMeters = ref([])
  
  // Options
  const timeRangeOptions = ref([
    { label: 'Last 7 Days', value: '7d' },
    { label: 'Last 30 Days', value: '30d' },
    { label: 'Last 3 Months', value: '3m' },
    { label: 'Last 6 Months', value: '6m' },
    { label: 'Last Year', value: '1y' },
    { label: 'Custom Range', value: 'custom' }
  ])
  
  const reportTypeOptions = ref([
    { label: 'Energy Consumption Report', value: 'energy_consumption' },
    { label: 'Performance Report', value: 'performance' },
    { label: 'Cost Analysis Report', value: 'cost_analysis' },
    { label: 'Peak Demand Report', value: 'peak_demand' },
    { label: 'Efficiency Report', value: 'efficiency' }
  ])
  
  const availableMeters = ref([
    { name: 'Main Building Meter', id: 'meter_1', location: 'Building A' },
    { name: 'Production Line Meter', id: 'meter_2', location: 'Factory Floor' }
  ])
  
  // Methods
  const selectAllMeters = () => {
    selectedMeters.value = [...availableMeters.value]
  }
  
  const generateReport = () => {
    console.log('Generating report with:', {
      timeRange: selectedTimeRange.value,
      reportType: selectedReportType.value,
      fromDate: fromDate.value,
      toDate: toDate.value,
      meters: selectedMeters.value
    })
    // Add your report generation logic here
  }
  
  const exportReport = () => {
    console.log('Exporting report...')
    // Add your export logic here
  }
  </script>
  
  <style scoped>
  /* Custom styles for PrimeVue components to match transparent theme */
  :deep(.p-dropdown) {
    background-color: transparent;
    border-color: rgb(75, 85, 99, 0.5);
    color: white;
  }
  
  :deep(.p-dropdown:not(.p-disabled):hover) {
    border-color: rgb(107, 114, 128, 0.7);
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  :deep(.p-dropdown:not(.p-disabled).p-focus) {
    border-color: rgb(249, 115, 22);
    box-shadow: 0 0 0 1px rgb(249, 115, 22, 0.5);
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  :deep(.p-dropdown-panel) {
    background-color: rgba(31, 41, 55, 0.95);
    border-color: rgb(75, 85, 99, 0.5);
    backdrop-filter: blur(12px);
  }
  
  :deep(.p-dropdown-item) {
    color: white;
  }
  
  :deep(.p-dropdown-item:not(.p-highlight):not(.p-disabled):hover) {
    background-color: rgba(75, 85, 99, 0.5);
  }
  
  :deep(.p-inputtext) {
    background-color: transparent;
    border-color: rgb(75, 85, 99, 0.5);
    color: white;
  }
  
  :deep(.p-inputtext:enabled:hover) {
    border-color: rgb(107, 114, 128, 0.7);
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  :deep(.p-inputtext:enabled:focus) {
    border-color: rgb(249, 115, 22);
    box-shadow: 0 0 0 1px rgb(249, 115, 22, 0.5);
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  :deep(.p-calendar-panel) {
    background-color: rgba(31, 41, 55, 0.95);
    border-color: rgb(75, 85, 99, 0.5);
    backdrop-filter: blur(12px);
  }
  
  :deep(.p-datepicker-header) {
    background-color: transparent;
    border-color: rgb(75, 85, 99, 0.5);
    color: white;
  }
  
  :deep(.p-datepicker-calendar td span) {
    color: white;
  }
  
  :deep(.p-datepicker-calendar td span:hover) {
    background-color: rgba(249, 115, 22, 0.2);
  }
  
  :deep(.p-multiselect) {
    background-color: transparent;
    border-color: rgb(75, 85, 99, 0.5);
    color: white;
  }
  
  :deep(.p-multiselect:not(.p-disabled):hover) {
    border-color: rgb(107, 114, 128, 0.7);
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  :deep(.p-multiselect:not(.p-disabled).p-focus) {
    border-color: rgb(249, 115, 22);
    box-shadow: 0 0 0 1px rgb(249, 115, 22, 0.5);
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  :deep(.p-multiselect-panel) {
    background-color: rgba(31, 41, 55, 0.95);
    border-color: rgb(75, 85, 99, 0.5);
    backdrop-filter: blur(12px);
  }
  
  :deep(.p-multiselect-item) {
    color: white;
  }
  
  :deep(.p-multiselect-item:not(.p-highlight):not(.p-disabled):hover) {
    background-color: rgba(75, 85, 99, 0.5);
  }
  
  :deep(.p-button.p-button-outlined) {
    border-color: rgb(75, 85, 99, 0.5);
    color: rgb(209, 213, 219);
    background-color: transparent;
  }
  
  :deep(.p-button.p-button-outlined:enabled:hover) {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgb(107, 114, 128, 0.7);
  }
  </style>