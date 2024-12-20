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

// 添加 toast
const { toast } = useToast()

// 修改删除方法
async function handleClickDeleteBtn() {
  try {
    // 立即删除节点
    removeNodes(node.id)
    
    // 显示删除提示
    toast({
      title: 'Deleting conversation history...',
      description: 'The conversation block has been removed.'
    })
    
    // 在后台删除历史记录，添加 block_type 参数
    const response = await axios.post(Block_Action_API, {
      action_type: 'delete',
      workspace_id: workspace_id.value,
      block_id: block_id.value,
      block_type: 'conversation' // 添加 block_type 标识
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

// 监听 blockChats 的化
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

// 添加车发送功能
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
    event.stopPropagation()
    isInMessageArea.value = true
    return
  }
  
  // 检查点击的元素是否在 drag-handle 区域内
  const dragHandle = (event.target as HTMLElement).closest('.drag-handle')
  if (dragHandle) {
    nodesDraggable.value = true
    return
  }

  // 如果是在以上区域内的点击，让事件继续传播以支持线功能
  isInMessageArea.value = false
}

function handleDragEnd(event: MouseEvent) {
  // 只有在消息区域或拖拽手柄区域时才阻止事件传播
  if (isInMessageArea.value || nodesDraggable.value) {
    event.stopPropagation()
  }
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

// 添加新的状态和方法
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
</script>

<template>
  <div 
    :id="node.id" 
    class="rounded-sm border border-gray-200 bg-white p-3 shadow-md fixed-width"
    :class="{ 'node-minimizing': isFullscreen }"
    @selectstart="handleSelectStart"
    @dragstart.prevent="isInMessageArea"
  >
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

.typing-dots {
  display: inline-flex;
  align-items: center;
  height: 20px;
}

.typing-dots span {
  animation: typingDot 1.4s infinite;
  font-size: 20px;
  line-height: 20px;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingDot {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.3;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #666;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  color: #1976d2;
}

/* 确保图标大小致 */
.action-btn i {
  font-size: 1rem;
}

.input-area {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.75rem;
  transition: border-color 0.2s;
  margin: 0;
}

.input-area:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.message-input {
  flex: 1;
  border: none;
  padding: 0;
  background: transparent;
  resize: none;
  max-height: 200px;
  min-height: 24px;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: #111827;
  margin-top: 0;
  padding-top: 0;
}

.message-input:focus {
  outline: none;
}

.message-input::placeholder {
  color: #9ca3af;
}

.send-button {
  padding: 0.5rem;
  border: none;
  background: #3b82f6;
  color: white;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #2563eb;
}

.send-button:disabled {
  background: #e5e7eb;
  cursor: not-allowed;
}

/* Update message bubbles to match fullscreen style */
.message-bubble {
  margin-bottom: 10px;
  padding: 0 12px;
  display: flex;
  text-align: left;
}

.user-message {
  background: #3b82f6;
  color: white;
  border-radius: 1rem;
  border-top-right-radius: 0.25rem;
  padding: 0.75rem 1rem;
}

.ai-message {
  background: #f3f4f6;
  color: #111827;
  border-radius: 1rem;
  border-top-left-radius: 0.25rem;
  padding: 0.75rem 1rem;
}

.input-wrapper {
  margin-top: 0;
  padding: 0;
}

/* Add transition for the node */
.rounded-sm {
  transition: all 0.3s ease;
}

.node-minimizing {
  transform: scale(0.95);
  opacity: 0.5;
}

/* Add transitions for all interactive elements */
.message-bubble,
.input-area,
.send-button,
.action-btn,
textarea {
  transition: all 0.2s ease;
}

/* Add hover effects */
.action-btn {
  transition: transform 0.2s ease, color 0.2s ease;
}

.action-btn:hover {
  transform: scale(1.1);
}

.send-button {
  transition: all 0.2s ease;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.05);
}

/* Smooth transition for message bubbles */
.message-bubble {
  animation: messageFadeIn 0.3s ease;
}

@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Add transition for input area focus */
.input-area {
  transition: all 0.2s ease;
}

.input-area:focus-within {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

/* Add transition for typing dots */
.typing-dots span {
  transition: transform 0.3s ease;
}
</style>
