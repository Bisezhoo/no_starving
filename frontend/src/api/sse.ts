import type { ParsedSseEvent, SseEventName } from "../types/chat";

const eventNames = new Set<string>([
  "meta",
  "delta",
  "tool_call",
  "tool_result",
  "card",
  "profile_update",
  "error",
  "done",
]);

export function parseSseChunk(chunk: string): ParsedSseEvent[] {
  return chunk
    .split(/\n\n/)
    .map((block) => block.trim())
    .filter(Boolean)
    .map(parseSseBlock)
    .filter((event): event is ParsedSseEvent => event !== null);
}

function parseSseBlock(block: string): ParsedSseEvent | null {
  let eventName: string | undefined;
  const dataLines: string[] = [];

  for (const line of block.split(/\n/)) {
    if (line.startsWith("event:")) {
      eventName = line.slice("event:".length).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trim());
    }
  }

  if (!eventName || !eventNames.has(eventName)) {
    return null;
  }

  const rawData = dataLines.join("\n");
  return {
    event: eventName as SseEventName,
    data: rawData ? JSON.parse(rawData) : {},
  };
}
