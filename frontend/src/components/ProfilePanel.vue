<template>
  <div class="profile-panel">
    <p v-if="!updates?.length" class="muted">暂无画像变化</p>
    <pre v-else>{{ formatted }}</pre>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ updates?: Record<string, unknown>[] }>();
const formatted = computed(() => JSON.stringify(props.updates, null, 2));
</script>
