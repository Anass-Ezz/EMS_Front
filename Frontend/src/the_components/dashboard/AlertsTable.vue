<template>
  <Card class="h-fit flex flex-col border-4 rounded-lg" :class="getContainerBorderClass()">

    <template #title>
      <div class="flex items-center justify-between mb-3 px-4 flex-shrink-0">
        <!-- Overall system state with back button when in detail view -->
        <div class="flex flex-row items-center gap-4">
          <!-- Back button (only show in detail view) -->
          <button 
            v-if="currentView === 'detail'"
            @click="goBackToEdgeList"
            class="px-4 rounded-full bg-gray-700 hover:bg-gray-600 transition-colors text-gray-300 hover:text-white"
            title="Back to Edge List"
          >
            <i class="pi pi-arrow-left text-lg"></i>
          </button>
          
          <p class="text-xl font-bold text-gray-100 m-0">
            {{ currentView === 'list' ? 'System States and Alerts' : `${selectedEdgeId}` }}
          </p>
          <span class="px-3 py-1 rounded-full text-sm font-medium" :class="getStateBadgeClass(getOverallState())">
            <i :class="getStateIcon(getOverallState())" class="text-m"></i>
            {{ getStateText(getOverallState()) }}
          </span>
        </div>
      </div>
    </template>

    <template #content>
      <!-- Loading state -->
      <div v-if="loading" class="flex items-center justify-center flex-1">
        <ProgressSpinner />
      </div>

      <!-- Edge List View -->
      <div v-else-if="currentView === 'list'" class="flex-1 h-[365px] overflow-y-auto">
        <div class="divide-y divide-gray-700">
          <div
            v-for="edge in sortedEdges"
            :key="edge.id"
            class="transition-colors"
          >
            <!-- Edge row -->
            <div
              class="flex items-center justify-between py-2 px-4 min-h-[48px] transition-colors"
              :class="{
                'cursor-pointer hover:bg-gray-700': edge.isOnline,
                'cursor-not-allowed text-gray-500 bg-gray-900': !edge.isOnline // Faded style for offline
              }"
              @click="edge.isOnline ? selectEdge(edge.id) : null"
            >
              <div class="flex flex-col flex-1 space-y-1">
                <!-- Edge ID -->
                <span
                  class="font-medium truncate"
                  :class="edge.isOnline ? getComponentNameClass(edgeStates[edge.id] || 0) : 'text-gray-500'"
                >
                  {{ edge.id }}
                </span>
                <!-- Edge description if available -->
                <span v-if="edge.description" class="text-xs truncate" :class="edge.isOnline ? 'text-gray-400' : 'text-gray-600'">
                  {{ edge.description }}
                </span>
              </div>

              <div class="flex items-center space-x-3 flex-shrink-0">
                <!-- State badge -->
                <span
                  class="px-2 py-1 rounded text-xs font-medium"
                  :class="edge.isOnline ? getStateBadgeClass(edgeStates[edge.id] || 0) : 'bg-gray-600 text-gray-300'"
                >
                  {{ edge.isOnline ? getStateText(edgeStates[edge.id] || 0) : 'Offline' }}
                </span>
                <!-- Arrow icon -->
                <i
                  class="pi pi-chevron-right text-sm"
                  :class="edge.isOnline ? 'text-gray-400' : 'text-gray-600'"
                ></i>
              </div>
            </div>
          </div>

          <!-- No edges message -->
          <div v-if="edges.length === 0" class="text-center py-8 text-gray-400">
            No edges found
          </div>
        </div>
      </div>

      <!-- Component Detail View -->
      <div v-else-if="currentView === 'detail'" class="flex-1 h-[365px] overflow-y-auto">
        <div class="divide-y divide-gray-700">
          <div
            v-for="(component, name) in sortedComponents"
            :key="name"
            class="transition-colors"
          >
            <!-- Component header -->
            <div
              class="flex items-center justify-between py-2 px-4 transition-colors min-h-[48px]"
              :class="[ component.state > 0 ? 'cursor-pointer hover:bg-gray-700' : 'cursor-default hover:bg-gray-800' ]"
              @click="component.state > 0 ? toggleExpanded(name) : null"
            >
              <div class="flex flex-col flex-1 space-y-1">
                <!-- Human-readable name (from factory) -->
                <span
                  class="font-medium truncate"
                  :class="getComponentNameClass(component.state)"
                >
                  {{ factories[component.factoryId]?.name || component.alias || name }}
                </span>
                <!-- Original component key -->
                <span class="text-xs text-gray-400 truncate">
                  {{ name }}
                </span>
              </div>

              <div class="flex items-center space-x-3 flex-shrink-0">
                <!-- State badge -->
                <span
                  class="px-2 py-1 rounded text-xs font-medium"
                  :class="getStateBadgeClass(component.state)"
                >
                  {{ getStateText(component.state) }}
                </span>
                <!-- Expand arrow (only show if state > 0) -->
                <i
                  v-if="component.state > 0"
                  :class="component.expanded ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
                  class="text-gray-400 transition-transform text-sm"
                ></i>
              </div>
            </div>

            <!-- Expanded content: only last updated and state channels list -->
            <div
              v-if="component.expanded && component.state > 0"
              class="bg-gray-800 px-4 py-3 border-l-4"
              :class="getExpandedBorderClass(component.state)"
            >
              <div class="text-sm text-gray-300">
                <!-- Last update date -->
                <div class="mb-4">
                  <span class="font-medium text-gray-200">Last Updated:</span>
                  <span class="ml-2">{{ components[name].lastUpdated || 'N/A' }}</span>
                </div>

                <!-- State channels table -->
                <div class="overflow-x-auto">
                  <table class="min-w-full text-left divide-y divide-gray-600 border-collapse text-base">
                    <tbody class="divide-y divide-gray-600">
                      <tr
                        v-for="ch in (stateChannels[name] || []).slice().sort((a, b) => levelToStateId(b.level) - levelToStateId(a.level))"
                        :key="ch.id"
                        class="hover:bg-gray-700"
                      >
                        <!-- Channel text -->
                        <td class="px-2 py-2">
                          <span class="text-lg">{{ ch.text }}</span>
                        </td>
                        <!-- Channel level -->
                        <td class="px-2 py-2">
                          <span :class="getLevelTextClass(ch.level)" class="text-lg">
                            {{ ch.level }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- No components message -->
          <div v-if="Object.keys(components).length === 0" class="text-center py-8 text-gray-400">
            No components found
          </div>
        </div>
      </div>

    </template>

  </Card>
</template>

<script setup>
import ProgressSpinner from 'primevue/progressspinner'
import { computed, inject, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'

// Inject global state (only websocket and auth)
const ws = inject('ws')
const auth = inject('auth')

const toast = useToast()

// View management
const currentView = ref('list') // 'list' or 'detail'
const selectedEdgeId = ref(null)

// Edge list state
const edges = ref([]) // Now holds all edges, online and offline
const edgeStates = ref({})

// Component detail state
const loading = ref(true)
const components = reactive({})
const factories = reactive({})
const stateChannels = reactive({})
const channelRequestMap = reactive({})

// Request tracking
let edgeReqId = null
let configRequestId = null
let edgeStatesReqId = null
let componentStatesReqId = null // new request id for component state polling

// Polling intervals
let fetchEdgesInterval = null
let fetchEdgeStatesInterval = null
let fetchComponentStatesInterval = null // new interval for component states

// Computed properties
// Removed the 'onlineEdges' computed property as we're now displaying all.

const sortedEdges = computed(() => {
  // Sort edges: online first, then offline. Within each group, sort by ID.
  const edgesCopy = [...edges.value]; // Create a shallow copy to avoid mutating the original ref
  return edgesCopy.sort((a, b) => {
    // Online edges come before offline edges
    if (a.isOnline && !b.isOnline) return -1;
    if (!a.isOnline && b.isOnline) return 1;
    // If same online status, sort alphabetically by ID
    return a.id.localeCompare(b.id);
  });
});

const sortedComponents = computed(() => {
  const entries = Object.entries(components)
  let sumEntry
  const others = entries.filter(([n]) => {
    if (n === '_sum') { sumEntry = [n, components[n]]; return false }
    return true
  })
  others.sort(([, a], [, b]) => b.state - a.state)
  if (sumEntry) others.push(sumEntry)
  return others.reduce((acc, [n, c]) => ({ ...acc, [n]: c }), {})
})

// Utility functions
function waitForSocketOpen(ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// Edge list functionality
async function fetchEdges() {
  try {
    await waitForSocketOpen(ws)
    edgeReqId = crypto.randomUUID()
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: edgeReqId,
      method: 'getEdges',
      params: { limit: 50, page: 0, searchParams: {} }
    }))
  } catch (err) {
    console.error('Error sending getEdges request:', err)
    toast.add({ severity: 'error', summary: 'WebSocket error', detail: 'Failed to request edges.', life: 3000 })
  }
}

