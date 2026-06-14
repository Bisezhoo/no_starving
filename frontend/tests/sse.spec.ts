import { describe, expect, it } from "vitest";
import { parseSseChunk } from "../src/api/sse";

describe("parseSseChunk", () => {
  it("parses done warnings without dropping cards", () => {
    const events = parseSseChunk(
      'event: done\ndata: {"reply":"ok","cards":[{"type":"meal","id":"1","title":"A"}],"warnings":["本次偏好可能未保存"]}\n\n',
    );

    expect(events[0].event).toBe("done");
    expect(events[0].data.cards).toHaveLength(1);
    expect(events[0].data.warnings).toEqual(["本次偏好可能未保存"]);
  });
});
