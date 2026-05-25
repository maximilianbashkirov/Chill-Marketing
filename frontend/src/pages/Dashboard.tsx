import { Box, Typography, Grid, Card, CardContent, Avatar } from '@mui/material'
import { motion } from 'framer-motion'
import {
  Analytics as AnalyticsIcon,
  Article as ArticleIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Lightbulb as LightbulbIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

const modules = [
  {
    title: 'Аналитика',
    description: 'Анализ маркетинговых идей на основе базы кейсов',
    icon: <AnalyticsIcon />,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    path: '/analytics',
    stats: '12 анализов',
  },
  {
    title: 'Контент',
    description: 'Оценка идей для постов, рилсов и подкастов',
    icon: <ArticleIcon />,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    path: '/content',
    stats: '8 анализов',
  },
  {
    title: 'СМИ',
    description: 'Проверка актуальности тем для статей и новостей',
    icon: <TrendingUpIcon />,
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    path: '/smi',
    stats: '5 тем',
  },
  {
    title: 'Исследования',
    description: 'Маркетинговые исследования с реальными данными',
    icon: <AssessmentIcon />,
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    path: '/market-research',
    stats: '3 исследования',
  },
  {
    title: 'Dot Analysis',
    description: 'Подбор маркетинговых моделей для вашего кейса',
    icon: <LightbulbIcon />,
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    path: '/dot-analysis',
    stats: '7 анализов',
  },
  {
    title: 'Помощь коллег',
    description: 'Сообщество для обмена и оценки идей',
    icon: <PeopleIcon />,
    color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    path: '/help-colleague',
    stats: '24 поста',
  },
]

export default function Dashboard() {
  const navigate = useNavigate()

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h3" sx={{ mb: 2, fontWeight: 700 }}>
          Добро пожаловать в Chill Marketing AI Bot
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 6, fontWeight: 400 }}>
          Ваш интеллектуальный помощник для решения маркетинговых задач
        </Typography>
      </motion.div>

      <Grid container spacing={3}>
        {modules.map((module, index) => (
          <Grid item xs={12} sm={6} md={4} key={module.title}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: 1.05, transition: { duration: 0.2 } }}
            >
              <Card
                onClick={() => navigate(module.path)}
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
                  },
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    <Avatar
                      sx={{
                        width: 56,
                        height: 56,
                        background: module.color,
                        mr: 2,
                        fontSize: 28,
                      }}
                    >
                      {module.icon}
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                        {module.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {module.stats}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {module.description}
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        style={{ marginTop: 48 }}
      >
        <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 2 }}>
              🚀 Начните работу прямо сейчас
            </Typography>
            <Typography variant="body1" sx={{ mb: 3, opacity: 0.9 }}>
              Выберите любой модуль выше или начните с аналитики вашей первой маркетинговой идеи
            </Typography>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  )
}
