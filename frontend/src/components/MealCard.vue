<template>
  <article class="result-card">
    <img v-if="card.imageUrl" :src="card.imageUrl" :alt="displayTitle" />
    <div class="card-body">
      <h3>{{ displayTitle }}</h3>
      <p v-if="card.localizedSummary" class="muted">{{ card.localizedSummary }}</p>
      <div class="meta-row">
        <span v-if="displayCategory">{{ displayCategory }}</span>
        <span v-if="displayCountry">{{ displayCountry }}</span>
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

const displayTitle = computed(() => props.card.localizedTitle || props.card.title);
const displayCategory = computed(() => props.card.localizedCategory || props.card.category);
const displayCountry = computed(() => props.card.localizedCountry || props.card.country);
const visibleTags = computed(() => (props.card.tags ?? []).filter(Boolean));
const viewDetail = () => emit("view-detail", props.card);
</script>
