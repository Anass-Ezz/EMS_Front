<template>
    <ExportStats/>
    <div class="grid grid-cols-11 my-2">
        <hr class="col-span-5">
        <p class="col-span-1 text-center text-2xl font-bold">
            History
        </p>
        <hr class="col-span-5">
    </div>
    <div class="grid grid-cols-12 gap-3">
        <div class="col-span-6">
            <DynamicCostTabBarChart
            :tabs="[
                { name:'Active Energy Export', channels:[
                    'meter0/ActiveEnergy',
                ]}
            ]"
            from-date="2025-01-01"
            to-date="2025-07-31"
            :height="200"
            :resolution="{ value:1, unit:'Months' }"
            />
        </div>
        <div class="col-span-6">
            <DynamicCostTabBarChart
            :tabs="[
                { name:'Generation Active Energy', channels:[
                    'pvinverter0/ActiveEnergy',
                    'windturbine0/ActiveEnergy',
                ]},

                { name:'Battery Active Energy', channels:[
                    'ess0/ChargeActiveEnergy',
                    'ess0/DischargeActiveEnergy'
                ]}
            ]"
            from-date="2025-01-01"
            to-date="2025-07-31"
            :height="200"
            :resolution="{ value:1, unit:'Months' }"
            />
        </div>
    </div>
</template>

<script setup>

import DynamicCostTabBarChart from "@/the_components/export/DynamicCostTabBarChart.vue";
import ExportStats from "@/the_components/export/ExportStats.vue";

</script>