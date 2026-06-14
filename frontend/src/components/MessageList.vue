<template>
  <div ref="listEl" class="message-list">
    <article v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
      <p v-if="message.role === 'user'">{{ message.content }}</p>
      <AssistantMessage v-else :message="message" />
    </article>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import type { ChatMessage } from "../types/chat";
import AssistantMessage from "./AssistantMessage.vue";

const props = defineProps<{ messages: ChatMessage[] }>();
const listEl = ref<HTMLElement | null>(null);

function scrollToBottom() {
  if (listEl.value) {
    listEl.value.scrollTop = listEl.value.scrollHeight;
  }
}

onMounted(scrollToBottom);

watch(() => props.messages, scrollToBottom, { deep: true, flush: "post" });
</script>
