export interface ToastInstance {
  success: (text: string, timeout?: number) => void;
  error: (text: string, timeout?: number) => void;
  warning: (text: string, timeout?: number) => void;
  info: (text: string, timeout?: number) => void;
}

export type ToastType = 'success' | 'error' | 'warning' | 'info';

const toastInstance: Ref<ToastInstance | null> = ref(null);

export function setToastInstance(instance: ToastInstance): void {
  toastInstance.value = instance;
}

function checkInstance(): boolean {
  if (!toastInstance.value) {
    console.warn('Toast instance not set. Call setToastInstance first.');
    return false;
  }
  return true;
}

export const toast = {
  success(text: string, timeout?: number): void {
    if (checkInstance()) {
      toastInstance.value!.success(text, timeout);
    }
  },
  
  error(text: string, timeout?: number): void {
    if (checkInstance()) {
      toastInstance.value!.error(text, timeout);
    }
  },
  
  warning(text: string, timeout?: number): void {
    if (checkInstance()) {
      toastInstance.value!.warning(text, timeout);
    }
  },
  
  info(text: string, timeout?: number): void {
    if (checkInstance()) {
      toastInstance.value!.info(text, timeout);
    }
  }
};