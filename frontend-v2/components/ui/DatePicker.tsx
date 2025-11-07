import React, { useState, useRef, useEffect } from 'react';
import {
  Button,
  useTheme,
  alpha,
  Popper,
  Paper,
  Box,
  Typography,
  IconButton,
  ClickAwayListener,
} from '@mui/material';
import { DateCalendar } from '@mui/x-date-pickers/DateCalendar';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

interface DatePickerProps {
  selectedDate: string | null;
  availableDates: string[];
  onDateSelect: (date: string | null) => void;
}

export default function DatePicker({
  selectedDate,
  availableDates,
  onDateSelect,
}: DatePickerProps) {
  const [open, setOpen] = useState(false);
  const anchorRef = useRef<HTMLButtonElement>(null);
  const theme = useTheme();

  // Convert string date to Date object
  const value = selectedDate ? new Date(selectedDate + 'T00:00:00') : null;

  // Format date for display
  const formatDisplayDate = (date: Date | null) => {
    if (!date) return 'Latest Newsletter';
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };

  // Handle date change
  const handleDateChange = (newValue: Date | null) => {
    if (newValue) {
      const dateStr = newValue.toISOString().split('T')[0];
      onDateSelect(dateStr);
    } else {
      onDateSelect(null);
    }
    setOpen(false);
  };

  // Check if date should be disabled (not in available dates)
  const isDateDisabled = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return !availableDates.includes(dateStr);
  };

  const [calendarValue, setCalendarValue] = useState<Date | null>(value);

  useEffect(() => {
    setCalendarValue(value);
  }, [value]);

  const handleCalendarChange = (newValue: Date | null) => {
    setCalendarValue(newValue);
    if (newValue) {
      const dateStr = newValue.toISOString().split('T')[0];
      if (availableDates.includes(dateStr)) {
        onDateSelect(dateStr);
        setOpen(false);
      }
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Button
        ref={anchorRef}
        variant="outlined"
        startIcon={<CalendarTodayIcon />}
        endIcon={<KeyboardArrowDownIcon sx={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />}
        onClick={() => setOpen(true)}
        sx={{
          textTransform: 'none',
          px: 2,
          py: 1,
          borderRadius: 2,
          borderColor: 'divider',
          color: 'text.primary',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: alpha(theme.palette.primary.main, 0.08),
          },
        }}
      >
        {formatDisplayDate(value)}
      </Button>

      <Popper
        open={open}
        anchorEl={anchorRef.current}
        placement="bottom"
        sx={{
          zIndex: 1300,
        }}
        modifiers={[
          {
            name: 'offset',
            options: {
              offset: [0, 12],
            },
          },
          {
            name: 'preventOverflow',
            enabled: true,
            options: {
              altAxis: true,
              altBoundary: true,
              tether: true,
              rootBoundary: 'viewport',
            },
          },
        ]}
      >
        <ClickAwayListener onClickAway={() => setOpen(false)}>
          <Paper
            elevation={12}
            sx={{
              borderRadius: 4,
              overflow: 'hidden',
              border: 1,
              borderColor: theme.palette.mode === 'dark' 
                ? alpha(theme.palette.primary.main, 0.3)
                : alpha(theme.palette.primary.main, 0.2),
              boxShadow: theme.palette.mode === 'dark' 
                ? '0 12px 48px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05)' 
                : '0 12px 48px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05)',
              bgcolor: 'background.paper',
              minWidth: 320,
            }}
          >
            <DateCalendar
              value={calendarValue}
              onChange={handleCalendarChange}
              shouldDisableDate={isDateDisabled}
              sx={{
                width: '100%',
                '& .MuiPickersCalendarHeader-root': {
                  px: 3,
                  pt: 3,
                  pb: 2,
                  '& .MuiPickersCalendarHeader-label': {
                    fontSize: '1.125rem',
                    fontWeight: 700,
                    color: 'text.primary',
                    textTransform: 'capitalize',
                  },
                  '& .MuiIconButton-root': {
                    color: 'text.secondary',
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    '&:hover': {
                      bgcolor: alpha(theme.palette.primary.main, 0.12),
                      color: 'primary.main',
                    },
                  },
                },
                '& .MuiDayCalendar-header': {
                  px: 3,
                  pb: 1,
                  '& .MuiTypography-root': {
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: 'text.secondary',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  },
                },
                '& .MuiDayCalendar-weekContainer': {
                  gap: 0.75,
                  px: 3,
                  pb: 2,
                },
                '& .MuiPickersDay-root': {
                  borderRadius: 2,
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  width: 40,
                  height: 40,
                  color: 'text.primary',
                  '&.Mui-selected': {
                    bgcolor: 'primary.main',
                    color: 'white',
                    fontWeight: 700,
                    boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.4)}`,
                    '&:hover': {
                      bgcolor: 'primary.dark',
                      boxShadow: `0 6px 16px ${alpha(theme.palette.primary.main, 0.5)}`,
                    },
                    '&:focus': {
                      bgcolor: 'primary.main',
                    },
                  },
                  '&:not(.Mui-selected):not(.Mui-disabled)': {
                    '&:hover': {
                      bgcolor: alpha(theme.palette.primary.main, 0.12),
                      color: 'primary.main',
                      fontWeight: 600,
                    },
                  },
                  '&.Mui-disabled': {
                    opacity: 0.25,
                    color: 'text.disabled',
                  },
                  '&.MuiPickersDay-today': {
                    border: `2px solid ${theme.palette.primary.main}`,
                    fontWeight: 600,
                    '&:not(.Mui-selected)': {
                      bgcolor: 'transparent',
                    },
                  },
                },
              }}
            />
            <Box
              sx={{
                px: 3,
                py: 0.5,
                borderTop: 1,
                borderColor: 'divider',
                bgcolor: alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.08 : 0.04),
                textAlign: 'center',
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  color: 'text.secondary',
                  '&:hover': {
                    color: 'primary.main',
                    cursor: 'default',
                  },
                }}
              >
                {availableDates.length} newsletter{availableDates.length !== 1 ? 's' : ''} available
              </Typography>
            </Box>
          </Paper>
        </ClickAwayListener>
      </Popper>
    </LocalizationProvider>
  );
}

