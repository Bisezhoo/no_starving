<template>
  <section class="assistant-message">
    <div v-if="message.streaming" class="assistant-streaming">
      <span class="streaming-text">疯狂思考中，请稍等</span>
      <span class="thinking-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </span>
    </div>

    <div v-if="message.warnings?.length" class="warning-strip">
      <span v-for="warning in message.warnings" :key="warning">{{ warning }}</span>
    </div>

    <div v-if="message.pending && !message.reply && !message.error && !message.cards.length" class="assistant-pending">
      <span class="thinking-text">思考中</span>
      <span class="thinking-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </span>
    </div>

    <div v-if="message.reply || message.error" class="assistant-reply">
      <MarkdownReply v-if="message.reply" :content="message.reply" />
      <p v-if="message.error" class="warning">{{ message.error }}</p>
    </div>

    <AssistantResultBlock v-if="message.cards.length" :message="message" />
  </section>
</template>

<script setup lang="ts">
import type { AssistantMessage } from "../types/chat";
import AssistantResultBlock from "./AssistantResultBlock.vue";
import MarkdownReply from "./MarkdownReply.vue";

defineProps<{ message: AssistantMessage }>();
</script>
