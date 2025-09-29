<template>
  <div class="card w-full h-[calc(97vh-100px)] overflow-hidden relative flex flex-col">
    <div 
      class="flex-1 overflow-hidden relative"
      :style="{ backgroundImage: dottedBackground }"
      @wheel.prevent="handleZoom"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="endDrag"
      @mouseleave="endDrag"
      ref="container"
    >
      <div 
        class="absolute top-0 left-0 origin-top-left transform-gpu transition-transform duration-100 ease-linear"
        :style="{
          transform: `translate(${position.x}px, ${position.y}px) scale(${zoom})`,
          cursor: isDragging ? 'grabbing' : 'grab'
        }"
        v-html="processedSvg"
        ref="svgContainer"
      ></div>
    </div>
  </div>
</template>

<script setup>
import svgContent from '@/assets/Diagrams/TestDiagram.svg?raw'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

// --- Router ---
const router = useRouter()

// --- Refs ---
const container = ref(null)
const svgContainer = ref(null)
const position = ref({ x: 0, y: 0 })
const zoom = ref(1)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const initialPosition = ref({ x: 0, y: 0 })
const counter = ref(0)
let animationId = null
let powerAnimationId = null
let gasFuelAnimationId = null

// --- State Management ---
// Edge device states (true = offline, false = online)
const edgeStates = ref([false, false, false, false]) // Initially all online

// Smart meter connection states (true = disconnected/ERROR, false = connected/OK)
const meterStates = ref({
  'sm-a-0': false,
  'sm-a-1': false,
  'sm-a-2': false,
  'sm-a-3': false,
  'sm-a-4': false,
  'sm-a-5': false,
  'sm-b-0': false,
  'sm-b-1': false,
  'sm-b-2': false,
  'sm-b-3': false,
  'sm-b-4': false,
})

// Smart meter power values (in kW) - initialized near max ratings
const meterPowerValues = ref({
  'sm-a-0': 450,  // Near 500kW max (Stamping Press)
  'sm-a-1': 420,  // Near 500kW max (Induction Heater)
  'sm-a-2': 85,   // Near 100kW max (Robotic Arms A)
  'sm-a-3': 42,   // Near 50kW max (Large Welder)
  'sm-a-4': 22,   // Near 25kW max (Feeder Motor)
  'sm-a-5': 27,   // Near 30kW max (Control + Utilities A)
  'sm-b-0': 90,   // Near 100kW max (Chassis Mounting)
  'sm-b-1': 72,   // Near 80kW max (Robotic Arms B)
  'sm-b-2': 22,   // Near 25kW max (Wiring Benches)
  'sm-b-3': 24,   // Near 25kW max (Control + Utilities B)
  'sm-b-4': 120,  // Near 150kW max (Solar Inverter)
})

// Gas meter data (gm-0 and gm-1) - flow in m³/s
const gasMeterData = ref({
  'gm-0': {
    temperature: 22,    // °C - ambient temperature
    pressure: 0.3,      // bar - low pressure from tank
    flow: 0.012,        // m³/s - for industrial oven (natural gas density ~0.717 kg/m³)
    state: false        // connection state
  },
  'gm-1': {
    temperature: 22,    // °C - ambient temperature
    pressure: 0.3,      // bar - low pressure from tank
    flow: 0.010,        // m³/s - for industrial oven
    state: false        // connection state
  }
})

// Fuel meter data (fm-0) - flow in kg/s
const fuelMeterData = ref({
  'fm-0': {
    temperature: 35,    // °C - preheated fuel
    pressure: 2.0,      // bar - realistic boiler pressure
    flow: 0.3,          // kg/s - realistic boiler consumption
    state: false        // connection state
  }
})

// Smart meter names mapping
const smartMeterNames = {
  'sm-a-0': 'WS-A Stamping Press Meter',
  'sm-a-1': 'WS-A Induction Heater Meter',
  'sm-a-2': 'WS-A Coil feeder Meter',
  'sm-a-3': 'WS-A Large Welder Meter',
  'sm-a-4': 'WS-A Controls Meter',
  'sm-a-5': 'WS-A Utilities Meter',
  'sm-b-0': 'WS-B Chassis Mounting Meter',
  'sm-b-1': 'WS-B Robotic Arms Meter',
  'sm-b-2': 'WS-B Wiring Benches Meter',
  'sm-b-3': 'WS-B Control Meter',
  'sm-b-4': 'WS-B Utilities Meter'
}

