<script setup lang="ts">
import { ref } from 'vue'
import { useEventBus } from '@vueuse/core'
import { MoreHorizontalIcon } from 'lucide-vue-next'
import { Handle, Position, useVueFlow, useNode } from '@vue-flow/core'
import { Menubar, MenubarMenu, MenubarTrigger, MenubarContent, MenubarItem } from '@/components/ui/menubar'
import { Input } from '@/components/ui/input'
import axios from 'axios'

import { LLMNodeData, LLMNodeEvents } from './index'

import type { NodeProps } from '@vue-flow/core'

const props = defineProps<NodeProps<LLMNodeData, LLMNodeEvents>>()
const { emit } = useEventBus('file-uploaded')

const title = ref(props.data.title)

const isEditTitle = ref(false)

const node = useNode()
const { removeNodes, nodes, addNodes } = useVueFlow()

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

const selectedFile = ref<File | null>(null)

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

const isUploading = ref(false)

async function handleUpload() {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  isUploading.value = true
  try {
    await axios.post('http://127.0.0.1:5000/upload', formData)
    const response = await axios.post('http://localhost:5000/download_vectorized_db')
    if (response.status === 200) {
      console.log('Document Download Success:', response.data.message)
      emit()
    } else {
      console.error('Document Download Failed:', response.data.error)
    }
  } catch (error) {
    console.error('Upload Failed:', error)
    alert('Upload Failed')
  } finally {
    isUploading.value = false
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

            <p class="text-sm text-gray-500">LLM</p>
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

      <span class="text-sm text-gray-500">drag and drop your documents in this node.</span>
      <div>
        <input type="file" @change="handleFileChange" />
        <button @click="handleUpload" :disabled="!selectedFile || isUploading">
          {{ isUploading ? 'Processing, please wait...' : 'Upload' }}
        </button>
      </div>
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
