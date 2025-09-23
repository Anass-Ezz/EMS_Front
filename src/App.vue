<!-- <script setup>
import { provide, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { createAuthGuard } from '@/router/authGuard'
import { useToast } from 'primevue/usetoast'
import { CurrentDataManager } from '@/utils/currentDataManager'

/* ─────────────────────────── basic setup ─────────────────────────── */
const router = useRouter()
const ws     = new WebSocket('ws://localhost:8082')
const toast  = useToast()

/* ───────────────────── shared reactive state ─────────────────────── */
const dateRange  = ref([null, null])
const resolution = ref({ value: 1, unit: 'Hours' })

const auth = reactive({
  ready : false,
  token : null
})

/* ─────────────── instantiate CurrentDataManager ─────────────── */
const currentDataManager = new CurrentDataManager(ws, auth)

/* expose via provide() */
provide('dateRange', { value: dateRange,  update: r => (dateRange.value  = r) })
provide('resolution', { value: resolution, update: r => (resolution.value = r) })
provide('ws',   ws)
provide('auth', auth)
provide('currentDataManager', currentDataManager)

/* ─────── refresh button support ─────── */
const refreshContext = reactive({
  count: 0,
  triggerRefresh () { this.count++ }
})
provide('refresh', refreshContext)

/* ───────────── optimistic login from storage ───────────── */
const storedToken = localStorage.getItem('token') || sessionStorage.getItem('token')
if (storedToken) {
  auth.token = storedToken
  auth.ready = true
}

/* guard must come after auth is initialised */
createAuthGuard(router, auth)

/* ───────────────────── socket verification ───────────────────── */
ws.onopen = () => {
  console.log('[App] WebSocket connected')

  if (!auth.token) return

  const VERIFY_ID = crypto.randomUUID()

  const handleVerify = event => {
    const msg = JSON.parse(event.data)
    if (msg.id !== VERIFY_ID) return
    ws.removeEventListener('message', handleVerify)

    if (msg.result) {
      console.log('[App] Token verified by server')
    } else {
      console.log('[App] Token invalid – logging out')
      auth.ready = false
      localStorage.removeItem('token')
      sessionStorage.removeItem('token')

      toast.add({
        severity: 'warn',
        summary: 'Session Expired',
        detail: 'Please log in again.',
        life: 3000
      })

      if (!router.currentRoute.value.path.startsWith('/auth')) {
        router.push({
          path  : '/auth/login',
          query : { redirect: router.currentRoute.value.fullPath }
        })
      }
    }
  }

  ws.addEventListener('message', handleVerify)

  ws.send(JSON.stringify({
    jsonrpc : '2.0',
    id      : VERIFY_ID,
    method  : 'authenticateWithToken',
    params  : { token: auth.token }
  }))
}

ws.onerror = err => {
  console.error('[App] WebSocket error', err)
  toast.add({
    severity: 'error',
    summary: 'WebSocket Error',
    detail: 'A connection error occurred. Please check your network.',
    life: 4000
  })
}

/* ─────────────── dev/console helpers ─────────────── */
watch(dateRange, ([s, e]) => {
  console.log('Date Range Updated –', s?.toISOString() ?? null, '→', e?.toISOString() ?? null)
}, { deep: true })

watch(resolution, r => {
  console.log('Resolution Updated –', r.value, r.unit)
}, { deep: true })
</script>

<template>
  <router-view />
</template>

<style scoped></style> -->




























<script setup>
import { provide, ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { createAuthGuard } from '@/router/authGuard'
import { CurrentDataManager } from '@/utils/currentDataManager'

/* NEW → */
import { createWs } from '@/utils/createWs'        // ⬅️ 1

/* ───────────────────────── setup ───────────────────────── */
const router = useRouter()

/* NEW → build socket & auth in one line */
const { ws, auth } = createWs(router)             // ⬅️ 2

/* rest of the file keeps working exactly the same */
const dateRange  = ref([null, null])
const resolution = ref({ value: 1, unit: 'Hours' })

/* currentDataManager now receives ws & auth as before */
const currentDataManager = new CurrentDataManager(ws, auth)

/* provide injections */
provide('dateRange',   { value: dateRange,  update: r => (dateRange.value  = r) })
provide('resolution',  { value: resolution, update: r => (resolution.value = r) })
provide('ws',          ws)
provide('auth',        auth)
provide('currentDataManager', currentDataManager)

/* refresh context unchanged */
const refreshContext = reactive({
  count: 0,
  triggerRefresh () { this.count++ }
})
provide('refresh', refreshContext)

/* guard comes after auth is ready */
createAuthGuard(router, auth)

/* dev console helpers (unchanged) */
watch(dateRange,   ([s,e]) => console.log('Date Range →', s, e), { deep:true })
watch(resolution,  r      => console.log('Resolution →', r),    { deep:true })
</script>

<template>
  <router-view />
</template>
