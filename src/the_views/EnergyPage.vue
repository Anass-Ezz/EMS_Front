<template>

    <EnergyStats/>
    <div class="grid grid-cols-11 my-2">
        <hr class="col-span-5">
        <p class="col-span-1 text-center text-2xl font-bold">
            History
        </p>
        <hr class="col-span-5">
    </div>
    <div class="grid grid-cols-12 gap-3">
        <div class="col-span-6">
            <DynamicEnergyTabBarChart
            :tabs="[
                { name:'Active Energy Export', channels:[
                    'meter0/ActiveEnergy',

                ]},
                { name:'Reactive Energy Export', channels:[
                    'meter0/ReactiveEnergy',

                ]}
            ]"
            from-date="2025-01-01"
            to-date="2025-07-31"
            :height="175"
            :resolution="{ value:1, unit:'Months' }"
            />
        </div>
        <div class="col-span-6">
            <DynamicEnergyTabBarChart
            :tabs="[
                { name:'Generation Active Energy', channels:[
                    'pvinverter0/ActiveEnergy',
                    'windturbine0/ActiveEnergy',
                ]},
                { name:'Generation Reactive Energy', channels:[
                    'pvinverter0/ReactiveEnergy',
                    'windturbine0/ReactiveEnergy'

                ]},
                { name:'Battery Active Energy', channels:[
                    'ess0/ChargeActiveEnergy',
                    'ess0/DischargeActiveEnergy'
                    
                ]},
                { name:'Battery Active Energy', channels:[
                    'ess0/ChargeReactiveEnergy',
                    'ess0/DischargeReactiveEnergy'

                ]}
            ]"
            from-date="2025-01-01"
            to-date="2025-07-31"
            :height="175"
            :resolution="{ value:1, unit:'Months' }"
            />
        </div>

    </div>



</template>

<script setup>

import DynamicEnergyTabBarChart from "@/the_components/energy/DynamicEnergyTabBarChart.vue";
import EnergyStats from "@/the_components/energy/EnergyStats.vue";

</script>