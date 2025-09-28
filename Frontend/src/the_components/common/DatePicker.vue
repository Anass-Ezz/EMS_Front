<template>
  <!-- Compact view -->
  <div class="range-box">
    <span class="range-text">
      {{ displayText }}
    </span>

    <Button
      label="Pick Date"
      icon="pi pi-calendar"
      size="small"
      @click="op.toggle($event)"
      class="pick-btn"
    />
  </div>

  <!-- Floating panel -->
  <OverlayPanel ref="op" :breakpoints="{ '960px':'90vw' }">
    <!-- Top row: Preset selector + Resolution -->
    <div class="top-controls">
      <!-- Preset selector -->
      <div class="preset-selector">
        <label class="panel-label">Time Range</label>
        <Dropdown
          v-model="selectedPreset"
          :options="presetOptions"
          optionLabel="label"
          class="w-full"
        />
      </div>
      
      <!-- Resolution selector -->
      <div class="resolution-selector">
        <label class="panel-label">Resolution</label>
        <div class="flex gap-2">
          <InputNumber 
            v-model="resolutionDraft.value" 
            :min="1" 
            :max="100"
            class="res-input"
          />
          <Dropdown 
            v-model="resolutionDraft.unit" 
            :options="resolutionOptions" 
            class="res-dropdown"
          />
        </div>
      </div>
    </div>

    <!-- Preview of selected time range -->
    <div class="preview mt-4">
      <span class="preview-label">Preview:</span>
      <span class="preview-dates">
        {{ previewStart }} — {{ previewEnd }}
      </span>
    </div>

    <!-- Date pickers (shown only when custom is selected) -->
    <div v-if="selectedPreset.value === 'custom'" class="custom-picker mt-4">
      <div class="grid grid-cols-2 gap-4">
        <!-- Start -->
        <div>
          <label class="panel-label">Start</label>
          <Calendar
            v-model="draftStart"
            :inline="true"
            showTime
            hourFormat="24"
            :manualInput="false"
            class="pv-dark"
          />
        </div>

        <!-- Stop -->
        <div>
          <label class="panel-label">Stop</label>
          <Calendar
            v-model="draftStop"
            :inline="true"
            showTime
            hourFormat="24"
            :manualInput="false"
            :minDate="minStopDate"
            class="pv-dark"
          />
        </div>
      </div>
    </div>

    <div class="flex justify-center mt-4">
      <Button
        :label="selectedPreset.value === 'custom' ? 'APPLY TIME RANGE' : 'APPLY'"
        class="apply-btn"
        @click="apply"
      />
    </div>
  </OverlayPanel>
</template>

<script setup>
import { ref, watch, computed, inject } from 'vue'
import Calendar from 'primevue/calendar'
import OverlayPanel from 'primevue/overlaypanel'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'

// Inject global state
const dateRangeContext = inject('dateRange')
const resolutionContext = inject('resolution')

// LocalStorage keys
const STORAGE_KEYS = {
  PRESET: 'dateRangePicker_preset',
  RESOLUTION: 'dateRangePicker_resolution',
  CUSTOM_DATES: 'dateRangePicker_customDates'
}

// Load from localStorage with defaults
const loadFromStorage = (key, defaultValue) => {
  try {
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : defaultValue
  } catch {
    return defaultValue
  }
}

// Save to localStorage
const saveToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // Storage not available, continue without saving
  }
}

// Preset duration mapping for optimization
const PRESET_DURATIONS = {
  'now': 0, // New "Now" preset
  '24h': 24 * 60 * 60 * 1000,
  '2d': 2 * 24 * 60 * 60 * 1000,
  '7d': 7 * 24 * 60 * 60 * 1000,
  '30d': 30 * 24 * 60 * 60 * 1000
}

// FIXED: Proper preset calculation with correct start/end times
const calculatePresetRange = (preset) => {
  const now = new Date()
  const end = new Date(now) // End is current time
  
  // Handle "Now" preset - both dates set to current time
  if (preset === 'now') {
    return [now, now]
  }
  
  // Calculate start time by subtracting duration from current time
  const duration = PRESET_DURATIONS[preset]
  if (!duration) {
    return [new Date(), new Date()]
  }
  
  const start = new Date(now.getTime() - duration)
  return [start, end]
}

// Initialize with defaults: "Now" preset and Hours resolution
const defaultPreset = { label: 'Now', value: 'now' } // Changed to "Now"
const defaultResolution = { value: 1, unit: 'Hours' }

// Load saved values or use defaults
const savedPreset = loadFromStorage(STORAGE_KEYS.PRESET, defaultPreset)
const savedResolution = loadFromStorage(STORAGE_KEYS.RESOLUTION, defaultResolution)
const savedCustomDates = loadFromStorage(STORAGE_KEYS.CUSTOM_DATES, null)

// Refs and state
const op = ref(null)
const selectedPreset = ref(savedPreset)

// Initialize resolution with saved/default values
const resolutionDraft = ref({
  value: savedResolution.value,
  unit: savedResolution.unit
})

// Initialize dates - use saved custom dates if preset is custom, otherwise calculate from preset
let initialStart, initialEnd
if (savedPreset.value === 'custom' && savedCustomDates) {
  initialStart = new Date(savedCustomDates.start)
  initialEnd = new Date(savedCustomDates.end)
} else {
  [initialStart, initialEnd] = calculatePresetRange(savedPreset.value)
}

const draftStart = ref(initialStart || new Date())
const draftStop = ref(initialEnd || new Date())

const presetOptions = [
  { label: 'Now', value: 'now' }, // Added "Now" preset at the top
  { label: 'Last 24 hours', value: '24h' },
  { label: 'Last 2 days', value: '2d' },
  { label: 'Last 7 days', value: '7d' },
  { label: 'Last 30 days', value: '30d' },
  { label: 'Custom', value: 'custom' }
]

