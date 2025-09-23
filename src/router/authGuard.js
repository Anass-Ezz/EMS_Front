// src/router/authGuard.js
export function createAuthGuard(router, auth) {
    router.beforeEach((to, from, next) => {
      // Public routes that never require authentication
      const publicRoutes = [
        '/auth/login',
        '/auth/access',
        '/auth/error',
        '/landing'
      ]
  
      // Always allow navigation to public routes
      if (publicRoutes.includes(to.path)) {
        return next()
      }
  
      /* ------------------------------------------------------------------
         NEW LOGIC:
         - We treat the user as "provisionally authenticated" if a token is
           present in storage, even if auth.ready is still false while the
           WebSocket is verifying it.
         - If the token later proves invalid, createWs.js will clear it and
           redirect the user to /auth/login.
      ------------------------------------------------------------------ */
      if (!auth.token) {
        return next({
          path: '/auth/login',
          query: { redirect: to.fullPath }   // Preserve destination
        })
      }
  
      // Token exists – allow navigation
      next()
    })
  }
  