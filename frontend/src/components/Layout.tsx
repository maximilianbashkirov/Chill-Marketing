import { useState, useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  CssBaseline,
  Avatar,
  Menu,
  MenuItem,
  Badge,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  Article as ArticleIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Lightbulb as LightbulbIcon,
  People as PeopleIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  AccountCircle,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { helpColleagueService } from '@services/helpColleagueService'
import SettingsDialog from './SettingsDialog'

const DRAWER_WIDTH = 280

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'AI-powered аналитика', icon: <AnalyticsIcon />, path: '/analytics' },
  { text: 'Контент', icon: <ArticleIcon />, path: '/content' },
  { text: 'СМИ', icon: <TrendingUpIcon />, path: '/smi' },
  { text: 'Исследования', icon: <AssessmentIcon />, path: '/market-research' },
  { text: 'Dot Analysis', icon: <LightbulbIcon />, path: '/dot-analysis' },
  { text: 'Помощь коллег', icon: <PeopleIcon />, path: '/help-colleague' },
]

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [unreadCount, setUnreadCount] = useState(0)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [notificationsEnabled, setNotificationsEnabled] = useState(() => {
    return localStorage.getItem('notifications-enabled') !== 'false'
  })
  const [postsPerPage, setPostsPerPage] = useState(() => {
    return Number(localStorage.getItem('posts-per-page')) || 20
  })
  const location = useLocation()
  const navigate = useNavigate()

  const handleNotificationsToggle = (enabled: boolean) => {
    setNotificationsEnabled(enabled)
    localStorage.setItem('notifications-enabled', String(enabled))
  }

  const handlePostsPerPageChange = (count: number) => {
    setPostsPerPage(count)
    localStorage.setItem('posts-per-page', String(count))
  }

  useEffect(() => {
    if (!notificationsEnabled) return
    const load = async () => {
      try {
        const count = await helpColleagueService.getUnreadCount()
        setUnreadCount(count)
      } catch { /* ignore */ }
    }
    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [notificationsEnabled])

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleProfileMenuClose = () => {
    setAnchorEl(null)
  }

  const handleNotificationsClick = async () => {
    try {
      await helpColleagueService.markNotificationsRead()
      setUnreadCount(0)
    } catch { /* ignore */ }
    navigate('/help-colleague')
  }

  const drawer = (
    <Box sx={{ height: '100%', bgcolor: 'background.paper', borderRight: '1px solid', borderColor: 'divider' }}>
      <Toolbar sx={{ px: 3, py: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
          >
            <Avatar
              sx={{
                width: 48,
                height: 48,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                fontSize: 24,
                fontWeight: 700,
              }}
            >
              CM
            </Avatar>
          </motion.div>
          <Box>
            <Typography variant="h6" noWrap sx={{ fontWeight: 700, fontSize: 16 }}>
              Chill Marketing
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: 11 }}>
              AI Bot v1.0
            </Typography>
          </Box>
        </Box>
      </Toolbar>

      <List sx={{ px: 2 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 3,
                  py: 1.5,
                  px: 2,
                  bgcolor: isActive ? 'primary.light' : 'transparent',
                  '&:hover': {
                    bgcolor: isActive ? 'primary.light' : 'action.hover',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive ? 'primary.dark' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? 'primary.dark' : 'text.primary',
                    fontSize: 14,
                  }}
                />
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>

      <Box sx={{ position: 'absolute', bottom: 0, width: '100%', p: 2 }}>
        <List>
          <ListItem disablePadding sx={{ mb: 1 }}>
            <ListItemButton sx={{ borderRadius: 3, py: 1.5, px: 2 }} onClick={() => setSettingsOpen(true)}>
              <ListItemIcon sx={{ minWidth: 40, color: 'text.secondary' }}>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="Настройки" primaryTypographyProps={{ fontSize: 14 }} />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <CssBaseline />

      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { sm: `${DRAWER_WIDTH}px` },
          bgcolor: 'background.paper',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' }, color: 'text.primary' }}
          >
            <MenuIcon />
          </IconButton>

          <Box sx={{ flexGrow: 1 }} />

          <IconButton sx={{ color: 'text.primary', mr: 1 }} onClick={handleNotificationsClick}>
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <IconButton onClick={handleProfileMenuOpen} sx={{ color: 'text.primary' }}>
            <AccountCircle />
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            PaperProps={{
              elevation: 0,
              sx: {
                overflow: 'visible',
                filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                mt: 1.5,
                minWidth: 200,
              },
            }}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={() => { handleProfileMenuClose(); navigate('/help-colleague/profile/1') }}>
              <Avatar sx={{ width: 32, height: 32, mr: 2, bgcolor: 'primary.main' }}>U</Avatar>
              Мой профиль
            </MenuItem>
            <MenuItem onClick={handleProfileMenuClose}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Выйти
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: 8,
        }}
      >
        <Outlet context={{ postsPerPage }} />
      </Box>

      <SettingsDialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        notificationsEnabled={notificationsEnabled}
        onNotificationsChange={handleNotificationsToggle}
        postsPerPage={postsPerPage}
        onPostsPerPageChange={handlePostsPerPageChange}
      />
    </Box>
  )
}
