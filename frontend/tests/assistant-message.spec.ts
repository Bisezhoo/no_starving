import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AssistantMessage from "../src/components/AssistantMessage.vue";

describe("AssistantMessage", () => {
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
});
