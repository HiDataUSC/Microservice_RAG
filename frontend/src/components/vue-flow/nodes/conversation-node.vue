<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { MoreHorizontalIcon } from 'lucide-vue-next'
import { Handle, Position, useVueFlow, useNode } from '@vue-flow/core'
import { Menubar, MenubarMenu, MenubarTrigger, MenubarContent, MenubarItem } from '@/components/ui/menubar'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import axios from 'axios'
import { useToast } from '@/components/ui/toast'
import FullscreenConversation from '@/components/fullscreen-conversation.vue'
import { Teleport } from 'vue'

import { LLMNodeData, LLMNodeEvents } from './index'

import type { NodeProps } from '@vue-flow/core'
import {file_names, documents, BASE_URL, Text_Generation_API, workspace_id, blockChats, Block_Action_API} from '@/store.ts'


const messages = ref<{ id: number; text: string; isUser: boolean }[]>([])
const userMessage = ref('')

const props = defineProps<NodeProps<LLMNodeData, LLMNodeEvents>>()

const title = ref(props.data.title)

const isEditTitle = ref(false)

const node = useNode()
const { removeNodes, nodes, addNodes, edges, nodesDraggable } = useVueFlow()

// Define workspace_id and block_id
const block_id = ref(node.id) // Use node ID as block ID

// 在 script setup 部分添加状态
const isGenerating = ref(false)

// Send message and receive response
async function sendMessage() {
  if (userMessage.value.trim() === '') return
  
  messages.value.push({ id: Date.now(), text: userMessage.value, isUser: true })
  
  // 在添加用户消息后滚动到底部
  nextTick(() => scrollToBottom())

  const userQuery = userMessage.value
  userMessage.value = ''

  // 添加一个临时的 AI 消息，显示加载状态
  const tempMessageId = Date.now() + 1
  messages.value.push({ id: tempMessageId, text: '...', isUser: false })
  nextTick(() => scrollToBottom())
  
  isGenerating.value = true
  
  try {
    const aiResponse = await getAiResponse(userQuery)
    // 更新临时消息的内容
    const messageIndex = messages.value.findIndex(m => m.id === tempMessageId)
    if (messageIndex !== -1) {
      messages.value[messageIndex].text = aiResponse
    }
  } catch (error) {
    // 如果发生错误，更新临时消息显示错误信息
    const messageIndex = messages.value.findIndex(m => m.id === tempMessageId)
    if (messageIndex !== -1) {
      messages.value[messageIndex].text = 'Error: Unable to get response from server.'
    }
  } finally {
    isGenerating.value = false
    nextTick(() => scrollToBottom())
  }
}

// Simulate AI response function (you can replace this with an actual API call)
async function getAiResponse(userText: string): Promise<string> {
  try {
    // 获取与当前节点相连的所有节点信息
    const nodeConnections = edges.value
      .filter(edge => edge.source === node.id || edge.target === node.id)
      .map(edge => {
        const connectedNodeId = edge.source === node.id ? edge.target : edge.source
        const connectedNode = nodes.value.find(n => n.id === connectedNodeId)
        return {
          id: connectedNodeId,
          type: connectedNode?.type || 'unknown'
        }
      })

    const response = await axios.post(Text_Generation_API, { 
      query: userText,
      workspace_id: workspace_id.value,
      block_id: block_id.value,
      connections: nodeConnections // 添加连接信息
    })
    return response.data.body || 'No answer was generated.'
  } catch (error) {
    console.error('Error fetching answer from server:', error)
    return 'Error: Unable to get response from server.'
  }
}

const { toast } = useToast()

