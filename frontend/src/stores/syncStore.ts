import { create } from 'zustand'
import { db } from '@/lib/db'

interface SyncState {
  isOnline: boolean
  isSyncing: boolean
  pendingCount: number
  lastSyncVersion: string | null
  lastSyncAt: string | null
  conflicts: Array<{
    operationUuid: string
    conflictType: string
    hint: string
  }>
  // Actions
  checkOnline: () => void
  startSync: () => Promise<void>
  resolveConflict: (operationUuid: string, resolution: 'SERVER' | 'CLIENT') => Promise<void>
}

export const useSyncStore = create<SyncState>((set, get) => ({
  isOnline: navigator.onLine,
  isSyncing: false,
  pendingCount: 0,
  lastSyncVersion: null,
  lastSyncAt: null,
  conflicts: [],

  checkOnline: () => {
    set({ isOnline: navigator.onLine })
  },

  startSync: async () => {
    // TODO: Implement in Sprint-3
    console.log('Sync:startSync')
  },

  resolveConflict: async (operationUuid, resolution) => {
    // TODO: Implement in Sprint-3
    console.log('Sync:resolveConflict', { operationUuid, resolution })
  },
}))
