import { Card, CardContent } from "@/components/ui/card";

/** One reusable "not available yet" card — used for Policies / Active Claims
 * / Renewals / Recent Payments (no Policy/Claim/Payment domain exists
 * anywhere in the backend, confirmed) and AI Summary / Current Intent (the
 * spec explicitly asks for a placeholder here, not real generation). Honest
 * about what's real vs not, rather than fabricating numbers. */
export function Customer360PlaceholderSection({
  title,
  message = "Not available yet — no backing data source integrated in this phase.",
}: {
  title: string;
  message?: string;
}) {
  return (
    <Card>
      <CardContent className="p-3">
        <p className="text-xs font-semibold">{title}</p>
        <p className="mt-1 text-[11px] text-muted-foreground">{message}</p>
      </CardContent>
    </Card>
  );
}
