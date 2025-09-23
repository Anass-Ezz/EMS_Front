<script setup>



import TabCharts from '@/the_components/common/TabCharts.vue';
import StatsConsumption from '@/the_components/consumption/StatsConsumption.vue';
import TheGraphs from '@/the_components/consumption/TheGraphs.vue';
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute()
const nodeLabel = computed(() => route.query.label || '—')
</script>

<template>
    <h1>{{nodeLabel}}</h1>
    <div class="grid grid-cols-12 gap-3">
        <StatsConsumption />
        <div class="col-span-12 xl:col-span-12 mb-10">
            <TheGraphs />
        </div>
        <div class="col-span-12 xl:col-span-6 ">
            <!-- <ConsumptionPowerHistory /> -->

            <TabCharts 
            :height="250"
            :tabs="[
                { name: 'Active/Reactive Power',         channels: ['meter0/ActivePower', 'meter0/ReactivePower'] },
                { name: 'Power Factor',                  channels: [{channel:'meter0/PowerFactor', sf:0.01}] },
                { name: 'Frequency',                     channels: [{channel:'meter0/Frequency', sf:0.1}] },
                { name: 'Power Per Phases',              channels: ['meter0/ActivePowerL1','meter0/ActivePowerL2','meter0/ActivePowerL3'] }
            ]"/>
        </div>
        <div class="col-span-12 xl:col-span-6 ">
            <!-- <ConsumptionVoltageCurrentHistory /> -->
            <TabCharts 
            :height="250"
            :tabs="[
                { name: 'Voltage',         channels: ['meter0/Voltage'] },
                { name: 'Voltage Phases',  channels: ['meter0/VoltageL1','meter0/VoltageL2','meter0/VoltageL3'] },
                { name: 'Current',         channels: ['meter0/Current'] },
                { name: 'Current Phases',  channels: ['meter0/CurrentL1','meter0/CurrentL2','meter0/CurrentL3'] }
            ]"/>
        </div>

    </div>
</template>
