<script setup>
import { useToast } from 'primevue/usetoast'; // Added toast import
import { onBeforeUnmount, onMounted, ref } from 'vue'

// Reactive object that holds the latest readings
const currentValues = ref({
  irradiance: '-',
  windspeed: '-',
  temperature: '-'
})

const toast = useToast()       // Initialized toast
const weatherOnline = ref(true) // Track connection status

let intervalId = null

/**
 * Fetch the *hourly* forecast for today and pull out the entry
 * that matches the present hour in the station’s local time-zone.
 */
async function fetchWeatherData () {
  try {
    const url = new URL('https://api.open-meteo.com/v1/forecast')
    const params = {
      latitude: 33.5731,
      longitude: -7.5898,
      // request only variables we need
      hourly: 'temperature_2m,windspeed_10m,shortwave_radiation',
      // keep the values in the station’s own time-zone (Africa/Casablanca for Casablanca)
      timezone: 'auto',
      // limit forecast to 1 day so the array contains exactly today’s 24 items
      forecast_days: 1,
      // make windspeed unit explicit so we know what we get
      windspeed_unit: 'kmh'
    }
    Object.entries(params).forEach(([k, v]) => url.searchParams.append(k, v))

    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()

    // Defensive check
    if (!data.hourly || !data.hourly.time?.length) return

    /* If previously offline, now reconnected → show toast */
    if (!weatherOnline.value) {
      weatherOnline.value = true
      toast.add({
        severity: 'success',
        summary: 'Weather API Reconnected',
        detail: 'Environment data is available again.',
        life: 3000
      })
    }

    /* Build the current hour in the *same* ISO-string format
       Open-Meteo uses, e.g. “2025-05-30T14:00”. Because the API
       already converted to the station’s local zone, we can rely
       on the client’s local clock when the user is in that zone. */
    const now = new Date()
    const currentHourStr =
      `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}T${String(now.getHours()).padStart(2, '0')}:00`

    // Find the matching index; fall back to the *last* available hour
    let idx = data.hourly.time.findIndex(t => t === currentHourStr)
    if (idx === -1) idx = data.hourly.time.length - 1

    currentValues.value = {
      irradiance: Math.round(data.hourly.shortwave_radiation[idx]),
      // API returns km/h → convert to m/s
      windspeed: Math.round(data.hourly.windspeed_10m[idx] / 3.6),
      temperature: Math.round(data.hourly.temperature_2m[idx])
    }
  } catch (err) {
    // On first failure, show toast once
    if (weatherOnline.value) {
      weatherOnline.value = false
      toast.add({
        severity: 'error',
        summary: 'Weather API Connection Lost',
        detail: 'Unable to fetch environment data.',
        life: 3000
      })
    }
    console.error('Error fetching weather data:', err)
  }
}

// First run + 30-second refresh loop
onMounted(() => {
  fetchWeatherData()
  intervalId = setInterval(fetchWeatherData, 30_000)
})

onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>
<template>

  <div class="font-semibold text-xl ">Environment</div>
  <Card class="p-0">
    <template #content>

      <div class="card">
        <div class="flex flex-rox gap-3 justify-around py-0">
          <!-- Irradiance -->
          <div class="flex flex-row gap-2 items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="20"
                fill="currentColor" class="bi bi-brightness-high text-orange-700"
                viewBox="0 0 16 16">
              <path d="M8 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6m0 1a4 4 0 1 0 0-8 4 4 0 0 0 0 8M8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0m0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13m8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5M3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8m10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0m-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0m9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707M4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708"/>
            </svg>
            <div class="text-2xl text-orange-500">
              {{ currentValues.irradiance }} <span class="text-lg">W/m²</span>
            </div>
          </div>

          <!-- Wind speed -->
          <div class="flex flex-row gap-2 items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="20"
                fill="currentColor" class="bi bi-wind text-blue-700"
                viewBox="0 0 16 16">
              <path d="M12.5 2A2.5 2.5 0 0 0 10 4.5a.5.5 0 0 1-1 0A3.5 3.5 0 1 1 12.5 8H.5a.5.5 0 0 1 0-1h12a2.5 2.5 0 0 0 0-5m-7 1a1 1 0 0 0-1 1 .5.5 0 0 1-1 0 2 2 0 1 1 2 2h-5a.5.5 0 0 1 0-1h5a1 1 0 0 0 0-2M0 9.5A.5.5 0 0 1 .5 9h10.042a3 3 0 1 1-3 3 .5.5 0 0 1 1 0 2 2 0 1 0 2-2H.5a.5.5 0 0 1-.5-.5"/>
            </svg>
            <div class="text-2xl text-blue-500">
              {{ currentValues.windspeed }} <span class="text-lg">m/s</span>
            </div>
          </div>

          <!-- Temperature -->
          <div class="flex flex-row gap-2 items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="20"
                fill="currentColor" class="bi bi-thermometer-half text-cyan-700"
                viewBox="0 0 16 16">
              <path d="M9.5 12.5a1.5 1.5 0 1 1-2-1.415V6.5a.5.5 0 0 1 1 0v4.585a1.5 1.5 0 0 1 1 1.415"/>
              <path d="M5.5 2.5a2.5 2.5 0 0 1 5 0v7.55a3.5 3.5 0 1 1-5 0zM8 1a1.5 1.5 0 0 0-1.5 1.5v7.987l-.167.15a2.5 2.5 0 1 0 3.333 0l-.166-.15V2.5A1.5 1.5 0 0 0 8 1"/>
            </svg>
            <div class="text-2xl text-cyan-500">
              {{ currentValues.temperature }} <span class="text-lg">°C</span>
            </div>
          </div>
        </div>
      </div>
    </template>


  </Card>
</template>