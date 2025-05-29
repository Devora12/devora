import { format, parseISO } from 'date-fns';

export const formatDate = (dateString) => {
  try {
    if (!dateString) return '';
    return format(parseISO(dateString), 'yyyy-MM-dd');
  } catch (e) {
    console.error("Date formatting error:", e);
    return dateString;
  }
};

export const calculateDaysDifference = (date1, date2) => {
  return Math.floor((new Date(date1) - new Date(date2)) / (1000 * 60 * 60 * 24));
};

export const formatNumber = (number, decimals = 1) => {
  return Number(number).toFixed(decimals);
};

export const getEfficiencyColor = (ratio) => {
  if (ratio > 0.5) return "text-green-500";
  if (ratio < 0.3) return "text-red-500";
  return "text-orange-500";
};