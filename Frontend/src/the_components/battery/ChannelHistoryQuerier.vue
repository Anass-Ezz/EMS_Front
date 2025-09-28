<template>  
        <MultiLineChart :response="response" :color="4"     :isLegend="false"/>
  </template>
  
  <script setup>
  import { inject, ref, watch } from 'vue'
  import MultiLineChart from '@/the_components/charts/MultiLineChart.vue'
  
  const ws   = inject('ws')
  const auth = inject('auth')   // reactive { ready: Boolean }
  
  

  const props = defineProps({
    channelAddress : { type: String,  required: true },
  })

  console.log(props.channelAddress)

  const channelSet = [
    props.channelAddress
  ]

  const response = ref({})
  function sendHistoricRequest () {
    const OUTER_ID = crypto.randomUUID()
    const INNER_ID = crypto.randomUUID()
    const today    = new Date().toISOString().slice(0, 10)
  
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id:      OUTER_ID,
      method:  'edgeRpc',
      params: {
        edgeId: 'edge0',
        payload: {
          jsonrpc: '2.0',
          id:      INNER_ID,
          method:  'queryHistoricTimeseriesData',
          params: {
            channels:   channelSet,
            fromDate:   today,
            toDate:     today,
            resolution: { value: 1, unit: 'Hours' },
            timezone:   'Africa/Casablanca'
          }
        }
      }
    }))
  
    const handler = ({ data }) => {
      const msg = JSON.parse(data)
  
      if (msg.id === OUTER_ID && msg.result) {
        response.value = msg.result
        ws.removeEventListener('message', handler)
      }
    }
  
    ws.addEventListener('message', handler)
  }
  
  watch(
    () => auth.ready,
    ready => { if (ready) sendHistoricRequest() },
    { immediate: true }
  )
  </script>
  
  <style scoped>
  /* Tailwind gère les espacements */
  </style>
  