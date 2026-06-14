<template>
  <section class="assistant-tabs">
    <div v-if="message.warnings?.length" class="warning-strip">
      <span v-for="warning in message.warnings" :key="warning">{{ warning }}</span>
    </div>

    <div class="tabs" role="tablist">
      <button v-for="tab in tabs" :key="tab.key" type="button" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
        {{ tab.label }}
      </button>
    </div>

    <div v-if="activeTab === 'reply'" class="tab-panel">
      <p>{{ message.reply }}</p>
      <p v-if="message.error" class="warning">{{ message.error }}</p>
    </div>

    <div v-else-if="activeTab === 'cards'" class="tab-panel card-grid">
      <template v-if="message.cards.length">
        <MealCard v-for="card in mealCards" :key="card.id" :card="card" />
        <CocktailCard v-for="card in cocktailCards" :key="card.id" :card="card" />
      </template>
      <p v-else class="muted">暂无推荐</p>
    </div>

    <div v-else-if="activeTab === 'steps'" class="tab-panel">
      <article v-for="card in message.cards" :key="card.id" class="steps-block">
        <h3>{{ card.title }}</h3>
        <ul>
          <li v-for="ingredient in card.ingredients ?? []" :key="ingredient.name">
            {{ ingredient.name }}<span v-if="ingredient.measure"> · {{ ingredient.measure }}</span>
          </li>
        </ul>
        <ol v-if="card.instructions?.length">
          <li v-for="step in card.instructions" :key="step">{{ step }}</li>
        </ol>
      </article>
    </div>

    <div v-else-if="activeTab === 'tools'" class="tab-panel">
      <ToolTracePanel :items="message.toolCalls" />
    </div>

    <div v-else class="tab-panel">
      <ProfilePanel :updates="message.profileUpdates" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { AssistantMessage, CocktailCard as CocktailCardType, MealCard as MealCardType } from "../types/chat";
import CocktailCard from "./CocktailCard.vue";
import MealCard from "./MealCard.vue";
import ProfilePanel from "./ProfilePanel.vue";
import ToolTracePanel from "./ToolTracePanel.vue";

const props = defineProps<{ message: AssistantMessage }>();

const activeTab = ref(props.message.cards.length ? "cards" : "reply");
const tabs = [
  { key: "reply", label: "回复" },
  { key: "cards", label: "推荐" },
  { key: "steps", label: "食材/步骤" },
  { key: "tools", label: "Tool 调用" },
  { key: "profile", label: "画像变化" },
];

const mealCards = computed(() => props.message.cards.filter((card): card is MealCardType => card.type === "meal"));
const cocktailCards = computed(() => props.message.cards.filter((card): card is CocktailCardType => card.type === "cocktail"));
</script>
