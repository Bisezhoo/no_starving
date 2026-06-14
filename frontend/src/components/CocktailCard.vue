<template>
  <article class="result-card">
    <img v-if="card.imageUrl" :src="card.imageUrl" :alt="card.title" />
    <div class="card-body">
      <h3>{{ card.title }}</h3>
      <p v-if="card.localizedSummary" class="muted">{{ card.localizedSummary }}</p>
      <div class="meta-row">
        <span v-if="card.category">{{ card.category }}</span>
        <span v-if="card.alcoholic">{{ card.alcoholic }}</span>
        <span v-if="card.glass">{{ card.glass }}</span>
      </div>
      <button class="card-detail-button" type="button" @click="viewDetail">查看详情</button>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { CocktailCard } from "../types/chat";

const props = defineProps<{ card: CocktailCard }>();
const emit = defineEmits<{ (event: "view-detail", card: CocktailCard): void }>();

const viewDetail = () => emit("view-detail", props.card);
</script>
