<template>
  <div
    class="w-full h-[800px]  bg-[#18181b]
          rounded-xl overflow-hidden
           "
  >
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      :fit-view-on-init="true"
      class="h-full w-full"
      @node-click="onNodeClick"
    >
      <Controls position="bottom-left" />
      <MiniMap />
    </VueFlow>
  </div>
</template>

<script setup>
import { Controls } from '@vue-flow/controls'
import { Position, VueFlow } from '@vue-flow/core'
// import { MiniMap } from '@vue-flow/minimap'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const base   = 'text-[11px] font-medium rounded px-2 py-1 shadow'
const yellow = `${base} bg-yellow-300 dark:bg-yellow-500`
const orange = `${base} bg-amber-400 dark:bg-amber-600`
const child  = `${base} bg-sky-600 dark:bg-sky-700 text-white overflow-hidden`
const boxBorder = '2px solid rgba(255,255,255,0.25)'

const rowH = 26, pad = 8, gW = 220
function makeGroup(id, items, x, y) {
  const group = {
    id,
    type: 'group',
    position: { x, y },
    style: {
      width:  `${gW}px`,
      height: `${items.length * rowH + pad * 2}px`,
      border: boxBorder,
      borderRadius: '8px 8px 0 0'
    },
    targetPosition: Position.Left,
    draggable: true,
    selectable: false,
    data: { label: '' }
  }

  const kids = items.map((txt, i) => ({
    id: `${id}-${i}`,
    parentNode: id,
    extent: 'parent',
    position: { x: pad, y: pad + i * rowH },
    data: { label: txt },
    class: child,
    style: { width: `${gW - pad * 2}px` },
    targetPosition: Position.Left,
    sourcePosition: Position.Right,
    draggable: false
  }))

  return [group, ...kids]
}


const Y1 = [
  'Y1-1 : SPARE','Y1-2 : FILTRE HARMONIQUE','Y1-3 : SPARE',
  'Y1-4 : UP COLLER AREA','Y1-5 : STM AREA','Y1-6 : ROT',
  'Y1-7 : ENTRY MILL','Y1-8 : FURNACE','Y1-9 : EXC 01B',
  'Y1-10: LOW STD02','Y1-11: LOW STD01','Y1-12: EXC 01A',
  'Y1-13: UP STD2','Y1-14: UP STD1','Y1-15: DESCALE PMPS'
]
const Y2 = [
  'Y2-1 : COMPENSATION','Y2-2 : SPARE CAPACITOR BANK','Y2-3 : AUX_PM',
  'Y2-4 : DR_PM','Y2-5 : UTIL STM','Y2-6 : MOC GAZ',
  'Y2-7 : HYD E014','Y2-8 : HYD E018','Y2-9 : HYD E019',
  'Y2-10: UTIL','Y2-11: FR1','Y2-12: STA_GAZ'
]
const Y3 = [
  'Y3-1 : LFC','Y3-2 : LFH','Y3-3 : RS','Y3-4 : AC','Y3-5 : NCV',
  'Y3-6 : CW','Y3-7 : CTL','Y3-8 : SYS6','Y3-9 : O8SM'
]
const Y4 = ['Y4-1 : MCC FOUR NORMAL','Y4-2 : MCC FOUR SECOURS','Y4-3 : SPARE']
const Y5 = [
  'Y5-1 : TOPR DR_PM','Y5-2 : BOT_DR_PM','Y5-3 : EXC','Y5-4 : G1','Y5-5 : G4',
  'Y5-6 : G5-6','Y5-7 : G2','Y5-8 : G3','Y5-9 : DESCALE PMPS',
  'Y5-10: SPARE','Y5-11: SPARE'
]
const Y6 = [
  'Y6-1 : FR2','Y6-2 : MCCE018','Y6-3 : MCCE019','Y6-4 : MCCE020',
  'Y6-5 : UTILLITE','Y6-6 : SPARE','Y6-7 : SPARE'
]
const Y7 = ['Y7-1 : FR2']

const Y4_ = ['Y4-1 : Départ 1 Oxygéne','Y4-2 : Départ 2 Oxygéne']

const Gas = [
  'Station gas1-1 lac', 'Station gas1-2 acr',
  'Station gas2 lac', 'Station gas3 lac', 'Station gas4 lac', 'Station gas5 lac', 
]


