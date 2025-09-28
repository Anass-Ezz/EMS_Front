<template>
  <p class="text-xl font-bold mb-4 flex flex-row gap-5 items-center">Weather Forecast 
    <span class="rounded-3xl bg-cyan-900 px-2 py-1 flex flex-row items-center gap-3">
      
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-geo-alt-fill" viewBox="0 0 16 16">
        <path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10m0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6"/>
      </svg>
      <span class="text-lg">32.2359° N, 7.9538° W </span>
    </span>
  </p>
  <div class="grid grid-cols-12 gap-3">
    
    <div class="col-span-3">

      <div class="card h-full text-center">

        <div class="text-xl text-gray-400 font-bold">Temperature</div>

        <div class="text-2xl font-bold">{{ currentValues.temperature }}°C</div>
        

        <div class="flex justify-center space-x-4 mt-2 items-center">
          
          <button @click="prevDay('temperature')" class="">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-left-circle" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-4.5-.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5z"/>
            </svg>
          </button>

          <span>{{ getDateLabel(tempDay) }}</span>

          <button @click="nextDay('temperature')" class="">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-right-circle" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0M4.5 7.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5z"/>
            </svg>
          </button>

        </div>
        

        <EnvironmentMetricsBarChart 
          metricName="Temperature"
          :chartData="tempData"
          :labels="tempTimeLabels"
          backgroundColor="rgba(255, 99, 132, 0.7)"
        />
      </div>
    </div>

    <div class="col-span-3">
      <div class="card h-full text-center">
        <div class="text-xl text-gray-400 font-bold">Humidity</div>
        <div class="text-2xl font-bold">{{ currentValues.humidity }}%</div>
        <div class="flex justify-center space-x-4 mt-2 items-center">
          <button @click="prevDay('humidity')">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-left-circle" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-4.5-.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5z"/>
            </svg>
          </button>
          <span>{{ getDateLabel(humidityDay) }}</span>
          <button @click="nextDay('humidity')">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-right-circle" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0M4.5 7.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5z"/>
            </svg>
          </button>
        </div>
        <EnvironmentMetricsBarChart 
          metricName="Humidity"
          :chartData="humidityData"
          :labels="humidityTimeLabels"
          backgroundColor="rgba(54, 162, 235, 0.7)"
        />
      </div>
    </div>

    <div class="col-span-3">
      <div class="card h-full text-center">
        <div class="text-xl text-gray-400 font-bold">Irradiance (GHI)</div>
        <div class="text-2xl font-bold">{{ currentValues.irradiance }} W/m²</div>
        <div class="flex justify-center space-x-4 mt-2 items-center">
          <button @click="prevDay('irradiance')">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-left-circle" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-4.5-.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5z"/>
            </svg>
          </button>
          <span>{{ getDateLabel(irradianceDay) }}</span>
          <button @click="nextDay('irradiance')">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-right-circle" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0M4.5 7.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5z"/>
            </svg>
          </button>
        </div>
        <EnvironmentMetricsBarChart 
          metricName="Irradiance"
          :chartData="irradianceData"
          :labels="irradianceTimeLabels"
          backgroundColor="rgba(255, 206, 86, 0.7)"
        />
      </div>
    </div>

    <div class="col-span-3">
      <div class="card h-full text-center">
        <div class="text-xl text-gray-400 font-bold">Windspeed (10m)</div>
        <div class="text-2xl font-bold">{{ currentValues.windspeed }} km/h</div>
        <div class="flex justify-center space-x-4 mt-2 items-center">
          <button @click="prevDay('windspeed')">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-left-circle" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-4.5-.5a.5.5 0 0 1 0 1H5.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L5.707 7.5z"/>
            </svg>
          </button>
          <span>{{ getDateLabel(windspeedDay) }}</span>
          <button @click="nextDay('windspeed')">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-right-circle" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0M4.5 7.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5z"/>
            </svg>
          </button>
        </div>
        <EnvironmentMetricsBarChart 
          metricName="Windspeed"
          :chartData="windspeedData"
          :labels="windspeedTimeLabels"
          backgroundColor="rgba(75, 192, 192, 0.7)"
        />
      </div>
    </div>

  </div>

</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useToast } from 'primevue/usetoast'
import EnvironmentMetricsBarChart from '@/the_components/charts/EnvironmentMetricsBarChart.vue'

/* ──────────────────────────
   Navigation state
───────────────────────────*/
const tempDay       = ref(0)
const humidityDay   = ref(0)
const irradianceDay = ref(0)
const windspeedDay  = ref(0)

/* ──────────────────────────
   Reactive data
───────────────────────────*/
const currentValues = ref({
  temperature : 24,
  humidity    : 65,
  irradiance  : 850,
  windspeed   : 12
})

const forecastData = ref({
  temperature : [],
  humidity    : [],
  irradiance  : [],
  windspeed   : [],
  time        : []
})

const toast = useToast()

/* ──────────────────────────
   Connection tracking
───────────────────────────*/
const weatherOnline = ref(true)

/* ──────────────────────────
   Computed helpers
───────────────────────────*/
const tempData       = computed(() =>   getDayData(forecastData.value.temperature,  tempDay.value)       ?? Array(6).fill(0))
const humidityData   = computed(() =>   getDayData(forecastData.value.humidity,    humidityDay.value)   ?? Array(6).fill(0))
const irradianceData = computed(() =>   getDayData(forecastData.value.irradiance,  irradianceDay.value) ?? Array(6).fill(0))
const windspeedData  = computed(() =>   getDayData(forecastData.value.windspeed,   windspeedDay.value)  ?? Array(6).fill(0))

