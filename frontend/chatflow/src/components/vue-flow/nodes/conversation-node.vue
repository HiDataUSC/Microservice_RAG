<script setup lang="ts">
import { ref } from 'vue'
import { Handle, Position, useNode } from '@vue-flow/core'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

// Placeholder for conversation messages
const messages = ref<{ id: number; text: string; isUser: boolean }[]>([])
const userMessage = ref('')

// Send message and receive response
async function sendMessage() {
  if (userMessage.value.trim() === '') return
  
  // Add user message to conversation
  messages.value.push({ id: Date.now(), text: userMessage.value, isUser: true })

  // Clear input
  userMessage.value = ''

  // Simulate an AI response
  const aiResponse = await getAiResponse(messages.value.at(-1)?.text || '')
  messages.value.push({ id: Date.now() + 1, text: aiResponse, isUser: false })
}

// Simulate AI response function (you can replace this with an actual API call)
async function getAiResponse(userText: string): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(`AI response to: "${userText}"`)
    }, 1000)
  })
}
</script>

<template>
  <div class="rounded-sm border border-gray-200 bg-white p-3 shadow-md max-w-xs">
    <Handle type="target" :position="Position.Left" />
    <div class="flex flex-col gap-y-4">
      <div class="flex gap-x-2 items-center">
        <!-- <img src="~@/assets/images/icon_Conversation.png" class="h-4 w-4" alt="Conversation icon" /> -->
        <h3 class="text-base">Conversation</h3>
      </div>
      <div class="text-sm text-gray-500">Interact with the model directly in this node.</div>

      <!-- Message Display Area -->
      <div class="h-40 overflow-y-auto border-t border-b border-gray-200 py-2">
        <div v-for="message in messages" :key="message.id" :class="{ 'text-right': message.isUser, 'text-left': !message.isUser }">
          <div
            class="p-2 rounded-lg"
            :class="message.isUser ? 'bg-blue-200' : 'bg-gray-200'"
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
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<style scoped>
.text-right {
  text-align: right;
}
.text-left {
  text-align: left;
}
</style>
