<template>
  <article class="result-card">
    <img v-if="card.imageUrl" :src="card.imageUrl" :alt="displayTitle" />
    <div class="card-body">
      <h3>{{ displayTitle }}</h3>
      <p v-if="card.localizedSummary" class="muted">{{ card.localizedSummary }}</p>
      <div class="meta-row">
        <span v-if="displayCategory">{{ displayCategory }}</span>
        <span v-if="displayAlcoholic">{{ displayAlcoholic }}</span>
        <span v-if="displayGlass">{{ displayGlass }}</span>
      </div>
      <button class="card-detail-button" type="button" @click="viewDetail">查看详情</button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { CocktailCard } from "../types/chat";

const props = defineProps<{ card: CocktailCard }>();
const emit = defineEmits<{ (event: "view-detail", card: CocktailCard): void }>();

const displayTitle = computed(() => props.card.localizedTitle || props.card.title);
const displayCategory = computed(() => props.card.localizedCategory || props.card.category);
const displayAlcoholic = computed(() => props.card.localizedAlcoholic || props.card.alcoholic);
const displayGlass = computed(() => props.card.localizedGlass || props.card.glass);
const viewDetail = () => emit("view-detail", props.card);
</script>