// Helper data structure for smart meter buttons
const smartMeters = computed(() => {
  return Object.keys(meterStates.value).map(id => ({ id }))
})

// --- Background ---
const dottedBackground = computed(() => {
  // Increased dot size and opacity for better visibility
  const dotSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20">
      <circle cx="2" cy="2" r="2" fill="currentColor" opacity="0.3" />
    </svg>
  `
  const dotSvgBase64 = btoa(dotSvg)
  return `url("data:image/svg+xml;base64,${dotSvgBase64}")`
})

// --- SVG Processing ---
const processedSvg = computed(() => {
  return svgContent
    .replace(/<g id="node-a"/g, '<g id="node-a" data-node="A" style="cursor: pointer"')
    .replace(/<g id="node-b"/g, '<g id="node-b" data-node="B" style="cursor: pointer"')
    .replace(/<g id="gm-0"/g, '<g id="gm-0" style="cursor: pointer"')
    .replace(/<g id="gm-1"/g, '<g id="gm-1" style="cursor: pointer"')
    .replace(/<g id="fm-0"/g, '<g id="fm-0" style="cursor: pointer"')
    .replace(/<g id="pv-0"/g, '<g id="pv-0" style="cursor: pointer"')
})

// --- Click Handling ---
const handleDiagramClick = (event) => {
  const nodeElement = event.target.closest('[data-node]')
  if (nodeElement) {
    const nodeId = nodeElement.getAttribute('data-node')
    alert(`Node ${nodeId} clicked!`)
    return;
  }
  
  // Handle smart meter clicks
  const smElement = event.target.closest('[id^="sm-"]')
  if (smElement) {
    const smId = smElement.id
    if (smartMeterNames[smId]) {
      // Navigate to meters page with meter info
      router.push({
        path: '/meters',
        query: { 
          meterId: smId,
          meterName: smartMeterNames[smId]
        }
      })
    }
    return;
  }
  
  // Handle gas meter clicks
  const gmElement = event.target.closest('[id^="gm-"]')
  if (gmElement) {
    const gmId = gmElement.id
    // Navigate to gas meters page with meter info
    router.push({
      path: '/gas-meters',
      query: { 
        meterId: gmId,
        meterName: `Gas Meter ${gmId.split('-')[1]} - Industrial Oven`
      }
    })
    return;
  }
  
  // Handle fuel meter clicks
  const fmElement = event.target.closest('[id^="fm-"]')
  if (fmElement) {
    const fmId = fmElement.id
    // Navigate to fuel meters page with meter info
    router.push({
      path: '/fuel-meters',
      query: { 
        meterId: fmId,
        meterName: `Fuel Meter ${fmId.split('-')[1]} - Chaudière`
      }
    })
    return;
  }
  
  // Handle PV meter clicks
  const pvElement = event.target.closest('#pv-0')
  if (pvElement) {
    const pvId = pvElement.id
    // Navigate to PV page
    router.push({
      path: '/pv',
      query: { 
        meterId: pvId,
        meterName: 'Solar PV System'
      }
    })
    return;
  }
}

// --- Panning/Zooming ---
const handleZoom = (event) => {
  if (!container.value) return
  
  const rect = container.value.getBoundingClientRect()
  
  // Get mouse position relative to container
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top
  
  // Calculate zoom
  const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.max(0.1, Math.min(5, zoom.value * zoomFactor))
  
  if (newZoom !== zoom.value) {
    // Get the point in the diagram space before zoom
    const diagramX = (mouseX - position.value.x) / zoom.value
    const diagramY = (mouseY - position.value.y) / zoom.value
    
    // Update zoom
    zoom.value = newZoom
    
    // Adjust position to keep the mouse point stationary
    position.value = {
      x: mouseX - diagramX * newZoom,
      y: mouseY - diagramY * newZoom
    }
  }
}

const startDrag = (event) => {
  if (event.target.closest('[data-node]') || event.target.closest('[id^="sm-"]') || event.target.closest('[id^="gm-"]') || event.target.closest('[id^="fm-"]') || event.target.closest('#pv-0')) {
    handleDiagramClick(event)
    return
  }
  isDragging.value = true
  dragStart.value = { x: event.clientX, y: event.clientY }
  initialPosition.value = { ...position.value }
  event.preventDefault()
}

const onDrag = (event) => {
  if (!isDragging.value) return
  const dx = event.clientX - dragStart.value.x
  const dy = event.clientY - dragStart.value.y
  position.value = {
    x: initialPosition.value.x + dx,
    y: initialPosition.value.y + dy
  }
}

const endDrag = () => {
  isDragging.value = false
}

// --- Text Animation (for text-0) ---
const updateTextPlaceholder = () => {
  if (!svgContainer.value) return
  nextTick(() => {
    const textGroup = svgContainer.value.querySelector('#text-0')
    if (textGroup) {
      const textDiv = textGroup.querySelector('div[style*="display: inline-block"]')
      if (textDiv) {
        textDiv.textContent = counter.value.toString()
      } else {
        console.warn('Text content div not found within #text-0 group')
        const foreignObjectDiv = textGroup.querySelector('foreignObject div div div')
        if (foreignObjectDiv) {
          foreignObjectDiv.textContent = counter.value.toString()
        }
      }
    } else {
      console.warn('Text placeholder group element with id="text-0" not found in SVG')
    }
  })
}
watch(counter, updateTextPlaceholder)

// --- Dynamic SVG Element Updates ---
const updateSvgElement = (elementId, value, isStateElement = false, isMeter = false, isGasFuel = false) => {
  if (!svgContainer.value) return
  nextTick(() => {
    const elementGroup = svgContainer.value.querySelector(`#${elementId}`)
    if (elementGroup) {
      let textDiv = elementGroup.querySelector('div[style*="display: inline-block"]')
      if (!textDiv) {
        textDiv = elementGroup.querySelector('foreignObject div div div')
      }
      if (textDiv) {
        if (isStateElement && isMeter) {
          // Smart Meter State Logic (e.g., sm-a-0-state)
          const isDisconnected = value // value is boolean for state
          textDiv.textContent = isDisconnected ? 'ERROR' : 'OK'
          textDiv.style.color = isDisconnected ? '#ef4444' : '#22c55e' // Red if ERROR, Green if OK
        } else if (!isStateElement && isMeter) {
          // Smart Meter Power Logic (e.g., sm-a-0-pwr)
          const powerText = value // value is the formatted string like "12.3 kW"
          textDiv.textContent = powerText
          textDiv.style.color = '#ffffff' // Ensure white text
          
          // Add black background highlight effect for power values
          textDiv.style.backgroundColor = 'rgba(150, 150, 150, 1)'
          textDiv.style.padding = '2px 4px'
          textDiv.style.borderRadius = '3px'
          textDiv.style.transition = 'background-color 0.3s ease-out'
          
          // Fade out the background after a short delay
          setTimeout(() => {
            if (textDiv) {
              textDiv.style.backgroundColor = 'transparent'
            }
          }, 200)
        } else if (isGasFuel) {
          // Gas/Fuel meter data
          textDiv.textContent = value
          textDiv.style.fontWeight = 'bold'
        } else {
          // Edge Device Logic (backward compatibility for edge states)
          const isOnline = value
          textDiv.textContent = isOnline ? 'ONLINE' : 'OFFLINE'
          textDiv.style.color = isOnline ? '#22c55e' : '#ef4444'
        }
        textDiv.style.fontWeight = 'bold'
      } else {
        console.warn(`Text content div not found within #${elementId} group`)
      }
    } else {
      // Only warn for state elements, as power elements might not exist initially or be named differently
      if (isStateElement) {
        console.warn(`SVG group element with id="${elementId}" not found`)
      }
    }
  })
}

