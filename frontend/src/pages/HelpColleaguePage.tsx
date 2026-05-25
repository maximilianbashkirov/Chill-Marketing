import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box, Typography, TextField, Button, Card, CardContent,
  Grid, IconButton, Chip, ToggleButtonGroup, ToggleButton,
  InputAdornment, CircularProgress, Avatar, MenuItem, Select,
} from '@mui/material'
import { motion } from 'framer-motion'
import {
  ThumbUp, ThumbDown, Comment as CommentIcon, Add as AddIcon,
  Search as SearchIcon, Whatshot as HotIcon, NewReleases as NewIcon,
  TrendingUp as TopIcon,
} from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import {
  loadPostsSuccess, addPostSuccess, setSort, setTags,
} from '@store/slices/helpColleagueSlice'
import { helpColleagueService } from '@services/helpColleagueService'
import type { RootState } from '@store/store'
import type { Post } from '@services/helpColleagueService'

const CATEGORY_COLORS: Record<string, string> = {
  idea: '#e3f2fd',
  problem: '#fce4ec',
  feedback: '#e8f5e9',
  collaboration: '#fff3e0',
}

const CATEGORY_LABELS: Record<string, string> = {
  idea: 'Идея',
  problem: 'Проблема',
  feedback: 'Обратная связь',
  collaboration: 'Коллаборация',
}

