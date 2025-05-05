import { defineStore } from 'pinia'

interface ToastMessage {
  id: number;
  text: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timeout?: number;
}

export const useToastStore = defineStore('toast', {
  state: () => ({
    messages: [] as ToastMessage[],
    counter: 0
  }),
  
  actions: {
    // Add a new toast message
    add(text: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', timeout: number = 3000) {
      const id = this.counter++
      
      const message: ToastMessage = {
        id,
        text,
        type,
        timeout
      }
      
      this.messages.push(message)
      
      // Set a timeout to automatically dismiss the message
      if (timeout > 0) {
        setTimeout(() => {
          this.dismiss(id)
        }, timeout)
      }
      
      return id
    },
    
    // Dismiss a toast message by ID
    dismiss(id: number) {
      const index = this.messages.findIndex(m => m.id === id)
      if (index !== -1) {
        this.messages.splice(index, 1)
      }
    },
    
    // Dismiss all toast messages
    clear() {
      this.messages = []
    },
    
    // Shortcut: Success message
    success(text: string, timeout?: number) {
      return this.add(text, 'success', timeout)
    },
    
    // Shortcut: Error message
    error(text: string, timeout?: number) {
      return this.add(text, 'error', timeout)
    },
    
    // Shortcut: Warning message
    warning(text: string, timeout?: number) {
      return this.add(text, 'warning', timeout)
    },
    
    // Shortcut: Info message
    info(text: string, timeout?: number) {
      return this.add(text, 'info', timeout)
    }
  }
})