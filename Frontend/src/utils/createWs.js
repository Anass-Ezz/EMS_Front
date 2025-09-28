// src/utils/createWs.js
// Helper to wire WebSocket + token verification so App.vue stays lean.

import { clearToken, getStoredToken } from '@/utils/auth'
import { useToast } from 'primevue/usetoast'
import { reactive } from 'vue'

/**
 * @param {import('vue-router').Router} router – Vue Router instance so we can redirect on expiry.
 * @returns {{ ws: WebSocket, auth: { ready: boolean, token: string|null } }}
 */
export function createWs(router) {
  const toast = useToast()

  /* ---------- shared auth state ---------- */
  const stored = getStoredToken()
  const auth = reactive({
    token: stored,
    ready: false               // becomes true only after socket & token verification
  })

  /* ---------- socket ---------- */
  const ws = new WebSocket('ws://localhost:8082')

  /* ---------- verify token on open ---------- */
  ws.onopen = () => {
    console.log('[createWs] WebSocket connected')

    // No token → unauthenticated area of app is allowed right away
    if (!auth.token) {
      auth.ready = true
      return
    }

    const VERIFY_ID = crypto.randomUUID()

    const handleVerify = event => {
      const msg = JSON.parse(event.data)
      if (msg.id !== VERIFY_ID) return
      ws.removeEventListener('message', handleVerify)

      if (msg.result) {
        console.log('[createWs] Token verified')
        auth.ready = true                 // ✅ ready only after success
      } else {
        console.log('[createWs] Token invalid – logging out')
        clearToken()
        auth.token = null
        auth.ready = false

        toast.add({
          severity: 'warn',
          summary:  'Session Expired',
          detail:   'Please log in again.',
          life:     3000
        })

        if (!router.currentRoute.value.path.startsWith('/auth')) {
          router.push({
            path:  '/auth/login',
            query: { redirect: router.currentRoute.value.fullPath }
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
    console.error('[createWs] WebSocket error', err)
    toast.add({
      severity: 'error',
      summary:  'WebSocket Error',
      detail:   'A connection error occurred. Please check your network.',
      life:     4000
    })
  }

  return { ws, auth }
}