// --- Power Animation Functions ---
// Helper function for small, realistic fluctuations
function fluctuatePower(currentValue, maxValue, variation = 0.03) {
  // Small fluctuations +/- 3% around current value
  const variationFactor = 1 + (Math.random() - 0.5) * variation
  const newValue = currentValue * variationFactor
  // Keep within reasonable bounds near max rating
  const minVal = maxValue * 0.7  // 70% of max
  const maxVal = maxValue * 1.05 // 105% of max (slight buffer)
  return Math.max(minVal, Math.min(maxVal, newValue))
}

// Animate power consumption values with realistic fluctuations
const animatePowerValues = () => {
  // Workshop A equipment (near max ratings)
  meterPowerValues.value['sm-a-0'] = fluctuatePower(meterPowerValues.value['sm-a-0'], 500)  // Stamping Press
  meterPowerValues.value['sm-a-1'] = fluctuatePower(meterPowerValues.value['sm-a-1'], 500)  // Induction Heater
  meterPowerValues.value['sm-a-2'] = fluctuatePower(meterPowerValues.value['sm-a-2'], 100)  // Robotic Arms A
  meterPowerValues.value['sm-a-3'] = fluctuatePower(meterPowerValues.value['sm-a-3'], 50)   // Large Welder
  meterPowerValues.value['sm-a-4'] = fluctuatePower(meterPowerValues.value['sm-a-4'], 25)   // Feeder Motor
  meterPowerValues.value['sm-a-5'] = fluctuatePower(meterPowerValues.value['sm-a-5'], 30)   // Control + Utilities A

  // Workshop B equipment (near max ratings)
  meterPowerValues.value['sm-b-0'] = fluctuatePower(meterPowerValues.value['sm-b-0'], 100)  // Chassis Mounting
  meterPowerValues.value['sm-b-1'] = fluctuatePower(meterPowerValues.value['sm-b-1'], 80)   // Robotic Arms B
  meterPowerValues.value['sm-b-2'] = fluctuatePower(meterPowerValues.value['sm-b-2'], 25)   // Wiring Benches
  meterPowerValues.value['sm-b-3'] = fluctuatePower(meterPowerValues.value['sm-b-3'], 25)   // Control + Utilities B

  // Solar PV (larger fluctuations but still reasonable)
  const pvVariation = 1 + (Math.random() - 0.5) * 0.1 // +/- 5%
  meterPowerValues.value['sm-b-4'] = Math.max(0, Math.min(150, meterPowerValues.value['sm-b-4'] * pvVariation))
}

