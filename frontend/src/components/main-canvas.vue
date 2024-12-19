<script setup lang="ts">
import { markRaw, nextTick, ref, onMounted, watch } from 'vue'
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

const props = defineProps<{
  data: { nodes: Node[]; edges: Edge[]; position: [number, number]; zoom: number }
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

onMounted(() => {
  nextTick(() => {
    if (props.data) {
      setNodes(props.data.nodes)
      setEdges(props.data.edges)
      setViewport({ x: props.data.position[0], y: props.data.position[1], zoom: props.data.zoom })
    }
  })
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

const selectedEdge = ref(null)
const edgeMenuPosition = ref({ x: 0, y: 0 })

function updateEdgeMenuPosition(edge) {
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
function handleEdgeClick({ edge }) {
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
</style>
