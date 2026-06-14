import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const __dirname = dirname(fileURLToPath(import.meta.url));
const css = readFileSync(resolve(__dirname, "../src/styles/app.css"), "utf-8");

function ruleFor(selector: string) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = css.match(new RegExp(`${escaped}\\s*\\{([^}]*)\\}`, "m"));
  return match?.[1] ?? "";
}

describe("chat page fixed viewport layout", () => {
  it("keeps the page viewport fixed while the message list scrolls", () => {
    expect(ruleFor("html,\nbody,\n#app")).toContain("height: 100%");
    expect(ruleFor(".app-shell")).toContain("height: 100vh");
    expect(ruleFor(".app-shell")).toContain("padding: 0 24px");
    expect(ruleFor(".app-shell")).toContain("overflow: hidden");
    expect(ruleFor(".chat-surface")).toContain("height: 100%");
    expect(ruleFor(".chat-surface")).toContain("grid-template-rows: auto minmax(0, 1fr) auto");
    expect(ruleFor(".message-list")).toContain("min-height: 0");
    expect(ruleFor(".message-list")).toContain("overflow-y: auto");
  });
});
