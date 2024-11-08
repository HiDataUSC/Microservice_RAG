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

const { findNode, nodes, addNodes, addEdges, project, vueFlowRef, onConnect, setNodes, setEdges, setViewport } = useVueFlow()

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

function handleOnDrop(event: DragEvent) {
  const type = event.dataTransfer?.getData('application/vueflow')
  if (type === 'workflow') {
    const { nodes, edges, position, zoom } = Test_data
    const [x = 0, y = 0] = position
    setNodes(nodes)
    setEdges(edges)
    setViewport({ x, y, zoom: zoom || 0 })
    return
  }

  const { left, top } = vueFlowRef.value!.getBoundingClientRect()

  const position = project({
    x: event.clientX - left,
    y: event.clientY - top
  })

  const newNode = {
    id: (nodes.value.length + 1).toString(),
    type,
    position,
    label: `${type} node`,
    data: {
      title: type
    }
  }

  addNodes([newNode])

  nextTick(() => {
    const node = findNode(newNode.id)
    const stop = watch(
      () => node!.dimensions,
      (dimensions: Dimensions) => {
        if (dimensions.width > 0 && dimensions.height > 0 && node) {
          node.position = {
            x: node.position.x - node.dimensions.width / 2,
            y: node.position.y - node.dimensions.height / 2
          }
          stop()
        }
      },
      { deep: true, flush: 'post' }
    )
  })
}

function handleOnDragOver(event: DragEvent) {
  event.preventDefault()

  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}
</script>

<template>
  <div class="relative h-full w-full" id="main-canvas" @drop="handleOnDrop" @dragover="handleOnDragOver">
    <VueFlow :nodes="props.data.nodes" :edges="props.data.edges" :node-types="nodeTypes">
      <Controls />
      <Background />
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
</style>