// --- Gas and Fuel Animation Functions ---
// Helper function for small, realistic fluctuations
function fluctuateGasFuelValue(currentValue, minValue, maxValue, variation = 0.05) {
  // Small fluctuations +/- 5% around current value
  const variationFactor = 1 + (Math.random() - 0.5) * variation
  const newValue = currentValue * variationFactor
  return Math.max(minValue, Math.min(maxValue, newValue))
}

// Animate gas and fuel meter values with realistic fluctuations
const animateGasFuelValues = () => {
  // Gas Meter 0 (gm-0) - flow in m³/s
  gasMeterData.value['gm-0'].temperature = fluctuateGasFuelValue(
    gasMeterData.value['gm-0'].temperature, 18, 28, 0.02
  ) // ±2% variation, 18-28°C
  
  gasMeterData.value['gm-0'].pressure = fluctuateGasFuelValue(
    gasMeterData.value['gm-0'].pressure, 0.2, 0.4, 0.03
  ) // ±3% variation, 0.2-0.4 bar
  
  gasMeterData.value['gm-0'].flow = fluctuateGasFuelValue(
    gasMeterData.value['gm-0'].flow, 0.012, 0.021, 0.04
  ) // ±4% variation, 0.012-0.021 m³/s (converted from kg/s using 0.717 kg/m³ density)

  // Gas Meter 1 (gm-1) - flow in m³/s
  gasMeterData.value['gm-1'].temperature = fluctuateGasFuelValue(
    gasMeterData.value['gm-1'].temperature, 18, 28, 0.02
  ) // ±2% variation, 18-28°C
  
  gasMeterData.value['gm-1'].pressure = fluctuateGasFuelValue(
    gasMeterData.value['gm-1'].pressure, 0.2, 0.4, 0.03
  ) // ±3% variation, 0.2-0.4 bar
  
  gasMeterData.value['gm-1'].flow = fluctuateGasFuelValue(
    gasMeterData.value['gm-1'].flow, 0.011, 0.017, 0.04
  ) // ±4% variation, 0.011-0.017 m³/s (converted from kg/s using 0.717 kg/m³ density)

  // Fuel Meter (fm-0) - flow in kg/s
  fuelMeterData.value['fm-0'].temperature = fluctuateGasFuelValue(
    fuelMeterData.value['fm-0'].temperature, 32, 40, 0.03
  ) // ±3% variation, 32-40°C (preheated)
  
  fuelMeterData.value['fm-0'].pressure = fluctuateGasFuelValue(
    fuelMeterData.value['fm-0'].pressure, 1.5, 2.5, 0.05
  ) // ±5% variation, 1.5-2.5 bar (realistic boiler pressure)
  
  fuelMeterData.value['fm-0'].flow = fluctuateGasFuelValue(
    fuelMeterData.value['fm-0'].flow, 0.085, 0.425, 0.03
  ) // ±3% variation, 0.085-0.425 kg/s (converted from L/s using 0.85 kg/L density)
}

