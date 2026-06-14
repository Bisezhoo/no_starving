import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import ToolTracePanel from "../src/components/ToolTracePanel.vue";

const toolCalls = [
  { id: "1", name: "search_meals", status: "success", resultCount: 5, durationMs: 11829 },
  { id: "2", name: "search_meals", status: "success", resultCount: 10, durationMs: 17941 },
];

describe("ToolTracePanel", () => {
  it("collapses tool calls into a compact summary by default", () => {
    const wrapper = mount(ToolTracePanel, {
      props: { items: toolCalls },
    });

    expect(wrapper.text()).toContain("Loaded 2 tools");
    expect(wrapper.text()).not.toContain("search_meals");
    expect(wrapper.text()).not.toContain("success");
    expect(wrapper.text()).not.toContain("11829ms");
  });

  it("expands and collapses tool call details when clicking the summary", async () => {
    const wrapper = mount(ToolTracePanel, {
      props: { items: toolCalls },
    });

    await wrapper.get("button.tool-trace-toggle").trigger("click");

    expect(wrapper.text()).toContain("search_meals");
    expect(wrapper.text()).toContain("success");
    expect(wrapper.text()).toContain("5 results");
    expect(wrapper.text()).toContain("11829ms");

    await wrapper.get("button.tool-trace-toggle").trigger("click");

    expect(wrapper.text()).toContain("Loaded 2 tools");
    expect(wrapper.text()).not.toContain("11829ms");
  });

  it("keeps the existing empty state when there are no tool calls", () => {
    const wrapper = mount(ToolTracePanel, {
      props: { items: [] },
    });

    expect(wrapper.text()).toContain("暂无 Tool 调用");
    expect(wrapper.find("button.tool-trace-toggle").exists()).toBe(false);
  });
});
