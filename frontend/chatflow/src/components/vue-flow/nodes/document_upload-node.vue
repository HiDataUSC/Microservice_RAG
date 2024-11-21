<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useEventBus } from '@vueuse/core'
import { MoreHorizontalIcon } from 'lucide-vue-next'
import { Handle, Position, useVueFlow, useNode } from '@vue-flow/core'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Menubar, MenubarMenu, MenubarTrigger, MenubarContent, MenubarItem } from '@/components/ui/menubar'
import { Input } from '@/components/ui/input'
import axios from 'axios'

import { LLMNodeData, LLMNodeEvents } from './index'

import type { NodeProps } from '@vue-flow/core'
import {file_names, documents, BASE_URL} from '@/main.js'

const props = defineProps<NodeProps<LLMNodeData, LLMNodeEvents>>()

const title = ref(props.data.title)

const isEditTitle = ref(false)
const showDropdown = ref(false)
const selectedFiles = ref<any[]>([])

const node = useNode()
const { removeNodes, nodes, addNodes } = useVueFlow()

onMounted(() => {
  node.node.data = {
    ...node.node.data,
    selectedFiles: []
  }
})

watch(selectedFiles, (newFiles) => {
  const newData = {
    ...node.node.data,
    title: title.value,
    selectedFiles: newFiles
  }
  node.node.data = newData
}, { deep: true })

function handleClickDeleteBtn() {
  removeNodes(node.id)
}

function handleClickDuplicateBtn() {
  const { type, position, label, data } = node.node
  const newNode = {
    id: (nodes.value.length + 1).toString(),
    type,
    position: {
      x: position.x + 100,
      y: position.y + 100
    },
    label,
    data
  }
  addNodes(newNode)
}

function handleFileSelect(fileName: string) {
  const document = documents.value.find(doc => doc.metadata.name === fileName)
  if (document && !selectedFiles.value.some(file => file.metadata.name === fileName)) {
    selectedFiles.value = [...selectedFiles.value, document]
  }
}

function handleSelectAll() {
  const allDocs = documents.value.filter(doc => 
    !selectedFiles.value.some(selected => selected.metadata.name === doc.metadata.name)
  )
  selectedFiles.value = [...selectedFiles.value, ...allDocs]
  showDropdown.value = false
}

function removeSelectedFile(file: any) {
  selectedFiles.value = selectedFiles.value.filter(f => f.metadata.name !== file.metadata.name)
}

function handleWheel(event: WheelEvent) {
  if (showDropdown.value) {
    event.preventDefault()
    const container = event.currentTarget as HTMLElement
    container.scrollTop += event.deltaY
  }
}

</script>

<template>
  <div class="rounded-sm border border-gray-200 bg-white p-3 shadow-md fixed-width">
    <Handle type="target" :position="Position.Left" />
    <div class="flex flex-col gap-y-4">
      <div class="flex justify-between">
        <div class="flex gap-x-2">
          <img src="~@/assets/images/icon_Knowledge.png" class="mt-1 h-4 w-4" alt="Knowledge icon" />
          <div class="flex flex-col gap-y-1">
            <Input v-model="title" class="h-5" v-if="isEditTitle" @blur="() => (isEditTitle = false)" />
            <h3 class="text-base" v-else>{{ title }}</h3>

            <p class="text-sm text-gray-500">Knowledge Base</p>
          </div>
        </div>

        <Menubar class="border-none">
          <menubar-menu>
            <menubar-trigger>
              <more-horizontal-icon />
            </menubar-trigger>
            <menubar-content>
              <menubar-item @click="handleClickDuplicateBtn"> Duplicated </menubar-item>
              <menubar-item @click="handleClickDeleteBtn"> Delete </menubar-item>
              <menubar-item @click="isEditTitle = true"> Rename </menubar-item>
            </menubar-content>
          </menubar-menu>
        </Menubar>
      </div>

      <span class="text-sm text-gray-500">Select Files in this knowledge base.</span>
      <div class="relative">
        <button 
          @click="showDropdown = !showDropdown"
          class="w-full p-2 border rounded flex justify-between items-center"
        >
          <span>Choose Files</span>
          <span class="ml-2">▼</span>
        </button>
      
        <div 
          v-show="showDropdown" 
          class="absolute top-full left-0 w-full mt-1 bg-white border rounded shadow-lg z-10"
        >
          <div 
            @click="handleSelectAll"
            class="p-2 hover:bg-gray-100 cursor-pointer text-blue-600 font-medium border-b"
          >
            Select All
          </div>
          <div class="max-h-40 overflow-y-auto">
            <div 
              v-for="file in file_names" 
              :key="file"
              @click="handleFileSelect(file); showDropdown = false"
              class="p-2 hover:bg-gray-100 cursor-pointer"
            >
              {{ file }}
            </div>
          </div>
        </div>
      </div>
      <ScrollArea class="h-[calc(400px-150px)] w-full">
        <div class="flex flex-col gap-2">
          <div 
            v-for="file in selectedFiles" 
            :key="file"
            class="flex items-center justify-between p-2 bg-gray-50 rounded"
          >
            <span>{{ file.metadata.name }}</span>
            <button 
              @click="removeSelectedFile(file)"
              class="text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        </div>
      </ScrollArea>
    </div>
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<style scoped>
.resizable-container {
  width: 100%;
  height: 100%;
}

.resizable-content {
  height: 100%;
  width: 100%;
}

.text-right {
  text-align: right;
}
.text-left {
  text-align: left;
}

.fixed-width {
  width: 600px;
}

.message-display-area {
  max-height: 200px;
  overflow-y: auto;
}

.message-bubble {
  margin-bottom: 10px;
}

.user-message {
  margin-left: 40px;
  margin-right: 0;
  max-width: calc(100% - 40px);
}

.ai-message {
  margin-left: 0px;
  margin-right: 40px;
  max-width: calc(100% - 40px);
}
</style>
