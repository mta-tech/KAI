'use client';

/**
 * Service Worker Provider Component
 *
 * Registers the service worker and provides update notifications.
 * Should be placed in the app layout.
 */

import { useEffect, useState } from 'react';
import {
  registerServiceWorker,
  skipWaiting,
  onUpdateAvailable,
  getServiceWorkerStatus,
  type ServiceWorkerStatus,
} from '@/lib/service-worker-registration';
import { toast } from 'sonner';

export function ServiceWorkerProvider({ children }: { children: React.ReactNode }) {
  const [swStatus, setSwStatus] = useState<ServiceWorkerStatus | null>(null);
  const [showUpdatePrompt, setShowUpdatePrompt] = useState(false);

  useEffect(() => {
    // Register service worker on mount
    registerServiceWorker().then((reg) => {
      if (reg) {
        setSwStatus(getServiceWorkerStatus());
      }
    });

    // Listen for update availability
    const unsubscribe = onUpdateAvailable(() => {
      setShowUpdatePrompt(true);
      showUpdateToast();
    });

    // Check for updates periodically
    const intervalId = setInterval(() => {
      if (navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'CHECK_UPDATES' });
      }
    }, 60 * 60 * 1000); // Check every hour

    return () => {
      unsubscribe();
      clearInterval(intervalId);
    };
  }, []);

  /**
   * Show toast notification when update is available
   */
  function showUpdateToast() {
    toast.success('New version available!', {
      description: 'A new version of KAI is available. Click to update.',
      action: {
        label: 'Update',
        onClick: () => {
          skipWaiting();
          setShowUpdatePrompt(false);
        },
      },
      duration: 0, // Don't auto-dismiss
    });
  }

  return <>{children}</>;
}

/**
 * Hook to use service worker status in components
 */
export function useServiceWorkerStatus() {
  const [status, setStatus] = useState<ServiceWorkerStatus>({
    isSupported: false,
    isRegistered: false,
    isActivated: false,
    isUpdating: false,
  });

  useEffect(() => {
    setStatus(getServiceWorkerStatus());

    const unsubscribe = onUpdateAvailable(() => {
      setStatus(getServiceWorkerStatus());
    });

    return unsubscribe;
  }, []);

  return status;
}
