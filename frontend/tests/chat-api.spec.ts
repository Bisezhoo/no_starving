import { describe, expect, it, vi } from "vitest";
import { loadChatHistory, streamChat } from "../src/api/chat";

describe("streamChat", () => {
  it("throws backend JSON error before parsing SSE", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 400,
        json: async () => ({ code: 400, message: "message 不能为空", data: {} }),
      })),
    );

    await expect(streamChat(" ", {})).rejects.toThrow("message 不能为空");
    vi.unstubAllGlobals();
  });

  it("loads chat history messages", async () => {
    const history = [
      { role: "user", content: "你是谁？", createdAt: "2026-06-14T10:00:00+00:00" },
      {
        role: "assistant",
        reply: "我是食谱助手",
        cards: [],
        toolCalls: [],
        warnings: [],
        createdAt: "2026-06-14T10:00:01+00:00",
      },
    ];
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({ code: 200, message: "success", data: { messages: history } }),
      })),
    );

    await expect(loadChatHistory()).resolves.toEqual(history);
    vi.unstubAllGlobals();
  });
});
