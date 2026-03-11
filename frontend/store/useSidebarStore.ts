import { create } from 'zustand'
import { UserState, ScheduleEvent, ViolationAlert as ViolationAlertType } from '@/types/chat'

interface SidebarState {
  isOpen: boolean
  toggle: () => void
  userState: UserState | null
  setUserState: (state: UserState) => void
  violations: ViolationAlertType[]
  addViolation: (violation: ViolationAlertType) => void
  dismissViolation: (id: string) => void
}

export const useSidebarStore = create<SidebarState>((set) => ({
  isOpen: false,
  toggle: () => set((state) => ({ isOpen: !state.isOpen })),
  userState: null,
  setUserState: (state) => set({ userState: state }),
  violations: [],
  addViolation: (violation) => set((state) => ({ violations: [...state.violations, violation] })),
  dismissViolation: (id) => set((state) => ({ violations: state.violations.filter((v) => v.id !== id) })),
}))
