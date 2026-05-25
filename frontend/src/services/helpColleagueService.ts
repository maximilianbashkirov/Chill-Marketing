import apiClient from './api'

export interface Post {
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
  tags: { id: number; name: string }[]
  created_at: string
}

export interface Comment {
  id: number
  post_id: number
  user_id: number
  content: string
  rating: number
  is_from_bot: boolean
  created_at: string
}

export interface CreatePostRequest {
  title: string
  description: string
  category?: string
  is_anonymous?: boolean
  tags?: string[]
}

export interface UserProfile {
  id: number
  full_name: string | null
  karma: number
  posts_count: number
  responses_count: number
  created_at: string
}

export interface Notification {
  id: number
  type: string
  message: string
  post_id: number
  is_read: boolean
  created_at: string
}

export interface Tag {
  id: number
  name: string
}

export const helpColleagueService = {
  getPosts: async (params?: {
    category?: string
    sort?: 'new' | 'hot' | 'top'
    tag?: string[]
    page?: number
    limit?: number
  }): Promise<Post[]> => {
    const response = await apiClient.get('/help-colleague/posts', { params })
    return response.data
  },

  getPostById: async (id: number): Promise<Post> => {
    const response = await apiClient.get(`/help-colleague/posts/${id}`)
    return response.data
  },

  getPostResponses: async (postId: number): Promise<Comment[]> => {
    const response = await apiClient.get(`/help-colleague/posts/${postId}/responses`)
    return response.data
  },

  createPost: async (request: CreatePostRequest): Promise<Post> => {
    const response = await apiClient.post('/help-colleague/posts', request)
    return response.data
  },

  createResponse: async (postId: number, content: string): Promise<Comment> => {
    const response = await apiClient.post(`/help-colleague/posts/${postId}/responses`, { content })
    return response.data
  },

  generateAiResponse: async (postId: number): Promise<Comment> => {
    const response = await apiClient.post(`/help-colleague/posts/${postId}/ai-response`)
    return response.data.data
  },

  votePost: async (postId: number, vote: 1 | -1): Promise<Post> => {
    const response = await apiClient.post(`/help-colleague/posts/${postId}/vote`, null, { params: { vote } })
    return response.data
  },

  rateResponse: async (responseId: number, rating: number): Promise<Comment> => {
    const response = await apiClient.post(`/help-colleague/responses/${responseId}/rate`, null, { params: { rating } })
    return response.data
  },

  closePost: async (postId: number): Promise<Post> => {
    const response = await apiClient.post(`/help-colleague/posts/${postId}/close`)
    return response.data
  },

  searchPosts: async (query: string): Promise<Post[]> => {
    const response = await apiClient.get('/help-colleague/search', { params: { q: query } })
    return response.data
  },

  getTags: async (): Promise<Tag[]> => {
    const response = await apiClient.get('/help-colleague/tags')
    return response.data
  },

  getUserProfile: async (userId: number): Promise<UserProfile> => {
    const response = await apiClient.get(`/help-colleague/profile/${userId}`)
    return response.data
  },

  getUserPosts: async (userId: number): Promise<Post[]> => {
    const response = await apiClient.get(`/help-colleague/profile/${userId}/posts`)
    return response.data
  },

  getUserResponses: async (userId: number): Promise<Comment[]> => {
    const response = await apiClient.get(`/help-colleague/profile/${userId}/responses`)
    return response.data
  },

  getNotifications: async (): Promise<Notification[]> => {
    const response = await apiClient.get('/help-colleague/notifications')
    return response.data
  },

  getUnreadCount: async (): Promise<number> => {
    const response = await apiClient.get('/help-colleague/notifications/unread-count')
    return response.data.count
  },

  markNotificationsRead: async (): Promise<void> => {
    await apiClient.post('/help-colleague/notifications/read')
  },
}
