<!-- src/components/dashboard/charts/CircleProgress.vue -->
<script setup>
import { useLayout } from '@/layout/composables/layout'
import Chart from 'primevue/chart'
import { onMounted, ref, watch } from 'vue'

const { getPrimary, getSurface, isDarkTheme } = useLayout()

/* ─── props ─── */
const props = defineProps({
  value1:    { type: Number, required: true }, // inner ring
  value2:    { type: Number, required: true }, // outer ring
  max:       { type: Number, required: true },
  imagePath: { type: String, required: true },
  size:      { type: Number, default: 70 }
})

/* ─── refs ─── */
const chartRef     = ref(null)
const chartData    = ref(null)
const chartOptions = ref(null)

/* helpers ------------------------------------------------------------ */
function pct (v) { return (v / props.max) * 100 }

function buildData () {
  const css = getComputedStyle(document.documentElement)
  return {
    datasets: [
      {
        // outer ring – value2
        data: [pct(props.value2), 100 - pct(props.value2)],
        backgroundColor: [
          css.getPropertyValue('--p-primary-300'),
          'transparent'
        ],
        borderWidth: 0,
        cutout: '70%',
        borderRadius: 20
      },
      {
        // inner ring – value1
        data: [pct(props.value1), 100 - pct(props.value1)],
        backgroundColor: [
          css.getPropertyValue('--p-orange-500'),
          css.getPropertyValue('--surface-border')
        ],
        borderWidth: 0,
        cutout: '90%',
        borderRadius: 20
      }
    ]
  }
}

function buildOptions () {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,               // disable default sweep
    plugins: {
      legend:  { display: false },
      tooltip: { enabled: false }
    }
  }
}

/* in-place update ---------------------------------------------------- */
function updateChart () {
  const inst = chartRef.value?.chart
  if (!inst) return

  // update percentages
  inst.data.datasets[0].data = [pct(props.value2), 100 - pct(props.value2)]
  inst.data.datasets[1].data = [pct(props.value1), 100 - pct(props.value1)]

  // update colours if theme changed
  const css = getComputedStyle(document.documentElement)
  inst.data.datasets[0].backgroundColor[0] =
    css.getPropertyValue('--p-primary-300')
  inst.data.datasets[1].backgroundColor = [
    css.getPropertyValue('--p-orange-500'),
    css.getPropertyValue('--surface-border')
  ]

  inst.update('none')               // redraw without animation
}

/* watch values + theme ------------------------------------------------ */
watch(
  [() => props.value1, () => props.value2, getPrimary, getSurface, isDarkTheme],
  updateChart
)

/* first render -------------------------------------------------------- */
onMounted(() => {
  chartData.value    = buildData()
  chartOptions.value = buildOptions()
})
</script>

<template>
  <div :style="{ width: `${size}px`, height: `${size}px` }" class="relative">
    <Chart
      ref="chartRef"
      type="doughnut"
      :data="chartData"
      :options="chartOptions"
      class="h-full w-full"
    />
    <div class="absolute inset-0 flex items-center justify-center">
      <img
        :src="imagePath"
        alt="center icon"
        :style="{ width: `${size * 0.5}px`, height: `${size * 0.5}px` }"
        class="object-contain"
      />
    </div>
  </div>
</template>

<style scoped></style>
