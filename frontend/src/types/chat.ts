export type SseEventName =
  | "meta"
  | "delta"
  | "tool_call"
  | "tool_result"
  | "card"
  | "profile_update"
  | "error"
  | "done";

export type ParsedSseEvent = {
  event: SseEventName;
  data: Record<string, unknown>;
};

export type IngredientItem = {
  name: string;
  measure?: string;
};

export type BaseCard = {
  id: string;
  detailLevel?: "summary" | "detail";
  title: string;
  localizedTitle?: string;
  localizedLanguage?: string;
  imageUrl?: string;
  tags?: string[];
  ingredients?: IngredientItem[];
  instructions?: string[];
  localizedSummary?: string;
  localizedInstructions?: string[];
  matchReasons?: string[];
};

export type MealCard = BaseCard & {
  type: "meal";
  category?: string;
  country?: string;
  sourceUrl?: string;
  youtubeUrl?: string;
};

export type CocktailCard = BaseCard & {
  type: "cocktail";
  category?: string;
  alcoholic?: string;
  glass?: string;
};

export type Card = MealCard | CocktailCard;
