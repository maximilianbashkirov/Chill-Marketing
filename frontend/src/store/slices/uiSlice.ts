import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  currentModule: string | null
  notifications: any[]
}

const initialState: UIState = {
  sidebarOpen: true,
  theme: 'light',
  currentModule: null,
  notifications: [],
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar(state) {
      state.sidebarOpen = !state.sidebarOpen
    },
    setSidebarOpen(state, action: PayloadAction<boolean>) {
      state.sidebarOpen = action.payload
    },
    setTheme(state, action: PayloadAction<'light' | 'dark'>) {
      state.theme = action.payload
    },
    setCurrentModule(state, action: PayloadAction<string | null>) {
      state.currentModule = action.payload
    },
    addNotification(state, action: PayloadAction<any>) {
      state.notifications.unshift(action.payload)
    },
    removeNotification(state, action: PayloadAction<number>) {
      state.notifications = state.notifications.filter(
        (_, index) => index !== action.payload
      )
    },
    clearNotifications(state) {
      state.notifications = []
    },
  },
})

export const {
  toggleSidebar,
  setSidebarOpen,
  setTheme,
  setCurrentModule,
  addNotification,
  removeNotification,
  clearNotifications,
} = uiSlice.actions

export default uiSlice.reducer
