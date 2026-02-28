// Simple date utility functions to replace date-fns dependency

export function format(date: Date, formatStr: string): string {
  const d = new Date(date);

  const year = d.getFullYear();
  const month = d.getMonth();
  const day = d.getDate();
  const hours = d.getHours();
  const minutes = d.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const hours12 = hours % 12 || 12;

  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const fullMonthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  let result = formatStr;

  // Year
  result = result.replace(/yyyy/g, year.toString());
  result = result.replace(/yy/g, year.toString().slice(-2));

  // Month
  result = result.replace(/MMMM/g, fullMonthNames[month]);
  result = result.replace(/MMM/g, monthNames[month]);
  result = result.replace(/MM/g, (month + 1).toString().padStart(2, '0'));
  result = result.replace(/M/g, (month + 1).toString());

  // Day
  result = result.replace(/dd/g, day.toString().padStart(2, '0'));
  result = result.replace(/d/g, day.toString());

  // Hours
  result = result.replace(/hh/g, hours12.toString().padStart(2, '0'));
  result = result.replace(/h/g, hours12.toString());
  result = result.replace(/HH/g, hours.toString().padStart(2, '0'));
  result = result.replace(/H/g, hours.toString());

  // Minutes
  result = result.replace(/mm/g, minutes.toString().padStart(2, '0'));
  result = result.replace(/m/g, minutes.toString());

  // AM/PM
  result = result.replace(/a/g, ampm.toLowerCase());

  return result;
}

export function startOfDay(date: Date): Date {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

export function endOfDay(date: Date): Date {
  const d = new Date(date);
  d.setHours(23, 59, 59, 999);
  return d;
}

export function subDays(date: Date, days: number): Date {
  const d = new Date(date);
  d.setDate(d.getDate() - days);
  return d;
}

export function subMonths(date: Date, months: number): Date {
  const d = new Date(date);
  d.setMonth(d.getMonth() - months);
  return d;
}

export function isWithinInterval(date: Date, interval: { start: Date; end: Date }): boolean {
  const d = new Date(date);
  const start = new Date(interval.start);
  const end = new Date(interval.end);
  return d >= start && d <= end;
}