<template>
  <section class="assistant-message">
    <div v-if="message.warnings?.length" class="warning-strip">
      <span v-for="warning in message.warnings" :key="warning">{{ warning }}</span>
    </div>

    <div v-if="message.reply || message.error" class="assistant-reply">
      <p v-if="message.reply">{{ message.reply }}</p>
      <p v-if="message.error" class="warning">{{ message.error }}</p>
    </div>

    <AssistantResultBlock v-if="message.cards.length" :message="message" />
  </section>
</template>

<script setup lang="ts">
import type { AssistantMessage } from "../types/chat";
import AssistantResultBlock from "./AssistantResultBlock.vue";

defineProps<{ message: AssistantMessage }>();
</script>
