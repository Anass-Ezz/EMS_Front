// composables/useWeekHeatmap.js
import { ref, computed } from 'vue'

export function useWeekHeatmap({ period, timeline, dailyDataMap, meterIds, meterNames, isEmissions = false, constants = null }) {
  // Group days into weeks
  const weeks = computed(() => {
    if (!period.value.from || !period.value.to || !timeline.value?.length) return []
    const days = Array.from(dailyDataMap.value.keys()).sort()
    const weeksList = []
    let currentWeek = []
    let weekStart = null

    for (const day of days) {
      const date = new Date(day)
      if (!weekStart) {
        weekStart = new Date(date)
        weekStart.setDate(weekStart.getDate() - weekStart.getDay()) // Start on Sunday
      }

      const diff = Math.floor((date - weekStart) / (1000 * 60 * 60 * 24))
      if (diff >= 7) {
        weeksList.push([...currentWeek])
        currentWeek = []
        weekStart.setDate(weekStart.getDate() + 7)
        // Re-check new week start
        while (new Date(day) - weekStart >= 7 * 24 * 60 * 60 * 1000) {
          weekStart.setDate(weekStart.getDate() + 7)
        }
      }
      currentWeek.push(day)
    }
    if (currentWeek.length) weeksList.push(currentWeek)
    return weeksList
  })

  const currentWeekIndex = ref(0)

  const visibleWeekDays = computed(() => {
    return weeks.value[currentWeekIndex.value] || []
  })

  const canSlide = computed(() => weeks.value.length > 1)

  const prevWeek = () => {
    if (currentWeekIndex.value > 0) currentWeekIndex.value--
  }

  const nextWeek = () => {
    if (currentWeekIndex.value < weeks.value.length - 1) currentWeekIndex.value++
  }

  const buildHeatmapOption = () => {
    const days = visibleWeekDays.value
    if (!days.length || !meterIds.length) {
      return { title: { text: 'No data', left: 'center', top: 'center', textStyle: { color: '#9ca3af' } } }
    }

    const heatMapData = []
    const values = []

    meterIds.forEach((meterId, meterIndex) => {
      days.forEach((day, dayIndex) => {
        const key = `${day}-${meterId}`
        const data = dailyDataMap.value.get(key)
        let value = 0
        if (data) {
          value = isEmissions
            ? (data.kW * data.dtHours * constants.CO2_FACTOR_ELEC_KG_PER_KWH) / 1000
            : data.totalConsumption || 0
        }
        heatMapData.push([meterIndex, dayIndex, value])
        values.push(value)
      })
    })

    const minVal = Math.min(...values)
    const maxVal = Math.max(...values)

    return {
      tooltip: {
        position: 'top',
        formatter: (params) => {
          const meterName = meterNames[params.data[0]]
          const day = days[params.data[1]]
          const val = params.data[2]
          const dateStr = new Date(day).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
          const unit = isEmissions ? 'tCO₂e' : 'kWh'
          return `${dateStr}<br/>${meterName}<br/>${isEmissions ? 'Emissions' : 'Consumption'}: ${val.toFixed(isEmissions ? 3 : 2)} ${unit}`
        }
      },
      grid: { height: '70%', top: '15%', left: '15%', right: '5%' },
      xAxis: {
        type: 'category',
        data: meterNames,
        axisLabel: { color: '#9ca3af', fontSize: 10, rotate: 45 },
        axisLine: { show: false },
        axisTick: { show: false },
        splitArea: { show: true }
      },
      yAxis: {
        type: 'category',
        data: days.map(d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
        axisLabel: { color: '#9ca3af', fontSize: 10 },
        axisLine: { show: false },
        axisTick: { show: false },
        splitArea: { show: true }
      },
      visualMap: {
        min: minVal,
        max: maxVal,
        orient: 'horizontal',
        left: 'center',
        bottom: '2%',
        inRange: {
          color: ['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe', '#fef3c7', '#fbbf24', '#f59e0b', '#ea580c', '#dc2626']
        },
        textStyle: { color: '#e5e7eb' },
        formatter: (v) => (isEmissions ? v.toFixed(3) : v.toFixed(2)) + (isEmissions ? ' tCO₂e' : ' kWh')
      },
      series: [{
        type: 'heatmap',
        data: heatMapData,
        label: { show: false },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }
        }
      }]
    }
  }

  return {
    weeks,
    currentWeekIndex,
    visibleWeekDays,
    canSlide,
    prevWeek,
    nextWeek,
    buildHeatmapOption
  }
}