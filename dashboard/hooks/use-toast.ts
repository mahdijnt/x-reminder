"use client";

import * as React from "react";

export type ToastVariant = "default" | "destructive";

export type ToastInput = {
  title?: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactNode;
  variant?: ToastVariant;
  duration?: number;
};

type ToastState = ToastInput & {
  id: string;
  open: boolean;
};

const TOAST_LIMIT = 5;
const TOAST_REMOVE_DELAY_MS = 300;

let memoryToasts: ToastState[] = [];
let toastIdCounter = 0;

const listeners = new Set<(toasts: ToastState[]) => void>();

function notifyListeners() {
  for (const listener of listeners) listener(memoryToasts);
}

function removeToast(id: string) {
  memoryToasts = memoryToasts.filter((t) => t.id !== id);
  notifyListeners();
}

function dismissToast(id: string) {
  memoryToasts = memoryToasts.map((t) =>
    t.id === id ? { ...t, open: false } : t
  );
  notifyListeners();

  window.setTimeout(() => removeToast(id), TOAST_REMOVE_DELAY_MS);
}

export function toast(input: ToastInput) {
  const id = String(++toastIdCounter);
  const duration = input.duration ?? 4000;

  const next: ToastState = {
    id,
    open: true,
    variant: input.variant ?? "default",
    title: input.title,
    description: input.description,
    action: input.action,
    duration,
  };

  memoryToasts = [next, ...memoryToasts].slice(0, TOAST_LIMIT);
  notifyListeners();

  window.setTimeout(() => dismissToast(id), duration);

  return {
    id,
    dismiss: () => dismissToast(id),
  };
}

export function useToast() {
  const [toasts, setToasts] = React.useState<ToastState[]>(memoryToasts);

  React.useEffect(() => {
    const listener = (nextToasts: ToastState[]) => setToasts(nextToasts);
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, []);

  return {
    toasts,
    dismiss: (id: string) => dismissToast(id),
  };
}
