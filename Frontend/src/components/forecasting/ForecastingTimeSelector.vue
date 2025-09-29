<template>
  <div class="flex items-center justify-between  rounded-lg ">
    <!-- Navigation Controls (moved to left) -->
    <div class="flex items-center space-x-2">
      <button
        @click="navigateBack"
        class="nav-button"
        :disabled="isNavigating"
      >
        <i class="bi bi-chevron-left"></i>
      </button>
      
      <div class="period-display">
        <span class="text-white font-semibold">{{ currentDateLabel }}</span>
      </div>
      
      <button
        @click="navigateForward"
        class="nav-button"
        :disabled="isNavigating"
      >
        <i class="bi bi-chevron-right"></i>
      </button>
    </div>

    <!-- Time Range Selector (moved to right) -->
    <div class="range-toggle-container">
      <div class="range-toggle-wrapper">
        <input
          v-for="option in timeRangeOptions"
          :key="option.value"
          :id="`toggle-${option.value}`"
          v-model="internalTimeRange"
          :value="option.value"
          type="radio"
          :name="`time-range-${componentId}`"
          class="range-toggle-input"
        />
        <label
          v-for="option in timeRangeOptions"
          :key="`label-${option.value}`"
          :for="`toggle-${option.value}`"
          class="range-toggle-label"
          :class="{
            'active': internalTimeRange === option.value,
            'first': option.value === timeRangeOptions[0].value,
            'last': option.value === timeRangeOptions[timeRangeOptions.length - 1].value
          }"
        >
          {{ option.label }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'day',
    validator: v => ['day', 'week', 'month'].includes(v),
  },
  currentOffset: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue', 'offset-change'])

const timeRangeOptions = [
  { label: 'Day', value: 'day' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
]

const componentId = ref(Math.random().toString(36).substr(2, 9))
const isNavigating = ref(false)

const internalTimeRange = computed({
  get: () => props.modelValue,
  set: v => {
    emit('update:modelValue', v)
  }
})

const currentDateLabel = computed(() => {
  const offset = props.currentOffset
  const range = props.modelValue
  const now = new Date()
  
  let startDate, endDate
  
  switch (range) {
    case 'day':
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + offset)
      endDate = new Date(startDate)
      endDate.setDate(endDate.getDate() + 1)
      break
    case 'week':
      const startOfWeek = new Date(now)
      startOfWeek.setDate(now.getDate() - now.getDay() + 1 + (offset * 7)) // Monday
      startDate = new Date(startOfWeek.getFullYear(), startOfWeek.getMonth(), startOfWeek.getDate())
      endDate = new Date(startDate)
      endDate.setDate(endDate.getDate() + 7)
      break
    case 'month':
      startDate = new Date(now.getFullYear(), now.getMonth() + offset, 1)
      endDate = new Date(now.getFullYear(), now.getMonth() + offset + 1, 1)
      break
    default:
      startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + offset)
      endDate = new Date(startDate)
      endDate.setDate(endDate.getDate() + 1)
  }
  
  if (range === 'day') {
    return startDate.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    })
  } else if (range === 'week') {
    return `${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
  } else {
    return startDate.toLocaleDateString('en-US', { 
      month: 'long', 
      year: 'numeric' 
    })
  }
})

const navigateBack = () => {
  if (isNavigating.value) return
  
  isNavigating.value = true
  const newOffset = props.currentOffset - 1
  emit('offset-change', newOffset)
  
  setTimeout(() => {
    isNavigating.value = false
  }, 200)
}

const navigateForward = () => {
  if (isNavigating.value) return
  
  isNavigating.value = true
  const newOffset = props.currentOffset + 1
  emit('offset-change', newOffset)
  
  setTimeout(() => {
    isNavigating.value = false
  }, 200)
}

// Reset offset when time range changes
watch(() => props.modelValue, () => {
  emit('offset-change', 0)
})
</script>

<style scoped>
.range-toggle-container {
  display: inline-block;
}

.range-toggle-wrapper {
  position: relative;
  display: inline-flex;
  background: #374151;
  border-radius: 8px;
  padding: 3px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
}

.range-toggle-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.range-toggle-label {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 70px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
  color: #9ca3af;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  white-space: nowrap;
  z-index: 1;
}

.range-toggle-label:hover {
  color: #d1d5db;
}

.range-toggle-label.active {
  color: #f8fafc;
  background: #4b5563;
  font-weight: 600;
  box-shadow: 
    0 1px 3px rgba(0, 0, 0, 0.2),
    0 1px 2px rgba(0, 0, 0, 0.15),
    inset 0 0 0 1px rgba(148, 163, 184, 0.1);
  transform: translateY(-1px);
}

.range-toggle-label.active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.range-toggle-label:not(.active):hover {
  background: rgba(75, 85, 99, 0.3);
  transform: translateY(-0.5px);
}

.nav-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #4b5563;
  border: 1px solid #6b7280;
  border-radius: 6px;
  color: #d1d5db;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 16px;
}

.nav-button:hover:not(:disabled) {
  background: #6b7280;
  border-color: #9ca3af;
  color: #ffffff;
  transform: translateY(-1px);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.period-display {
  min-width: 120px;
  text-align: center;
  padding: 8px 16px;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
}

@media (max-width: 640px) {
  .range-toggle-label {
    min-width: 60px;
    padding: 4px 8px;
    font-size: 12px;
  }
  
  .nav-button {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
  
  .period-display {
    min-width: 100px;
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>
