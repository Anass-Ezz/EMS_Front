<template>
    <BatteryStats/>
    <div class="grid grid-cols-12 gap-5  mt-3">
        <div class="col-span-6 row-span-2 grid grid-cols-12 gap-x-4 ">
            <div class="h-[140px] col-span-6 ">
                <div class="font-semibold text-xl mb-4">Min/Max Cell Voltage</div>
                <ChannelHistoryQuerier :channelAddress="['ess0/MaxCellVoltage', 'ess0/MinCellVoltage']"/>
            </div>
            <div class="h-[140px] col-span-6">
                <div class="font-semibold text-xl mb-4">Min/Max Cell Temperature</div>
                <ChannelHistoryQuerier :channelAddress="['ess0/MaxCellTemperature', 'ess0/MinCellTemperature']"/>
            </div>
            <div class="h-[160px] col-span-12 pt-0">
                <div class="font-semibold text-xl mb-4">Battery Capacity</div>
                <ChannelHistoryQuerier :channelAddress="['ess0/Capacity']"/>
            </div>
        </div>

        <div class="col-span-6 row-span-2">

            <TabCharts 
            :height="300"
            :tabs="[
                { name: 'SoC',         channels: ['ess0/Soc'] },
                { name: 'Battery Voltage',  channels: ['ess0/BatteryPackVoltage'] },
                { name: 'Battery Current',         channels: ['ess0/BatteryPackCurrent'] },
            ]"/>

        </div>
        <div class="col-span-6 row-span-2">
            <div class="font-semibold text-xl mb-4">AC Voltage and Current Measurments</div>
            <TabCharts 
            :height="218"
            :tabs="[
                { name: 'Voltage',         channels: ['windturbine0/Voltage'] },
                { name: 'Voltage Phases',  channels: ['windturbine0/VoltageL1','windturbine0/VoltageL2','windturbine0/VoltageL3'] },
                { name: 'Current',         channels: ['windturbine0/Current'] },
                { name: 'Current Phases',  channels: ['windturbine0/CurrentL1','windturbine0/CurrentL2','windturbine0/CurrentL3'] }
            ]"/>
        </div>
        <div class="col-span-6 row-span-2">
            <div class="font-semibold text-xl mb-4">Power Measurments</div>
            <TabCharts 
            :height="218"
            :tabs="[
                { name: 'Active/Reactive Power',         channels: ['windturbine0/ActivePower', 'windturbine0/ReactivePower'] },
                { name: 'Power Factor',                  channels: [{channel:'windturbine0/PowerFactor', sf:0.01}] },
                { name: 'Frequency',                     channels: [{channel:'windturbine0/Frequency', sf:0.1}] },
                { name: 'Power Per Phases',              channels: ['windturbine0/ActivePowerL1','windturbine0/ActivePowerL2','windturbine0/ActivePowerL3'] }
            ]"/>
        </div>
    </div>

</template>

<script setup>


import ChannelHistoryQuerier from '@/the_components/common/ChannelHistoryQuerier.vue';
import BatteryStats from '@/the_components/battery/BatteryStats.vue';
import TabCharts from '@/the_components/common/TabCharts.vue';

</script>