import { parseSseChunk } from "./sse";
import type { ParsedSseEvent, SseEventName } from "../types/chat";

type EventHandlers = Partial<Record<SseEventName, (data: Record<string, unknown>) => void>>;

export async function streamChat(
  message: string,
  handlers: EventHandlers,
  signal?: AbortSignal,
  endpoint = "/api/chat/stream",
): Promise<void> {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!response.ok) {
    const error = await readJsonError(response);
    throw new Error(error.message || `请求失败：${response.status}`);
  }

  if (!response.body) {
    throw new Error("连接失败，请重试");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let doneReceived = false;

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      for (const event of parseSseChunk(`${part}\n\n`)) {
        dispatch(event, handlers);
        if (event.event === "done") {
          doneReceived = true;
        }
      }
    }
  }

  if (buffer.trim()) {
    for (const event of parseSseChunk(`${buffer}\n\n`)) {
      dispatch(event, handlers);
      if (event.event === "done") {
        doneReceived = true;
      }
    }
  }

  if (!doneReceived) {
    throw new Error("生成中断，请重试");
  }
}

function dispatch(event: ParsedSseEvent, handlers: EventHandlers): void {
  handlers[event.event]?.(event.data);
}

async function readJsonError(response: Response): Promise<{ message?: string }> {
  try {
    return (await response.json()) as { message?: string };
  } catch {
    return {};
  }
}
