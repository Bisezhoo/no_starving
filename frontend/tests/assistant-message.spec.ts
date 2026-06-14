import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AssistantMessage from "../src/components/AssistantMessage.vue";

describe("AssistantMessage", () => {
  it("renders thinking placeholder while assistant reply is pending", () => {
    const wrapper = mount(AssistantMessage, {
      props: {
        message: {
          role: "assistant",
          reply: "",
          cards: [],
          toolCalls: [],
          warnings: [],
          profileUpdates: [],
          pending: true,
        },
      },
    });

    expect(wrapper.text()).toContain("思考中");
    expect(wrapper.find(".assistant-pending").exists()).toBe(true);
  });

  it("renders plain assistant reply without result tabs when there are no cards", () => {
    const wrapper = mount(AssistantMessage, {
      props: {
        message: {
          role: "assistant",
          reply: "你好！我是你的食谱助手。",
          cards: [],
          toolCalls: [],
          warnings: [],
          profileUpdates: [],
        },
      },
    });

    expect(wrapper.text()).toContain("你好！我是你的食谱助手。");
    expect(wrapper.text()).not.toContain("推荐");
    expect(wrapper.text()).not.toContain("暂无推荐");
    expect(wrapper.find(".assistant-result-block").exists()).toBe(false);
  });

  it("keeps text reply and renders result block when cards exist", () => {
    const wrapper = mount(AssistantMessage, {
      props: {
        message: {
          role: "assistant",
          reply: "好的，我给你 3 个中餐选择。",
          cards: [
            {
              type: "meal",
              id: "1",
              title: "Chicken Handi",
              localizedSummary: "适合配米饭。",
              imageUrl: "https://img.example/x.jpg",
              tags: [],
              ingredients: [{ name: "Chicken", measure: "500g" }],
            },
          ],
          toolCalls: [],
          warnings: ["本次偏好可能未保存"],
          profileUpdates: [],
        },
      },
    });

    expect(wrapper.text()).toContain("好的，我给你 3 个中餐选择。");
    expect(wrapper.text()).toContain("Chicken Handi");
    expect(wrapper.text()).toContain("本次偏好可能未保存");
    expect(wrapper.find(".assistant-result-block").exists()).toBe(true);
  });

  it("renders basic markdown reply without exposing markdown markers or raw html", () => {
    const wrapper = mount(AssistantMessage, {
      props: {
        message: {
          role: "assistant",
          reply:
            "### 🍽️ 我能做什么？\n1. **搜索菜肴食谱** — 根据菜名查找\n- 🏠 **清空冰箱** — 用家里食材找菜\n[查看来源](https://example.com/recipe)\n\n```txt\nchicken\nrice\n```\n---\n**有什么想吃的，尽管告诉我。**\n<script>alert('xss')</script>",
          cards: [],
          toolCalls: [],
          warnings: [],
          profileUpdates: [],
        },
      },
    });

    expect(wrapper.find("h3").text()).toContain("🍽️ 我能做什么？");
    expect(wrapper.find("ol li strong").text()).toBe("搜索菜肴食谱");
    expect(wrapper.find("ul li strong").text()).toBe("清空冰箱");
    expect(wrapper.find("a").attributes("href")).toBe("https://example.com/recipe");
    expect(wrapper.find("pre code").text()).toContain("chicken");
    expect(wrapper.find("hr").exists()).toBe(true);
    expect(wrapper.find("script").exists()).toBe(false);
    expect(wrapper.text()).not.toContain("###");
    expect(wrapper.text()).not.toContain("**");
    expect(wrapper.text()).not.toContain("---");
    expect(wrapper.html()).not.toContain("<script>");
    expect(wrapper.text()).not.toContain("alert('xss')");
    expect(wrapper.find(".assistant-result-block").exists()).toBe(false);
  });
});
