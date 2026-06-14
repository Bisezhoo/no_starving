<template>
  <section class="assistant-result-block">
    <div class="result-block-header">
      <strong>推荐结果</strong>
    </div>

    <div :class="['card-grid', { 'card-slider': isExpanded && hasOverflowCards }]">
      <template v-for="card in visibleCards" :key="card.id">
        <MealCard v-if="isMealCard(card)" :card="card" @view-detail="openDetail" />
        <CocktailCard v-else-if="isCocktailCard(card)" :card="card" @view-detail="openDetail" />
      </template>
    </div>

    <p v-if="hasOverflowCards && isExpanded" class="slider-hint">左右滑动查看更多</p>
    <div v-if="hasOverflowCards" class="result-toggle-row">
      <button class="result-toggle" type="button" @click="toggleExpanded">
        {{ isExpanded ? "收起" : "查看更多" }}
      </button>
    </div>

    <div v-if="selectedCard" class="detail-modal-backdrop" @click.self="closeDetail">
      <article class="detail-modal" role="dialog" aria-modal="true" :aria-label="`${displayTitle(selectedCard)} 详情`">
        <header class="detail-modal-header">
          <div>
            <p class="detail-modal-eyebrow">推荐详情</p>
            <h3>{{ displayTitle(selectedCard) }}</h3>
          </div>
          <button class="detail-modal-close" type="button" @click="closeDetail">关闭</button>
        </header>

        <p v-if="selectedCard.localizedSummary" class="muted">{{ selectedCard.localizedSummary }}</p>

        <div v-if="detailMetaItems(selectedCard).length" class="meta-row">
          <span v-for="item in detailMetaItems(selectedCard)" :key="item">{{ item }}</span>
        </div>

        <section v-if="ingredientsFor(selectedCard).length" class="detail-section">
          <h4>食材 / 配料</h4>
          <ul class="detail-ingredient-list">
            <li v-for="ingredient in ingredientsFor(selectedCard)" :key="ingredient.name">
              {{ ingredient.name }}<span v-if="ingredient.measure"> · {{ ingredient.measure }}</span>
            </li>
          </ul>
        </section>

        <section v-if="stepsFor(selectedCard).length" class="detail-section">
          <h4>做法步骤</h4>
          <ol class="detail-step-list">
            <li v-for="step in stepsFor(selectedCard)" :key="step">{{ step }}</li>
          </ol>
        </section>
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
const selectedCard = ref<Card | null>(null);
const hasOverflowCards = computed(() => props.message.cards.length > DEFAULT_VISIBLE_CARD_COUNT);
const visibleCards = computed(() => isExpanded.value || !hasOverflowCards.value
  ? props.message.cards
  : props.message.cards.slice(0, DEFAULT_VISIBLE_CARD_COUNT));

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
};

const isMealCard = (card: Card): card is MealCardType => card.type === "meal";
const isCocktailCard = (card: Card): card is CocktailCardType => card.type === "cocktail";
const displayTitle = (card: Card) => card.localizedTitle || card.title;
const ingredientsFor = (card: Card) => card.localizedIngredients?.length ? card.localizedIngredients : card.ingredients ?? [];
const stepsFor = (card: Card) => card.localizedInstructions?.length ? card.localizedInstructions : card.instructions ?? [];
const detailMetaItems = (card: Card) => {
  if (isMealCard(card)) {
    return [
      card.localizedCategory || card.category,
      card.localizedCountry || card.country,
    ].filter(Boolean);
  }

  return [
    card.localizedCategory || card.category,
    card.localizedAlcoholic || card.alcoholic,
    card.localizedGlass || card.glass,
  ].filter(Boolean);
};

const openDetail = (card: Card) => {
  selectedCard.value = card;
};

const closeDetail = () => {
  selectedCard.value = null;
};
</script>