// Resolution options
const resolutionOptions = [
  'Seconds', 'Minutes', 'Hours', 'Days', 'Weeks', 'Months', 'Years'
]

// Preview of the selected time range
const previewRange = computed(() => {
  if (selectedPreset.value.value === 'custom') {
    return [draftStart.value, draftStop.value]
  }
  return calculatePresetRange(selectedPreset.value.value)
})

const previewStart = computed(() => formatDate(previewRange.value[0]))
const previewEnd = computed(() => formatDate(previewRange.value[1]))

// Apply the selected configuration
const apply = () => {
  let start, end
  
  // Use selectedPreset.value.value to get the preset key
  if (selectedPreset.value.value !== 'custom') {
    [start, end] = calculatePresetRange(selectedPreset.value.value)
    // Update draft values to match applied preset
    draftStart.value = start
    draftStop.value = end
  } else {
    start = draftStart.value
    end = draftStop.value
    // Save custom dates to localStorage
    saveToStorage(STORAGE_KEYS.CUSTOM_DATES, {
      start: start.toISOString(),
      end: end.toISOString()
    })
  }
  
  // Ensure dates are valid
  if (!(start instanceof Date)) start = new Date(start)
  if (!(end instanceof Date)) end = new Date(end)
  
  // Save current selections to localStorage
  saveToStorage(STORAGE_KEYS.PRESET, selectedPreset.value)
  saveToStorage(STORAGE_KEYS.RESOLUTION, {
    value: resolutionDraft.value.value,
    unit: resolutionDraft.value.unit
  })
  
  // Update global state
  dateRangeContext.update([start, end])
  resolutionContext.update({
    value: resolutionDraft.value.value,
    unit: resolutionDraft.value.unit
  })
  
  op.value?.hide()
}

// Optimized date formatting - cached formatter
const dateFormatter = new Intl.DateTimeFormat('en-GB', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: false
})

// Format dates for display
const formatDate = (d) => {
  if (!d) return '––'
  return dateFormatter.format(d).replace(',', '')
}

// Display text in compact view
const displayText = computed(() => {
  const [start, end] = dateRangeContext.value.value
  if (!start || !end) return 'Select time range'
  
  const res = resolutionContext.value.value
  const resText = `${res.value} ${res.unit}`
  
  // Show preset name for non-custom selections
  if (selectedPreset.value.value !== 'custom') {
    return `${selectedPreset.value.label} | Resolution: ${resText}`
  }
  
  // Show actual dates only for custom selection
  const startText = formatDate(start)
  const endText = formatDate(end)
  return `${startText} — ${endText} | Resolution: ${resText}`
})

// Watch for preset changes and save to localStorage
watch(selectedPreset, (newPreset) => {
  saveToStorage(STORAGE_KEYS.PRESET, newPreset)
}, { deep: true })

// Watch for resolution changes and save to localStorage
watch(resolutionDraft, (newResolution) => {
  saveToStorage(STORAGE_KEYS.RESOLUTION, newResolution)
}, { deep: true })

// Sync with external changes
watch(() => dateRangeContext.value.value, (newRange) => {
  if (newRange[0]) draftStart.value = newRange[0]
  if (newRange[1]) draftStop.value = newRange[1]
})

watch(() => resolutionContext.value.value, (newRes) => {
  resolutionDraft.value = { ...newRes }
})

// Prevent stop < start
const minStopDate = computed(() => 
  draftStart.value ? new Date(draftStart.value) : null
)

// Initialize the global state with saved/default values on component mount
dateRangeContext.update([draftStart.value, draftStop.value])
resolutionContext.update({
  value: resolutionDraft.value.value,
  unit: resolutionDraft.value.unit
})
</script>

<style scoped>
/* Compact view */
.range-box {
  display: flex;
  align-items: center;
  gap: .75rem;
  background: #0f172a;
  border: 1px solid #0ea5e9;
  border-radius: 6px;
  padding: .5rem 1rem;
  width: max-content;
}

.range-text {
  color: #e2e8f0;
  white-space: nowrap;
  font-family: monospace;
  font-size: 0.9em;
}

.pick-btn {
  flex-shrink: 0;
}

/* Top controls row */
.top-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.preset-selector,
.resolution-selector {
  width: 100%;
}

/* Panel labels */
.panel-label {
  display: block;
  font-size: .75rem;
  color: #cbd5e1;
  margin-bottom: .25rem;
}

/* Calendar styling */
.pv-dark {
  --surface-a: #111827;
  --surface-b: #1e293b;
  --text-color: #e2e8f0;
  --text-color-secondary: #94a3b8;
  --highlight-bg: #3b82f6;
  --highlight-text-color: #fff;
  border: 1px solid #0ea5e9;
  border-radius: 6px;
}

/* Apply button */
.apply-btn {
  background: linear-gradient(90deg, #35a5ff, #7a6bff);
  border: none;
  color: #fff;
  padding-inline: 2rem;
  width: 100%;
}

/* Resolution controls */
.resolution-selector .flex {
  align-items: center;
}

.res-input {
  width: 80px;
}

.res-dropdown {
  flex: 1;
}

/* Custom picker */
.custom-picker {
  border-top: 1px solid #334155;
  padding-top: 1rem;
}

/* Preview section */
.preview {
  background: #1e293b;
  border-radius: 6px;
  padding: 0.75rem;
  margin-top: 1rem;
  font-family: monospace;
  font-size: 0.9em;
}

.preview-label {
  color: #94a3b8;
  margin-right: 0.5rem;
}

.preview-dates {
  color: #e2e8f0;
}
</style>