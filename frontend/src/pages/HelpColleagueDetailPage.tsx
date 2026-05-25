import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box, Typography, TextField, Button, Card, CardContent,
  Chip, IconButton, Avatar, CircularProgress, Divider, Alert,
} from '@mui/material'
import {
  ThumbUp, ThumbDown, ArrowBack, SmartToy as BotIcon,
  Close as CloseIcon, Send as SendIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { helpColleagueService, Post, Comment } from '@services/helpColleagueService'

const CATEGORY_COLORS: Record<string, string> = {
  idea: '#e3f2fd',
  problem: '#fce4ec',
  feedback: '#e8f5e9',
  collaboration: '#fff3e0',
}

export default function HelpColleagueDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [post, setPost] = useState<Post | null>(null)
  const [responses, setResponses] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    if (id) loadData(Number(id))
  }, [id])

  const loadData = async (postId: number) => {
    setLoading(true)
    try {
      const [p, r] = await Promise.all([
        helpColleagueService.getPostById(postId),
        helpColleagueService.getPostResponses(postId),
      ])
      setPost(p)
      setResponses(r)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const handleVote = async (vote: 1 | -1) => {
    if (!post) return
    try {
      const updated = await helpColleagueService.votePost(post.id, vote)
      setPost(updated)
    } catch (e) { console.error(e) }
  }

  const handleRateResponse = async (respId: number, rating: number) => {
    try {
      const updated = await helpColleagueService.rateResponse(respId, rating)
      setResponses(prev => prev.map(r => r.id === respId ? { ...r, rating: updated.rating } : r))
    } catch (e) { console.error(e) }
  }

  const handleSendComment = async () => {
    if (!post || !newComment.trim()) return
    setSending(true)
    try {
      const created = await helpColleagueService.createResponse(post.id, newComment)
      setResponses(prev => [...prev, created])
      setPost(prev => prev ? { ...prev, responses_count: prev.responses_count + 1 } : prev)
      setNewComment('')
    } catch (e) { console.error(e) }
    setSending(false)
  }

  const handleAiResponse = async () => {
    if (!post) return
    setAiLoading(true)
    try {
      const aiResp = await helpColleagueService.generateAiResponse(post.id)
      setResponses(prev => [...prev, aiResp])
      setPost(prev => prev ? { ...prev, responses_count: prev.responses_count + 1 } : prev)
    } catch (e) { console.error(e) }
    setAiLoading(false)
  }

  const handleClose = async () => {
    if (!post) return
    try {
      const updated = await helpColleagueService.closePost(post.id)
      setPost(updated)
    } catch (e) { console.error(e) }
  }

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
  if (!post) return <Alert severity="error">Пост не найден</Alert>

  return (
    <Box>
      <Button startIcon={<ArrowBack />} onClick={() => navigate('/help-colleague')} sx={{ mb: 2 }}>
        К ленте
      </Button>

      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Chip label={post.category} size="small"
              sx={{ bgcolor: CATEGORY_COLORS[post.category] || '#f5f5f5', fontWeight: 600 }} />
            <Typography variant="caption" color="text.secondary">
              {new Date(post.created_at).toLocaleDateString()}
            </Typography>
          </Box>

          <Typography variant="h5" sx={{ fontWeight: 700, mb: 2 }}>{post.title}</Typography>
          <Typography variant="body1" sx={{ mb: 3, whiteSpace: 'pre-wrap' }}>{post.description}</Typography>

          {post.tags?.length > 0 && (
            <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
              {post.tags.map(t => <Chip key={t.id} label={t.name} size="small" variant="outlined" />)}
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <IconButton onClick={() => handleVote(1)} size="small"><ThumbUp fontSize="small" /></IconButton>
              <Typography sx={{ mx: 1, fontWeight: 600, minWidth: 24, textAlign: 'center' }}>
                {post.rating}
              </Typography>
              <IconButton onClick={() => handleVote(-1)} size="small"><ThumbDown fontSize="small" /></IconButton>
            </Box>
            <Typography variant="body2" color="text.secondary">
              {post.responses_count} ответов
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Статус: {post.status === 'open' ? 'Открыт' : 'Закрыт'}
            </Typography>
            {post.status === 'open' && (
              <>
                <Button size="small" variant="outlined" startIcon={<BotIcon />}
                  onClick={handleAiResponse} disabled={aiLoading} sx={{ ml: 'auto' }}>
                  {aiLoading ? 'Генерация...' : 'AI ответ'}
                </Button>
                <Button size="small" variant="outlined" color="error"
                  startIcon={<CloseIcon />} onClick={handleClose}>
                  Закрыть
                </Button>
              </>
            )}
          </Box>
        </CardContent>
      </Card>

      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Ответы ({responses.length})
      </Typography>

      {post.status === 'open' && (
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <TextField fullWidth multiline rows={2}
            placeholder="Написать ответ..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
          />
          <Button variant="contained" onClick={handleSendComment}
            disabled={!newComment.trim() || sending}
            sx={{ alignSelf: 'flex-end', minWidth: 100, height: 40 }}>
            <SendIcon />
          </Button>
        </Box>
      )}

      {responses.map((resp, idx) => (
        <motion.div key={resp.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}>
          <Card sx={{ mb: 2, bgcolor: resp.is_from_bot ? '#f0f4ff' : 'white' }}>
            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {resp.is_from_bot ? (
                    <Avatar sx={{ width: 28, height: 28, bgcolor: 'primary.main' }}><BotIcon sx={{ fontSize: 16 }} /></Avatar>
                  ) : (
                    <Avatar sx={{ width: 28, height: 28, bgcolor: 'grey.400' }}>
                      {String(resp.user_id).charAt(0)}
                    </Avatar>
                  )}
                  <Typography variant="caption" color="text.secondary">
                    {resp.is_from_bot ? 'AI ассистент' : `Пользователь #${resp.user_id}`}
                    {resp.is_from_bot && ' • Автоматический ответ'}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {new Date(resp.created_at).toLocaleDateString()}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mb: 1 }}>{resp.content}</Typography>
              {!resp.is_from_bot && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <IconButton size="small" onClick={() => handleRateResponse(resp.id, resp.rating === 1 ? 0 : 1)}>
                    <ThumbUp fontSize="small" color={resp.rating > 0 ? 'primary' : 'inherit'} />
                  </IconButton>
                  <Typography variant="caption">{resp.rating}</Typography>
                  <IconButton size="small" onClick={() => handleRateResponse(resp.id, resp.rating === -1 ? 0 : -1)}>
                    <ThumbDown fontSize="small" color={resp.rating < 0 ? 'error' : 'inherit'} />
                  </IconButton>
                </Box>
              )}
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </Box>
  )
}
