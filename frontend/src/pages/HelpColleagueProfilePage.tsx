import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box, Typography, Card, CardContent, Chip, Avatar,
  CircularProgress, Button,
} from '@mui/material'
import {
  ArrowBack, ThumbUp, Comment as CommentIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { helpColleagueService, UserProfile, Post, Comment } from '@services/helpColleagueService'

export default function HelpColleagueProfilePage() {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [responses, setResponses] = useState<Comment[]>([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<'posts' | 'responses'>('posts')

  useEffect(() => {
    if (userId) loadData(Number(userId))
  }, [userId])

  const loadData = async (uid: number) => {
    setLoading(true)
    try {
      const [prof, userPosts, userResponses] = await Promise.all([
        helpColleagueService.getUserProfile(uid),
        helpColleagueService.getUserPosts(uid),
        helpColleagueService.getUserResponses(uid),
      ])
      setProfile(prof)
      setPosts(userPosts)
      setResponses(userResponses)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
  if (!profile) return <Typography color="error">Пользователь не найден</Typography>

  return (
    <Box>
      <Button startIcon={<ArrowBack />} onClick={() => navigate('/help-colleague')} sx={{ mb: 2 }}>
        К ленте
      </Button>

      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 3 }}>
          <Avatar sx={{ width: 72, height: 72, bgcolor: 'primary.main', fontSize: 32 }}>
            {profile.full_name?.charAt(0) || `U${profile.id}`}
          </Avatar>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              {profile.full_name || `Пользователь #${profile.id}`}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              На платформе с {new Date(profile.created_at).toLocaleDateString()}
            </Typography>
            <Box sx={{ display: 'flex', gap: 3, mt: 1 }}>
              <Box><Typography variant="h6">{profile.karma}</Typography><Typography variant="caption">Карма</Typography></Box>
              <Box><Typography variant="h6">{profile.posts_count}</Typography><Typography variant="caption">Постов</Typography></Box>
              <Box><Typography variant="h6">{profile.responses_count}</Typography><Typography variant="caption">Ответов</Typography></Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button variant={tab === 'posts' ? 'contained' : 'outlined'} onClick={() => setTab('posts')}>
          Посты ({profile.posts_count})
        </Button>
        <Button variant={tab === 'responses' ? 'contained' : 'outlined'} onClick={() => setTab('responses')}>
          Ответы ({profile.responses_count})
        </Button>
      </Box>

      {tab === 'posts' && posts.map((post, idx) => (
        <motion.div key={post.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}>
          <Card sx={{ mb: 2, cursor: 'pointer' }} onClick={() => navigate(`/help-colleague/${post.id}`)}>
            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Chip label={post.category} size="small" />
                <Typography variant="caption" color="text.secondary">
                  {new Date(post.created_at).toLocaleDateString()}
                </Typography>
              </Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>{post.title}</Typography>
              <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <ThumbUp fontSize="small" color="primary" />
                  <Typography variant="caption">{post.rating}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <CommentIcon fontSize="small" color="action" />
                  <Typography variant="caption">{post.responses_count}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      ))}

      {tab === 'responses' && responses.map((resp, idx) => (
        <motion.div key={resp.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}>
          <Card sx={{ mb: 2, cursor: 'pointer' }} onClick={() => navigate(`/help-colleague/${resp.post_id}`)}>
            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
              <Typography variant="body2" sx={{ mb: 1, whiteSpace: 'pre-wrap' }}>{resp.content.slice(0, 200)}{resp.content.length > 200 ? '...' : ''}</Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <ThumbUp fontSize="small" color={resp.rating > 0 ? 'primary' : 'disabled'} />
                  <Typography variant="caption">{resp.rating}</Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {new Date(resp.created_at).toLocaleDateString()}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </Box>
  )
}
