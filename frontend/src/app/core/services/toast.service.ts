import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  readonly toasts = signal<Toast[]>([]);
  private nextId = 0;

  show(message: string, type: 'success' | 'error' | 'info' = 'success'): void {
    const id = this.nextId++;
    const newToast: Toast = { id, message, type };
    this.toasts.update(prev => [...prev, newToast]);

    // Automatically remove toast after 5 seconds (5000ms)
    setTimeout(() => {
      this.remove(id);
    }, 5000);
  }

  remove(id: number): void {
    this.toasts.update(prev => prev.filter(t => t.id !== id));
  }
}
