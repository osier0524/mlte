<template>
  <Teleport to="body">
    <div v-if="messages.length > 0" class="toast-container">
      <transition-group name="toast-fade">
        <div 
          v-for="msg in messages" 
          :key="msg.id"
          class="toast-message"
          :class="[`toast-${msg.type}`]"
        >
          <div class="toast-content">
            <div class="toast-icon">
              <span v-if="msg.type === 'success'">✓</span>
              <span v-else-if="msg.type === 'error'">✕</span>
              <span v-else-if="msg.type === 'warning'">!</span>
              <span v-else>i</span>
            </div>
            <div class="toast-text">{{ msg.text }}</div>
          </div>
          <button 
            @click="removeMessage(msg.id)" 
            class="toast-close"
          >
            ×
          </button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface ToastMessage {
  id: number;
  text: string;
  type: ToastType;
}

const messages = ref<ToastMessage[]>([])
const counter = ref(0)

const addMessage = (text: string, type: ToastType = 'info', timeout: number = 3000): number => {
  const id = counter.value++
  messages.value.push({ id, text, type })
  
  if (timeout > 0) {
    setTimeout(() => removeMessage(id), timeout)
  }
  
  return id
}

const removeMessage = (id: number): void => {
  const index = messages.value.findIndex(m => m.id === id)
  if (index !== -1) {
    messages.value.splice(index, 1)
  }
}

defineExpose({
  success: (text: string, timeout?: number) => addMessage(text, 'success', timeout),
  error: (text: string, timeout?: number) => addMessage(text, 'error', timeout),
  warning: (text: string, timeout?: number) => addMessage(text, 'warning', timeout),
  info: (text: string, timeout?: number) => addMessage(text, 'info', timeout),
  addMessage,
  removeMessage
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  left: 50%; 
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
}

.toast-message {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: white;
  color: #333;
  min-width: 250px;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-weight: bold;
  flex-shrink: 0;
}

.toast-text {
  font-size: 14px;
  line-height: 1.4;
}

.toast-close {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  color: #666;
  margin-left: 12px;
  padding: 4px;
}

.toast-close:hover {
  color: #333;
}

.toast-success {
  border-left: 4px solid #4CAF50;
}

.toast-success .toast-icon {
  color: white;
  background-color: #4CAF50;
}

.toast-error {
  border-left: 4px solid #F44336;
}

.toast-error .toast-icon {
  color: white;
  background-color: #F44336;
}

.toast-warning {
  border-left: 4px solid #FFC107;
}

.toast-warning .toast-icon {
  color: white;
  background-color: #FFC107;
}

.toast-info {
  border-left: 4px solid #2196F3;
}

.toast-info .toast-icon {
  color: white;
  background-color: #2196F3;
}

.toast-fade-enter-active {
  animation: slide-in 0.3s ease forwards;
}

.toast-fade-leave-active {
  animation: slide-in 0.3s ease reverse forwards;
}

@keyframes slide-in {
  from {
    transform: translateY(-100%) translateX(-50%);
    opacity: 0;
  }
  to {
    transform: translateY(0) translateX(-50%);
    opacity: 1;
  }
}
</style>