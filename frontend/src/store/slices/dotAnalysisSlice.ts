import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface DotAnalysisState {
  currentAnalysis: any | null
  history: any[]
  isLoading: boolean
  error: string | null
}

const initialState: DotAnalysisState = {
  currentAnalysis: null,
  history: [],
  isLoading: false,
  error: null,
}

const dotAnalysisSlice = createSlice({
  name: 'dotAnalysis',
  initialState,
  reducers: {
    startAnalysis(state) {
      state.isLoading = true
      state.error = null
    },
    analysisSuccess(state, action: PayloadAction<any>) {
      state.isLoading = false
      state.currentAnalysis = action.payload
      state.history.unshift(action.payload)
    },
    analysisFailure(state, action: PayloadAction<string>) {
      state.isLoading = false
      state.error = action.payload
    },
    clearAnalysis(state) {
      state.currentAnalysis = null
      state.error = null
    },
  },
})

export const {
  startAnalysis,
  analysisSuccess,
  analysisFailure,
  clearAnalysis,
} = dotAnalysisSlice.actions

export default dotAnalysisSlice.reducer
