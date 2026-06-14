<template>
  <form class="composer" @submit.prevent="submit">
    <textarea
      v-model="draft"
      maxlength="1000"
      rows="2"
      :disabled="disabled"
      aria-label="输入消息"
      placeholder="想吃什么？（Ctrl+Enter 换行）"
      @keydown="onKeydown"
    />
    <button type="submit" :disabled="disabled || !draft.trim()" aria-label="发送">
      <Loader2 v-if="disabled" :size="18" class="spin" />
      <Send v-else :size="18" />
    </button>
  </form>
</template>

<script setup lang="ts">
import { Loader2, Send } from "lucide-vue-next";
import { ref } from "vue";

defineProps<{ disabled: boolean }>();
const emit = defineEmits<{ send: [message: string] }>();
const draft = ref("");

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Enter") {
    if (e.ctrlKey || e.metaKey) {
      // Ctrl+Enter / Cmd+Enter → 换行（不阻止默认行为）
      return;
    }
    // Enter → 发送消息，阻止默认的换行行为
    e.preventDefault();
    submit();
  }
}

function submit() {
  const message = draft.value.trim();
  if (!message) {
    return;
  }
  emit("send", message);
  draft.value = "";
}
</script>

<style scoped>
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
