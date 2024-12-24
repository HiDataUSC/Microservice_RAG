<script setup lang="ts">
import { markRaw, nextTick, ref, onMounted, watch, onUnmounted } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import StartNode from '@/components/vue-flow/nodes/start-node.vue'
import EndNode from '@/components/vue-flow/nodes/end-node.vue'
import LLMNode from '@/components/vue-flow/nodes/LLM-node.vue'
import CodeNode from '@/components/vue-flow/nodes/code-node.vue'
import KnowledgeNode from '@/components/vue-flow/nodes/knowledge-node.vue'
import ApiNode from '@/components/vue-flow/nodes/api-node.vue'
import ConversationNode from '@/components/vue-flow/nodes/conversation-node.vue'
import Document_uploadNode from '@/components/vue-flow/nodes/document_upload-node.vue'
import { Test_data } from '@/lib/constant'

import type { Dimensions, Elements } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'
import type { Edge as EdgeType } from '@vue-flow/core'

interface MainCanvasData {
  nodes: Node<any, any, string>[]
  edges: Edge[]
  position: [number, number]
  zoom: number
}

const props = defineProps<{
  data: MainCanvasData
}>()

const nodeTypes = {
  start: markRaw(StartNode),
  end: markRaw(EndNode),
  LLM: markRaw(LLMNode),
  code: markRaw(CodeNode),
  knowledge: markRaw(KnowledgeNode),
  api: markRaw(ApiNode),
  conversation: markRaw(ConversationNode),
  document_upload: markRaw(Document_uploadNode)
}

const { findNode, nodes, addNodes, addEdges, project, vueFlowRef, onConnect, setNodes, setEdges, setViewport, removeEdges, viewport } = useVueFlow()

const initialTouchDistance = ref(0)
const initialTouchCenter = ref({ x: 0, y: 0 })
const lastTouchCenter = ref({ x: 0, y: 0 })
const isMultiTouch = ref(false)
const isPanning = ref(false)

function getTouchCenter(touch1: Touch, touch2: Touch) {
  return {
    x: (touch1.clientX + touch2.clientX) / 2,
    y: (touch1.clientY + touch2.clientY) / 2
  }
}

function handleWheel(event: WheelEvent) {
  event.preventDefault()
  
  const isTouchpad = event.deltaMode === 0
  
  if (!isTouchpad) return
  
  const { deltaX, deltaY, ctrlKey } = event
  
  if (!ctrlKey) {
    isPanning.value = true
    document.getElementById('main-canvas')?.classList.add('panning')
    
    setTimeout(() => {
      isPanning.value = false
      document.getElementById('main-canvas')?.classList.remove('panning')
    }, 1000)
  }
  
  if (ctrlKey) {
    const zoomFactor = deltaY > 0 ? 0.95 : 1.05
    setViewport({
      x: viewport.value.x,
      y: viewport.value.y,
      zoom: viewport.value.zoom * zoomFactor
    })
    return
  }
  
  setViewport({
    x: viewport.value.x - deltaX * 1.5,
    y: viewport.value.y - deltaY * 1.5,
    zoom: viewport.value.zoom
  })
}

function handleTouchStart(event: TouchEvent) {
  if (event.touches.length === 2) {
    isMultiTouch.value = true
    const touch1 = event.touches[0]
    const touch2 = event.touches[1]
    
    initialTouchDistance.value = Math.hypot(
      touch2.clientX - touch1.clientX,
      touch2.clientY - touch1.clientY
    )
    
    const center = getTouchCenter(touch1, touch2)
    initialTouchCenter.value = center
    lastTouchCenter.value = center
  }
}

function handleTouchMove(event: TouchEvent) {
  if (!isMultiTouch.value || event.touches.length !== 2) return
  
  isPanning.value = true
  document.getElementById('main-canvas')?.classList.add('panning')
  
  const touch1 = event.touches[0]
  const touch2 = event.touches[1]
  
  const currentCenter = getTouchCenter(touch1, touch2)
  
  const currentDistance = Math.hypot(
    touch2.clientX - touch1.clientX,
    touch2.clientY - touch1.clientY
  )
  
  const scale = currentDistance / initialTouchDistance.value
  const zoomChange = scale > 1 ? 1.02 : scale < 1 ? 0.98 : 1
  
  const dx = currentCenter.x - lastTouchCenter.value.x
  const dy = currentCenter.y - lastTouchCenter.value.y
  
  setViewport({
    x: viewport.value.x + dx,
    y: viewport.value.y + dy,
    zoom: viewport.value.zoom * (Math.abs(scale - 1) > 0.1 ? zoomChange : 1)
  })
  
  lastTouchCenter.value = currentCenter
}

function handleTouchEnd() {
  isMultiTouch.value = false
  initialTouchDistance.value = 0
  initialTouchCenter.value = { x: 0, y: 0 }
  lastTouchCenter.value = { x: 0, y: 0 }
  
  setTimeout(() => {
    isPanning.value = false
    document.getElementById('main-canvas')?.classList.remove('panning')
  }, 1000)
}

onMounted(() => {
  nextTick(() => {
    if (props.data) {
      setNodes(props.data.nodes)
      setEdges(props.data.edges)
      setViewport({ x: props.data.position[0], y: props.data.position[1], zoom: props.data.zoom })
    }
  })

  const vueFlowElement = vueFlowRef.value
  if (vueFlowElement) {
    vueFlowElement.addEventListener('wheel', handleWheel, { passive: false })
    vueFlowElement.addEventListener('touchstart', handleTouchStart)
    vueFlowElement.addEventListener('touchmove', handleTouchMove)
    vueFlowElement.addEventListener('touchend', handleTouchEnd)
  }
})

