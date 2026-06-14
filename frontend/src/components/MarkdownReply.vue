<template>
  <div class="markdown-reply" v-html="safeHtml" />
</template>

<script setup lang="ts">
import DOMPurify from "dompurify";
import { marked } from "marked";
import { computed } from "vue";

const props = defineProps<{ content: string }>();

const safeHtml = computed(() => {
  const html = marked.parse(props.content, {
    async: false,
    breaks: true,
    gfm: true,
  }) as string;

  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true },
  });
});
</script>