export default function HelpColleaguePage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { posts, isLoading, sort } = useSelector((state: RootState) => state.helpColleague)

  const [newPostTitle, setNewPostTitle] = useState('')
  const [newPostContent, setNewPostContent] = useState('')
  const [newPostCategory, setNewPostCategory] = useState('idea')
  const [newPostTags, setNewPostTags] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [availableTags, setAvailableTags] = useState<{ id: number; name: string }[]>([])
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [filterCategory, setFilterCategory] = useState('')

  useEffect(() => {
    loadPosts()
    loadTags()
  }, [sort, filterCategory, selectedTags])

  const loadPosts = useCallback(async () => {
    try {
      const data = await helpColleagueService.getPosts({
        sort,
        category: filterCategory || undefined,
        tag: selectedTags.length > 0 ? selectedTags : undefined,
      })
      dispatch(loadPostsSuccess(data))
    } catch (err) {
      console.error('Ошибка загрузки постов:', err)
    }
  }, [sort, filterCategory, selectedTags, dispatch])

  const loadTags = async () => {
    try {
      const tags = await helpColleagueService.getTags()
      setAvailableTags(tags)
      dispatch(setTags(tags))
    } catch (e) { console.error(e) }
  }

  const handleCreatePost = async () => {
    if (!newPostTitle.trim() || !newPostContent.trim()) return
    try {
      const tags = newPostTags.split(',').map(t => t.trim()).filter(Boolean)
      const post = await helpColleagueService.createPost({
        title: newPostTitle,
        description: newPostContent,
        category: newPostCategory,
        tags,
      })
      dispatch(addPostSuccess(post))
      setNewPostTitle('')
      setNewPostContent('')
      setNewPostTags('')
      setShowForm(false)
    } catch (err) {
      console.error('Ошибка создания поста:', err)
    }
  }

  const handleVote = async (postId: number, vote: 1 | -1, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await helpColleagueService.votePost(postId, vote)
      loadPosts()
    } catch (err) { console.error(err) }
  }

  const handleSearch = async () => {
    if (!searchText.trim()) {
      loadPosts()
      return
    }
    try {
      const data = await helpColleagueService.searchPosts(searchText)
      dispatch(loadPostsSuccess(data))
    } catch (err) { console.error(err) }
  }

  const handleSortChange = (_: any, newSort: 'new' | 'hot' | 'top' | null) => {
    if (newSort) dispatch(setSort(newSort))
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Помощь коллег</Typography>
          <Typography color="text.secondary">Обменивайтесь идеями и получайте обратную связь от сообщества</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setShowForm(!showForm)}>
          Создать пост
        </Button>
      </Box>

      {/* ─── Create form ─── */}
      {showForm && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <TextField fullWidth label="Заголовок" value={newPostTitle}
              onChange={(e) => setNewPostTitle(e.target.value)} sx={{ mb: 2 }} />
            <TextField fullWidth multiline rows={3} label="Ваша идея/вопрос"
              value={newPostContent} onChange={(e) => setNewPostContent(e.target.value)} sx={{ mb: 2 }} />
            <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
              <Select value={newPostCategory} onChange={(e) => setNewPostCategory(e.target.value)} size="small" sx={{ minWidth: 160 }}>
                <MenuItem value="idea">Идея</MenuItem>
                <MenuItem value="problem">Проблема</MenuItem>
                <MenuItem value="feedback">Обратная связь</MenuItem>
                <MenuItem value="collaboration">Коллаборация</MenuItem>
              </Select>
              <TextField label="Теги (через запятую)" size="small"
                value={newPostTags} onChange={(e) => setNewPostTags(e.target.value)}
                sx={{ flex: 1, minWidth: 200 }} />
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button variant="contained" onClick={handleCreatePost}>Опубликовать</Button>
              <Button variant="outlined" onClick={() => setShowForm(false)}>Отмена</Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* ─── Toolbar: sort / search / filter ─── */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <ToggleButtonGroup value={sort} exclusive onChange={handleSortChange} size="small">
          <ToggleButton value="new" sx={{
            '&.Mui-selected': { bgcolor: '#e3f2fd', color: '#1565c0', '&:hover': { bgcolor: '#bbdefb' } },
          }}>
            <NewIcon sx={{ mr: 0.5, fontSize: 18 }} />Новые
          </ToggleButton>
          <ToggleButton value="hot" sx={{
            '&.Mui-selected': { bgcolor: '#fbe9e7', color: '#bf360c', '&:hover': { bgcolor: '#ffccbc' } },
          }}>
            <HotIcon sx={{ mr: 0.5, fontSize: 18 }} />Горячие
          </ToggleButton>
          <ToggleButton value="top" sx={{
            '&.Mui-selected': { bgcolor: '#fff8e1', color: '#f57f17', '&:hover': { bgcolor: '#ffecb3' } },
          }}>
            <TopIcon sx={{ mr: 0.5, fontSize: 18 }} />Топ
          </ToggleButton>
        </ToggleButtonGroup>

        <TextField size="small" placeholder="Поиск..." value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          InputProps={{
            startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>,
          }}
          sx={{ minWidth: 220 }}
        />

        <Select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}
          displayEmpty size="small" sx={{ minWidth: 150 }}>
          <MenuItem value="">Все категории</MenuItem>
          <MenuItem value="idea">Идеи</MenuItem>
          <MenuItem value="problem">Проблемы</MenuItem>
          <MenuItem value="feedback">Обратная связь</MenuItem>
          <MenuItem value="collaboration">Коллаборация</MenuItem>
        </Select>
      </Box>

      {/* ─── Tags filter ─── */}
      {availableTags.length > 0 && (
        <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
          {availableTags.map(tag => (
            <Chip key={tag.id} label={tag.name} size="small"
              variant={selectedTags.includes(tag.name) ? 'filled' : 'outlined'}
              color={selectedTags.includes(tag.name) ? 'primary' : 'default'}
              onClick={() => setSelectedTags(prev =>
                prev.includes(tag.name) ? prev.filter(t => t !== tag.name) : [...prev, tag.name]
              )}
            />
          ))}
        </Box>
      )}

      {/* ─── Posts feed ─── */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
      ) : posts.length === 0 ? (
        <Typography color="text.secondary" sx={{ textAlign: 'center', py: 8 }}>
          Пока нет постов. Будьте первым!
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {posts.map((post: Post, index: number) => (
            <Grid item xs={12} key={post.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
              >
                <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
                  onClick={() => navigate(`/help-colleague/${post.id}`)}>
                  <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Chip label={CATEGORY_LABELS[post.category] || post.category} size="small"
                          sx={{ bgcolor: CATEGORY_COLORS[post.category] || '#f5f5f5', fontWeight: 600 }} />
                        {post.tags?.map(t => (
                          <Chip key={t.id} label={t.name} size="small" variant="outlined" />
                        ))}
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(post.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>

                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>{post.title}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{
                      mb: 2, overflow: 'hidden', textOverflow: 'ellipsis',
                      display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
                    }}>
                      {post.description}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <IconButton onClick={(e) => handleVote(post.id, 1, e)} size="small">
                          <ThumbUp fontSize="small" />
                        </IconButton>
                        <Typography variant="body2" sx={{ mx: 0.5, fontWeight: 600, minWidth: 20, textAlign: 'center' }}>
                          {post.rating}
                        </Typography>
                        <IconButton onClick={(e) => handleVote(post.id, -1, e)} size="small">
                          <ThumbDown fontSize="small" />
                        </IconButton>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <CommentIcon fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">{post.responses_count}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 'auto' }}>
                        <Avatar sx={{ width: 24, height: 24, fontSize: 12, bgcolor: 'grey.400' }}>
                          {post.is_anonymous ? '?' : `U${post.user_id}`}
                        </Avatar>
                        <Typography variant="caption" color="text.secondary">
                          {post.is_anonymous ? 'Аноним' : `User #${post.user_id}`}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  )
}