async function fetchEdgeStates() {
  // Only fetch states for currently online edges
  const onlineEdgeIds = edges.value.filter(e => e.isOnline).map(e => e.id)
  if (onlineEdgeIds.length === 0) return
  
  try {
    await waitForSocketOpen(ws)
    edgeStatesReqId = crypto.randomUUID()
    
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: edgeStatesReqId,
      method: 'getEdgesChannelsValues',
      params: {
        ids: onlineEdgeIds,
        channels: ['_sum/State']
      }
    }))
  } catch (err) {
    console.error('Error fetching edge states:', err)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to fetch edge states.', life: 3000 })
  }
}

// Component detail functionality
async function getEdgeConfig(edgeId) {
  await waitForSocketOpen(ws)
  const OUT = crypto.randomUUID(), INN = crypto.randomUUID()
  configRequestId = OUT
  ws.send(JSON.stringify({
    jsonrpc:'2.0', id:OUT, method:'edgeRpc', params:{
      edgeId: edgeId, payload:{
        jsonrpc:'2.0', id:INN, method:'getEdgeConfig', params:{}
      }
    }
  }))
}

// New polling-based component state fetch (replaces subscribeChannels)
async function fetchComponentStates() {
  if (!selectedEdgeId.value || Object.keys(components).length === 0) return
  try {
    await waitForSocketOpen(ws)
    componentStatesReqId = crypto.randomUUID()
    const componentChannels = Object.keys(components).map(n => `${n}/State`)
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: componentStatesReqId,
      method: 'getEdgesChannelsValues',
      params: {
        ids: [selectedEdgeId.value],
        channels: componentChannels
      }
    }))
  } catch (err) {
    console.error('Error fetching component states:', err)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to fetch component states.', life: 3000 })
  }
}

