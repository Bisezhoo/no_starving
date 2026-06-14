import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import CocktailCard from "../src/components/CocktailCard.vue";
import MealCard from "../src/components/MealCard.vue";

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
  });
});
