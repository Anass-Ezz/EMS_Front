<template>
    <PvStats/>
    <div class="grid grid-cols-12 gap-5 mt-3">
        <div class="col-span-5 flex flex-row justify-between gap-2">
            <div class="h-[200px] w-full relative">
                <div class="flex justify-between items-center mb-4">
                    <div class="font-semibold text-xl">DC Voltage</div>
                    <button 
                        @click="downloadCSV('dc-voltage')"
                        class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
                    >
                        <i class="bi bi-download text-xs"></i>
                        Save CSV
                    </button>
                </div>
                <ChannelHistoryQuerier 
                    :channelAddress="['pvinverter0/DcPvVoltage']" 
                    :unit-config="[{channel:'pvinverter0/DcPvVoltage', unit:'V'}]"
                    :scale-config="[{channel:'pvinverter0/DcPvVoltage', sf:0.001}]"
                />
            </div>
            <div class="h-[200px] w-full relative">
                <div class="flex justify-between items-center mb-4">
                    <div class="font-semibold text-xl">DC Power</div>
                    <button 
                        @click="downloadCSV('dc-power')"
                        class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
                    >
                        <i class="bi bi-download text-xs"></i>
                        Save CSV
                    </button>
                </div>
                <ChannelHistoryQuerier 
                    :channelAddress="['pvinverter0/DcPvPower']" 
                    :unit-config="[{channel:'pvinverter0/DcPvPower', unit:'kW'}]"
                    :scale-config="[{channel:'pvinverter0/DcPvPower', sf:0.001}]"
                />
            </div>
        </div>
        <div class="col-span-7 row-span-2 relative">
            <div class="absolute top-2 right-2 z-10">
                <button 
                    @click="downloadCSV('pv-power-charts')"
                    class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1 shadow-lg"
                >
                    <i class="bi bi-download text-xs"></i>
                    Save CSV
                </button>
            </div>
            <TabCharts 
            :height="460"
            :tabs="[
                { name: 'Active/Reactive Power',         channels: [{channel:'pvinverter0/ActivePower', sf:0.001, unit:'kW'}, {channel:'pvinverter0/ReactivePower', sf:0.001, unit:'kVAR'}] },
                { name: 'Power Factor',                  channels: [{channel:'pvinverter0/PowerFactor', sf:0.001, unit:''}] },
                { name: 'Frequency',                     channels: [{channel:'pvinverter0/Frequency', sf:0.001, unit:'Hz'}] },
                { name: 'Power Per Phases',              channels: [{channel:'pvinverter0/ActivePowerL1', sf:0.001, unit:'kW'},{channel:'pvinverter0/ActivePowerL2', sf:0.001, unit:'kW'},{channel:'pvinverter0/ActivePowerL3', sf:0.001, unit:'kW'}] }
            ]"/>
        </div>
        <div class="col-span-5 pt-7 relative">
            <div class="absolute top-8 right-2 z-10">
                <button 
                    @click="downloadCSV('pv-voltage-current-charts')"
                    class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1 shadow-lg"
                >
                    <i class="bi bi-download text-xs"></i>
                    Save CSV
                </button>
            </div>
            <TabCharts 
            class="rounded-lg"
            :height="218"
            :tabs="[
                { name: 'Voltage',         channels: [{channel:'pvinverter0/Voltage', sf:0.001, unit:'V'}] },
                { name: 'Voltage Phases',  channels: [{channel:'pvinverter0/VoltageL1', sf:0.001, unit:'V'},{channel:'pvinverter0/VoltageL2', sf:0.001, unit:'V'},{channel:'pvinverter0/VoltageL3', sf:0.001, unit:'V'}] },
                { name: 'Current',         channels: [{channel:'pvinverter0/Current', sf:0.001, unit:'A'}] },
                { name: 'Current Phases',  channels: [{channel:'pvinverter0/CurrentL1', sf:0.001, unit:'A'},{channel:'pvinverter0/CurrentL2', sf:0.001, unit:'A'},{channel:'pvinverter0/CurrentL3', sf:0.001, unit:'A'}] }
            ]"/>
        </div>




    </div>


</template>

<script setup>
import PvStats from '@/components/pv/PvStats.vue';
import ChannelHistoryQuerier from '@/the_components/common/ChannelHistoryQuerier.vue';
import TabCharts from '@/the_components/common/TabCharts.vue';

// CSV download function
const downloadCSV = (type) => {
  const csvContent = 'Timestamp,Value\n' + 
    new Date().toISOString() + ',0\n' + 
    new Date(Date.now() - 3600000).toISOString() + ',0\n'
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${type}-data.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

</script>