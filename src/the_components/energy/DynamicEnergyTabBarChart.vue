<template>
  <div class="min-h-screen text-white p-6">
    <!-- Header Section -->
    <div class="grid grid-cols-1 mb-6">
      <!-- Meter Selection -->
      <div class="border border-gray-600 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-speedometer2 text-orange-500 text-xl mr-3"></i>
            <h1 class="text-xl font-semibold">Meter Selection</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-green-500 text-sm">● 2</span>
            <span class="text-red-500 text-sm">● 0</span>
            <span class="text-yellow-500 text-sm">● 0</span>
            <Dropdown v-model="selectedMeter" :options="meters" optionLabel="name" 
                      class="bg-orange-600 border-orange-600">
              <template #value="slotProps">
                <span class="text-white">{{ slotProps.value ? slotProps.value.name : 'Main Distribution Panel' }}</span>
              </template>
            </Dropdown>
          </div>
        </div>

        <!-- Meter Info -->
        <div class="flex items-center justify-between bg-gray-800 bg-opacity-30 rounded p-4 border border-gray-700">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <div>
              <h3 class="font-medium">{{ meterInfo.name }}</h3>
              <p class="text-sm text-gray-400">{{ meterInfo.code }} • {{ meterInfo.location }} • {{ meterInfo.type }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-8">
            <div class="text-right">
              <div class="text-green-500 font-bold">ONLINE</div>
              <div class="text-xs text-gray-400">Status</div>
            </div>
            <div class="text-right">
              <div class="text-white font-bold">86.2%</div>
              <div class="text-xs text-gray-400">Current Load</div>
            </div>
            <div class="text-right">
              <div class="text-white font-bold">94%</div>
              <div class="text-xs text-gray-400">Efficiency</div>
            </div>
            <div class="text-right">
              <div class="text-white font-bold">Just now</div>
              <div class="text-xs text-gray-400">Last Reading</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards (Updated: 5 columns) -->
    <div class="grid grid-cols-5 gap-6 mb-6">
      <div class="border border-gray-600 rounded-lg p-6">
        <div class="text-gray-400 text-sm mb-2">CURRENT POWER</div>
        <div class="text-3xl font-bold text-red-500">21.7 <span class="text-lg text-gray-400">kW</span></div>
      </div>
      <div class="border border-gray-600 rounded-lg p-6">
        <div class="text-gray-400 text-sm mb-2">CURRENT REACTIVE POWER</div>
        <div class="text-3xl font-bold text-blue-500">14.2 <span class="text-lg text-gray-400">kVAR</span></div>
      </div>
      <div class="border border-gray-600 rounded-lg p-6">
        <div class="text-gray-400 text-sm mb-2">CURRENT POWER FACTOR</div>
        <div class="text-3xl font-bold text-green-500">0.92</div>
      </div>
      <div class="border border-gray-600 rounded-lg p-6">
        <div class="text-gray-400 text-sm mb-2">ENERGY TODAY</div>
        <div class="text-3xl font-bold text-orange-500">518 <span class="text-lg text-gray-400">kWh</span></div>
      </div>
      <div class="border border-gray-600 rounded-lg p-6">
        <div class="text-gray-400 text-sm mb-2">COST TODAY</div>
        <div class="text-3xl font-bold text-green-500">$62.16</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-12 gap-6 mb-6">
      <!-- Monthly Energy Chart (Now spans 8 columns) - WITH API INTEGRATION -->
      <div class="col-span-8 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-bar-chart text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Monthly Energy Consumption</h3>
            <p class="text-sm text-gray-400">Daily energy usage over the last 30 days</p>
          </div>
        </div>
        <div class="h-80">
          <div v-if="monthlyEnergyDataLoading" class="flex items-center justify-center h-full">
            <div class="text-gray-500">Loading...</div>
          </div>
          <v-chart 
            v-else 
            :option="monthlyEnergyChartOption" 
            class="w-full h-full"
          />
        </div>
      </div>

      <!-- Load Distribution (Remaining 4 columns) -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-pie-chart text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Load Distribution</h3>
            <p class="text-sm text-gray-400">Power distribution across phases</p>
          </div>
        </div>
        <div class="h-80">
          <v-chart :option="loadDistributionOption" class="w-full h-full"></v-chart>
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="grid grid-cols-12 gap-6">
      <!-- Power Fluctuation (Now spans 8 columns) - TEXT REMOVED -->
      <div class="col-span-8 border border-gray-600 rounded-lg p-6">
        <div class="flex items-baseline mb-4">
          <i class="bi bi-lightning text-orange-500 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold">Power Fluctuation This Week</h3>
            <p class="text-sm text-gray-400">Daily power peaks over the last 7 days</p>
          </div>
        </div>
        <!-- REMOVED: Date/time and peak text -->
        <div class="h-64"> <!-- Increased height to use freed space -->
          <div v-if="powerFluctuationDataLoading" class="flex items-center justify-center h-full">
            <div class="text-gray-500">Loading...</div>
          </div>
          <v-chart 
            v-else 
            :option="powerFluctuationOption" 
            class="w-full h-full"
          />
        </div>
      </div>

      <!-- Meter Alerts (Remaining 4 columns) -->
      <div class="col-span-4 border border-gray-600 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-baseline">
            <i class="bi bi-exclamation-triangle text-orange-500 text-xl mr-3"></i>
            <h3 class="font-semibold">Meter Alerts</h3>
          </div>
          <div class="flex items-center">
            <span class="bg-red-600 text-white px-2 py-1 rounded text-xs mr-2">1 Critical</span>
            <span class="text-gray-400 text-sm">{{ meterInfo.code }}</span>
          </div>
        </div>

        <div class="space-y-3 mb-4">
          <div class="flex items-center p-3 bg-green-900 bg-opacity-50 border border-green-600 rounded">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
            <div class="flex-1">
              <div class="text-sm font-medium text-green-400">Voltage within normal operating range</div>
              <div class="text-xs text-gray-400">Voltage L1: 220.5V</div>
            </div>
            <div class="text-xs text-gray-400">1 min ago</div>
          </div>

          <div class="flex items-center p-3 bg-red-900 bg-opacity-50 border border-red-600 rounded">
            <div class="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
            <div class="flex-1">
              <div class="text-sm font-medium text-red-400">Current imbalance detected between phases</div>
              <div class="text-xs text-gray-400">Phase Imbalance: 8.2%</div>
            </div>
            <div class="text-xs text-gray-400">12 min ago</div>
          </div>
        </div>

        <div class="flex justify-between text-sm">
          <div class="text-center">
            <div class="text-red-500 font-bold text-lg">1</div>
            <div class="text-gray-400">Critical</div>
          </div>
          <div class="text-center">
            <div class="text-yellow-500 font-bold text-lg">0</div>
            <div class="text-gray-400">Warning</div>
          </div>
          <div class="text-center">
            <div class="text-blue-500 font-bold text-lg">0</div>
            <div class="text-gray-400">Info</div>
          </div>
          <div class="text-center">
            <div class="text-green-500 font-bold text-lg">1</div>
            <div class="text-gray-400">Normal</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Meter Readings Table -->
    <div class="mt-6 border border-gray-600 rounded-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-baseline">
          <i class="bi bi-table text-orange-500 text-xl mr-3"></i>
          <h3 class="font-semibold">Live Meter Readings</h3>
        </div>
        <div class="text-sm text-gray-400">Updates every 5 seconds</div>
      </div>

      <DataTable :value="meterReadings" class="custom-table">
        <Column field="timestamp" header="Timestamp" class="text-gray-300"></Column>
        <Column field="vL1" header="V L1" class="text-gray-300"></Column>
        <Column field="vL2" header="V L2" class="text-gray-300"></Column>
        <Column field="vL3" header="V L3" class="text-gray-300"></Column>
        <Column field="aL1" header="A L1" class="text-gray-300"></Column>
        <Column field="aL2" header="A L2" class="text-gray-300"></Column>
        <Column field="aL3" header="A L3" class="text-gray-300"></Column>
        <Column field="kw" header="kW" class="text-gray-300"></Column>
        <Column field="pf" header="PF" class="text-gray-300"></Column>
        <Column field="hz" header="Hz" class="text-gray-300"></Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, reactive, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import Dropdown from 'primevue/dropdown'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// Inject required contexts (same as your example)
const ws = inject('ws')
const auth = inject('auth')
const dateRangeContext = inject('dateRange')
const resolutionContext = inject('resolution')
const refreshContext = inject('refresh')

// Route for accessing query parameters
const route = useRoute()

// Reactive data
const selectedMeter = ref({ name: 'Main Distribution Panel', code: 'MTR-001' })
const meters = ref([
  { name: 'Main Distribution Panel', code: 'MTR-001' },
  { name: 'Secondary Panel A', code: 'MTR-002' }
])

// Loading states for API data
const monthlyEnergyDataLoading = ref(false)
const powerFluctuationDataLoading = ref(false)

// Chart data storage
const monthlyEnergyData = ref({
  dates: [],
  activeEnergy: [],
  reactiveEnergy: []
})

const powerFluctuationData = ref({
  dates: [],
  peakPower: []
})

// Computed properties for date range and resolution (same as your example)
const fromDate = computed(() => {
  if (!dateRangeContext.value.value[0]) return null
  const date = new Date(dateRangeContext.value.value[0])
  return date.toISOString().split('T')[0] // Format as YYYY-MM-DD
})

const toDate = computed(() => {
  if (!dateRangeContext.value.value[1]) return null
  const date = new Date(dateRangeContext.value.value[1])
  return date.toISOString().split('T')[0] // Format as YYYY-MM-DD
})

const resolution = computed(() => resolutionContext.value.value)

// Computed property to handle meter info from route or default
const meterInfo = computed(() => {
  const meterId = route.query.meterId
  const meterName = route.query.meterName
  
  if (meterId && meterName) {
    // Update selected meter based on route parameters
    const meterOption = { name: meterName, code: meterId.toUpperCase() }
    selectedMeter.value = meterOption
    
    // Return meter info based on route parameters
    return {
      name: meterName,
      code: meterId.toUpperCase(),
      location: 'Building A - Ground Floor',
      type: '3-Phase Digital'
    }
  }
  
  // Default fallback
  return {
    name: 'Main Distribution Panel',
    code: 'MTR-001',
    location: 'Building A - Ground Floor',
    type: '3-Phase Digital'
  }
})

const meterReadings = ref([
  { timestamp: '1:14:02 PM', vL1: '220.5', vL2: '224.7', vL3: '218.6', aL1: '99.3', aL2: '111.9', aL3: '99.7', kw: '21.8', pf: '0.92', hz: '50.0' },
  { timestamp: '1:13:56 PM', vL1: '220.5', vL2: '224.7', vL3: '218.6', aL1: '99.7', aL2: '115.8', aL3: '100.6', kw: '21.5', pf: '0.92', hz: '50.0' },
  { timestamp: '1:13:51 PM', vL1: '220.5', vL2: '224.7', vL3: '218.6', aL1: '96.1', aL2: '114.9', aL3: '100.4', kw: '21.1', pf: '0.92', hz: '50.0' },
  { timestamp: '1:13:45 PM', vL1: '220.5', vL2: '224.7', vL3: '218.6', aL1: '97.1', aL2: '112.0', aL3: '101.0', kw: '21.7', pf: '0.92', hz: '50.0' },
  { timestamp: '1:13:40 PM', vL1: '220.5', vL2: '224.7', vL3: '218.6', aL1: '97.7', aL2: '115.9', aL3: '97.8', kw: '21.6', pf: '0.92', hz: '50.0' }
])

// Wait for WebSocket to be open
function waitForSocketOpen(ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// Fetch monthly energy data (daily consumption)
async function fetchMonthlyEnergyData() {
  if (!fromDate.value || !toDate.value || !auth.ready) return
  
  monthlyEnergyDataLoading.value = true
  
  try {
    await waitForSocketOpen(ws)
    
    const OUTER = crypto.randomUUID()
    const INNER = crypto.randomUUID()
    
    // Send request for energy data
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER,
      method: 'edgeRpc',
      params: {
        edgeId: 'edge0', // Using edge0 as requested
        payload: {
          jsonrpc: '2.0',
          id: INNER,
          method: 'queryHistoricTimeseriesEnergyPerPeriod',
          params: {
            channels: [
              'meter0/ActiveEnergy',
              'meter0/ReactiveEnergy'
            ],
            fromDate: fromDate.value,
            toDate: toDate.value,
            resolution: {
              value: resolution.value.value,
              unit: resolution.value.unit
            },
            timezone: 'Africa/Casablanca'
          }
        }
      }
    }))
    
    // Handle response
    const handleMessage = ({ data }) => {
      const msg = JSON.parse(data)
      if (msg.id === OUTER && msg.result) {
        const result = msg.result.payload?.result ?? msg.result
        
        if (result && result.timestamps && result.channels) {
          // Process the data
          const timestamps = result.timestamps.map(ts => {
            const date = new Date(ts)
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
          })
          
          const activeEnergy = result.channels[0]?.values || []
          const reactiveEnergy = result.channels[1]?.values || []
          
          monthlyEnergyData.value = {
            dates: timestamps,
            activeEnergy: activeEnergy,
            reactiveEnergy: reactiveEnergy
          }
          
          // Update chart option with real data
          updateMonthlyEnergyChartOption()
        }
        
        monthlyEnergyDataLoading.value = false
        ws.removeEventListener('message', handleMessage)
      }
    }
    
    ws.addEventListener('message', handleMessage)
    
  } catch (error) {
    console.error('Error fetching monthly energy data:', error)
    monthlyEnergyDataLoading.value = false
  }
}

