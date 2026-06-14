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

onMounted(async () => {
  try {
    const history = await loadChatHistory();
    if (messages.value.length === 0) {
      messages.value = history;
    }
  } catch {
    messages.value = [];
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
          message.error = String(data.message ?? "请求失败");
        });
      },
      done: (data) => {
        updateAssistant((message) => {
          message.pending = false;
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
      message.error = error instanceof Error ? error.message : "请求失败";
    });
  } finally {
    sending.value = false;
  }
}
</script>
