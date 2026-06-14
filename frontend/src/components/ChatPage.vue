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
import { ref } from "vue";
import { streamChat } from "../api/chat";
import type { AssistantMessage, Card, ChatMessage, ToolTraceItem } from "../types/chat";
import MessageComposer from "./MessageComposer.vue";
import MessageList from "./MessageList.vue";

const messages = ref<ChatMessage[]>([]);
const sending = ref(false);

async function send(content: string) {
  const assistant: AssistantMessage = {
    role: "assistant",
    reply: "",
    cards: [],
    toolCalls: [],
    warnings: [],
    profileUpdates: [],
  };
  messages.value.push({ role: "user", content }, assistant);
  sending.value = true;

  try {
    await streamChat(content, {
      delta: (data) => {
        assistant.reply += String(data.text ?? "");
      },
      card: (data) => {
        assistant.cards = (data.cards as Card[]) ?? assistant.cards;
      },
      tool_call: (data) => {
        assistant.toolCalls.push({ ...(data as ToolTraceItem), status: String(data.status ?? "started") });
      },
      tool_result: (data) => {
        assistant.toolCalls.push(data as ToolTraceItem);
      },
      profile_update: (data) => {
        assistant.profileUpdates?.push(data);
      },
      error: (data) => {
        assistant.error = String(data.message ?? "请求失败");
      },
      done: (data) => {
        assistant.reply = String(data.reply ?? assistant.reply);
        assistant.cards = (data.cards as Card[]) ?? assistant.cards;
        assistant.toolCalls = (data.toolCalls as ToolTraceItem[]) ?? assistant.toolCalls;
        assistant.warnings = (data.warnings as string[]) ?? [];
      },
    });
  } catch (error) {
    assistant.error = error instanceof Error ? error.message : "请求失败";
  } finally {
    sending.value = false;
  }
}
</script>
