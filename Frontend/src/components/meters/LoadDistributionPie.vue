<!-- src/components/meters/LoadDistributionPie.vue -->
<template>
    <v-chart
      ref="chartRef"
      :option="chartOption"
      :autoresize="true"
      class="w-full h-full"
    />
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted, shallowRef } from 'vue'
  import { use } from 'echarts/core'
  import { CanvasRenderer } from 'echarts/renderers'
  import { PieChart } from 'echarts/charts'
  import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent
  } from 'echarts/components'
  import VChart from 'vue-echarts'
  
  use([
    CanvasRenderer,
    PieChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent
  ])
  
  const chartRef = ref(null)
  
  // Use shallowRef for chart option to avoid unnecessary reactivity on large object
  const chartOption = shallowRef({
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
        data: generateRandomPhaseData(),
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
        },
        animation: true,
        animationDuration: 1000,
        animationEasing: 'cubicInOut'
      }
    ]
  })
  
  let intervalId = null
  
  function generateRandomPhaseData() {
    const base = 33.33
    const variance = 0.8 // 👈 Very small fluctuation for "real-time" effect
  
    let p1 = base + (Math.random() * variance * 2 - variance) // ~32.53 to 34.13
    let p2 = base + (Math.random() * variance * 2 - variance)
    let p3 = 100 - p1 - p2
  
    // Tiny rebalance if needed (should rarely happen with small variance)
    if (p3 < 32.5 || p3 > 34.1) {
      const total = p1 + p2 + p3
      const diff = 100 - total
      p1 += diff / 3
      p2 += diff / 3
      p3 += diff / 3
    }
  
    // Round to 2 decimals
    p1 = parseFloat(p1.toFixed(2))
    p2 = parseFloat(p2.toFixed(2))
    p3 = parseFloat(p3.toFixed(2))
  
    return [
      { value: p1, name: 'Phase 1', itemStyle: { color: '#f97316' } },
      { value: p2, name: 'Phase 2', itemStyle: { color: '#06b6d4' } },
      { value: p3, name: 'Phase 3', itemStyle: { color: '#10b981' } }
    ]
  }
  
  function updateChartData() {
    if (!chartRef.value) return
  
    const newSeriesData = generateRandomPhaseData()
  
    // 👇 SET FULL OPTION (not partial merge) to avoid disappearing chart
    chartRef.value.setOption({
      series: [{
        data: newSeriesData,
        animation: true,
        animationDuration: 800,
        animationEasing: 'cubicInOut'
      }]
    }, false) // 👈 false = replace, not merge — safer for dynamic updates
  }
  
  onMounted(() => {
    // Start real-time updates every 1 second
    intervalId = setInterval(() => {
      updateChartData()
    }, 300000) // 👈 Every 1 second for "live" feel
  })
  
  onUnmounted(() => {
    if (intervalId) {
      clearInterval(intervalId)
    }
  })
  </script>
  
  <style scoped>
  /* Add scoped styles if needed later */
  </style>