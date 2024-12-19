<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { MoreHorizontalIcon } from 'lucide-vue-next'
import { Handle, Position, useVueFlow, useNode } from '@vue-flow/core'
import { Menubar, MenubarMenu, MenubarTrigger, MenubarContent, MenubarItem } from '@/components/ui/menubar'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import axios from 'axios'

import { LLMNodeData, LLMNodeEvents } from './index'

import type { NodeProps } from '@vue-flow/core'
import {file_names, documents, BASE_URL, Text_Generation_API, workspace_id, blockChats} from '@/store.ts'


const messages = ref<{ id: number; text: string; isUser: boolean }[]>([])
const userMessage = ref('')

const props = defineProps<NodeProps<LLMNodeData, LLMNodeEvents>>()

const title = ref(props.data.title)

const isEditTitle = ref(false)

const node = useNode()
const { removeNodes, nodes, addNodes, edges } = useVueFlow()

// Define workspace_id and block_id
const block_id = ref(node.id) // Use node ID as block ID

// Send message and receive response
async function sendMessage() {
  if (userMessage.value.trim() === '') return
  
  messages.value.push({ id: Date.now(), text: userMessage.value, isUser: true })

  const userQuery = userMessage.value
  userMessage.value = ''

  const aiResponse = await getAiResponse(userQuery)
  messages.value.push({ id: Date.now() + 1, text: aiResponse, isUser: false })
}

// Simulate AI response function (you can replace this with an actual API call)
async function getAiResponse(userText: string): Promise<string> {
  try {
    const response = await axios.post(Text_Generation_API, { 
      query: userText,
      workspace_id: workspace_id.value,
      block_id: block_id.value
    })
    return response.data.body || 'No answer was generated.'
  } catch (error) {
    console.error('Error fetching answer from server:', error)
    return 'Error: Unable to get response from server.'
  }
}

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

function handleScroll(event: WheelEvent) {
  event.stopPropagation();
}

// 从 blockChats 中加载消息
const loadMessages = () => {
  if (!Array.isArray(blockChats.value)) {
    console.error('blockChats.value is not an array:', blockChats.value)
    return
  }

  const blockChat = blockChats.value.find(chat => chat.blockId === node.id)
  if (blockChat) {
    messages.value = blockChat.messages
  }
}

// 监听 blockChats 的变化
watch(blockChats, () => {
  loadMessages()
}, { deep: true })

// 组件挂载时加载消息
onMounted(() => {
  loadMessages()
})
</script>

<template>
  <div class="rounded-sm border border-gray-200 bg-white p-3 shadow-md fixed-width">
    <Handle type="target" :position="Position.Left" />
    <div class="flex flex-col gap-y-4">
      <div class="flex justify-between">
        <div class="flex gap-x-2">
          <img src="~@/assets/images/icon_LLM.png" class="mt-1 h-4 w-4" alt="LLM icon" />
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

      <span class="text-sm text-gray-500">Chat with your document directly in this node.</span>
      <div class="flex flex-col gap-y-4">
        <!-- Message Display Area -->
        <div
          class="message-display-area h-40 overflow-y-auto overflow-x-hidden border-t border-b border-gray-200 py-2"
          @wheel="handleScroll"
        >
          <div
            v-for="message in messages"
            :key="message.id"
            :class="{ 'text-right': message.isUser, 'text-left': !message.isUser }"
            class="message-bubble"
          >
            <div
              class="p-2 rounded-lg w-full"
              :class="message.isUser ? 'bg-blue-200 user-message' : 'bg-gray-200 ai-message'"
              style="white-space: pre-wrap; word-break: break-word;"
            >
              {{ message.text }}
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="flex gap-x-2 items-center">
          <Input v-model="userMessage" placeholder="Type your message..." class="flex-1" />
          <Button @click="sendMessage">Send</Button>
        </div>
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
