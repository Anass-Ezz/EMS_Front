<template>
    <PvStats/>
    <div class="grid grid-cols-12 gap-5 mt-3">
        <div class="col-span-5 flex flex-row justify-between gap-2">
            <div class="h-[200px] w-full">
                <div class="font-semibold text-xl mb-4">DC Voltage</div>
                <ChannelHistoryQuerier :channelAddress="['pvinverter0/DcPvVoltage']"/>
            </div>
            <div class="h-[200px] w-full ">
                <div class="font-semibold text-xl mb-4">DC Power</div>
                <ChannelHistoryQuerier :channelAddress="['pvinverter0/DcPvPower']"/>
            </div>
        </div>
        <div class="col-span-7 row-span-2">
            <TabCharts 
            :height="460"
            :tabs="[
                { name: 'Active/Reactive Power',         channels: ['pvinverter0/ActivePower', 'pvinverter0/ReactivePower'] },
                { name: 'Power Factor',                  channels: [{channel:'pvinverter0/PowerFactor', sf:0.01}] },
                { name: 'Frequency',                     channels: ['pvinverter0/Frequency'] },
                { name: 'Power Per Phases',              channels: ['pvinverter0/ActivePowerL1','pvinverter0/ActivePowerL2','pvinverter0/ActivePowerL3'] }
            ]"/>
        </div>
        <div class="col-span-5 pt-7 ">
            <TabCharts 
            class="rounded-lg"
            :height="218"
            :tabs="[
                { name: 'Voltage',         channels: ['pvinverter0/Voltage'] },
                { name: 'Voltage Phases',  channels: ['pvinverter0/VoltageL1','pvinverter0/VoltageL2','pvinverter0/VoltageL3'] },
                { name: 'Current',         channels: ['pvinverter0/Current'] },
                { name: 'Current Phases',  channels: ['pvinverter0/CurrentL1','pvinverter0/CurrentL2','pvinverter0/CurrentL3'] }
            ]"/>
        </div>




    </div>


</template>

<script setup>
import PvStats from '@/the_components/pv/PvStats.vue';
import ChannelHistoryQuerier from '@/the_components/common/ChannelHistoryQuerier.vue';
import TabCharts from '@/the_components/common/TabCharts.vue';

</script>