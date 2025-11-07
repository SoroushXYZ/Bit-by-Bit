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
  newsletterDate: string | null; // The actual date of the current newsletter
  onDateSelect: (date: string | null) => void;
}

export default function DatePicker({
  selectedDate,
  availableDates,
  newsletterDate,
  onDateSelect,
}: DatePickerProps) {
  const [open, setOpen] = useState(false);
  const anchorRef = useRef<HTMLButtonElement>(null);
  const theme = useTheme();

  // Convert string date to Date object for calendar
  // If selectedDate is null (Latest), use newsletterDate to highlight the actual date in calendar
  const calendarValue = selectedDate 
    ? new Date(selectedDate + 'T00:00:00') 
    : (newsletterDate ? new Date(newsletterDate + 'T00:00:00') : null);

  // Format date for display - only show date if selectedDate is explicitly set
  const formatDisplayDate = () => {
    if (!selectedDate) return 'Latest Newsletter';
    const date = new Date(selectedDate + 'T00:00:00');
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

  const handleCalendarChange = (newValue: Date | null) => {
    if (newValue) {
      const dateStr = newValue.toISOString().split('T')[0];
      if (availableDates.includes(dateStr)) {
        onDateSelect(dateStr);
        setOpen(false);
      }
      // Don't update calendar value if date is not available - let it stay on current selection
    } else {
      onDateSelect(null);
      setOpen(false);
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
        {formatDisplayDate()}
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
              slotProps={{
                day: (ownerState) => {
                  const dayDate = ownerState.day;
                  const dayDateStr = dayDate.toISOString().split('T')[0];
                  // Highlight if it's the newsletter date when selectedDate is null (Latest)
                  // Only highlight if it's not already selected by the calendar
                  const isNewsletterDate = !selectedDate && newsletterDate && dayDateStr === newsletterDate;
                  const isSelectedByCalendar = calendarValue && dayDateStr === calendarValue.toISOString().split('T')[0];
                  
                  return {
                    sx: {
                      ...(isNewsletterDate && !isSelectedByCalendar && {
                        border: `2px solid ${theme.palette.primary.main}`,
                        bgcolor: alpha(theme.palette.primary.main, 0.1),
                        fontWeight: 600,
                      }),
                    },
                  };
                },
              }}
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