function fetchComponentChannels(name) {
  const OUT = crypto.randomUUID(), INN = crypto.randomUUID()
  channelRequestMap[OUT] = name
  ws.send(JSON.stringify({ 
    jsonrpc:'2.0', id:OUT, method:'edgeRpc', params:{
      edgeId: selectedEdgeId.value, payload:{ 
        jsonrpc:'2.0', id:crypto.randomUUID(), method:'componentJsonApi', params:{
          componentId:'_componentManager', payload:{ 
            jsonrpc:'2.0', method:'getStateChannelsOfComponent', params:{ componentId:name }, id:INN 
          }
        } 
      }
    }
  }))
}

// Navigation functions
function selectEdge(edgeId) {
  selectedEdgeId.value = edgeId
  currentView.value = 'detail'
  loading.value = true
  
  // Clear previous component data
  Object.keys(components).forEach(key => delete components[key])
  Object.keys(factories).forEach(key => delete factories[key])
  Object.keys(stateChannels).forEach(key => delete stateChannels[key])
  
  // Stop edge state polling
  if (fetchEdgeStatesInterval) {
    clearInterval(fetchEdgeStatesInterval)
    fetchEdgeStatesInterval = null
  }
  
  // Stop previous component state polling if any
  if (fetchComponentStatesInterval) {
    clearInterval(fetchComponentStatesInterval)
    fetchComponentStatesInterval = null
  }
  
  // Load edge config
  getEdgeConfig(edgeId)
}

function goBackToEdgeList() {
  currentView.value = 'list'
  selectedEdgeId.value = null
  
  // Clear component data
  Object.keys(components).forEach(key => delete components[key])
  Object.keys(factories).forEach(key => delete factories[key])
  Object.keys(stateChannels).forEach(key => delete stateChannels[key])
  
  // Stop component state polling
  if (fetchComponentStatesInterval) {
    clearInterval(fetchComponentStatesInterval)
    fetchComponentStatesInterval = null
  }
  
  // Restart edge state polling (only if there are online edges to monitor)
  if (auth.ready && edges.value.filter(e => e.isOnline).length > 0) { // Check for online edges
    fetchEdgeStates()
    fetchEdgeStatesInterval = setInterval(fetchEdgeStates, 2000)
  }
}

function toggleExpanded(n) {
  if (!components[n] || components[n].state <= 0) return
  components[n].expanded = !components[n].expanded
  if (components[n].expanded && !stateChannels[n]) fetchComponentChannels(n)
}

