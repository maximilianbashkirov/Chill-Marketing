import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Tag {
  id: number
  name: string
}

interface Post {
  id: number
  user_id: number
  title: string
  description: string
  category: string
  is_anonymous: boolean
  responses_count: number
  rating: number
  hot_score: number
  status: string
  tags: Tag[]
  created_at: string
}

interface Comment {
  id: number
  post_id: number
  user_id: number
  content: string
  rating: number
  is_from_bot: boolean
  created_at: string
}

interface HelpColleagueState {
  posts: Post[]
  currentPost: Post | null
  responses: Comment[]
  isLoading: boolean
  error: string | null
  sort: 'new' | 'hot' | 'top'
  category: string
  searchQuery: string
  tags: Tag[]
  unreadCount: number
}

const initialState: HelpColleagueState = {
  posts: [],
  currentPost: null,
  responses: [],
  isLoading: false,
  error: null,
  sort: 'new',
  category: '',
  searchQuery: '',
  tags: [],
  unreadCount: 0,
}

const helpColleagueSlice = createSlice({
  name: 'helpColleague',
  initialState,
  reducers: {
    startLoading(state) {
      state.isLoading = true
      state.error = null
    },
    loadPostsSuccess(state, action: PayloadAction<Post[]>) {
      state.isLoading = false
      state.posts = action.payload
    },
    loadPostsFailure(state, action: PayloadAction<string>) {
      state.isLoading = false
      state.error = action.payload
    },
    addPostSuccess(state, action: PayloadAction<Post>) {
      state.posts.unshift(action.payload)
    },
    setCurrentPost(state, action: PayloadAction<Post | null>) {
      state.currentPost = action.payload
    },
    setResponses(state, action: PayloadAction<Comment[]>) {
      state.responses = action.payload
    },
    addResponse(state, action: PayloadAction<Comment>) {
      state.responses.push(action.payload)
    },
    updatePostInList(state, action: PayloadAction<Post>) {
      const updated = action.payload
      const idx = state.posts.findIndex(p => p.id === updated.id)
      if (idx >= 0) state.posts[idx] = updated
      if (state.currentPost?.id === updated.id) state.currentPost = updated
    },
    updateResponseRating(state, action: PayloadAction<{ id: number; rating: number }>) {
      const resp = state.responses.find(r => r.id === action.payload.id)
      if (resp) resp.rating = action.payload.rating
    },
    setSort(state, action: PayloadAction<'new' | 'hot' | 'top'>) {
      state.sort = action.payload
    },
    setCategory(state, action: PayloadAction<string>) {
      state.category = action.payload
    },
    setSearchQuery(state, action: PayloadAction<string>) {
      state.searchQuery = action.payload
    },
    setTags(state, action: PayloadAction<Tag[]>) {
      state.tags = action.payload
    },
    setUnreadCount(state, action: PayloadAction<number>) {
      state.unreadCount = action.payload
    },
    clearCurrentPost(state) {
      state.currentPost = null
      state.responses = []
    },
  },
})

export const {
  startLoading,
  loadPostsSuccess,
  loadPostsFailure,
  addPostSuccess,
  setCurrentPost,
  setResponses,
  addResponse,
  updatePostInList,
  updateResponseRating,
  setSort,
  setCategory,
  setSearchQuery,
  setTags,
  setUnreadCount,
  clearCurrentPost,
} = helpColleagueSlice.actions

export default helpColleagueSlice.reducer
