<script setup>
/* --------------------------------------------------------- *
 *  Sun-position gizmo page  –  Leaflet.Terminator friendly
 * --------------------------------------------------------- */

import { ref, onMounted, onUnmounted } from 'vue';
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet';
import * as L from 'leaflet';
import * as SunCalc from 'suncalc';
import 'leaflet/dist/leaflet.css';

/* Make Leaflet visible to UMD plugins that expect global `L` */
window.L = L;

/* 1 ▸ fixed site coordinates */
const LAT  = 32.2359;
const LON  = -7.9538;
const ZOOM = 8;

/* 2 ▸ reactive state */
const now      = ref(new Date());
const position = ref({ azimuth: 0, altitude: 0 });   // radians
const times    = ref({});                            // sunrise, sunset…

/* 3 ▸ helpers */
const radToDeg = r => r * 180 / Math.PI;

function update() {
  now.value = new Date();

  /* current solar position */
  const pos = SunCalc.getPosition(now.value, LAT, LON);
  position.value = { azimuth: pos.azimuth, altitude: pos.altitude };

  /* today’s key solar times & azimuths */
  const t = SunCalc.getTimes(now.value, LAT, LON);
  times.value = {
    dawn            : t.dawn,
    sunrise         : t.sunrise,
    solarNoon       : t.solarNoon,
    sunset          : t.sunset,
    dusk            : t.dusk,
    dayLengthMin    : (t.sunset - t.sunrise) / 1000 / 60,
    sunriseAzimuth  : SunCalc.getPosition(t.sunrise, LAT, LON).azimuth,
    sunsetAzimuth   : SunCalc.getPosition(t.sunset,  LAT, LON).azimuth
  };
}

/* 4 ▸ start / stop the 1-minute ticker */
let tick;
onMounted(() => {
  update();
  tick = setInterval(update, 60_000);
});
onUnmounted(() => clearInterval(tick));

/* 5 ▸ add day/night overlays when the Leaflet map is ready */
async function onMapReady(map) {
  /* load the plugin ***after*** window.L exists */
  await import('@joergdietrich/leaflet.terminator');

  const night = L.terminator({ fillOpacity: 0.45, color: '#000' }).addTo(map);
  const day   = L.terminator({ fillOpacity: 0.18, color: '#ffd800', fill: true }).addTo(map);

  /* refresh both masks every five minutes */
  setInterval(() => {
    night.setTime();
    day.setTime();
  }, 300_000);
}
</script>

<template>
  <div class="sun-page p-4 grid gap-4">
    <!-- ╭───────────────────  MAP  ───────────────────╮ -->
    <LMap
      :center="[LAT, LON]"
      :zoom="ZOOM"
      :zoomControl="true"
      :scrollWheelZoom="true"
      :dragging="false"
      class="h-[70vh] w-full rounded-2xl shadow"
      @ready="onMapReady"
    >
      <LTileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    </LMap>

    <!-- ╭─────────────────  GIZMO  ──────────────────╮ -->
    <div class="pointer-events-none absolute inset-0 flex items-center justify-center">
      <svg viewBox="-110 -110 220 220" class="h-64 w-64">
        <!-- outer rim -->
        <circle r="110" fill="none" stroke="#000" stroke-width="1" />

        <!-- daylight fan inside gizmo -->
        <path d="M-110 0 A110 110 0 0 1 110 0 L0 0 Z"
              fill="rgba(255,216,0,0.15)" />

        <!-- sun-path arc -->
        <path d="M-100 0 A100 100 0 0 1 100 0"
              stroke="#ffe000" stroke-width="8" fill="none" />

        <!-- sunrise / sunset azimuth rays -->
        <line
          :x2="100 * Math.sin(times.sunriseAzimuth)"
          :y2="-100 * Math.cos(times.sunriseAzimuth)"
          stroke="#ff6500" stroke-width="7" />
        <line
          :x2="100 * Math.sin(times.sunsetAzimuth)"
          :y2="-100 * Math.cos(times.sunsetAzimuth)"
          stroke="#ff6500" stroke-width="7" />

        <!-- live Sun marker -->
        <circle
          :cx="100 * Math.sin(position.azimuth)"
          :cy="-100 * Math.cos(position.azimuth)"
          r="7" fill="#777" stroke="#000" stroke-width="1.5" />
      </svg>
    </div>

    <!-- ╭───────────────  DATA PANEL  ───────────────╮ -->
    <Card header="Solar data (live)" class="w-full">
      <template #content>
        <ul class="text-sm leading-6">
          <li><b>Now:</b>      {{ now.toLocaleTimeString() }}</li>
          <li><b>Dawn:</b>     {{ times.dawn?.toLocaleTimeString?.() }}</li>
          <li>
            <b>Sunrise:</b>    {{ times.sunrise?.toLocaleTimeString?.() }}
            &nbsp; <b>Az:</b>  {{ radToDeg(times.sunriseAzimuth).toFixed(1) }}°
          </li>
          <li><b>Noon:</b>     {{ times.solarNoon?.toLocaleTimeString?.() }}</li>
          <li>
            <b>Sunset:</b>     {{ times.sunset?.toLocaleTimeString?.() }}
            &nbsp; <b>Az:</b>  {{ radToDeg(times.sunsetAzimuth).toFixed(1) }}°
          </li>
          <li><b>Dusk:</b>     {{ times.dusk?.toLocaleTimeString?.() }}</li>
          <li><b>Day length:</b> {{ Math.round(times.dayLengthMin) }} min</li>
          <li><b>Altitude:</b> {{ radToDeg(position.altitude).toFixed(1) }}°</li>
          <li><b>Azimuth:</b>  {{ radToDeg(position.azimuth).toFixed(1) }}°</li>
        </ul>
      </template>
    </Card>
  </div>
</template>

<style scoped>
/* make it clear the map is fixed-centre */
.sun-page :deep(.leaflet-container) {
  cursor: default;
}
</style>
