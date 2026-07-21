import type { TimelineItem as TimelineItemType } from "@/features/conversations/types";

import { TimelineEvent } from "./timeline-event";
import { TimelineMessage } from "./timeline-message";

export function TimelineItemRow({ item }: { item: TimelineItemType }) {
  if (item.type === "message") return <TimelineMessage item={item} />;
  return <TimelineEvent item={item} />;
}
