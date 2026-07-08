import { create } from 'zustand'
import { db, type LocalProject, type LocalUnit } from '@/lib/db'

interface ProjectState {
  activeProjects: LocalProject[]
  activeUnits: LocalUnit[]
  selectedProjectId: number | null
  selectedUnitId: number | null
  isLoading: boolean
  // Actions
  loadProjects: () => Promise<void>
  loadUnits: (projectId: number) => Promise<void>
  selectProject: (projectId: number) => void
  selectUnit: (unitId: number) => void
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  activeProjects: [],
  activeUnits: [],
  selectedProjectId: null,
  selectedUnitId: null,
  isLoading: false,

  loadProjects: async () => {
    // TODO: Implement in Sprint-2
    console.log('Project:loadProjects')
  },

  loadUnits: async (projectId) => {
    // TODO: Implement in Sprint-2
    console.log('Project:loadUnits', projectId)
  },

  selectProject: (projectId) => set({ selectedProjectId: projectId }),
  selectUnit: (unitId) => set({ selectedUnitId: unitId }),
}))
