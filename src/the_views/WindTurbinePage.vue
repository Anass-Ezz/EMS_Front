<template>
    <WindTurbineStats/>
    <div class="grid grid-cols-12 gap-5 mt-3">
        <div class="col-span-6 grid grid-cols-12 gap-4">
            <div class="h-[200px] col-span-4">
                <div class="font-semibold text-xl mb-4">Wind Speed</div>
                <ChannelHistoryQuerier :channelAddress="['windturbine0/MaxWindPower']"/>
            </div>
            <div class="h-[200px] col-span-4">
                <div class="font-semibold text-xl mb-4">Wind Power</div>
                <ChannelHistoryQuerier :channelAddress="['windturbine0/MaxWindPower']"/>
            </div>
            <div class="h-[200px] col-span-4">
                <div class="font-semibold text-xl mb-4">Pitch Angle</div>
                <ChannelHistoryQuerier :channelAddress="['windturbine0/PitchAngle']"/>
            </div>
        </div>
        <div class="col-span-6 row-span-2">
            <!-- <PowersHistory/> -->
            <TabCharts 
            :height="460"
            :tabs="[
                { name: 'Active/Reactive Power',         channels: ['windturbine0/ActivePower', 'windturbine0/ReactivePower'] },
                { name: 'Power Factor',                  channels: [{channel:'windturbine0/PowerFactor', sf:0.01}] },
                { name: 'Frequency',                     channels: [{channel:'windturbine0/Frequency', sf:0.1}] },
                { name: 'Power Per Phases',              channels: ['windturbine0/ActivePowerL1','windturbine0/ActivePowerL2','windturbine0/ActivePowerL3'] }
            ]"/>
        </div>
        <div class="col-span-6 pt-7">
            <!-- <VolatgeCurrentHistory/> -->
            <TabCharts 
            :height="218"
            :tabs="[
                { name: 'Voltage',         channels: ['windturbine0/Voltage'] },
                { name: 'Voltage Phases',  channels: ['windturbine0/VoltageL1','windturbine0/VoltageL2','windturbine0/VoltageL3'] },
                { name: 'Current',         channels: ['windturbine0/Current'] },
                { name: 'Current Phases',  channels: ['windturbine0/CurrentL1','windturbine0/CurrentL2','windturbine0/CurrentL3'] }
            ]"/>
        </div>
    </div>

</template>

<script setup>


import ChannelHistoryQuerier from '@/the_components/common/ChannelHistoryQuerier.vue';
import WindTurbineStats from '@/the_components/wind_turbine/WindTurbineStats.vue';
import TabCharts from '@/the_components/common/TabCharts.vue';

</script>