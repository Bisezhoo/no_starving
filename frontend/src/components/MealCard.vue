<template>
  <article class="result-card">
    <img v-if="card.imageUrl" :src="card.imageUrl" :alt="card.title" />
    <div class="card-body">
      <h3>{{ card.title }}</h3>
      <p v-if="card.localizedSummary" class="muted">{{ card.localizedSummary }}</p>
      <div class="meta-row">
        <span v-if="card.category">{{ card.category }}</span>
        <span v-if="card.country">{{ card.country }}</span>
      </div>
      <div v-if="visibleTags.length" class="tag-row">
        <span v-for="tag in visibleTags" :key="tag">{{ tag }}</span>
      </div>
      <button class="card-detail-button" type="button" @click="viewDetail">查看详情</button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { MealCard } from "../types/chat";

const props = defineProps<{ card: MealCard }>();
const emit = defineEmits<{ (event: "view-detail", card: MealCard): void }>();

const visibleTags = computed(() => (props.card.tags ?? []).filter(Boolean));
const viewDetail = () => emit("view-detail", props.card);
</script>
