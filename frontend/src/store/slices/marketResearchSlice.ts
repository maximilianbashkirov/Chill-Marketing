import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface MarketResearchState {
  currentResearch: any | null
  history: any[]
  isLoading: boolean
  error: string | null
}

const initialState: MarketResearchState = {
  currentResearch: null,
  history: [],
  isLoading: false,
  error: null,
}

const marketResearchSlice = createSlice({
  name: 'marketResearch',
  initialState,
  reducers: {
    startResearch(state) {
      state.isLoading = true
      state.error = null
    },
    researchSuccess(state, action: PayloadAction<any>) {
      state.isLoading = false
      state.currentResearch = action.payload
      state.history.unshift(action.payload)
    },
    researchFailure(state, action: PayloadAction<string>) {
      state.isLoading = false
      state.error = action.payload
    },
    clearResearch(state) {
      state.currentResearch = null
      state.error = null
    },
  },
})

export const {
  startResearch,
  researchSuccess,
  researchFailure,
  clearResearch,
} = marketResearchSlice.actions

export default marketResearchSlice.reducer
