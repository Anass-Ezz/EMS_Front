<!-- FactorySingleLine_PowerFramed.vue -->
<template>
  <section class="power-diagram rounded-2xl bg-zinc-900 ring-1 ring-white/10 overflow-hidden">
    <!-- Global title OUTSIDE the Electricity frame -->
    <header class="flex items-center justify-between px-5 py-3 border-b border-white/10">
      <h2 class="text-white text-xl font-semibold tracking-wide">
        Schéma unifilaire de l’usine
      </h2>

      <!-- drag toggle -->
      <label class="flex items-center gap-2 text-white/80 text-sm select-none">
        <input type="checkbox" v-model="lockNodes" class="accent-white" />
        {{ lockNodes ? 'Lock nodes' : 'Unlock nodes (drag to adjust)' }}
      </label>
    </header>

    <div class="h-[860px]">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :fit-view-on-init="true"
        :min-zoom="0.35"
        :max-zoom="2"
        :default-viewport="{ x: 0, y: 0, zoom: 0.9 }"
        :pan-on-drag="true"
        :zoom-on-scroll="true"
        :nodes-draggable="!lockNodes"
        :nodes-connectable="false"
        class="h-full w-full"
      >
        <Controls position="bottom-left" />
        <MiniMap pannable zoomable style="background: rgba(255,255,255,0.06)" />
      </VueFlow>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { VueFlow, Position } from '@vue-flow/core'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

/* -------- helpers -------- */
const N = (id, x, y, label, cls = '', opts = {}) => ({
  id, position: { x, y }, data: { label }, class: cls, draggable: true, ...opts
})
const group = (id, x, y, w, h, style = {}) => ({
  id, type: 'group', position: { x, y }, draggable: false, selectable: false, style
})

/* ====== LOCK / UNLOCK ====== */
const lockNodes = ref(false)

/* ====== MAIN ELECTRICITY FRAME (covers everything) ====== */
const POWER = { id: 'frame-power', x: -40, y: 10, w: 2030, h: 740 }
const powerFrame = group(POWER.id, POWER.x, POWER.y, POWER.w, POWER.h, {
  width: `${POWER.w}px`,
  height:`${POWER.h}px`,
  border: '2px dashed rgba(255,255,255,0.7)',
  background: 'rgba(255,255,255,0.03)',
  borderRadius: '18px',
  boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.06)'
})
/* Big label for the main frame (NOW REALLY BIG) */
const powerLabel = N('power-label', 18, -48, 'Electricity Power', 'label-main', {
  parentNode: POWER.id, extent: 'parent', draggable: false
})

/* ====== WORKSHOP FRAMES ====== */
const frameA = group('wsa', 80, 140, 980, 560, {
  width: '980px', height: '560px',
  border: '2px dashed rgba(255,168,0,0.9)',
  background: 'rgba(255,168,0,0.10)', borderRadius: '14px'
})
const frameB = group('wsb', 1120, 140, 820, 560, {
  width: '820px', height: '560px',
  border: '2px dashed rgba(90,150,255,0.95)',
  background: 'rgba(90,150,255,0.12)', borderRadius: '14px'
})

