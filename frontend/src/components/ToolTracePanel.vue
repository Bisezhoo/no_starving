<template>
  <div class="trace-list">
    <p v-if="!items.length" class="muted">暂无 Tool 调用</p>
    <article v-for="item in items" :key="item.id || `${item.name}-${item.status}`" class="trace-item">
      <div>
        <strong>{{ item.name }}</strong>
        <span>{{ item.status }}</span>
      </div>
      <small>
        <span v-if="item.resultCount !== undefined">{{ item.resultCount }} results</span>
        <span v-if="item.durationMs !== undefined"> · {{ item.durationMs }}ms</span>
      </small>
      <p v-if="item.error" class="warning">{{ item.error }}</p>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { ToolTraceItem } from "../types/chat";

defineProps<{ items: ToolTraceItem[] }>();
</script>
