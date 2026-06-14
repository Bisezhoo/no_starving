<template>
  <section class="assistant-result-block">
    <div class="result-block-header">
      <strong>推荐结果</strong>
    </div>

    <div :class="['card-grid', { 'card-slider': isExpanded && hasOverflowCards }]">
      <template v-for="card in visibleCards" :key="card.id">
        <MealCard v-if="isMealCard(card)" :card="card" />
        <CocktailCard v-else-if="isCocktailCard(card)" :card="card" />
      </template>
    </div>

    <div v-if="hasOverflowCards" class="result-toggle-row">
      <button class="result-toggle" type="button" @click="toggleExpanded">
        {{ isExpanded ? "收起" : "查看更多" }}
      </button>
    </div>

    <div v-if="hasSteps" class="result-section">
      <article v-for="card in visibleCards" :key="card.id" class="steps-block">
        <h3>{{ card.title }}</h3>
        <ul v-if="card.ingredients?.length">
          <li v-for="ingredient in card.ingredients" :key="ingredient.name">
            {{ ingredient.name }}<span v-if="ingredient.measure"> · {{ ingredient.measure }}</span>
          </li>
        </ul>
        <ol v-if="stepsFor(card).length">
          <li v-for="step in stepsFor(card)" :key="step">{{ step }}</li>
        </ol>
      </article>
    </div>

    <div v-if="message.toolCalls.length" class="result-section">
      <ToolTracePanel :items="message.toolCalls" />
    </div>

    <div v-if="message.profileUpdates?.length" class="result-section">
      <ProfilePanel :updates="message.profileUpdates" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { AssistantMessage, Card, CocktailCard as CocktailCardType, MealCard as MealCardType } from "../types/chat";
import CocktailCard from "./CocktailCard.vue";
import MealCard from "./MealCard.vue";
import ProfilePanel from "./ProfilePanel.vue";
import ToolTracePanel from "./ToolTracePanel.vue";

const props = defineProps<{ message: AssistantMessage }>();

const DEFAULT_VISIBLE_CARD_COUNT = 3;

const isExpanded = ref(false);
const hasOverflowCards = computed(() => props.message.cards.length > DEFAULT_VISIBLE_CARD_COUNT);
const visibleCards = computed(() => isExpanded.value || !hasOverflowCards.value
  ? props.message.cards
  : props.message.cards.slice(0, DEFAULT_VISIBLE_CARD_COUNT));

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
};

const isMealCard = (card: Card): card is MealCardType => card.type === "meal";
const isCocktailCard = (card: Card): card is CocktailCardType => card.type === "cocktail";
const stepsFor = (card: Card) => card.localizedInstructions?.length ? card.localizedInstructions : card.instructions ?? [];
const hasSteps = computed(() => visibleCards.value.some((card) => card.ingredients?.length || stepsFor(card).length));
</script>
