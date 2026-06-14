import { describe, expect, it, vi } from "vitest";
import { streamChat } from "../src/api/chat";

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
});
