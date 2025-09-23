<template>
  <div class="w-full h-full">
    <v-chart
      v-if="chartOptions"
      class="chart"
      :option="chartOptions"
      autoresize
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import {
  TooltipComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

// Register only the necessary ECharts components
use([
  CanvasRenderer,
  PieChart,
  TooltipComponent,
])

/* ─── props ──────────────────────────────────────────────────── */
const props = defineProps({
  wind:    { type: Number, required: true },
  solar:   { type: Number, required: true },
  battery: { type: Number, required:true }
})

// ✅ FIX #1: Store the inner <path> elements for each icon.
// This allows for both single-path and multi-path icons.
const ICON_DATA = {
  solar: `<path d="M8 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6m0 1a4 4 0 1 0 0-8 4 4 0 0 0 0 8M8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0m0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13m8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5M3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8m10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0m-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0m9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707M4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708"/>`,
  wind: `<path d="M12.5 2A2.5 2.5 0 0 0 10 4.5a.5.5 0 0 1-1 0A3.5 3.5 0 1 1 12.5 8H.5a.5.5 0 0 1 0-1h12a2.5 2.5 0 0 0 0-5m-7 1a1 1 0 0 0-1 1 .5.5 0 0 1-1 0 2 2 0 1 1 2 2h-5a.5.5 0 0 1 0-1h5a1 1 0 0 0 0-2M0 9.5A.5.5 0 0 1 .5 9h10.042a3 3 0 1 1-3 3 .5.5 0 0 1 1 0 2 2 0 1 0 2-2H.5a.5.5 0 0 1-.5-.5"/>`,
  battery: `
    <path d="M9.585 2.568a.5.5 0 0 1 .226.58L8.677 6.832h1.99a.5.5 0 0 1 .364.843l-5.334 5.667a.5.5 0 0 1-.842-.49L5.99 9.167H4a.5.5 0 0 1-.364-.843l5.333-5.667a.5.5 0 0 1 .616-.09z"/>
    <path d="M2 4h4.332l-.94 1H2a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1h2.38l-.308 1H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2"/>
    <path d="M2 6h2.45L2.908 7.639A1.5 1.5 0 0 0 3.313 10H2zm8.595-2-.308 1H12a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H9.276l-.942 1H12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z"/>
    <path d="M12 10h-1.783l1.542-1.639q.146-.156.241-.34zm0-3.354V6h-.646a1.5 1.5 0 0 1 .646.646M16 8a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8"/>
  `
}

/**
 * ✅ FIX #2: Generalized helper function.
 * It now takes the entire inner SVG content, not just a single path.
 * @param {string} innerContent The SVG content (e.g., one or more <path> tags).
 * @param {string} color The hex color to apply to the icon.
 * @returns {string} A Base64-encoded data URL for the complete SVG.
 */
function createIconDataURL(innerContent, color) {
  // By setting the fill on the top-level <svg> element, it cascades to all child paths.
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="${color}">
                 ${innerContent}
               </svg>`;
  return 'data:image/svg+xml;base64,' + btoa(svg);
}


/* ─── computed: ECharts options ------------------------------- */
const chartOptions = computed(() => {
  const baseData = [
    { value: props.wind,    name: 'Wind Export',    iconKey: 'wind' },
    { value: props.solar,   name: 'Solar Export',   iconKey: 'solar' },
    { value: props.battery, name: 'Battery Export', iconKey: 'battery' }
  ].sort((a, b) => b.value - a.value);

  const colorPalette = ['#c23531', '#d48265', '#B5495B'];

  const richStyles = {};
  baseData.forEach((item, index) => {
    richStyles[`icon${index}`] = {
      height: 20,
      width: 20,
      align: 'center',
      backgroundColor: {
        // Use the new, more flexible ICON_DATA object
        image: createIconDataURL(ICON_DATA[item.iconKey], colorPalette[index])
      }
    };
  });

  return {
    color: colorPalette,

    tooltip: {
      trigger: 'item',
      formatter: (params) => `${params.name}<br/>${params.value.toLocaleString()} MAD (${params.percent}%)`
    },
    
    legend: { show: false },
    
    series: [
      {
        name: 'Export Revenue',
        type: 'pie',
        radius: '90%', 
        center: ['50%', '50%'],
        data: baseData,
        itemStyle: {},
        
        label: {
          show: true,
          position: 'outside',
          formatter: (params) => `{icon${params.dataIndex}|}`,
          rich: richStyles
        },
        
        labelLine: {
          show: true,
          length: 15,
          length2: 20,
          smooth: true,
          lineStyle: {
            color: '#aaa',
            width: 1
          }
        },

        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})
</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>