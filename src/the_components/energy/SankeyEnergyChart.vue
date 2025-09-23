<!-- src/the_components/EnergyFlowSankey.vue -->
<template>
  <div>

    <v-chart
    class="w-full"
    :option="option"
    :style="{ height: height + 'px' }"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { SankeyChart } from 'echarts/charts'
import { TooltipComponent, TitleComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, SankeyChart, TooltipComponent, TitleComponent])

/* ─── props ──────────────────────────────────────────────────────── */
const props = defineProps({
  height: { type: Number, default: 400 },
  flows: {
    type: Object,
    default: () => ({
      pvToBuffer:       300,
      windToBuffer:     260,
      battToBuffer:     120,
      bufferToLoad:     540,
      bufferToBattery:   80
    })
  },
  labels: {
    type: Object,
    default: () => ({
      pv:    'PV',
      wind:  'Wind',
      load:  'Export',
      buf:   'AC Bus',
      batt:  'Battery'      // visible label for BOTH battery nodes
    })
  }
})

/* ─── ECharts option ─────────────────────────────────────────────── */
const option = computed(() => {
  const L = props.labels
  const F = props.flows

  return {
    // title: { text: 'Last Month Energy Flow', left: 'center'},
    tooltip: { trigger: 'item', formatter: '{b0} → {b1}: {c} kWh' },
    series: [{
      type: 'sankey',
      nodeAlign: 'left',
      nodeWidth: 10,
      nodeGap: 12,
      label: { color: '#FFFF', fontWeight: 800 },
      /* distinct node IDs, same visible label for the two batteries */
      data: [
        { name: L.pv,    depth: 0 },
        { name: L.wind,  depth: 0 },
        {
          name: 'batteryOut',
          depth: 0,
          label: { formatter: () => L.batt }
        },
        { name: L.buf,   depth: 1 },
        { name: L.load,  depth: 2 },
        {
          name: 'batteryIn',
          depth: 0,
          label: { formatter: () => L.batt }
        }
      ],
      links: [
        { source: L.pv,        target: L.buf,        value: F.pvToBuffer },
        { source: L.wind,      target: L.buf,        value: F.windToBuffer },
        { source: 'batteryOut', target: L.buf,       value: F.battToBuffer },
        { source: L.buf,       target: L.load,       value: F.bufferToLoad },
        { source: L.buf,       target: 'batteryIn',  value: F.bufferToBattery }
      ]
    }]
  }
})
</script>

<style scoped>
/* Tailwind (if present) handles fonts & colours */
</style>
