<template>
  <div v-if="!items.length" class="trace-list">
    <p class="muted">暂无 Tool 调用</p>
  </div>

  <div v-else class="tool-trace-panel">
    <button
      class="tool-trace-toggle"
      type="button"
      :aria-expanded="isExpanded"
      :aria-label="isExpanded ? '收起 Tool 调用明细' : '展开 Tool 调用明细'"
      @click="toggleExpanded"
    >
      <SquareTerminal :size="16" aria-hidden="true" />
      <span>{{ toolCountLabel }}</span>
      <ChevronDown v-if="isExpanded" :size="15" aria-hidden="true" />
      <ChevronRight v-else :size="15" aria-hidden="true" />
    </button>

    <div v-if="isExpanded" class="trace-list trace-list-expanded">
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
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { ChevronDown, ChevronRight, SquareTerminal } from "lucide-vue-next";
import type { ToolTraceItem } from "../types/chat";

const props = defineProps<{ items: ToolTraceItem[] }>();

const isExpanded = ref(false);
const toolCountLabel = computed(() => `Loaded ${props.items.length} ${props.items.length === 1 ? "tool" : "tools"}`);

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
};
</script>
