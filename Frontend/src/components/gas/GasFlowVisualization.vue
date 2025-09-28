<template>
  <div class="h-full flex flex-col items-center justify-center">
    <!-- Gas Flow Animation -->
    <div class="relative w-32 h-32 mb-6">
      <!-- Flow direction indicator -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div 
          class="w-16 h-16 border-4 border-blue-500 rounded-full animate-pulse"
          :class="{ 'animate-spin': flow > 0.008 }"
        ></div>
      </div>
      
      <!-- Flow rate display -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="text-center">
          <div class="text-2xl font-bold text-blue-500">{{ flow.toFixed(4) }}</div>
          <div class="text-sm text-gray-400">kg/s</div>
        </div>
      </div>
    </div>

    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 gap-4 w-full">
      <!-- Temperature -->
      <div class="bg-gray-800 bg-opacity-30 rounded-lg p-4 border border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i class="bi bi-thermometer text-red-500 text-lg mr-2"></i>
            <span class="text-sm text-gray-400">Temperature</span>
          </div>
          <div class="text-right">
            <div class="text-lg font-bold text-red-500">{{ temperature.toFixed(1) }}°C</div>
          </div>
        </div>
      </div>

      <!-- Pressure -->
      <div class="bg-gray-800 bg-opacity-30 rounded-lg p-4 border border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i class="bi bi-speedometer2 text-green-500 text-lg mr-2"></i>
            <span class="text-sm text-gray-400">Pressure</span>
          </div>
          <div class="text-right">
            <div class="text-lg font-bold text-green-500">{{ pressure.toFixed(2) }} bar</div>
          </div>
        </div>
      </div>

      <!-- Flow Status -->
      <div class="bg-gray-800 bg-opacity-30 rounded-lg p-4 border border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <i class="bi bi-wind text-blue-500 text-lg mr-2"></i>
            <span class="text-sm text-gray-400">Flow Status</span>
          </div>
          <div class="text-right">
            <div 
              class="text-lg font-bold"
              :class="flow > 0.008 ? 'text-green-500' : 'text-yellow-500'"
            >
              {{ flow > 0.008 ? 'ACTIVE' : 'LOW' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  flow: {
    type: Number,
    required: true
  },
  temperature: {
    type: Number,
    required: true
  },
  pressure: {
    type: Number,
    required: true
  }
})
</script>

<style scoped>
/* Animation styles */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
