<template>
  <form class="composer" @submit.prevent="submit">
    <textarea
      v-model="draft"
      maxlength="1000"
      rows="2"
      :disabled="disabled"
      aria-label="输入消息"
      placeholder="想吃什么？"
    />
    <button type="submit" :disabled="disabled || !draft.trim()" aria-label="发送">
      <Send :size="18" />
    </button>
  </form>
</template>

<script setup lang="ts">
import { Send } from "lucide-vue-next";
import { ref } from "vue";

defineProps<{ disabled: boolean }>();
const emit = defineEmits<{ send: [message: string] }>();
const draft = ref("");

function submit() {
  const message = draft.value.trim();
  if (!message) {
    return;
  }
  emit("send", message);
  draft.value = "";
}
</script>