// Message handling
function handleMessage(evt) {
  const msg = JSON.parse(evt.data)
  
  // Handle edge list response
  if (msg.id === edgeReqId) {
    if (msg.error) {
      toast.add({ severity: 'error', summary: 'Edge fetch error', detail: msg.error.message, life: 4000 })
      return
    }
    if (msg.result) {
      edges.value = Array.isArray(msg.result) ? msg.result : msg.result.edges ?? []
      loading.value = false
      
      // Start fetching edge states after getting edges, only if in list view and there are online edges
      if (currentView.value === 'list' && edges.value.filter(e => e.isOnline).length > 0) {
        fetchEdgeStates()
        if (!fetchEdgeStatesInterval) {
          fetchEdgeStatesInterval = setInterval(fetchEdgeStates, 2000)
        }
      }
    }
    return
  }
  
  // Handle edge states response
  if (msg.id === edgeStatesReqId && msg.result) {
    // Clear existing edge states before updating to remove states for edges that went offline
    Object.keys(edgeStates.value).forEach(key => delete edgeStates.value[key]);
    
    Object.entries(msg.result).forEach(([edgeId, channels]) => {
      if (channels['_sum/State'] !== undefined) {
        edgeStates.value[edgeId] = channels['_sum/State']
      }
    })
    return
  }
  
  // Handle edge config response
  if (msg.id === configRequestId && msg.result) {
    const cfg = msg.result.payload.result
    Object.assign(factories, cfg.factories)
    Object.entries(cfg.components).forEach(([n, c]) => {
      components[n] = { alias:c.alias, factoryId:c.factoryId, state:0, expanded:false, lastUpdated:null }
    })
    
    // Start polling component states
    fetchComponentStates()
    fetchComponentStatesInterval = setInterval(fetchComponentStates, 2000)
    
    loading.value = false
    return
  }
  
  // Handle component channels response (for expanded view additional info)
  if (channelRequestMap[msg.id] && msg.result) {
    stateChannels[channelRequestMap[msg.id]] = msg.result.payload.result.channels
    delete channelRequestMap[msg.id]
    return
  }
  
  // Handle polled component states response
  if (msg.id === componentStatesReqId && msg.result) {
    const values = msg.result[selectedEdgeId.value] || {}
    Object.entries(values).forEach(([chan, val]) => {
      const componentName = chan.replace('/State','')
      if (components[componentName]) {
        components[componentName].state = val
        components[componentName].lastUpdated = new Date().toLocaleString()
      }
    })
    return
  }
}

// Helper functions
function getStateText(s){ return {0:'OK',1:'INFO',2:'WARNING',3:'FAULT'}[s]||'UNKNOWN' }
function getStateBadgeClass(s){ return {0:'bg-green-100 text-green-800 border-green-200',1:'bg-blue-100 text-blue-800 border-blue-200',2:'bg-yellow-100 text-yellow-800 border-yellow-200',3:'bg-red-100 text-red-800 border-red-200'}[s] }
function getComponentNameClass(s){ return {0:'text-green-400',1:'text-blue-400',2:'text-yellow-400',3:'text-red-400'}[s] }
function getContainerBorderClass(){ return {0:'border-green-500',1:'border-blue-500',2:'border-yellow-500',3:'border-red-500'}[getOverallState()] }
function getStateIcon(s){ return {0:'pi pi-check-circle text-green-500',1:'pi pi-info-circle text-blue-500',2:'pi pi-exclamation-triangle text-yellow-500',3:'pi pi-times-circle text-red-500'}[s] }
function getExpandedBorderClass(s){ return {0:'border-green-400',1:'border-blue-400',2:'border-yellow-400',3:'border-red-400'}[s] }
function levelToStateId(l){ return {INFO:1,WARNING:2,FAULT:3}[l]||0 }
function getLevelTextClass(level){ return {INFO:'text-blue-400',WARNING:'text-yellow-400',FAULT:'text-red-400'}[level]||'text-gray-300' }

function getOverallState() {
  if (currentView.value === 'detail') {
    return components['_sum']?.state || 0
  } else {
    // Return highest state among only online edges
    const onlineEdgeStates = Object.values(edgeStates.value)
    return onlineEdgeStates.length > 0 ? Math.max(...onlineEdgeStates) : 0
  }
}

async function initialize() {
  if (auth.ready) {
    await fetchEdges()
    // Start polling for edges
    fetchEdgesInterval = setInterval(fetchEdges, 5000) // Poll edges every 5 seconds
  }
}

onMounted(() => {
  if (!ws) {
    toast.add({ severity: 'error', summary: 'WebSocket missing', detail: 'No WebSocket instance provided.', life: 3000 })
    return
  }
  
  ws.addEventListener('message', handleMessage)
  initialize()
})

onUnmounted(() => {
  // Clean up all intervals
  if (fetchEdgesInterval) clearInterval(fetchEdgesInterval)
  if (fetchEdgeStatesInterval) clearInterval(fetchEdgeStatesInterval)
  if (fetchComponentStatesInterval) clearInterval(fetchComponentStatesInterval)
  
  // Remove WebSocket listener
  ws.removeEventListener('message', handleMessage)
})

watch(() => auth.ready, r => { if (r) initialize() })
</script>

<style scoped>
.overflow-y-auto::-webkit-scrollbar{width:6px}
.overflow-y-auto::-webkit-scrollbar-track{background:#374151;border-radius:3px}
.overflow-y-auto::-webkit-scrollbar-thumb{background:#6b7280;border-radius:3px}
.overflow-y-auto::-webkit-scrollbar-thumb:hover{background:#9ca3af}
</style>