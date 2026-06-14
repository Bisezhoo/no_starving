<template>
  <div class="message-list">
    <article v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
      <p v-if="message.role === 'user'">{{ message.content }}</p>
      <AssistantMessageTabs v-else :message="message" />
    </article>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from "../types/chat";
import AssistantMessageTabs from "./AssistantMessageTabs.vue";

defineProps<{ messages: ChatMessage[] }>();
</script>