/* ====== NODES (no total smart meters, no edge labels) ====== */
const nodes = ref([
  /* frame & title */
  powerFrame,
  { ...powerLabel },

  /* MV grid and MV transformers */
  N('mv-grid', 650, -10, 'MV Grid Supply 20kV', 'node source', {
    parentNode: POWER.id, extent: 'parent', sourcePosition: Position.Bottom,
    style: { width: '300px', textAlign: 'center' }
  }),
  N('mv-tx-a', 320, 140, 'MV Transformer\n(20kV → 6.6/3.3kV)', 'node transformer', {
    parentNode: POWER.id, extent: 'parent',
    targetPosition: Position.Top, sourcePosition: Position.Bottom,
    style: { width: '230px', whiteSpace: 'pre-line' }
  }),
  N('mv-tx-b', 1060, 140, 'MV Transformer\n(20kV → 0.4kV)', 'node transformer', {
    parentNode: POWER.id, extent: 'parent',
    targetPosition: Position.Top, sourcePosition: Position.Right,
    style: { width: '230px', whiteSpace: 'pre-line' }
  }),

  /* workshop frames inside power frame */
  { ...frameA, parentNode: POWER.id, extent: 'parent' },
  { ...frameB, parentNode: POWER.id, extent: 'parent' },

  /* === WORKSHOP A === */
  N('a-hv', 230, 310, 'Workshop A\nHV panel', 'node panel', {
    parentNode: 'wsa', extent: 'parent', sourcePosition: Position.Bottom, targetPosition: Position.Top
  }),
  N('a-lv', 570, 410, 'Workshop A LV panel\n(480V & 230V)', 'node panel', {
    parentNode: 'wsa', extent: 'parent', sourcePosition: Position.Bottom, targetPosition: Position.Top,
    style: { width: '200px' }
  }),
  N('a-lv-tx', 720, 320, 'LV Transformer\n(480V → 230V)', 'node transformer', {
    parentNode: 'wsa', extent: 'parent', targetPosition: Position.Left, sourcePosition: Position.Bottom,
    style: { width: '200px' }
  }),

  // HV branches
  N('a-sm-press', 120, 460, 'Smart Meter\nPress (HV)', 'node meter', { parentNode: 'wsa', extent: 'parent' }),
  N('a-press',    110, 530, 'Stamping Press',            'node load',  { parentNode: 'wsa', extent: 'parent' }),
  N('a-sm-heater',300, 460, 'Smart Meter\nHeater (HV)', 'node meter', { parentNode: 'wsa', extent: 'parent' }),
  N('a-heater',   290, 530, 'Induction Heater',         'node load',  { parentNode: 'wsa', extent: 'parent' }),

  // LV branches
  N('a-sm-coil',  430, 460, 'Smart Meter\nCoil Feeder (LV)', 'node meter', { parentNode: 'wsa', extent: 'parent' }),
  N('a-coil',     430, 530, 'Feeder Motor',                'node load',  { parentNode: 'wsa', extent: 'parent' }),
  N('a-sm-welder',600, 460, 'Smart Meter\nWelder (LV)',    'node meter', { parentNode: 'wsa', extent: 'parent' }),
  N('a-welder',   590, 530, 'Welder /\nRobotic arms',      'node load',  { parentNode: 'wsa', extent: 'parent' }),
  N('a-sm-ctrl',  770, 460, 'Smart Meter\nControl (LV)',   'node meter', { parentNode: 'wsa', extent: 'parent' }),
  N('a-ctrl',     760, 530, 'PLC, Sensors,\nRelays …',     'node load',  { parentNode: 'wsa', extent: 'parent' }),
  N('a-sm-util',  930, 460, 'Smart Meter\nUtility (LV)',   'node meter', { parentNode: 'wsa', extent: 'parent' }),
  N('a-util',     920, 530, 'Lighting, doors,\nScreens …', 'node load',  { parentNode: 'wsa', extent: 'parent' }),

  /* === WORKSHOP B === */
  N('b-lv', 1440, 410, 'Workshop B LV panel\n(480V & 230V)', 'node panel', {
    parentNode: 'wsb', extent: 'parent', sourcePosition: Position.Bottom, targetPosition: Position.Top
  }),
  N('b-lv-tx', 1720, 320, 'LV Transformer\n(480V → 230V)', 'node transformer', {
    parentNode: 'wsb', extent: 'parent', targetPosition: Position.Left, style: { width: '200px' }
  }),
  N('b-sm-chassis',1270, 460, 'Smart Meter\nChassis Mounting (LV)', 'node meter', { parentNode: 'wsb', extent: 'parent' }),
  N('b-chassis',   1265, 530, 'Chassis Mounting',                'node load',  { parentNode: 'wsb', extent: 'parent' }),
  N('b-sm-robot',  1450, 460, 'Smart Meter\nRobotic Arms (LV)',   'node meter', { parentNode: 'wsb', extent: 'parent' }),
  N('b-robot',     1445, 530, 'Robotic Arms',                    'node load',  { parentNode: 'wsb', extent: 'parent' }),
  N('b-sm-wiring', 1630, 460, 'Smart Meter\nWiring Benches (LV)', 'node meter', { parentNode: 'wsb', extent: 'parent' }),
  N('b-wiring',    1625, 530, 'Wiring Benches',                  'node load',  { parentNode: 'wsb', extent: 'parent' }),
  N('b-sm-util',   1795, 460, 'Smart Meter\nUtility (LV)',        'node meter', { parentNode: 'wsb', extent: 'parent' }),
  N('b-util',      1790, 530, 'Lighting, ventilation,\ndoors…',  'node load',  { parentNode: 'wsb', extent: 'parent' }),
  N('b-sm-ctrl',   1960, 460, 'Smart Meter\nControl (LV)',        'node meter', { parentNode: 'wsb', extent: 'parent' }),
  N('b-ctrl',      1955, 530, 'PLC, Sensors,\nRelays …',          'node load',  { parentNode: 'wsb', extent: 'parent' }),
])

