import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ChatPage from "../src/components/ChatPage.vue";

type StreamHandlers = Partial<Record<string, (data: Record<string, unknown>) => void>>;

function createDeferred() {
  let resolve!: () => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<void>((promiseResolve, promiseReject) => {
    resolve = promiseResolve;
    reject = promiseReject;
  });
  return { promise, resolve, reject };
}

const { loadChatHistoryMock, streamChatMock } = vi.hoisted(() => ({
  loadChatHistoryMock: vi.fn(),
  streamChatMock: vi.fn(),
}));

vi.mock("../src/api/chat", () => ({
  loadChatHistory: loadChatHistoryMock,
  streamChat: streamChatMock,
}));

describe("ChatPage", () => {
  beforeEach(() => {
    loadChatHistoryMock.mockReset();
    streamChatMock.mockReset();
    loadChatHistoryMock.mockResolvedValue([]);
  });

  it("shows default welcome message when chat history is empty", async () => {
    loadChatHistoryMock.mockResolvedValueOnce([]);

    const wrapper = mount(ChatPage);
    await flushPromises();

    expect(loadChatHistoryMock).toHaveBeenCalledOnce();
    expect(wrapper.text()).toContain("你好！我是你的 食谱助手（Recipe Assistant）");
    expect(wrapper.text()).toContain("搜索菜肴食谱");
    expect(wrapper.text()).toContain("查找饮品配方");
    expect(wrapper.text()).toContain("有什么想做的菜或想喝的饮品");
  });

  it("loads chat history on mount", async () => {
    loadChatHistoryMock.mockResolvedValueOnce([
      { role: "user", content: "昨天想吃什么？", createdAt: "2026-06-14T10:00:00+00:00" },
      {
        role: "assistant",
        reply: "推荐鸡肉饭",
        cards: [],
        toolCalls: [],
        warnings: [],
        createdAt: "2026-06-14T10:00:01+00:00",
      },
    ]);

    const wrapper = mount(ChatPage);
    await flushPromises();

    expect(loadChatHistoryMock).toHaveBeenCalledOnce();
    expect(wrapper.text()).toContain("昨天想吃什么？");
    expect(wrapper.text()).toContain("推荐鸡肉饭");
  });

  it("does not insert default welcome message when chat history exists", async () => {
    loadChatHistoryMock.mockResolvedValueOnce([
      { role: "user", content: "昨天想吃什么？", createdAt: "2026-06-14T10:00:00+00:00" },
      {
        role: "assistant",
        reply: "推荐鸡肉饭",
        cards: [],
        toolCalls: [],
        warnings: [],
        createdAt: "2026-06-14T10:00:01+00:00",
      },
    ]);

    const wrapper = mount(ChatPage);
    await flushPromises();

    expect(wrapper.text()).toContain("昨天想吃什么？");
    expect(wrapper.text()).toContain("推荐鸡肉饭");
    expect(wrapper.text()).not.toContain("你好！我是你的 食谱助手（Recipe Assistant）");
  });

  it("shows default welcome message and still sends when chat history fails", async () => {
    loadChatHistoryMock.mockRejectedValueOnce(new Error("history unavailable"));
    streamChatMock.mockImplementationOnce(async (_message: string, handlers: StreamHandlers) => {
      handlers.done?.({
        reply: "推荐鸡肉饭",
        cards: [],
        toolCalls: [],
        warnings: [],
      });
    });

    const wrapper = mount(ChatPage);
    await flushPromises();

    expect(wrapper.text()).toContain("你好！我是你的 食谱助手（Recipe Assistant）");

    await wrapper.find("textarea").setValue("推荐一道晚餐");
    await wrapper.find("form").trigger("submit.prevent");
    await flushPromises();

    expect(streamChatMock).toHaveBeenCalledWith("推荐一道晚餐", expect.any(Object));
    expect(wrapper.text()).toContain("推荐一道晚餐");
    expect(wrapper.text()).toContain("推荐鸡肉饭");
  });

  it("renders assistant text received from stream callbacks", async () => {
    streamChatMock.mockImplementationOnce(async (_message: string, handlers: StreamHandlers) => {
      await Promise.resolve();
      handlers.delta?.({ text: "你好" });
      await Promise.resolve();
      handlers.delta?.({ text: "，我是食谱助手" });
      await Promise.resolve();
      handlers.done?.({
        reply: "你好，我是食谱助手",
        cards: [],
        toolCalls: [],
        warnings: [],
      });
    });

    const wrapper = mount(ChatPage);

    await wrapper.find("textarea").setValue("你是谁？");
    await wrapper.find("form").trigger("submit.prevent");
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("你是谁？");
    expect(wrapper.text()).toContain("你好，我是食谱助手");
    expect(wrapper.find(".assistant-result-block").exists()).toBe(false);
    expect(wrapper.find(".assistant-tabs").exists()).toBe(false);
  });

  it("shows thinking placeholder before stream content arrives", async () => {
    const deferred = createDeferred();
    let streamHandlers: StreamHandlers = {};
    streamChatMock.mockImplementationOnce(async (_message: string, handlers: StreamHandlers) => {
      streamHandlers = handlers;
      await deferred.promise;
    });

    const wrapper = mount(ChatPage);

    await wrapper.find("textarea").setValue("推荐一道晚餐");
    await wrapper.find("form").trigger("submit.prevent");
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("推荐一道晚餐");
    expect(wrapper.text()).toContain("思考中");

    streamHandlers.delta?.({ text: "推荐番茄鸡蛋面" });
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).not.toContain("思考中");
    expect(wrapper.text()).toContain("推荐番茄鸡蛋面");

    streamHandlers.done?.({
      reply: "推荐番茄鸡蛋面",
      cards: [],
      toolCalls: [],
      warnings: [],
    });
    deferred.resolve();
    await flushPromises();
  });

  it("shows streaming hint after meta and hides it after done", async () => {
    const deferred = createDeferred();
    let streamHandlers: StreamHandlers = {};
    streamChatMock.mockImplementationOnce(async (_message: string, handlers: StreamHandlers) => {
      streamHandlers = handlers;
      await deferred.promise;
    });

    const wrapper = mount(ChatPage);

    await wrapper.find("textarea").setValue("推荐一道晚餐");
    await wrapper.find("form").trigger("submit.prevent");
    await wrapper.vm.$nextTick();

    streamHandlers.meta?.({ requestId: "r1" });
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("疯狂思考中，请稍等");

    streamHandlers.delta?.({ text: "推荐番茄鸡蛋面" });
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("疯狂思考中，请稍等");
    expect(wrapper.text()).toContain("推荐番茄鸡蛋面");

    streamHandlers.done?.({
      reply: "推荐番茄鸡蛋面",
      cards: [],
      toolCalls: [],
      warnings: [],
    });
    deferred.resolve();
    await flushPromises();

    expect(wrapper.text()).not.toContain("疯狂思考中，请稍等");
    expect(wrapper.text()).toContain("推荐番茄鸡蛋面");
  });

  it("hides streaming hint when stream returns an error after meta", async () => {
    const deferred = createDeferred();
    let streamHandlers: StreamHandlers = {};
    streamChatMock.mockImplementationOnce(async (_message: string, handlers: StreamHandlers) => {
      streamHandlers = handlers;
      await deferred.promise;
    });

    const wrapper = mount(ChatPage);

    await wrapper.find("textarea").setValue("推荐一道晚餐");
    await wrapper.find("form").trigger("submit.prevent");
    await wrapper.vm.$nextTick();

    streamHandlers.meta?.({ requestId: "r1" });
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("疯狂思考中，请稍等");

    streamHandlers.error?.({ message: "服务暂时不可用" });
    deferred.resolve();
    await flushPromises();

    expect(wrapper.text()).not.toContain("疯狂思考中，请稍等");
    expect(wrapper.text()).toContain("服务暂时不可用");
  });

  it("replaces thinking placeholder with stream error message", async () => {
    const deferred = createDeferred();
    streamChatMock.mockImplementationOnce(async () => {
      await deferred.promise;
    });

    const wrapper = mount(ChatPage);

    await wrapper.find("textarea").setValue("推荐一道晚餐");
    await wrapper.find("form").trigger("submit.prevent");
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("思考中");

    deferred.reject(new Error("服务暂时不可用"));
    await flushPromises();

    expect(wrapper.text()).not.toContain("思考中");
    expect(wrapper.text()).toContain("服务暂时不可用");
  });
});
