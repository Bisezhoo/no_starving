import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AssistantMessageTabs from "../src/components/AssistantMessageTabs.vue";

describe("AssistantMessageTabs", () => {
  it("shows non-blocking warnings without hiding cards", () => {
    const wrapper = mount(AssistantMessageTabs, {
      props: {
        message: {
          role: "assistant",
          reply: "ok",
          cards: [
            {
              type: "meal",
              id: "1",
              title: "Chicken Handi",
              imageUrl: "https://img.example/x.jpg",
              tags: [],
              ingredients: [],
            },
          ],
          toolCalls: [],
          warnings: ["本次偏好可能未保存"],
        },
      },
    });

    expect(wrapper.text()).toContain("本次偏好可能未保存");
    expect(wrapper.text()).toContain("Chicken Handi");
  });
});
