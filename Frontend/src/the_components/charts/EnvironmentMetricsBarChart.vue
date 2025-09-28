<template>
    <Chart
      type="bar"
      :data="chartData"
      :options="chartOptions"
    />
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import Chart from 'primevue/chart'
  
  const props = defineProps({
    metricName: String,
    chartData: Array,
    labels: Array,
    backgroundColor: {
      type: String,
      default: 'rgba(54, 162, 235, 0.7)'
    }
  })
  
  const chartData = computed(() => ({
    labels: props.labels.length ? props.labels : generateDefaultLabels(),
    datasets: [{
      label: props.metricName,
      data: props.chartData,
      backgroundColor: props.backgroundColor,
      barPercentage: 0.9,
      categoryPercentage: 0.8
    }]
  }))
  
  const chartOptions = computed(() => ({
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: { display: false },
        // title: { display: true, text: 'Time Period' }
      },
      y: {
        beginAtZero: true,
        // title: { display: true, text: props.metricName },
        grid: { color: 'rgba(255,255,255,0.1)' }
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: (items) => `${props.metricName} at ${items[0].label}`,
          label: (context) => `${props.metricName}: ${context.parsed.y}`
        }
      }
    }
  }))
  
  function generateDefaultLabels() {
    return props.chartData.map((_, i) => `T+${i + 1}`)
  }
  </script>