// Computed properties for formatted gas/fuel display
const gasMeterDisplay = computed(() => {
  const display = {}
  for (const [id, data] of Object.entries(gasMeterData.value)) {
    display[`${id}-tmp`] = `${data.temperature.toFixed(1)} °C`
    display[`${id}-bar`] = `${data.pressure.toFixed(2)} bar`
    display[`${id}-flow`] = `${data.flow.toFixed(4)} m³/s` // 4 decimal places for m³/s
    display[`${id}-state`] = data.state
  }
  return display
})

const fuelMeterDisplay = computed(() => {
  const display = {}
  for (const [id, data] of Object.entries(fuelMeterData.value)) {
    display[`${id}-tmp`] = `${data.temperature.toFixed(1)} °C`
    display[`${id}-bar`] = `${data.pressure.toFixed(2)} bar`
    display[`${id}-flow`] = `${data.flow.toFixed(1)} kg/s`
    display[`${id}-state`] = data.state
  }
  return display
})

const meterPowerDisplay = computed(() => {
  const display = {}
  for (const [id, value] of Object.entries(meterPowerValues.value)) {
    display[id] = `${value.toFixed(1)} kW`
  }
  return display
})

// --- Watchers for dynamic updates ---
watch(edgeStates, (newStates) => {
  newStates.forEach((isOffline, index) => {
    const isOnline = !isOffline
    updateSvgElement(`edge-${index}-state`, isOnline, false) // false for isStateElement flag for edges
  })
}, { deep: true })

watch(meterStates, (newStates) => {
  Object.entries(newStates).forEach(([id, isDisconnected]) => {
    updateSvgElement(`${id}-state`, isDisconnected, true, true) // true for isStateElement and isMeter
  })
}, { deep: true })

watch(meterPowerDisplay, (newPowers) => {
  Object.entries(newPowers).forEach(([id, powerText]) => {
    updateSvgElement(`${id}-pwr`, powerText, false, true) // false for isStateElement, true for isMeter
  })
}, { deep: true })

// Gas meter watchers
watch(gasMeterDisplay, (newData) => {
  Object.entries(newData).forEach(([id, value]) => {
    if (id.includes('-state')) {
      updateSvgElement(id, value, true, true, true) // state element
    } else {
      updateSvgElement(id, value, false, false, true) // data element
    }
  })
}, { deep: true })

// Fuel meter watchers
watch(fuelMeterDisplay, (newData) => {
  Object.entries(newData).forEach(([id, value]) => {
    if (id.includes('-state')) {
      updateSvgElement(id, value, true, true, true) // state element
    } else {
      updateSvgElement(id, value, false, false, true) // data element
    }
  })
}, { deep: true })

// --- Counter Animation ---
const startAnimation = () => {
  if (animationId) {
    clearInterval(animationId)
  }
  animationId = setInterval(() => {
    counter.value++
  }, 1000)
}

// --- Power Animation ---
const startPowerAnimation = () => {
  if (powerAnimationId) {
    clearInterval(powerAnimationId)
  }
  powerAnimationId = setInterval(() => {
    animatePowerValues()
  }, 2000) // Update every 2 seconds
}

