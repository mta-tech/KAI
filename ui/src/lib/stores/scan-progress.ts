import { create } from 'zustand';

interface ScanProgress {
  connectionId: string;
  connectionAlias: string;
  startedAt: Date;
  withAI: boolean;
}

interface ScanProgressStore {
  scans: Map<string, ScanProgress>;
  startScan: (connectionId: string, connectionAlias: string, withAI: boolean) => void;
  completeScan: (connectionId: string) => void;
  isScanning: (connectionId: string) => boolean;
  getActiveScan: (connectionId: string) => ScanProgress | undefined;
  getAllScans: () => ScanProgress[];
}

export const useScanProgress = create<ScanProgressStore>((set, get) => ({
  scans: new Map(),

  startScan: (connectionId, connectionAlias, withAI) => {
    set((state) => {
      const newScans = new Map(state.scans);
      newScans.set(connectionId, {
        connectionId,
        connectionAlias,
        startedAt: new Date(),
        withAI,
      });
      return { scans: newScans };
    });
  },

  completeScan: (connectionId) => {
    set((state) => {
      const newScans = new Map(state.scans);
      newScans.delete(connectionId);
      return { scans: newScans };
    });
  },

  isScanning: (connectionId) => {
    return get().scans.has(connectionId);
  },

  getActiveScan: (connectionId) => {
    return get().scans.get(connectionId);
  },

  getAllScans: () => {
    return Array.from(get().scans.values());
  },
}));
