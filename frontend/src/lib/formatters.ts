import { format, formatDistanceToNow } from "date-fns";

export function formatDate(date: string | Date, pattern = "PPpp"): string {
  return format(new Date(date), pattern);
}

export function formatRelative(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

export function formatEnum(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
