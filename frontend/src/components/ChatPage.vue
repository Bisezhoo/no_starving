<template>
  <main class="app-shell">
    <section class="chat-surface">
      <header class="topbar">
        <h1>智能食谱助手</h1>
        <span :class="['status-dot', sending ? 'busy' : 'ready']">{{ sending ? "生成中" : "就绪" }}</span>
      </header>

      <MessageList :messages="messages" />
      <MessageComposer :disabled="sending" @send="send" />
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { loadChatHistory, streamChat } from "../api/chat";
import type { AssistantMessage, Card, ChatMessage, ToolTraceItem } from "../types/chat";
import MessageComposer from "./MessageComposer.vue";
import MessageList from "./MessageList.vue";

const messages = ref<ChatMessage[]>([]);
const sending = ref(false);

const DEFAULT_WELCOME_REPLY = `你好！我是你的 食谱助手（Recipe Assistant） 🍳🥗

简单来说，我是一位专门帮你查找各种美味菜肴和饮品食谱的智能助手！无论你想做什么菜、调制什么饮品，我都能帮你找到合适的食谱。

🍽️ 我能做什么？
🥘 搜索菜肴食谱 — 根据菜名、食材、菜系或类别来查找各种美食（中餐、意大利菜、墨西哥菜等）
🍹 查找饮品配方 — 搜索鸡尾酒、无酒精饮料等各种饮品配方
📋 提供详细信息 — 包括食材清单、烹饪步骤、份量等
💡 我可以帮你解决这些场景：
🏠 今晚吃什么？ → 帮你推荐菜肴
🛒 冰箱里有鸡肉和洋葱 → 帮你找能做的菜
🎉 朋友聚会调杯酒 → 帮你查鸡尾酒配方
🥗 想吃素食/低卡/某国菜系 → 帮你精准搜索
有什么想做的菜或想喝的饮品，尽管告诉我吧！😊`;

function createDefaultWelcomeMessage(): AssistantMessage {
  return {
    role: "assistant",
    reply: DEFAULT_WELCOME_REPLY,
    cards: [],
    toolCalls: [],
    warnings: [],
    profileUpdates: [],
  };
}

onMounted(async () => {
  try {
    const history = await loadChatHistory();
    if (messages.value.length === 0) {
      messages.value = history.length > 0 ? history : [createDefaultWelcomeMessage()];
    }
  } catch {
    if (messages.value.length === 0) {
      messages.value = [createDefaultWelcomeMessage()];
    }
  }
});

async function send(content: string) {
  const assistant: AssistantMessage = {
    role: "assistant",
    reply: "",
    cards: [],
    toolCalls: [],
    warnings: [],
    profileUpdates: [],
    pending: true,
    streaming: false,
  };
  messages.value.push({ role: "user", content }, assistant);
  const assistantIndex = messages.value.length - 1;
  const updateAssistant = (updater: (message: AssistantMessage) => void) => {
    const message = messages.value[assistantIndex];
    if (message?.role === "assistant") {
      updater(message);
    }
  };
  sending.value = true;

  try {
    await streamChat(content, {
      meta: () => {
        updateAssistant((message) => {
          message.pending = false;
          message.streaming = true;
        });
      },
      delta: (data) => {
        updateAssistant((message) => {
          message.pending = false;
          message.reply += String(data.text ?? "");
        });
      },
      card: (data) => {
        updateAssistant((message) => {
          message.pending = false;
          message.cards = (data.cards as Card[]) ?? message.cards;
        });
      },
      tool_call: (data) => {
        updateAssistant((message) => {
          message.toolCalls.push({ ...(data as ToolTraceItem), status: String(data.status ?? "started") });
        });
      },
      tool_result: (data) => {
        updateAssistant((message) => {
          message.toolCalls.push(data as ToolTraceItem);
        });
      },
      profile_update: (data) => {
        updateAssistant((message) => {
          message.profileUpdates?.push(data);
        });
      },
      error: (data) => {
        updateAssistant((message) => {
          message.pending = false;
          message.streaming = false;
          message.error = String(data.message ?? "请求失败");
        });
      },
      done: (data) => {
        updateAssistant((message) => {
          message.pending = false;
          message.streaming = false;
          message.reply = String(data.reply ?? message.reply);
          message.cards = (data.cards as Card[]) ?? message.cards;
          message.toolCalls = (data.toolCalls as ToolTraceItem[]) ?? message.toolCalls;
          message.warnings = (data.warnings as string[]) ?? [];
        });
      },
    });
  } catch (error) {
    updateAssistant((message) => {
      message.pending = false;
      message.streaming = false;
      message.error = error instanceof Error ? error.message : "请求失败";
    });
  } finally {
    sending.value = false;
  }
}
</script>
