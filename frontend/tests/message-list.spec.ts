import { flushPromises, mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { afterEach, describe, expect, it } from "vitest";
import MessageList from "../src/components/MessageList.vue";
import type { ChatMessage } from "../src/types/chat";

let currentScrollHeight = 0;
let originalScrollHeight: PropertyDescriptor | undefined;

function installScrollHeightStub() {
  originalScrollHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "scrollHeight");
  Object.defineProperty(HTMLElement.prototype, "scrollHeight", {
    configurable: true,
    get() {
      return currentScrollHeight;
    },
  });
}

function restoreScrollHeightStub() {
  if (originalScrollHeight) {
    Object.defineProperty(HTMLElement.prototype, "scrollHeight", originalScrollHeight);
  }
}

afterEach(() => {
  restoreScrollHeightStub();
  currentScrollHeight = 0;
});

describe("MessageList", () => {
  it("scrolls to the bottom on mount and whenever messages change", async () => {
    installScrollHeightStub();
    currentScrollHeight = 200;
    const messages: ChatMessage[] = [{ role: "user", content: "第一条" }];

    const wrapper = mount(MessageList, {
      props: { messages },
    });
    const list = wrapper.find(".message-list").element as HTMLElement;
    await flushPromises();

    expect(list.scrollTop).toBe(200);

    currentScrollHeight = 360;
    messages.push({
      role: "assistant",
      reply: "思考中",
      cards: [],
      toolCalls: [],
      warnings: [],
    });
    await wrapper.setProps({ messages: [...messages] });
    await flushPromises();

    expect(list.scrollTop).toBe(360);

    currentScrollHeight = 520;
    const assistant = messages[1];
    if (assistant.role === "assistant") {
      assistant.reply = "思考中，正在推荐一道晚餐";
    }
    await wrapper.setProps({ messages: [...messages] });
    await nextTick();
    await flushPromises();

    expect(list.scrollTop).toBe(520);
  });
});
