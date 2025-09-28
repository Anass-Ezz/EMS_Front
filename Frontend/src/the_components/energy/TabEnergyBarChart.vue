<!-- src/the_components/energy/TabBarChart.vue -->
<template>
  <div class="w-full">
    <Tabs :value="tab">
      <!-- ─── tab headers ─────────────────────────────────────────── -->
      <TabList>
        <Tab value="active" @click="tab = 'active'">Active Energy</Tab>
        <Tab value="reactive" @click="tab = 'reactive'">Reactive Energy</Tab>
      </TabList>

      <!-- ─── tab panels ──────────────────────────────────────────── -->
      <TabPanels>
        <TabPanel value="active" class="h-[255px]">
          <MultiStackedBarChart
            v-if="activeResponse"
            :response="activeResponse"
            overlay
            class="w-full h-full"
            />
          </TabPanel>
          
          <TabPanel value="reactive" class="h-[255px]">
            <MultiStackedBarChart
            v-if="reactiveResponse"
            :response="reactiveResponse"
            overlay
            class="w-full h-full"
          />
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import MultiStackedBarChart from '@/the_components/charts/MultiStackedBarChart.vue'

/* ─── props from parent ───────────────────────────────────────────── */
const props = defineProps({
  /**  
   * Objects keyed by category name, each value = { last: <Wh>, current: <Wh> }  
   * e.g. { 'Solar gen.': { last: 450000, current: 500000 }, … }
   */
  activeBars:   { type: Object, required: true },
  reactiveBars: { type: Object, required: true }
})

/* ─── local tab state ─────────────────────────────────────────────── */
const tab = ref('active')

/* ─── build a “timestamps + data” response shape ──────────────────── */
function toResponse(bars) {
  const categories = Object.keys(bars)
  const lastArr    = categories.map(cat => bars[cat].last)
  const curArr     = categories.map(cat => bars[cat].current)

  return {
    timestamps: categories,       // x-axis labels = each category
    data: {
      'Last month':    lastArr,
      'Current month': curArr
    }
  }
}

const activeResponse   = computed(() => toResponse(props.activeBars))
const reactiveResponse = computed(() => toResponse(props.reactiveBars))
</script>

<style scoped>
/* PrimeVue / Tailwind handle styling */
</style>
