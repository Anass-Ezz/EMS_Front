<template>
    <RangeToggle v-model="range" class="mb-4"/>
    
    <div class="">        
        <InfoTiles :range="range"/>

        <div class="h-[400px]  grid grid-cols-12 mb-5 gap-4">
            <div class="col-span-6">
                <p class="text-xl font-bold m-0 mb-2 flex gap-2">
                    Power Flow Live 
                    <img 
                    src="@/assets/images/RedDot.gif" 
                    alt="Background image"
                    class="h-[13px] mt-2"
                    />
                </p>
                <div class=" border border-gray-600 rounded-lg">
                    <PowerFlowSankey 
                    :height="350" 
                    :auto-refresh="true" 
                    :refresh-interval="3000" 
                    />
                </div>
            </div>
            <div class="col-span-4 h-[365px]">
                <p class="text-xl font-bold m-0 mb-2 flex gap-2">
                    Energy Consumption 
                    <span class="text-[14px] text-gray-400 bg-slate-800 px-1 rounded-lg transition-all duration-300">
                        {{ rangeLabel }}
                    </span>
                </p>
                <div class=" border border-gray-600 rounded-lg h-full">
                    <EnergyPie :range="range"/>
                </div>
            </div>
            <div class="col-span-2 h-[365px]">
                <p class="text-xl font-bold m-0 mb-2 flex gap-2">
                    Energy Cost 
                    <span class="text-[14px] text-gray-400 bg-slate-800 px-1 rounded-lg transition-all duration-300">
                        {{ rangeLabel }}
                    </span>
                </p>
                <div class=" border border-gray-600 rounded-lg h-full">
                    <CostPie :range="range"/>
                </div>
            </div>
        </div> 

        <div class="grid grid-cols-11 my-2">
            <hr class="col-span-5">
            <p class="col-span-1 text-center text-2xl font-bold">
                History
            </p>
            <hr class="col-span-5">
        </div>
        
        <div class="grid grid-cols-12 ">
            <div class="col-span-12 border border-gray-600 rounded-lg" >
                <EnergyHistogram/>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'

import InfoTiles from '@/components/dashboard/InfoTiles.vue'
import PowerFlowSankey from '@/components/charts/PowerFlowSankey.vue'
import TabSankeyChart from '@/components/dashboard/TabSankeyChart.vue'
import EnergyPie from '@/components/charts/EnergyPie.vue'
import CostPie from '@/components/charts/CostPie.vue'
import EnergyHistogram from '@/components/charts/EnergyHistogram.vue'
import RangeToggle from '@/components/dashboard/RangeToggle.vue'

const range = ref('day') // 'day' | 'week' | 'month'

const rangeLabel = computed(() => {
  switch(range.value) {
    case 'day': return 'Today'
    case 'week': return 'This Week'
    case 'month': return 'This Month'
    default: return 'Today'
  }
})
</script>