<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { MoreHorizontalIcon } from 'lucide-vue-next'
import { Handle, Position, useVueFlow, useNode } from '@vue-flow/core'
import { Menubar, MenubarMenu, MenubarTrigger, MenubarContent, MenubarItem } from '@/components/ui/menubar'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import axios from 'axios'
import { useToast } from '@/components/ui/toast'

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

// Send message and receive response
async function sendMessage() {
  if (userMessage.value.trim() === '') return
  
  messages.value.push({ id: Date.now(), text: userMessage.value, isUser: true })
  
  // 在添加用户消息后滚动到底部
  nextTick(() => scrollToBottom())

  const userQuery = userMessage.value
  userMessage.value = ''

  const aiResponse = await getAiResponse(userQuery)
  messages.value.push({ id: Date.now() + 1, text: aiResponse, isUser: false })
  
  // 在添加 AI 响应后滚动到底部
  nextTick(() => scrollToBottom())
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

// 添加 toast
const { toast } = useToast()

// 修改删除方法
async function handleClickDeleteBtn() {
  try {
    // 立即删除节点
    removeNodes(node.id)
    
    // 显示删除中的提示
    toast({
      title: 'Deleting conversation history...',
      description: 'The conversation block has been removed.'
    })
    
    // 在后台删除历史记录
    const response = await axios.post(Block_Action_API, {
      action_type: 'delete',
      workspace_id: workspace_id.value,
      block_id: block_id.value
    })
    
    if (response.status === 200) {
      // 删除成功的提示
      toast({
        title: 'Success',
        description: 'Conversation history has been deleted'
      })
    } else {
      // 如果删除历史记录失败，提示用户但不恢复节点
      toast({
        title: 'Warning',
        description: 'Block removed but there was an issue deleting the conversation history',
        variant: 'destructive'
      })
    }
  } catch (error) {
    // 如果发生错误，提示用户但不恢复节点
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

// 从 blockChats 中加载消息
const loadMessages = () => {
  if (!Array.isArray(blockChats.value)) {
    console.error('blockChats.value is not an array:', blockChats.value)
    return
  }

  const blockChat = blockChats.value.find(chat => chat.blockId === node.id)
  if (blockChat) {
    messages.value = blockChat.messages
    // 在加载消息后滚动到底部
    nextTick(() => scrollToBottom())
  }
}

// 监听 blockChats 的��化
watch(blockChats, () => {
  loadMessages()
}, { deep: true })

// 组件挂载时加载消息
onMounted(() => {
  loadMessages()
  
  // 添加拖拽相关的事件监听
  const nodeElement = document.getElementById(node.id)
  if (nodeElement) {
    nodeElement.addEventListener('mousedown', handleDragStart)
    nodeElement.addEventListener('mouseup', handleDragEnd)
    // 添加 mouseleave 以处理拖出节点的情况
    nodeElement.addEventListener('mouseleave', handleDragEnd)
  }
})

// 在 onUnmounted 中清理事件监听
onUnmounted(() => {
  const nodeElement = document.getElementById(node.id)
  if (nodeElement) {
    nodeElement.removeEventListener('mousedown', handleDragStart)
    nodeElement.removeEventListener('mouseup', handleDragEnd)
    nodeElement.removeEventListener('mouseleave', handleDragEnd)
  }
})

// 添加回车发送功能
function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// 设置节点默认不可拖拽
nodesDraggable.value = false

// 修改拖拽处理函数
function handleDragStart(event: MouseEvent) {
  // 检查点击的元素是否在消息区域内
  const messageArea = (event.target as HTMLElement).closest('.message-display-area')
  if (messageArea) {
    // 阻止事件冒泡，防止触发画布拖拽
    event.stopPropagation()
    isInMessageArea.value = true
    return
  }
  
  // 检查点击的元素是否在 drag-handle 区域内
  const dragHandle = (event.target as HTMLElement).closest('.drag-handle')
  if (dragHandle) {
    nodesDraggable.value = true
  }
}

function handleDragEnd(event: MouseEvent) {
  // 阻止事件冒泡
  event.stopPropagation()
  isInMessageArea.value = false
  nodesDraggable.value = false
}

// 添加鼠标离开消息区域的处理
function handleMouseLeave(event: MouseEvent) {
  event.stopPropagation()
  isInMessageArea.value = false
}

// 添加文本选择开始处理
function handleSelectStart(event: Event) {
  if (isInMessageArea.value) {
    event.stopPropagation()
  }
}

// 添加状态来跟踪是否在消息区域内
const isInMessageArea = ref(false)

// 在 script setup 部分添加一个新的函数
function scrollToBottom() {
  const messageArea = document.querySelector(`#${node.id} .message-display-area`)
  if (messageArea) {
    messageArea.scrollTop = messageArea.scrollHeight
  }
}
</script>

<template>
  <div 
    :id="node.id" 
    class="rounded-sm border border-gray-200 bg-white p-3 shadow-md fixed-width"
    @selectstart="handleSelectStart"
    @dragstart.prevent
  >
    <Handle type="target" :position="Position.Left" />
    <div class="flex flex-col gap-y-4">
      <div class="drag-handle">
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
              {{ message.text }}
            </div>
          </div>
        </div>

        <div class="input-area flex gap-x-2 items-center">
          <textarea
            v-model="userMessage"
            placeholder="Type your message... (Press Enter to send)"
            class="flex-1 min-h-[40px] max-h-[120px] p-2 rounded-md border border-input bg-background resize-none overflow-y-auto"
            @keypress="handleKeyPress"
            @mousedown.stop
            @dragstart.prevent
            @mouseenter="isInMessageArea = true"
            @mouseleave="handleMouseLeave"
          />
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
  user-select: text;
  position: relative;
  z-index: 1;
  pointer-events: auto;
  /* 确保消息区域可以独立处理事件 */
  isolation: isolate;
  -webkit-user-drag: none;
}

.message-bubble {
  margin-bottom: 10px;
  padding: 0 12px;
  display: flex;
  text-align: left;
  user-select: text;
  pointer-events: auto;
  -webkit-user-drag: none;
}

.user-message {
  background-color: #e3f2fd;
  border: 1px solid #bbdefb;
  cursor: text;
  position: relative;
  z-index: 2;
}

.ai-message {
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  cursor: text;
  position: relative;
  z-index: 2;
}

textarea {
  font-family: inherit;
  line-height: 1.5;
  position: relative;
  z-index: 2;
  user-select: text;
  -webkit-user-drag: none;
  &:focus {
    outline: none;
    border-color: hsl(var(--primary));
    ring: 1px solid hsl(var(--primary));
  }
}

.drag-handle {
  cursor: move;
  padding: 8px;
  width: 100%;
  user-select: none;
  position: relative;
  z-index: 3;
  pointer-events: auto;
  /* 确保拖拽句柄的事件不会影响其他区域 */
  isolation: isolate;
}

.message-display-area,
.input-area {
  cursor: default;
  user-select: text;
}

/* 添加防止拖拽时选中文本 */
.drag-handle * {
  user-select: none;
}

.input-area {
  cursor: default;
  user-select: text;
  position: relative;
  z-index: 2;
  isolation: isolate;
  pointer-events: auto;
}
</style>
