import React, { useState, useEffect } from 'react';
import { Calendar, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DatePickerProps {
  selectedDate: string | null;
  availableDates: string[];
  onDateSelect: (date: string | null) => void;
  className?: string;
}

export default function DatePicker({ 
  selectedDate, 
  availableDates, 
  onDateSelect, 
  className 
}: DatePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());

  // Format date for display
  const formatDisplayDate = (dateStr: string | null) => {
    if (!dateStr) return 'Latest Newsletter';
    // Parse date in local timezone to avoid timezone issues
    const [year, month, day] = dateStr.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    
    // Debug logging (remove in production)
    console.log('Formatting date:', { dateStr, year, month, day, date: date.toISOString() });
    
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  // Check if date is available
  const isDateAvailable = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return availableDates.includes(dateStr);
  };

  // Check if date is selected
  const isDateSelected = (date: Date) => {
    if (!selectedDate) return false;
    const dateStr = date.toISOString().split('T')[0];
    return dateStr === selectedDate;
  };

  // Get days in month
  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  // Navigate months
  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      if (direction === 'prev') {
        newMonth.setMonth(prev.getMonth() - 1);
      } else {
        newMonth.setMonth(prev.getMonth() + 1);
      }
      return newMonth;
    });
  };

  // Handle date selection
  const handleDateClick = (date: Date) => {
    if (isDateAvailable(date)) {
      const dateStr = date.toISOString().split('T')[0];
      onDateSelect(dateStr);
      setIsOpen(false);
    }
  };


  const days = getDaysInMonth(currentMonth);
  const monthYear = currentMonth.toLocaleDateString('en-US', { 
    month: 'long', 
    year: 'numeric' 
  });

  return (
    <div className={cn("relative", className)}>
      {/* Date Display Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="group flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/20 transition-all duration-200 text-sm font-medium text-gray-800 dark:text-gray-200"
      >
        <Calendar className="w-4 h-4" />
        <span className="truncate max-w-[200px]">
          {formatDisplayDate(selectedDate)}
        </span>
        <ChevronDown className={cn(
          "w-4 h-4 transition-transform duration-200",
          isOpen && "rotate-180"
        )} />
      </button>

      {/* Calendar Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Calendar Panel */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 z-50 w-80 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border border-white/20 dark:border-gray-700/50 rounded-xl shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200/50 dark:border-gray-700/50">
              <button
                onClick={() => navigateMonth('prev')}
                className="p-2 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-lg transition-colors"
              >
                <ChevronDown className="w-4 h-4 rotate-90" />
              </button>
              
              <h3 className="font-semibold text-gray-800 dark:text-gray-200">
                {monthYear}
              </h3>
              
              <button
                onClick={() => navigateMonth('next')}
                className="p-2 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-lg transition-colors"
              >
                <ChevronDown className="w-4 h-4 -rotate-90" />
              </button>
            </div>


            {/* Calendar Grid */}
            <div className="p-4">
              {/* Day Headers */}
              <div className="grid grid-cols-7 gap-1 mb-2">
                {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                  <div key={day} className="text-center text-xs font-medium text-gray-500 dark:text-gray-400 py-2">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Days */}
              <div className="grid grid-cols-7 gap-1">
                {days.map((day, index) => {
                  if (!day) {
                    return <div key={index} className="h-8" />;
                  }

                  const isAvailable = isDateAvailable(day);
                  const isSelected = isDateSelected(day);
                  const isToday = day.toDateString() === new Date().toDateString();

                  return (
                    <button
                      key={day.toISOString()}
                      onClick={() => handleDateClick(day)}
                      disabled={!isAvailable}
                      className={cn(
                        "h-8 w-8 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center",
                        isAvailable
                          ? "hover:bg-blue-100 dark:hover:bg-blue-900/30 cursor-pointer"
                          : "cursor-not-allowed opacity-30",
                        isSelected
                          ? "bg-blue-500 text-white shadow-lg"
                          : isToday
                          ? "bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
                          : "text-gray-700 dark:text-gray-300"
                      )}
                    >
                      {day.getDate()}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Footer Info */}
            <div className="px-4 py-3 bg-gray-50/50 dark:bg-gray-800/50 border-t border-gray-200/50 dark:border-gray-700/50">
              <p className="text-xs text-gray-600 dark:text-gray-400 text-center">
                {availableDates.length} newsletter{availableDates.length !== 1 ? 's' : ''} available
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
