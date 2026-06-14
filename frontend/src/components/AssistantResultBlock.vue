<template>
  <section class="assistant-result-block">
    <div class="result-block-header">
      <strong>推荐结果</strong>
    </div>

    <div class="card-grid">
      <MealCard v-for="card in mealCards" :key="card.id" :card="card" />
      <CocktailCard v-for="card in cocktailCards" :key="card.id" :card="card" />
    </div>

    <div v-if="hasSteps" class="result-section">
      <article v-for="card in message.cards" :key="card.id" class="steps-block">
        <h3>{{ card.title }}</h3>
        <ul v-if="card.ingredients?.length">
          <li v-for="ingredient in card.ingredients" :key="ingredient.name">
            {{ ingredient.name }}<span v-if="ingredient.measure"> · {{ ingredient.measure }}</span>
          </li>
        </ul>
        <ol v-if="card.instructions?.length">
          <li v-for="step in card.instructions" :key="step">{{ step }}</li>
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
import { computed } from "vue";
import type { AssistantMessage, CocktailCard as CocktailCardType, MealCard as MealCardType } from "../types/chat";
import CocktailCard from "./CocktailCard.vue";
import MealCard from "./MealCard.vue";
import ProfilePanel from "./ProfilePanel.vue";
import ToolTracePanel from "./ToolTracePanel.vue";

const props = defineProps<{ message: AssistantMessage }>();

const mealCards = computed(() => props.message.cards.filter((card): card is MealCardType => card.type === "meal"));
const cocktailCards = computed(() => props.message.cards.filter((card): card is CocktailCardType => card.type === "cocktail"));
const hasSteps = computed(() => props.message.cards.some((card) => card.ingredients?.length || card.instructions?.length));
</script>
