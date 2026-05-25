import { configureStore } from '@reduxjs/toolkit'
import analyticsReducer from './slices/analyticsSlice'
import contentReducer from './slices/contentSlice'
import smiReducer from './slices/smiSlice'
import marketResearchReducer from './slices/marketResearchSlice'
import dotAnalysisReducer from './slices/dotAnalysisSlice'
import helpColleagueReducer from './slices/helpColleagueSlice'
import uiReducer from './slices/uiSlice'

export const store = configureStore({
  reducer: {
    analytics: analyticsReducer,
    content: contentReducer,
    smi: smiReducer,
    marketResearch: marketResearchReducer,
    dotAnalysis: dotAnalysisReducer,
    helpColleague: helpColleagueReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
        ignoredPaths: ['api'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