const [g1 , ...y1] = makeGroup('g1', Y1, 340,  -200)
const [g2 , ...y2] = makeGroup('g2', Y2, 340,  240)
const [g3 , ...y4] = makeGroup('g3', Y4, 1050,  620)
const [g4 , ...y6] = makeGroup('g4', Y6, 1050,  -220)
const [g5 , ...y5] = makeGroup('g5', Y5, 1050,  10)
const [g6 , ...y3] = makeGroup('g6', Y3, 1050,  340)
const [g7 , ...y7] = makeGroup('g7', Y7, 1570, -222.5)
const [g8 , ...y4_] = makeGroup('g8', Y4_, 340, 600)
const [g9 , ...gas] = makeGroup('g9', Gas, 700,   800)

const singles = [
  { id:'tr1',  position:{x:20, y:-7.5},  data:{label:'TR1'}, class:yellow,
    sourcePosition:Position.Right },

  { id:'mss1', position:{x:180,y:-7.5}, data:{label:'Q1-1 : MSS1'}, class:orange,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'tr23', position:{x:20, y:393.5}, data:{label:'TR2/TR3'}, class:yellow,
    sourcePosition:Position.Right },

  { id:'mss2', position:{x:180,y:393.5}, data:{label:'Q2-1 : MSS2'}, class:orange,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'q40',  position:{x:100,y:623.3}, data:{label:'Q4-0 (O2)'}, class:orange,
    targetPosition:Position.Top, sourcePosition:Position.Right },

  { id:'q6',   position:{x:760,y:-131.5},  data:{label:'Q6-0 : AUX_PM'}, class:orange,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'q5',   position:{x:790,y:150}, data:{label:'Q5-0 : DR_PM'}, class:orange,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'q3',   position:{x:760,y:454.5}, data:{label:'Q3-1 : MSS3'}, class:orange,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'q4',   position:{x:760,y:656}, data:{label:'Q4-1 : MSS4'}, class:orange,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'q7',   position:{x:1380,y:-212},  data:{label:'Q7-0 : FR2'},  class:orange,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'r6',   position:{x:1330,y:504}, data:{label:'R6'}, class:child,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'r1',   position:{x:700,y:750}, data:{label:'R1'}, class:child,
    targetPosition:Position.Left, sourcePosition:Position.Right },

  { id:'odd0',   position:{x:1380,y:-108}, data:{label:'Chanfreinage'}, class:child,
    targetPosition:Position.Left, sourcePosition:Position.Right }
]


const nodes = ref([
  ...singles,
  g1,...y1,
  g2,...y2,
  g3,...y4,
  g4,...y6,
  g5,...y5,
  g6,...y3,
  g7,...y7,
  g8,...y4_,
  g9,...gas
])

const edges = ref([
  { id:'e1', source:'tr1',  target:'mss1', type:'smoothstep' },
  { id:'e2', source:'mss1', target:'g1',   type:'smoothstep' },

  { id:'e3', source:'g2-2', target:'q6', type:'smoothstep' },   
  { id:'e4', source:'q6',   target:'g4', type:'smoothstep' },
  { id:'e5', source:'g4-0',  target:'q7', type:'smoothstep' },
  { id:'e6', source:'q7',   target:'g7', type:'smoothstep' },

  { id:'e7', source:'tr23', target:'mss2', type:'smoothstep' },
  { id:'e8', source:'mss2', target:'g2',   type:'smoothstep' },
  { id:'e9', source:'tr23', target:'q40',  type:'smoothstep' },

  { id:'e10', source:'g2-3', target:'q5', type:'smoothstep' }, 
  { id:'e11', source:'q5',   target:'g5', type:'smoothstep' },

  { id:'e12', source:'g2-9', target:'q3', type:'smoothstep' }, 
  { id:'e13', source:'q3',   target:'g6', type:'smoothstep' },
  { id:'e14', source:'g6-6', target:'r6', type:'smoothstep' }, 

  { id:'e15', source:'g2-10', target:'q4', type:'smoothstep' }, 
  { id:'e16', source:'q4',    target:'g3', type:'smoothstep' },


  { id:'e17', source:'q40',    target:'g8', type:'smoothstep' },
  { id:'e18', source:'g2-11',    target:'r1', type:'smoothstep' },
  { id:'e19', source:'g2-11',    target:'g9', type:'smoothstep' },
  { id:'e20', source:'g4-4',    target:'odd0', type:'smoothstep' }
])

function onNodeClick({ node }) {

  if (node.type === 'group') return
  const label = node.data.label
  router.push({
    name: 'consumptionPage',
    query: { label }
  })
}
</script>
