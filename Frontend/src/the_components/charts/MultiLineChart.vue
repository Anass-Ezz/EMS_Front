<template>
  <div class="h-full w-full">
    <v-chart
      class="chart"
      :option="chartOption"
      autoresize
      :update-options="{ notMerge: true }"
    />
  </div>
</template>

<script setup>
import { LineChart } from 'echarts/charts';
import {
    DataZoomComponent,
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent,
} from 'echarts/components';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { ref, watch } from 'vue';
import VChart from 'vue-echarts';

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
]);

const props = defineProps({
  response: { type: Object, required: true },
  isLegend: { type: Boolean, required: true },
  color: { type: Number, default: -1 },
  scaleConfig: { type: Array, default: () => [] },
  unitConfig: { type: Array, default: () => [] },
});

const chartOption = ref({});

const getRandomColor = () => {
  const hue = Math.floor(Math.random() * 360);
  return `hsl(${hue}, 70%, 50%)`;
};

watch(
  () => props.response,
  (newResponse) => {
    if (!newResponse?.payload?.result?.timestamps?.length) {
      chartOption.value = {};
      return;
    }

    const { timestamps, data } = newResponse.payload.result;
    const sfMap = Object.fromEntries(
      props.scaleConfig.map(c =>
        typeof c === 'string' ? [c, 1] : [c.channel, c.sf ?? 1]
      )
    );
    
    const unitMap = Object.fromEntries(
      props.unitConfig.map(c =>
        typeof c === 'string' ? [c, ''] : [c.channel, c.unit ?? '']
      )
    );

    const seriesData = Object.keys(data).map((channelName) => {
      const lineColor = props.color >= 0
          ? `hsl(${(props.color * 60) % 360}, 70%, 50%)`
          : getRandomColor();
      const scalingFactor = sfMap[channelName] ?? 1;

      return {
        name: channelName,
        type: 'line',
        smooth: true,
        symbol: 'none',
        connectNulls: true,
        data: (data[channelName] || []).map((value, i) => [
          timestamps[i],
          value == null ? null : Math.round((value * scalingFactor) * 100) / 100,
        ]),
        lineStyle: {
          color: lineColor,
          width: 2,
        },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{
              offset: 0, color: lineColor.replace('hsl', 'hsla').replace(')', ', 0.5)')
            }, {
              offset: 1, color: lineColor.replace('hsl', 'hsla').replace(')', ', 0)')
            }]
          },
          origin: 'start'
        },
      };
    });

    const css = getComputedStyle(document.documentElement);
    const textColor = css.getPropertyValue('--text-color-secondary') || '#ccc';
    const gridColor = css.getPropertyValue('--surface-d') || '#333';

    chartOption.value = {
      grid: {
        top: '10px', right: '2%', bottom: props.isLegend ? '40px' : '20px', left: '2%',
        containLabel: true,
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } },
        formatter: (params) => {
          if (!params || params.length === 0) return '';
          
          let tooltipText = `${params[0].axisValueLabel}<br/>`;
          params.forEach(param => {
            const unit = unitMap[param.seriesName] || '';
            const value = param.value[1];
            const formattedValue = value != null ? value.toFixed(2) : 'N/A';
            tooltipText += `${param.marker}${param.seriesName}: ${formattedValue} ${unit}<br/>`;
          });
          return tooltipText;
        }
      },
      legend: {
        show: props.isLegend, data: Object.keys(data), bottom: 0,
        textStyle: { color: textColor },
      },
      xAxis: {
        type: 'time',
        // --- THE FIX IS HERE ---
        // This combination forces the chart to be completely flush with the edges.
        min: timestamps[0],
        max: timestamps[timestamps.length - 1],
        boundaryGap: [0, 0], // THIS IS THE KEY: Removes padding at the start and end of the axis.
        // --- END OF FIX ---
        axisLabel: {
          color: textColor,
        },
        axisLine: {
          lineStyle: { color: gridColor },
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: { 
          color: textColor,
          formatter: (value) => {
            // Get the unit for the first series (assuming all series in a chart have the same unit)
            const firstChannel = Object.keys(data)[0];
            const unit = unitMap[firstChannel] || '';
            return unit ? `${value} ${unit}` : value;
          }
        },
        splitLine: { lineStyle: { color: gridColor, type: 'dashed' } },
      },
      dataZoom: [
        { type: 'inside', filterMode: 'weakFilter' },
      ],
      series: seriesData,
    };
  },
  { immediate: true, deep: true }
);
</script>

<style scoped>
.chart {
  height: 100%;
  width: 100%;
}
</style>