// Fetch power fluctuation data (daily peaks)
async function fetchPowerFluctuationData() {
  if (!fromDate.value || !toDate.value || !auth.ready) return
  
  powerFluctuationDataLoading.value = true
  
  try {
    await waitForSocketOpen(ws)
    
    const OUTER = crypto.randomUUID()
    const INNER = crypto.randomUUID()
    
    // Send request for power data
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER,
      method: 'edgeRpc',
      params: {
        edgeId: 'edge0', // Using edge0 as requested
        payload: {
          jsonrpc: '2.0',
          id: INNER,
          method: 'queryHistoricTimeseriesData',
          params: {
            channels: [
              'meter0/ActivePower'
            ],
            fromDate: fromDate.value,
            toDate: toDate.value,
            resolution: {
              value: resolution.value.value,
              unit: resolution.value.unit
            },
            timezone: 'Africa/Casablanca'
          }
        }
      }
    }))
    
    // Handle response
    const handleMessage = ({ data }) => {
      const msg = JSON.parse(data)
      if (msg.id === OUTER && msg.result) {
        const result = msg.result.payload?.result ?? msg.result
        
        if (result && result.timestamps && result.channels) {
          // Process the data to get daily peaks
          const timestamps = result.timestamps.map(ts => {
            const date = new Date(ts)
            return date.toLocaleDateString('en-US', { weekday: 'short' })
          })
          
          // Get max power value for each day (simplified)
          const powerValues = result.channels[0]?.values || []
          
          powerFluctuationData.value = {
            dates: timestamps,
            peakPower: powerValues
          }
          
          // Update chart option with real data
          updatePowerFluctuationChartOption()
        }
        
        powerFluctuationDataLoading.value = false
        ws.removeEventListener('message', handleMessage)
      }
    }
    
    ws.addEventListener('message', handleMessage)
    
  } catch (error) {
    console.error('Error fetching power fluctuation data:', error)
    powerFluctuationDataLoading.value = false
  }
}