onUnmounted(() => {
  const vueFlowElement = vueFlowRef.value
  if (vueFlowElement) {
    vueFlowElement.removeEventListener('wheel', handleWheel)
    vueFlowElement.removeEventListener('touchstart', handleTouchStart)
    vueFlowElement.removeEventListener('touchmove', handleTouchMove)
    vueFlowElement.removeEventListener('touchend', handleTouchEnd)
  }
})

watch(
  () => props.data,
  (newData) => {
    if (newData) {
      setNodes(newData.nodes)
      setEdges(newData.edges)
      
      nextTick(() => {
        setViewport({ x: newData.position[0], y: newData.position[1], zoom: newData.zoom })
      })
    }
  },
  { immediate: true }
)

onConnect((params) => {
  addEdges(params)
})

const selectedEdge = ref<EdgeType | null>(null)
const edgeMenuPosition = ref({ x: 0, y: 0 })

function updateEdgeMenuPosition(edge: EdgeType) {
  const sourceNode = nodes.value.find(n => n.id === edge.source)
  const targetNode = nodes.value.find(n => n.id === edge.target)
  
  if (sourceNode && targetNode) {
    const vueFlowEl = vueFlowRef.value?.getBoundingClientRect()
    if (!vueFlowEl) return

    const centerX = (
      sourceNode.position.x + sourceNode.dimensions.width / 2 + 
      targetNode.position.x + targetNode.dimensions.width / 2
    ) / 2
    const centerY = (
      sourceNode.position.y + sourceNode.dimensions.height / 2 + 
      targetNode.position.y + targetNode.dimensions.height / 2
    ) / 2

    const x = centerX * viewport.value.zoom + viewport.value.x + vueFlowEl.left
    const y = centerY * viewport.value.zoom + viewport.value.y + vueFlowEl.top - 20

    edgeMenuPosition.value = { x, y }
  }
}

// Handle edge click event
function handleEdgeClick({ edge }: { edge: EdgeType }) {
  if (selectedEdge.value === edge) {
    selectedEdge.value = null
    return
  }
  
  selectedEdge.value = edge
  updateEdgeMenuPosition(edge)
}

// Watch for changes in node positions and viewport
watch([nodes, viewport], () => {
  if (selectedEdge.value) {
    updateEdgeMenuPosition(selectedEdge.value)
  }
}, { deep: true })

// Handle node drag events
function handleNodeDrag() {
  if (selectedEdge.value) {
    updateEdgeMenuPosition(selectedEdge.value)
  }
}

// Handle viewport change events
function handleViewportChange() {
  if (selectedEdge.value) {
    updateEdgeMenuPosition(selectedEdge.value)
  }
}

// Handle edge deletion
function handleDeleteEdge(e: MouseEvent) {
  e.stopPropagation()
  if (selectedEdge.value) {
    removeEdges([selectedEdge.value])
    selectedEdge.value = null
  }
}

// Clear selection when clicking on canvas
function handlePaneClick() {
  selectedEdge.value = null
}
</script>

<template>
  <div class="relative h-full w-full" id="main-canvas">
    <VueFlow 
      :nodes="props.data.nodes" 
      :edges="props.data.edges" 
      :node-types="nodeTypes" 
      @edge-click="handleEdgeClick"
      @pane-click="handlePaneClick"
      @node-drag-start="handleNodeDrag"
      @node-drag="handleNodeDrag"
      @node-drag-stop="handleNodeDrag"
      @move-start="handleViewportChange"
      @move="handleViewportChange"
      @move-end="handleViewportChange"
      @zoom="handleViewportChange"
      :prevent-scrolling="false"
      :zoom-on-scroll="false"
      :pan-on-scroll="false"
    >
      <Controls />
      <Background />
      <Teleport to="body">
        <div 
          v-if="selectedEdge"
          class="fixed z-50"
          :style="{
            left: `${edgeMenuPosition.x}px`,
            top: `${edgeMenuPosition.y}px`,
            transform: 'translate(-50%, -50%)'
          }"
        >
          <button 
            @click="handleDeleteEdge"
            class="flex items-center justify-center p-1.5 rounded-md bg-white shadow-md border border-gray-200 hover:bg-red-50 transition-colors group"
            title="Delete connection"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              stroke-width="2" 
              stroke-linecap="round" 
              stroke-linejoin="round"
              class="text-gray-400 group-hover:text-red-500"
            >
              <path d="M18 6 6 18" />
              <path d="m6 6 12 12" />
            </svg>
          </button>
        </div>
      </Teleport>
    </VueFlow>
  </div>
</template>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';
@import '@vue-flow/controls/dist/style.css';

#main-canvas {
  --vf-handle: hsl(var(--primary));
  position: relative;
  overflow: hidden;

  .vue-flow__handle {
    width: 18px;
    height: 18px;
  }
}

.vue-flow__edge {
  cursor: pointer;
}

.vue-flow__edge:hover {
  stroke-width: 2;
}

.vue-flow__edge.selected {
  stroke: #ef4444;
  stroke-width: 2;
}

/* 隐藏默认滚动条 */
.vue-flow__viewport {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  &::-webkit-scrollbar {
    display: none; /* Chrome, Safari, Opera */
  }
}
</style>
