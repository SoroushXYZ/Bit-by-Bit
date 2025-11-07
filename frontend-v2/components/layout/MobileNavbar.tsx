import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  useTheme,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import { useState } from 'react';
import ThemeToggle from '@/components/theme/ThemeToggle';
import DatePicker from '@/components/ui/DatePicker';
import { useNewsletterContext } from '@/contexts/NewsletterContext';

/**
 * Mobile-optimized navbar with drawer menu
 */
export default function MobileNavbar() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const theme = useTheme();
  const { selectedDate, availableDates, newsletterDate, selectDate } = useNewsletterContext();

  const toggleDrawer = (open: boolean) => () => {
    setDrawerOpen(open);
  };

  const menuItems = [
    { label: 'Home', href: '/' },
    { label: 'Newsletters', href: '/newsletters' },
    { label: 'About', href: '/about' },
  ];

  return (
    <>
      <AppBar
        position="sticky"
        elevation={2}
        sx={{
          backgroundColor: 'background.paper',
          color: 'text.primary',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between', minHeight: 64 }}>
          <Typography
            variant="h5"
            component="div"
            sx={{
              fontWeight: 700,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Bit-by-Bit
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1, justifyContent: 'center' }}>
            <DatePicker
              selectedDate={selectedDate}
              availableDates={availableDates}
              newsletterDate={newsletterDate}
              onDateSelect={selectDate}
            />
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ThemeToggle />
            <IconButton
              edge="end"
              color="inherit"
              aria-label="menu"
              onClick={toggleDrawer(true)}
            >
              <MenuIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
        PaperProps={{
          sx: {
            width: 280,
            backgroundColor: 'background.paper',
          },
        }}
      >
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontWeight={600}>
            Menu
          </Typography>
          <IconButton onClick={toggleDrawer(false)} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.label} disablePadding>
              <ListItemButton
                onClick={toggleDrawer(false)}
                sx={{
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontWeight: 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>
    </>
  );
}