// Chart configurations
const monthlyEnergyChartOption = ref({
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: [], // Will be populated with real data
    axisLabel: {
      color: '#9ca3af',
      fontSize: 10
    },
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      show: false // Hide Y-axis labels
    },
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    },
    splitLine: {
      lineStyle: {
        type: 'dotted',
        color: '#4b5563',
        opacity: 0.3
      }
    }
  },
  series: [
    {
      name: 'Active Energy',
      type: 'bar',
      stack: 'energy',
      data: [], // Will be populated with real data
      itemStyle: {
        color: '#f97316'
      }
    },
    {
      name: 'Reactive Energy',
      type: 'bar',
      stack: 'energy',
      data: [], // Will be populated with real data
      itemStyle: {
        color: '#06b6d4'
      }
    }
  ],
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#374151',
    borderColor: '#6b7280',
    textStyle: {
      color: '#ffffff'
    }
  },
  legend: {
    show: true,
    bottom: 0,
    data: ['Active Energy', 'Reactive Energy'],
    textStyle: {
      color: '#ffffff',
      fontSize: 10
    },
    icon: 'roundRect',
    itemWidth: 12,
    itemHeight: 8
  }
})

const loadDistributionOption = ref({
  tooltip: {
    trigger: 'item',
    backgroundColor: '#374151',
    borderColor: '#6b7280',
    textStyle: {
      color: '#ffffff'
    }
  },
  series: [
    {
      type: 'pie',
      radius: ['50%', '70%'],
      center: ['50%', '50%'],
      data: [
        { value: 35, name: 'Phase 1', itemStyle: { color: '#f97316' } },
        { value: 32, name: 'Phase 2', itemStyle: { color: '#06b6d4' } },
        { value: 33, name: 'Phase 3', itemStyle: { color: '#10b981' } }
      ],
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}: {c}%',
        fontSize: 13,
        color: '#ffffff',
        padding: [2, 4],
        borderRadius: 3,
        shadowBlur: 2,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      },
      labelLine: {
        show: true,
        length: 10,
        length2: 15,
        lineStyle: {
          color: '#ffffff',
          opacity: 0.8
        }
      },
      clockwise: true,
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 5,
        borderWidth: 1,
        borderColor: '#1f2937'
      },
      padAngle: 2,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
})