/* Edges (no labels) */
const E = (id, s, t) => ({ id, source: s, target: t, type: 'smoothstep', style: { strokeWidth: 2 } })
const edges = ref([
  E('e1','mv-grid','mv-tx-a'), E('e2','mv-grid','mv-tx-b'),

  // Workshop A
  E('e3','mv-tx-a','a-hv'),
  E('e4','a-hv','a-sm-press'), E('e5','a-sm-press','a-press'),
  E('e6','a-hv','a-sm-heater'), E('e7','a-sm-heater','a-heater'),
  E('e8','mv-tx-b','a-lv-tx'), E('e9','a-lv-tx','a-lv'), E('e10','mv-tx-b','a-lv'),
  E('e11','a-lv','a-sm-coil'), E('e12','a-sm-coil','a-coil'),
  E('e13','a-lv','a-sm-welder'), E('e14','a-sm-welder','a-welder'),
  E('e15','a-lv','a-sm-ctrl'), E('e16','a-sm-ctrl','a-ctrl'),
  E('e17','a-lv','a-sm-util'), E('e18','a-sm-util','a-util'),

  // Workshop B
  E('e19','mv-tx-b','b-lv'), E('e20','mv-tx-b','b-lv-tx'), E('e21','b-lv-tx','b-lv'),
  E('e22','b-lv','b-sm-chassis'), E('e23','b-sm-chassis','b-chassis'),
  E('e24','b-lv','b-sm-robot'),   E('e25','b-sm-robot','b-robot'),
  E('e26','b-lv','b-sm-wiring'),  E('e27','b-sm-wiring','b-wiring'),
  E('e28','b-lv','b-sm-util'),    E('e29','b-sm-util','b-util'),
  E('e30','b-lv','b-sm-ctrl'),    E('e31','b-sm-ctrl','b-ctrl'),
])

/* Sync lock state to nodes (keeps groups & label non-draggable) */
watch(lockNodes, (locked) => {
  nodes.value = nodes.value.map(n =>
    ({ ...n, draggable: !locked && n.type !== 'group' && n.id !== 'power-label' })
  )
})
</script>

<style scoped>
/* -------------------------------------------
   FONT SIZE CONTROLS (tweak here as you like)
-------------------------------------------- */
.power-diagram{
  /* Big title for the main Electricity frame */
  --font-title-main: clamp(44px, 5vw, 80px);

  /* Node label sizes by type */
  --font-source:      14px;
  --font-transformer: 14px;
  --font-panel:       14px;
  --font-meter:       13px;
  --font-load:        13px;
}

/* subtle grid on dark */
:deep(.vue-flow) {
  background-image: radial-gradient(rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 16px 16px;
}

/* MAIN FRAME LABEL — BIG */
.label-main {
  background: transparent;
  color: #ffffff;
  font-weight: 900;
  font-size: var(--font-title-main);   /* 👈 sized via variable */
  letter-spacing: 0.5px;
  text-shadow: 0 10px 24px rgba(0,0,0,0.6);
  padding: 0;
  pointer-events: none; /* don’t block drags under it */
}

/* ---- SHAPES ---- */
/* 1) Source (MV Grid): pill */
.node.source {
  background: #ffffff;
  color: #0b1220;
  border-radius: 999px;
  padding: 8px 14px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.5);
}
.node.source .vue-flow__node-default__label { font-size: var(--font-source); font-weight: 700; }

/* 2) Transformer: block with “coil tabs” */
.node.transformer {
  position: relative;
  background: #ffffff;
  color: #0b1220;
  border-radius: 10px;
  padding: 10px 12px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.5);
}
.node.transformer::before,
.node.transformer::after {
  content: "";
  position: absolute;
  left: -10px;
  width: 6px; height: 50%;
  top: 25%;
  background: #e5e7eb;
  border-radius: 3px;
}
.node.transformer::after { left: auto; right: -10px; }
.node.transformer .vue-flow__node-default__label { font-size: var(--font-transformer); font-weight: 600; }

/* 3) Panels (HV/LV): diamond */
.node.panel {
  background: #ffffff;
  color: #0b1220;
  width: 180px; height: 80px;
  border-radius: 12px;
  transform: rotate(45deg);
  display: grid; place-items: center;
  box-shadow: 0 10px 24px rgba(0,0,0,0.5);
}
.node.panel .vue-flow__node-default__label {
  transform: rotate(-45deg);
  text-align: center;
  white-space: pre-line;
  font-size: var(--font-panel);
  font-weight: 700;
}

/* 4) Smart Meter (machine-side): circular */
.node.meter {
  background: #ffffff;
  color: #0b1220;
  border-radius: 999px;
  padding: 10px 14px;
  min-width: 160px;
  text-align: center;
  box-shadow: 0 10px 24px rgba(0,0,0,0.5);
}
.node.meter .vue-flow__node-default__label { font-size: var(--font-meter); font-weight: 600; }

/* 5) Load: dashed rounded rectangle */
.node.load {
  background: transparent;
  color: #e5e7eb;
  border: 2px dashed #9ca3af;
  border-radius: 12px;
  padding: 10px 12px;
  min-width: 160px;
}
.node.load .vue-flow__node-default__label { font-size: var(--font-load); }

/* crisper edges for dark bg */
:deep(.vue-flow__edge .vue-flow__edge-path) {
  stroke: #e5e7eb;
  stroke-width: 2.25;
}
</style>
