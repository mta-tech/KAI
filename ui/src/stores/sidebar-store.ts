import { create } from 'zustand';

interface SidebarState {
  isOpen: boolean;
  isMobile: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
  setMobile: (isMobile: boolean) => void;
}

export const useSidebarStore = create<SidebarState>((set) => ({
  isOpen: false,
  isMobile: false,

  open: () => set({ isOpen: true }),

  close: () => set({ isOpen: false }),

  toggle: () => set((state) => ({ isOpen: !state.isOpen })),

  setMobile: (isMobile) => set({ isMobile, isOpen: false }),
}));