const powerFluctuationOption = ref({
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: [], // Will be populated with real data
    axisLabel: {
      color: '#9ca3af',
      fontSize: 10
    },
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    },
    splitLine: {
      show: false
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      show: false // Hide Y-axis labels
    },
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    },
    splitLine: {
      lineStyle: {
        type: 'dotted',
        color: '#4b5563',
        opacity: 0.2
      }
    }
  },
  series: [
    {
      type: 'line',
      data: [], // Will be populated with real data
      itemStyle: {
        color: '#6b7280'
      },
      lineStyle: {
        color: '#6b7280',
        width: 2,
        opacity: 0.8
      },
      symbol: 'circle',
      symbolSize: 6,
      smooth: true,
      areaStyle: {
        color: '#6b7280',
        opacity: 0.1
      }
    }
  ],
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#374151',
    borderColor: '#6b7280',
    textStyle: {
      color: '#ffffff'
    }
  }
})

// Update chart options with real data
function updateMonthlyEnergyChartOption() {
  monthlyEnergyChartOption.value.xAxis.data = monthlyEnergyData.value.dates
  monthlyEnergyChartOption.value.series[0].data = monthlyEnergyData.value.activeEnergy
  monthlyEnergyChartOption.value.series[1].data = monthlyEnergyData.value.reactiveEnergy
}

function updatePowerFluctuationChartOption() {
  powerFluctuationOption.value.xAxis.data = powerFluctuationData.value.dates
  powerFluctuationOption.value.series[0].data = powerFluctuationData.value.peakPower
}

// Watch for changes in date range, resolution, and refresh
watch(
  () => [fromDate.value, toDate.value, resolution.value, refreshContext?.count], 
  () => { 
    if (auth.ready) {
      fetchMonthlyEnergyData()
      fetchPowerFluctuationData()
    }
  },
  { deep: true }
)

watch(
  () => auth.ready,
  r => { 
    if (r) {
      fetchMonthlyEnergyData()
      fetchPowerFluctuationData()
    }
  },
  { immediate: true }
)

// Initial data fetch
onMounted(() => {
  if (auth.ready) {
    fetchMonthlyEnergyData()
    fetchPowerFluctuationData()
  }
})
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

/* Dropdown custom styling */
.p-dropdown {
  background: #ea580c !important;
  border: 1px solid #ea580c !important;
}

.p-dropdown .p-dropdown-label {
  color: white !important;
}
</style>