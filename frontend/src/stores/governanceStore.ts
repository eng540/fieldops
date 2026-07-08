import { create } from 'zustand'

interface GovernanceState {
  activeDecisions: Array<{
    id: number
    unitId: number
    decision: string
    paymentPct: number
    flag: string
    matchedRule: string
    reason: string
    policyVersion: number
  }>
  isLoading: boolean
  // Actions
  loadDecisions: (unitId: number) => Promise<void>
  requestOverride: (decisionId: number, justification: string) => Promise<void>
}

export const useGovernanceStore = create<GovernanceState>((set, get) => ({
  activeDecisions: [],
  isLoading: false,

  loadDecisions: async (unitId) => {
    // TODO: Implement in Sprint-4
    console.log('Governance:loadDecisions', unitId)
  },

  requestOverride: async (decisionId, justification) => {
    // TODO: Implement in Sprint-4
    console.log('Governance:requestOverride', { decisionId, justification })
  },
}))