const tempTimeLabels       = computed(() => getTimeLabels(tempDay.value))
const humidityTimeLabels   = computed(() => getTimeLabels(humidityDay.value))
const irradianceTimeLabels = computed(() => getTimeLabels(irradianceDay.value))
const windspeedTimeLabels  = computed(() => getTimeLabels(windspeedDay.value))

/* ──────────────────────────
   Generic helpers
───────────────────────────*/
function getDayData(data, day) {
  if (!data?.length) return null
  const start = day * 24
  return data.slice(start, start + 24)
}

function getDateLabel(dayIdx) {
  const hrs = forecastData.value.time
  if (!hrs?.length) {
    const d = new Date()
    d.setDate(d.getDate() + dayIdx)
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }
  const i = dayIdx * 24
  return i < hrs.length
    ? new Date(hrs[i]).toLocaleDateString([], { month: 'short', day: 'numeric' })
    : 'N/A'
}

function getTimeLabels(dayIdx) {
  const hrs = forecastData.value.time
  if (!hrs?.length) return ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
  const slice = getDayData(hrs, dayIdx)
  return slice
    ? slice.map(t => new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
    : ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
}

/* ──────────────────────────
   API calls
───────────────────────────*/
/* 1️⃣ 7-day / hourly forecast → charts */
async function fetchForecastData() {
  try {
    const url = new URL('https://api.open-meteo.com/v1/forecast')
    const params = {
      latitude      : 33.5731,
      longitude     : -7.5898,
      hourly        : 'temperature_2m,relative_humidity_2m,windspeed_10m,shortwave_radiation',
      timezone      : 'auto',
      forecast_days : 7,
      windspeed_unit: 'kmh'
    }
    Object.entries(params).forEach(([k, v]) => url.searchParams.append(k, v))
    const res  = await fetch(url)
    const data = await res.json()

    if (!weatherOnline.value) {
      weatherOnline.value = true
      toast.add({
        severity: 'success',
        summary: 'Weather API Reconnected',
        detail: 'Forecast data is available again.',
        life: 3000
      })
    }

    forecastData.value = {
      temperature : data.hourly.temperature_2m,
      humidity    : data.hourly.relative_humidity_2m,
      windspeed   : data.hourly.windspeed_10m,
      irradiance  : data.hourly.shortwave_radiation,
      time        : data.hourly.time
    }
  } catch (e) {
    if (weatherOnline.value) {
      weatherOnline.value = false
      toast.add({
        severity: 'error',
        summary: 'Weather API Connection Lost',
        detail: 'Unable to fetch forecast data.',
        life: 3000
      })
    }
    console.error('Error fetching forecast data:', e)
  }
}

/* 2️⃣ Current conditions → headline numbers */
let currentTimer = null

async function fetchCurrentData() {
  try {
    const url = new URL('https://api.open-meteo.com/v1/forecast')
    const params = {
      latitude      : 33.5731,
      longitude     : -7.5898,
      current       : 'temperature_2m,relative_humidity_2m,windspeed_10m,shortwave_radiation',
      timezone      : 'auto',
      windspeed_unit: 'kmh'
    }
    Object.entries(params).forEach(([k, v]) => url.searchParams.append(k, v))
    const res  = await fetch(url)
    const data = await res.json()

    if (!weatherOnline.value) {
      weatherOnline.value = true
      toast.add({
        severity: 'success',
        summary: 'Weather API Reconnected',
        detail: 'Current data is available again.',
        life: 3000
      })
    }

    if (data.current) {
      currentValues.value = {
        temperature : Math.round(data.current.temperature_2m),
        humidity    : Math.round(data.current.relative_humidity_2m),
        irradiance  : Math.round(data.current.shortwave_radiation),
        windspeed   : Math.round(data.current.windspeed_10m)
      }
    }
  } catch (e) {
    if (weatherOnline.value) {
      weatherOnline.value = false
      toast.add({
        severity: 'error',
        summary: 'Weather API Connection Lost',
        detail: 'Unable to fetch current data.',
        life: 3000
      })
    }
    console.error('Error fetching current data:', e)
  }
}

/* ──────────────────────────
   Lifecycle
───────────────────────────*/
onMounted(() => {
  fetchForecastData()          // one-off for charts
  fetchCurrentData()           // initial headline values
  currentTimer = setInterval(fetchCurrentData, 30_000) // refresh every 30 s

  // Also refresh forecast once on mount
  fetchForecastData()
})

onBeforeUnmount(() => {
  if (currentTimer) clearInterval(currentTimer)
})

/* ──────────────────────────
   Day navigation
───────────────────────────*/
function prevDay(metric) {
  switch (metric) {
    case 'temperature': if (tempDay.value       > 0) tempDay.value--       ; break
    case 'humidity'  : if (humidityDay.value   > 0) humidityDay.value--   ; break
    case 'irradiance': if (irradianceDay.value > 0) irradianceDay.value-- ; break
    case 'windspeed' : if (windspeedDay.value  > 0) windspeedDay.value--  ; break
  }
}

function nextDay(metric) {
  switch (metric) {
    case 'temperature': if (tempDay.value       < 6) tempDay.value++       ; break
    case 'humidity'  : if (humidityDay.value   < 6) humidityDay.value++   ; break
    case 'irradiance': if (irradianceDay.value < 6) irradianceDay.value++ ; break
    case 'windspeed' : if (windspeedDay.value  < 6) windspeedDay.value++  ; break
  }
}
</script>
