<template>
  <v-chart
    v-if="chartOption.series && chartOption.series.length > 0"
    class="chart"
    :option="chartOption"
    autoresize
  />
</template>

<script setup>
import { ref, watch } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent]);

const props = defineProps({
  response: { type: Object, required: true },
  overlay: { type: Boolean, default: false },
});

const chartOption = ref({});

function toDateLabel(iso) {
  return iso.slice(0, iso.length >= 13 ? 10 : 7);
}

function randomRGBA() {
  const r = 100 + ~~(Math.random() * 120);
  const g = 100 + ~~(Math.random() * 120);
  const b = 100 + ~~(Math.random() * 120);
  return `rgba(${r},${g},${b},0.7)`;
}

watch(
  [() => props.response, () => props.overlay],
  ([newResponse, isOverlay]) => {
    const core = newResponse.payload?.result ?? newResponse;
    const { timestamps = [], data = {} } = core;

    if (timestamps.length === 0) {
      chartOption.value = {};
      return;
    }

    const labels = timestamps.map(toDateLabel);

    const seriesData = Object.entries(data).map(([key, arr]) => ({
      name: key,
      type: 'bar',
      stack: isOverlay ? undefined : 'total',
      barGap: '20%',
      data: arr.map(v => (v == null ? 0 : v / 1000)),
      itemStyle: {
        color: randomRGBA(),
        borderRadius: 2,
      },
      barWidth: '30%',
    }));

    const css = getComputedStyle(document.documentElement);
    const textColor = css.getPropertyValue('--text-color-secondary') || '#ccc';
    const gridLineColor = css.getPropertyValue('--surface-d') || 'rgba(255,255,255,0.1)';

    chartOption.value = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
      },
      legend: {
        show: true,
        bottom: 10,
        textStyle: { color: textColor },
        itemWidth: 12,
      },
      // --- THE FIX IS HERE ---
      // This new grid configuration minimizes padding around the chart.
      grid: {
        top: '10px',
        right: '3%',
        bottom: '40px', // Reserve a fixed space for the x-axis labels and the legend.
        left: '2%',
        containLabel: true, // CRUCIAL: Automatically adjusts padding to ensure labels are not cut off.
      },
      // --- END OF FIX ---
      xAxis: {
        type: 'category',
        data: labels,
        axisTick: { alignWithLabel: true },
        axisLine: { show: true, lineStyle: { color: gridLineColor } },
        splitLine: { show: false },
        axisLabel: { color: textColor },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: textColor },
        splitLine: { show: true, lineStyle: { color: gridLineColor } },
      },
      series: seriesData,
    };
  },
  { immediate: true, deep: true }
);
</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>