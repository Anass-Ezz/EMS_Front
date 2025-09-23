<script setup>
import { ref } from 'vue';
import ConnectedEdges from '@/the_components/dashboard/ConnectedEdges.vue';
import Environment from '@/the_components/dashboard/Environment.vue';
import Overview3d from '@/the_components/dashboard/Overview3d.vue';
import StatsOverview from '@/the_components/dashboard/StatsOverview.vue';
import AlertsTable from '@/the_components/dashboard/AlertsTable.vue';
import TabCharts from '@/the_components/common/TabCharts.vue';


// Reactive state to store the processed flow direction values
// Initialize with 0 for no flow
const flowDirections = ref({
  solarPanelFlow: 0,
  windTurbineFlow: 0,
  batteryFlow: 0,
  consumptionFlow: 0,
});

// Helper function to get the flow direction (1, -1, or 0) for generation/battery
// Positive value -> 1 (forward/out)
// Negative value -> -1 (backward/in)
// Zero value -> 0 (no flow)
const getDirection = (value) => {
  if (value > 0) return 1;
  if (value < 0) return -1;
  return 0; // Handles 0 or non-numeric values
};

// Method to handle the 'update:flowData' event emitted by StatsOverview
const handleFlowDataUpdate = (data) => {
  // Log the raw data received from the child
  console.log('Parent received RAW flow data from StatsOverview:', data);

  // Apply the logic to determine flow direction for each source
  flowDirections.value.solarPanelFlow = getDirection(data.solarPower);
  flowDirections.value.windTurbineFlow = getDirection(data.windPower);
  flowDirections.value.batteryFlow = getDirection(data.batteryPower);

  // Special logic for consumption (meter):
  // Positive consumption (using power) should be -1 (flow INTO the factory from grid)
  // Negative consumption (exporting power) should be 1 (flow OUT of the factory to grid)
  if (data.consumptionPower > 0) {
    flowDirections.value.consumptionFlow = -1;
  } else if (data.consumptionPower < 0) {
    flowDirections.value.consumptionFlow = 1;
  } else {
    flowDirections.value.consumptionFlow = 0;
  }

  // Log the PROCESSED flow directions that will be passed to Overview3d
  console.log('Parent calculated FLOW DIRECTIONS for Overview3d:', flowDirections.value);
};

</script>

<template>
    <div class="grid grid-cols-12 gap-2">
        <!-- Listen for the 'update:flowData' event from StatsOverview -->
        <!-- When it's emitted, call the handleFlowDataUpdate method -->
        <StatsOverview @update:flowData="handleFlowDataUpdate" />

        <div class="col-span-3 flex gap-3 flex-col">
            <Overview3d
            :isOrthographic="true"
            :orthoZoom="1"
            :lightIntensityMultiplier="1000"
            :environmentExposure="20"
            :showDebugInfo="true"
            :cameraInitialPosition="{ x: -3.21, y: 8.13, z: 6.97 }"

            :sphereSize="0.05"
            :sphereGlowIntensity="0.0"
            :bloomStrength="3"
            :bloomRadius="0.8"
            :bloomThreshold="0.0"



            :windTurbineFlow="flowDirections.windTurbineFlow"
            :solarPanelFlow="flowDirections.solarPanelFlow"
            :batteryFlow="flowDirections.batteryFlow"
            :consumptionFlow="flowDirections.consumptionFlow"
            />
            <Environment/>
        </div>
        <div class="col-span-9 gap-3 flex flex-col ">
            <div class="grid grid-cols-12 gap-2">

                <div class="col-span-7 h-fit">
                    <TabCharts
                        :height="335"
                        isLegend:true
                        :tabs="[
                        { name: 'Available Generation',         channels: ['pvinverter0/DcPvPower', 'windturbine0/MaxWindPower'] },
                        { name: 'Current Generation',  channels: ['pvinverter0/ActivePower', 'windturbine0/ActivePower'] },
                        { name: 'Battery',         channels: ['ess/ActivePower'] },
                        { name: 'Consumption',         channels: ['meter0/ActivePower', 'meter0/ReactivePower'] }
                    ]"/>
                </div>
                <div class="col-span-5 h-[445px]">
                    <AlertsTable/>
                </div>
            </div>
            <ConnectedEdges />
            <!-- <TestComponenet /> -->
        </div>
    </div>
</template>