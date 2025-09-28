<!-- src/components/RangeToggleBarPrime.vue -->
<template>
    <div class="w-full flex items-center justify-end py-2">
      <div class="range-toggle-container">
        <div class="range-toggle-wrapper">
          <input
            v-for="option in options"
            :key="option.value"
            :id="`toggle-${option.value}`"
            v-model="internalValue"
            :value="option.value"
            type="radio"
            :name="`range-toggle-${componentId}`"
            class="range-toggle-input"
          />
          <label
            v-for="option in options"
            :key="`label-${option.value}`"
            :for="`toggle-${option.value}`"
            class="range-toggle-label"
            :class="{
              'active': internalValue === option.value,
              'first': option.value === options[0].value,
              'last': option.value === options[options.length - 1].value
            }"
          >
            {{ option.label }}
          </label>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed, ref } from 'vue'
  
  const props = defineProps({
    modelValue: {
      type: String,
      default: 'day',
      validator: v => ['day', 'week', 'month'].includes(v),
    },
  })
  
  const emit = defineEmits(['update:modelValue', 'change'])
  
  const options = [
    { label: 'Day', value: 'day' },
    { label: 'Week', value: 'week' },
    { label: 'Month', value: 'month' },
  ]
  
  // Generate unique component ID for radio group
  const componentId = ref(Math.random().toString(36).substr(2, 9))
  
  const internalValue = computed({
    get: () => props.modelValue,
    set: v => {
      emit('update:modelValue', v)
      emit('change', v)
    }
  })
  </script>
  
  <style scoped>
  .range-toggle-container {
    display: inline-block;
  }
  
  .range-toggle-wrapper {
    position: relative;
    display: inline-flex;
    background: #f1f5f9;
    border-radius: 10px;
    padding: 4px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  /* Dark mode styles */
  @media (prefers-color-scheme: dark) {
    .range-toggle-wrapper {
      background: #1e293b;
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
    }
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
    min-width: 80px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    color: #64748b;
    background: transparent;
    border-radius: 7px;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    user-select: none;
    white-space: nowrap;
    z-index: 1;
  }
  
  /* Dark mode label styles */
  @media (prefers-color-scheme: dark) {
    .range-toggle-label {
      color: #94a3b8;
    }
  }
  
  .range-toggle-label:hover {
    color: #475569;
  }
  
  /* Dark mode hover styles */
  @media (prefers-color-scheme: dark) {
    .range-toggle-label:hover {
      color: #cbd5e1;
    }
  }
  
  .range-toggle-label.active {
    color: #1e293b;
    background: #ffffff;
    font-weight: 600;
    box-shadow: 
      0 1px 3px rgba(0, 0, 0, 0.12),
      0 1px 2px rgba(0, 0, 0, 0.08);
    transform: translateY(-1px);
  }
  
  /* Dark mode active styles */
  @media (prefers-color-scheme: dark) {
    .range-toggle-label.active {
      color: #f8fafc;
      background: #334155;
      box-shadow: 
        0 1px 3px rgba(0, 0, 0, 0.2),
        0 1px 2px rgba(0, 0, 0, 0.15),
        inset 0 0 0 1px rgba(148, 163, 184, 0.1);
    }
  }
  
  /* Focus styles for accessibility */
  .range-toggle-input:focus + .range-toggle-label {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }
  
  /* Smooth transition when switching between options */
  .range-toggle-label.active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  /* Subtle hover effect for inactive labels */
  .range-toggle-label:not(.active):hover {
    background: rgba(255, 255, 255, 0.5);
    transform: translateY(-0.5px);
  }
  
  /* Responsive adjustments */
  @media (max-width: 640px) {
    .range-toggle-label {
      min-width: 70px;
      padding: 6px 12px;
      font-size: 13px;
    }
  }
  </style>