// --- Gas and Fuel Animation ---
const startGasFuelAnimation = () => {
  if (gasFuelAnimationId) {
    clearInterval(gasFuelAnimationId)
  }
  gasFuelAnimationId = setInterval(() => {
    animateGasFuelValues()
  }, 1000) // Update every second
}

const stopAnimation = () => {
  if (animationId) {
    clearInterval(animationId)
    animationId = null
  }
  if (powerAnimationId) {
    clearInterval(powerAnimationId)
    powerAnimationId = null
  }
  if (gasFuelAnimationId) {
    clearInterval(gasFuelAnimationId)
    gasFuelAnimationId = null
  }
}

// --- Center and Fit Diagram ---
const centerAndFitDiagram = () => {
  nextTick(() => {
    if (!container.value || !svgContainer.value) return
    
    const svgElement = svgContainer.value.querySelector('svg')
    if (!svgElement) return
    
    // Wait for SVG to be fully rendered
    setTimeout(() => {
      const containerRect = container.value.getBoundingClientRect()
      const containerWidth = containerRect.width
      const containerHeight = containerRect.height
      
      // Get the SVG's natural dimensions
      const svgRect = svgElement.getBBox ? svgElement.getBBox() : svgElement.getBoundingClientRect()
      const svgWidth = svgRect.width
      const svgHeight = svgRect.height
      
      if (svgWidth > 0 && svgHeight > 0) {
        // Calculate zoom to fit with padding
        const scaleX = containerWidth / svgWidth
        const scaleY = containerHeight / svgHeight
        const newZoom = Math.min(scaleX, scaleY) * 0.8 // 80% to add padding
        
        // Center the diagram
        const scaledWidth = svgWidth * newZoom
        const scaledHeight = svgHeight * newZoom
        const centeredX = (containerWidth - scaledWidth) / 2
        const centeredY = (containerHeight - scaledHeight) / 2
        
        zoom.value = newZoom
        position.value = { x: centeredX, y: centeredY }
      }
    }, 50)
  })
}

// --- Lifecycle ---
onMounted(() => {
  startAnimation()
  startPowerAnimation()
  startGasFuelAnimation()
  
  // Center and fit diagram after SVG is rendered
  setTimeout(() => {
    centerAndFitDiagram()
  }, 200)
  
  // Initial updates for all elements
  updateTextPlaceholder()
  
  edgeStates.value.forEach((isOffline, index) => {
    const isOnline = !isOffline
    updateSvgElement(`edge-${index}-state`, isOnline, false)
  })
  
  Object.entries(meterStates.value).forEach(([id, isDisconnected]) => {
    updateSvgElement(`${id}-state`, isDisconnected, true, true)
  })
  
  Object.entries(meterPowerDisplay.value).forEach(([id, powerText]) => {
    updateSvgElement(`${id}-pwr`, powerText, false, true)
  })
  
  // Initial gas meter updates
  Object.entries(gasMeterDisplay.value).forEach(([id, value]) => {
    if (id.includes('-state')) {
      updateSvgElement(id, value, true, true, true)
    } else {
      updateSvgElement(id, value, false, false, true)
    }
  })
  
  // Initial fuel meter updates
  Object.entries(fuelMeterDisplay.value).forEach(([id, value]) => {
    if (id.includes('-state')) {
      updateSvgElement(id, value, true, true, true)
    } else {
      updateSvgElement(id, value, false, false, true)
    }
  })
})

onUnmounted(() => {
  stopAnimation()
})

// Update if SVG content changes
watch(processedSvg, () => {
  nextTick(() => {
    updateTextPlaceholder()
    
    edgeStates.value.forEach((isOffline, index) => {
      const isOnline = !isOffline
      updateSvgElement(`edge-${index}-state`, isOnline, false)
    })
    
    Object.entries(meterStates.value).forEach(([id, isDisconnected]) => {
      updateSvgElement(`${id}-state`, isDisconnected, true, true)
    })
    
    Object.entries(meterPowerDisplay.value).forEach(([id, powerText]) => {
      updateSvgElement(`${id}-pwr`, powerText, false, true)
    })
    
    // Re-center after SVG update
    setTimeout(() => {
      centerAndFitDiagram()
    }, 100)
  })
})
</script>

<style scoped>
/* The dotted background is handled via the computed style binding */
</style>