async function handleClickDeleteBtn() {
  try {
    removeNodes(node.id)
    toast({
      title: 'Deleting conversation history...',
      description: 'The conversation block has been removed.'
    })
    
    const response = await axios.post(Block_Action_API, {
      action_type: 'delete',
      workspace_id: workspace_id.value,
      block_id: block_id.value,
      block_type: 'conversation' 
    })
    
    if (response.status === 200) {
      toast({
        title: 'Success',
        description: 'Conversation history has been deleted'
      })
    } else {
      toast({
        title: 'Warning',
        description: 'Block removed but there was an issue deleting the conversation history',
        variant: 'destructive'
      })
    }
  } catch (error) {
    toast({
      title: 'Error',
      description: 'Block removed but failed to delete conversation history',
      variant: 'destructive'
    })
    console.error('Error deleting conversation block:', error)
  }
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

const loadMessages = () => {
  if (!Array.isArray(blockChats.value)) {
    console.error('blockChats.value is not an array:', blockChats.value)
    return
  }

  const blockChat = blockChats.value.find(chat => chat.blockId === node.id)
  if (blockChat) {
    messages.value = blockChat.messages
    nextTick(() => scrollToBottom())
  }
}

watch(blockChats, () => {
  loadMessages()
}, { deep: true })

onMounted(() => {
  loadMessages()
  
  const nodeElement = document.getElementById(node.id)
  if (nodeElement) {
    nodeElement.addEventListener('mousedown', handleDragStart)
    nodeElement.addEventListener('mouseup', handleDragEnd)
    nodeElement.addEventListener('mouseleave', handleDragEnd)
  }
})

onUnmounted(() => {
  const nodeElement = document.getElementById(node.id)
  if (nodeElement) {
    nodeElement.removeEventListener('mousedown', handleDragStart)
    nodeElement.removeEventListener('mouseup', handleDragEnd)
    nodeElement.removeEventListener('mouseleave', handleDragEnd)
  }
})

function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

nodesDraggable.value = false

function handleDragStart(event: MouseEvent) {
  const messageArea = (event.target as HTMLElement).closest('.message-display-area')
  if (messageArea) {
    event.stopPropagation()
    isInMessageArea.value = true
    return
  }
  
  const dragHandle = (event.target as HTMLElement).closest('.drag-handle')
  if (dragHandle) {
    nodesDraggable.value = true
    return
  }

  isInMessageArea.value = false
}

function handleDragEnd(event: MouseEvent) {
  if (isInMessageArea.value || nodesDraggable.value) {
    event.stopPropagation()
  }
  isInMessageArea.value = false
  nodesDraggable.value = false
}

function handleMouseLeave(event: MouseEvent) {
  event.stopPropagation()
  isInMessageArea.value = false
}

function handleSelectStart(event: Event) {
  if (isInMessageArea.value) {
    event.stopPropagation()
  }
}

const isInMessageArea = ref(false)

function scrollToBottom() {
  const messageArea = document.querySelector(`#${node.id} .message-display-area`)
  if (messageArea) {
    messageArea.scrollTop = messageArea.scrollHeight
  }
}

const isFullscreen = ref(false)

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const handleSend = (message: string) => {
  // Use the existing sendMessage function
  userMessage.value = message;
  sendMessage();
};

// Add autoResize function
const textarea = ref<HTMLTextAreaElement | null>(null);

const autoResize = () => {
  if (textarea.value) {
    textarea.value.style.height = 'auto';
    textarea.value.style.height = `${textarea.value.scrollHeight}px`;
  }
};

const handleExitFullscreen = () => {
  // Add a small delay to allow the animation to complete
  isFullscreen.value = false;
};

// 添加计算连接节点的逻辑
const connectedNodes = computed(() => {
  return edges.value
    .filter(edge => edge.source === node.id || edge.target === node.id)
    .map(edge => {
      const connectedNodeId = edge.source === node.id ? edge.target : edge.source
      const connectedNode = nodes.value.find(n => n.id === connectedNodeId)
      return {
        id: connectedNodeId,
        title: connectedNode?.data?.title || connectedNodeId
      }
    })
})

// 格式化显示文本
const connectedNodesText = computed(() => {
  return connectedNodes.value
    .map(node => node.title)
    .join(', ')
})

// 添加气泡行数的计算
const bubbleRows = computed(() => {
  if (!connectedNodes.value.length) return 0;
  // 假设每个气泡宽度平均200px，加上间距6px，在600px宽度的容器中计算行数
  const bubblesPerRow = Math.floor(600 / (200 + 6));
  return Math.ceil(connectedNodes.value.length / bubblesPerRow);
});
</script>

<template>
  <div 
    :id="node.id" 
    class="rounded-sm border border-gray-200 bg-white p-3 shadow-md fixed-width"
    :class="{ 'node-minimizing': isFullscreen }"
    @selectstart="handleSelectStart"
    @dragstart.prevent="isInMessageArea"
  >
    <!-- 修改共享记忆提示为多个气泡 -->
    <div v-if="connectedNodes.length > 0" class="memory-sharing-bubbles">
      <div 
        v-for="node in connectedNodes" 
        :key="node.id" 
        class="memory-sharing-indicator"
      >
        Sharing with: {{ node.title }}
      </div>
    </div>

    <Handle type="target" :position="Position.Left" />
    
    <div class="drag-handle">
      <div class="flex justify-between items-center">
        <div class="flex gap-x-2">
          <img src="~@/assets/images/icon_LLM.png" class="mt-1 h-4 w-4" alt="LLM icon" />
          <div class="flex flex-col gap-y-1">
            <Input v-model="title" class="h-5" v-if="isEditTitle" @blur="() => (isEditTitle = false)" />
            <h3 class="text-base" v-else>{{ title }}</h3>
            <p class="text-sm text-gray-500">LLM</p>
          </div>
        </div>

        <div class="flex items-center">
          <button class="action-btn mr-2" @click="toggleFullscreen">
            <i class="fas" :class="isFullscreen ? 'fa-compress' : 'fa-expand'"></i>
          </button>
          
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
      </div>

      <span class="text-sm text-gray-500">Chat with AI</span>
    </div>

    <div class="flex flex-col gap-y-4">
      <div
        class="message-display-area h-40 overflow-y-auto overflow-x-hidden border-t border-b border-gray-200 py-2"
        @wheel="handleScroll"
        @mouseleave="handleMouseLeave"
        @mouseenter="isInMessageArea = true"
        @mousedown.stop
        @dragstart.prevent
      >
        <div
          v-for="message in messages"
          :key="message.id"
          :class="{ 'flex justify-end': message.isUser, 'flex justify-start': !message.isUser }"
          class="message-bubble"
          @dragstart.prevent
        >
          <div
            class="p-3 rounded-lg inline-block max-w-[85%]"
            :class="message.isUser ? 'bg-blue-200 user-message' : 'bg-gray-200 ai-message'"
            style="white-space: pre-wrap; word-break: break-word; user-select: text;"
          >
            <template v-if="!message.isUser && message.text === '...'">
              <span class="typing-dots">
                <span>.</span><span>.</span><span>.</span>
              </span>
            </template>
            <template v-else>
              {{ message.text }}
            </template>
          </div>
        </div>
      </div>

      <div class="input-wrapper">
        <div class="input-area">
          <textarea
            v-model="userMessage"
            placeholder="Type your message... (Press Enter to send)"
            class="message-input"
            @keypress="handleKeyPress"
            @mousedown.stop
            @dragstart.prevent
            @mouseenter="isInMessageArea = true"
            @mouseleave="handleMouseLeave"
            ref="textarea"
            @input="autoResize"
            rows="1"
          />
          <button 
            class="send-button" 
            @click="sendMessage"
            :disabled="isGenerating"
          >
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>
    <Handle type="source" :position="Position.Right" />
  </div>

  <Teleport to="body">
    <FullscreenConversation
      v-if="isFullscreen"
      :messages="messages"
      :is-generating="isGenerating"
      :user-input="userMessage"
      @update:user-input="(val) => userMessage = val"
      @exit="handleExitFullscreen"
      @send="sendMessage"
    />
  </Teleport>
</template>

<style scoped>
@import './css/conversation-node.css';
</style>

