<template>
  <Transition name="fullscreen">
    <div class="fullscreen-conversation">
      <div class="header">
        <div class="header-content">
          <h2>Conversation</h2>
          <button class="exit-fullscreen" @click="$emit('exit')" title="Exit fullscreen">
            <i class="fas fa-compress"></i>
          </button>
        </div>
      </div>
      
      <div class="conversation-content">
        <div class="messages" ref="messagesContainer">
          <div v-for="message in messages" :key="message.id" class="message">
            <div :class="['message-content', message.isUser ? 'user' : 'assistant']">
              <div class="message-bubble">
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
        </div>
        
        <div class="input-wrapper">
          <div class="input-area">
            <textarea
              v-model="userInput"
              @keydown.enter.prevent="handleSend"
              placeholder="Type your message... (Press Enter to send)"
              rows="1"
              ref="textarea"
              @input="autoResize"
            ></textarea>
            <button 
              @click="handleSend" 
              :disabled="isGenerating"
              class="send-button"
            >
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';

const props = defineProps<{
  messages: Array<{
    id: number;
    text: string;
    isUser: boolean;
  }>;
  isGenerating: boolean;
  userInput: string;
}>();

const emit = defineEmits(['exit', 'send', 'update:user-input']);

const userInput = computed({
  get: () => props.userInput,
  set: (value) => emit('update:user-input', value)
});

const messagesContainer = ref<HTMLElement | null>(null);
const textarea = ref<HTMLTextAreaElement | null>(null);

const handleSend = () => {
  if (userInput.value.trim() && !props.isGenerating) {
    emit('send', userInput.value);
    emit('update:user-input', '');
    if (textarea.value) {
      textarea.value.style.height = 'auto';
    }
  }
};

const autoResize = () => {
  if (textarea.value) {
    textarea.value.style.height = 'auto';
    textarea.value.style.height = `${textarea.value.scrollHeight}px`;
  }
};

// Auto scroll to bottom when messages update
watch(() => props.messages, () => {
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  }, 100);
}, { deep: true });
</script>

<style scoped>
.fullscreen-conversation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #ffffff;
  z-index: 9999;
  display: flex;
  flex-direction: column;
}

.header {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.75rem 1rem;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.header-content {
  max-width: 768px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1rem;
}

.header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.exit-fullscreen {
  padding: 0.5rem;
  border: none;
  background: none;
  cursor: pointer;
  color: #6b7280;
  border-radius: 0.375rem;
  transition: all 0.2s;
  font-size: 1.2rem;
}

.exit-fullscreen:hover {
  background: #f3f4f6;
  color: #111827;
}

.conversation-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 768px;
  margin: 0 auto;
  width: 100%;
  height: calc(100vh - 60px);
  position: relative;
  padding: 0 1rem;
  transition: all 0.3s ease;
  animation: slideUp 0.3s ease;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
  scroll-behavior: smooth;
}

.message {
  margin-bottom: 1.5rem;
}

.message-content {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.message-content.user {
  justify-content: flex-end;
}

.message-bubble {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  max-width: 80%;
  line-height: 1.5;
  position: relative;
  font-size: 0.9375rem;
  transition: all 0.2s ease;
}

.message-content.user .message-bubble {
  background: #3b82f6;
  color: white;
  border-top-right-radius: 0.25rem;
}

.message-content.assistant .message-bubble {
  background: #f3f4f6;
  color: #111827;
  border-top-left-radius: 0.25rem;
}

.input-wrapper {
  padding: 1rem;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
  margin: 0;
  animation: fadeIn 0.3s ease;
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
  transition: all 0.2s ease;
}

.input-area:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

textarea {
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
  transition: all 0.2s ease;
}

textarea:focus {
  outline: none;
}

textarea::placeholder {
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
  transition: all 0.2s ease;
}

.send-button:hover:not(:disabled) {
  background: #2563eb;
}

.send-button:disabled {
  background: #e5e7eb;
  cursor: not-allowed;
}

/* Typing animation */
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

/* Scrollbar styling */
.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: transparent;
}

.messages::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Add transition animations */
.fullscreen-enter-active,
.fullscreen-leave-active {
  transition: all 0.3s ease;
}

.fullscreen-enter-from,
.fullscreen-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.fullscreen-enter-to,
.fullscreen-leave-from {
  opacity: 1;
  transform: scale(1);
}

/* Optional: Add transition for the content */
.conversation-content {
  transition: all 0.3s ease;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Add transition for input area */
.input-wrapper {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Add smooth transition for all interactive elements */
.header,
.message-bubble,
.input-area,
.send-button,
textarea {
  transition: all 0.2s ease;
}
</style> 