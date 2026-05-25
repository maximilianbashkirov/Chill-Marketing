import { useState } from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  Switch, Typography, Box, Divider, Select, MenuItem, FormControlLabel,
} from '@mui/material'
import { DarkMode, LightMode, Notifications as NotifIcon, Language, ViewList } from '@mui/icons-material'
import { useThemeMode } from '../contexts/ThemeContext'

interface SettingsDialogProps {
  open: boolean
  onClose: () => void
  notificationsEnabled: boolean
  onNotificationsChange: (enabled: boolean) => void
  postsPerPage: number
  onPostsPerPageChange: (count: number) => void
}

export default function SettingsDialog({
  open, onClose,
  notificationsEnabled, onNotificationsChange,
  postsPerPage, onPostsPerPageChange,
}: SettingsDialogProps) {
  const { mode, toggleTheme } = useThemeMode()
  const [localNotif, setLocalNotif] = useState(notificationsEnabled)
  const [localPerPage, setLocalPerPage] = useState(postsPerPage)

  const handleSave = () => {
    onNotificationsChange(localNotif)
    onPostsPerPageChange(localPerPage)
    onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>Настройки</DialogTitle>
      <DialogContent>
        {/* Theme */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            {mode === 'dark' ? <DarkMode color="primary" /> : <LightMode color="warning" />}
            <Typography>Тема</Typography>
          </Box>
          <FormControlLabel
            control={<Switch checked={mode === 'dark'} onChange={toggleTheme} />}
            label={mode === 'dark' ? 'Тёмная' : 'Светлая'}
            labelPlacement="start"
            sx={{ m: 0 }}
          />
        </Box>
        <Divider sx={{ my: 0.5 }} />

        {/* Notifications */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <NotifIcon color="action" />
            <Typography>Уведомления</Typography>
          </Box>
          <Switch checked={localNotif} onChange={(_, v) => setLocalNotif(v)} />
        </Box>
        <Divider sx={{ my: 0.5 }} />

        {/* Posts per page */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <ViewList color="action" />
            <Typography>Постов на странице</Typography>
          </Box>
          <Select value={localPerPage} onChange={(e) => setLocalPerPage(Number(e.target.value))} size="small" sx={{ minWidth: 80 }}>
            <MenuItem value={10}>10</MenuItem>
            <MenuItem value={20}>20</MenuItem>
            <MenuItem value={50}>50</MenuItem>
          </Select>
        </Box>
        <Divider sx={{ my: 0.5 }} />

        {/* Language */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Language color="action" />
            <Typography>Язык</Typography>
          </Box>
          <Select value="ru" size="small" sx={{ minWidth: 120 }} disabled>
            <MenuItem value="ru">Русский</MenuItem>
          </Select>
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} color="inherit">Отмена</Button>
        <Button onClick={handleSave} variant="contained">Сохранить</Button>
      </DialogActions>
    </Dialog>
  )
}
