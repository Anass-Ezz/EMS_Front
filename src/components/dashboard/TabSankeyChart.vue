<template>
        <Tabs value="0" class="transparent-tabs" >
            <TabList>
                <Tab value="0" class="flex gap-1" >
                    Power Flow Live
                    <img 
                    src="@/assets/images/live.gif" 
                    alt="Background image"
                    class="fade-image h-[13px] mt-1"
                    />
                </Tab>
                <Tab value="1">Energy Flow (Today)</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="0">
                    <PowerFlowSankey 
                        :height="350" 
                        :auto-refresh="true" 
                        :refresh-interval="3000" 
                    />
                </TabPanel>
                <TabPanel value="1">
                    <p class="m-0">
                        Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim
                        ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Consectetur, adipisci velit, sed quia non numquam eius modi.
                    </p>
                </TabPanel>
            </TabPanels>
        </Tabs>
</template>

<script setup>
</script>

<style scoped>
/* Target all possible PrimeVue tab background elements */
.transparent-tabs {
    background: transparent !important;
}

/* Use :deep() to penetrate component encapsulation */
.transparent-tabs :deep(.p-tabs) {
    background: transparent !important;
}

.transparent-tabs :deep(.p-tabs-header) {
    background: transparent !important;
}

.transparent-tabs :deep(.p-tabs-nav) {
    background: transparent !important;
}

.transparent-tabs :deep(.p-tablist) {
    background: transparent !important;
    background-color: transparent !important;
}

/* Additional tab list targeting - try different possible class names */
.transparent-tabs :deep(.p-tabview-nav) {
    background: transparent !important;
    background-color: transparent !important;
}

.transparent-tabs :deep(.p-tabview-nav-container) {
    background: transparent !important;
    background-color: transparent !important;
}

.transparent-tabs :deep(.p-tabview-header) {
    background: transparent !important;
    background-color: transparent !important;
}

.transparent-tabs :deep(.p-tablist-tab-list) {
    background: transparent !important;
    background-color: transparent !important;
}

/* Target the wrapper around tab buttons */
.transparent-tabs :deep(.p-tablist-content) {
    background: transparent !important;
    background-color: transparent !important;
}

.transparent-tabs :deep(.p-tabs-panels) {
    background: transparent !important;
}

.transparent-tabs :deep(.p-tabpanels) {
    background: transparent !important;
    background-color: transparent !important;
}

.transparent-tabs :deep(.p-tabpanel) {
    background: transparent !important;
    background-color: transparent !important;
}

.transparent-tabs :deep(.p-tab) {
    background: transparent !important;
    background-color: transparent !important;
}

/* Alternative approach using ::v-deep (Vue 2 style, but sometimes works) */
.transparent-tabs::v-deep .p-tablist {
    background: transparent !important;
}

.transparent-tabs::v-deep .p-tabpanels {
    background: transparent !important;
}

/* Remove borders that might show background */
.transparent-tabs :deep(.p-tablist),
.transparent-tabs :deep(.p-tabpanels),
.transparent-tabs :deep(.p-tabs) {
    border: none !important;
    box-shadow: none !important;
}

/* If the card itself has a background, make it transparent too */
.card {
    background: transparent !important;
}



</style>