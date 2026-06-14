import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AssistantResultBlock from "../src/components/AssistantResultBlock.vue";
import CocktailCard from "../src/components/CocktailCard.vue";
import MealCard from "../src/components/MealCard.vue";
import type { AssistantMessage, Card, MealCard as MealCardModel } from "../src/types/chat";

const createMealCard = (id: string, title: string, localizedInstructions: string[] = []): MealCardModel => ({
  type: "meal",
  id,
  title,
  imageUrl: "",
  tags: [],
  ingredients: [],
  localizedInstructions,
});

const createAssistantMessage = (cards: Card[]): AssistantMessage => ({
  role: "assistant",
  reply: "",
  cards,
  toolCalls: [],
  warnings: [],
  profileUpdates: [],
});

describe("cards", () => {
  it("renders meal cards with missing optional fields", () => {
    const wrapper = mount(MealCard, {
      props: {
        card: {
          type: "meal",
          id: "1",
          title: "Chicken Handi",
          imageUrl: "",
          tags: [],
          ingredients: [],
        },
      },
    });

    expect(wrapper.text()).toContain("Chicken Handi");
    expect(wrapper.text()).toContain("查看详情");
  });

  it("renders cocktail cards with alcohol label", () => {
    const wrapper = mount(CocktailCard, {
      props: {
        card: {
          type: "cocktail",
          id: "2",
          title: "Lemonade",
          alcoholic: "Non alcoholic",
          tags: [],
          ingredients: [],
        },
      },
    });

    expect(wrapper.text()).toContain("Lemonade");
    expect(wrapper.text()).toContain("Non alcoholic");
    expect(wrapper.text()).toContain("查看详情");
  });

  it("does not render card details inline before opening the detail modal", () => {
    const wrapper = mount(AssistantResultBlock, {
      props: {
        message: createAssistantMessage([
          {
            ...createMealCard("1", "Chicken Rice", ["步骤 1：把鸡肉和米饭一起煮熟。"]),
            ingredients: [{ name: "Chicken", measure: "1 lb" }],
          },
        ]),
      },
    });

    expect(wrapper.text()).toContain("Chicken Rice");
    expect(wrapper.text()).toContain("查看详情");
    expect(wrapper.text()).not.toContain("步骤 1：把鸡肉和米饭一起煮熟。");
    expect(wrapper.text()).not.toContain("Chicken · 1 lb");
  });

  it("opens and closes a detail modal for a single card", async () => {
    const wrapper = mount(AssistantResultBlock, {
      props: {
        message: createAssistantMessage([
          {
            ...createMealCard("1", "Chicken Rice", ["步骤 1：把鸡肉和米饭一起煮熟。"]),
            ingredients: [{ name: "Chicken", measure: "1 lb" }],
          },
        ]),
      },
    });

    await wrapper.get("button.card-detail-button").trigger("click");

    expect(wrapper.find(".detail-modal").exists()).toBe(true);
    expect(wrapper.find(".detail-modal").text()).toContain("Chicken Rice");
    expect(wrapper.find(".detail-modal").text()).toContain("Chicken · 1 lb");
    expect(wrapper.find(".detail-modal").text()).toContain("步骤 1：把鸡肉和米饭一起煮熟。");

    await wrapper.get("button.detail-modal-close").trigger("click");

    expect(wrapper.find(".detail-modal").exists()).toBe(false);
  });

  it("prefers localized instructions in the detail modal", async () => {
    const wrapper = mount(AssistantResultBlock, {
      props: {
        message: {
          role: "assistant",
          reply: "",
          cards: [
            {
              type: "meal",
              id: "1",
              title: "Chicken Rice",
              imageUrl: "",
              tags: [],
              ingredients: [],
              instructions: ["Cook chicken with rice."],
              localizedInstructions: ["步骤 1：把鸡肉和米饭一起煮熟。"],
            },
          ],
          toolCalls: [],
          warnings: [],
          profileUpdates: [],
        },
      },
    });

    await wrapper.get("button.card-detail-button").trigger("click");

    expect(wrapper.find(".detail-modal").text()).toContain("步骤 1：把鸡肉和米饭一起煮熟。");
    expect(wrapper.find(".detail-modal").text()).not.toContain("Cook chicken with rice.");
  });

  it("renders all recommendation cards without toggle when three or fewer are returned", () => {
    const wrapper = mount(AssistantResultBlock, {
      props: {
        message: createAssistantMessage([
          createMealCard("1", "Meal 1"),
          createMealCard("2", "Meal 2"),
          createMealCard("3", "Meal 3"),
        ]),
      },
    });

    expect(wrapper.text()).toContain("Meal 1");
    expect(wrapper.text()).toContain("Meal 2");
    expect(wrapper.text()).toContain("Meal 3");
    expect(wrapper.find("button.result-toggle").exists()).toBe(false);
  });

  it("shows only three recommendation cards by default when more are returned", () => {
    const wrapper = mount(AssistantResultBlock, {
      props: {
        message: createAssistantMessage([
          createMealCard("1", "Meal 1", ["Step 1"]),
          createMealCard("2", "Meal 2", ["Step 2"]),
          createMealCard("3", "Meal 3", ["Step 3"]),
          createMealCard("4", "Meal 4", ["Step 4"]),
        ]),
      },
    });

    expect(wrapper.text()).toContain("Meal 1");
    expect(wrapper.text()).toContain("Meal 2");
    expect(wrapper.text()).toContain("Meal 3");
    expect(wrapper.text()).not.toContain("Meal 4");
    expect(wrapper.text()).toContain("查看更多");
    expect(wrapper.text()).not.toContain("Step 4");
  });

  it("expands all cards in a horizontal slider and then collapses them", async () => {
    const wrapper = mount(AssistantResultBlock, {
      props: {
        message: createAssistantMessage([
          createMealCard("1", "Meal 1"),
          createMealCard("2", "Meal 2"),
          createMealCard("3", "Meal 3"),
          createMealCard("4", "Meal 4"),
        ]),
      },
    });

    await wrapper.get("button.result-toggle").trigger("click");

    expect(wrapper.text()).toContain("Meal 4");
    expect(wrapper.find(".card-slider").exists()).toBe(true);
    expect(wrapper.get("button.result-toggle").text()).toBe("收起");

    await wrapper.get("button.result-toggle").trigger("click");

    expect(wrapper.text()).not.toContain("Meal 4");
    expect(wrapper.find(".card-slider").exists()).toBe(false);
    expect(wrapper.get("button.result-toggle").text()).toBe("查看更多");
  });

  it("opens details for a card that becomes visible after expanding the slider", async () => {
    const wrapper = mount(AssistantResultBlock, {
      props: {
        message: createAssistantMessage([
          createMealCard("1", "Meal 1"),
          createMealCard("2", "Meal 2"),
          createMealCard("3", "Meal 3"),
          createMealCard("4", "Meal 4", ["Step 4"]),
        ]),
      },
    });

    await wrapper.get("button.result-toggle").trigger("click");
    await wrapper.findAll("button.card-detail-button")[3].trigger("click");

    expect(wrapper.find(".detail-modal").text()).toContain("Meal 4");
    expect(wrapper.find(".detail-modal").text()).toContain("Step 4");
  });
});
