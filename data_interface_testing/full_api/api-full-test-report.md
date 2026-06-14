# TheMealDB & TheCocktailDB 全接口测试报告（30 次调用采样）

> **测试日期**: 2026-06-14
> **测试方法**: 每个接口使用 30 组不同参数调用，收集返回数据进行字段完整性分析
> **文档来源**: https://www.themealdb.com/api.php | https://www.thecocktaildb.com/api.php

---

## 📋 测试总览

| # | 接口 | 数据源 | 调用次数 | 去重结果数 | 返回字段数 |
|---|------|--------|---------|-----------|-----------|
| 1 | `search.php?s={name}` | TheMealDB | 30 词搜索 | 332 | 54 |
| 2 | `filter.php?i={ingredient}` | TheMealDB | 30 种食材 | 613 | 5 |
| 3 | `filter.php?c={category}` | TheMealDB | 14 个分类 | 667 | 5 |
| 4 | `filter.php?a={area}` | TheMealDB | 30 个地区 | 403 | 5 |
| 5 | `lookup.php?i={id}` | TheMealDB | 30 个 ID | 29 | 54 |
| 6 | `random.php` | TheMealDB | 30 次随机 | 29 | 54 |
| 7 | `categories.php` | TheMealDB | 1 次 | 14 | 4 |
| 8 | `search.php?s={name}` | TheCocktailDB | 30 词搜索 | 162 | 51 |
| 9 | `filter.php?i={ingredient}` | TheCocktailDB | 30 种食材 | 22 | 3 |
| 10 | `lookup.php?i={id}` | TheCocktailDB | 30 个 ID | 20 | 51 |
| 11 | `random.php` | TheCocktailDB | 30 次随机 | 28 | 51 |

---

## 1. TheMealDB — search.php?s={name}

- **调用次数**: 30 词搜索
- **去重后结果数**: 332
- **返回字段数**: 54
- **返回根 key**: `meals`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `dateModified` | 🟡 48.2% | 172 | 160 | 0 | 2025-12-08 09:30:20 |
| `idMeal` | ✅ 0% | 332 | 0 | 0 | 52795 |
| `strArea` | 🔵 8.1% | 305 | 27 | 0 | India |
| `strCategory` | ✅ 0% | 332 | 0 | 0 | Chicken |
| `strCountry` | ✅ 0% | 332 | 0 | 0 | India |
| `strCreativeCommonsConfirmed` | 🔴 100.0% | 0 | 332 | 0 | — |
| `strImageSource` | 🔴 100.0% | 0 | 332 | 0 | — |
| `strIngredient1` | ✅ 0% | 332 | 0 | 0 | Chicken |
| `strIngredient10` | 🟡 36.1% | 212 | 2 | 118 | Chilli powder |
| `strIngredient11` | 🟡 46.1% | 179 | 2 | 151 | Green chilli |
| `strIngredient12` | 🟠 55.7% | 147 | 4 | 181 | Yogurt |
| `strIngredient13` | 🟠 66.6% | 111 | 5 | 216 | Cream |
| `strIngredient14` | 🟠 75.3% | 82 | 6 | 244 | fenugreek |
| `strIngredient15` | 🔴 82.5% | 58 | 6 | 268 | Garam masala |
| `strIngredient16` | 🔴 88.6% | 38 | 11 | 283 | Salt |
| `strIngredient17` | 🔴 91.3% | 29 | 11 | 292 | Black Olives |
| `strIngredient18` | 🔴 94.3% | 19 | 12 | 301 | Salt |
| `strIngredient19` | 🔴 96.1% | 13 | 12 | 307 | Pepper |
| `strIngredient2` | ✅ 0% | 332 | 0 | 0 | Onion |
| `strIngredient20` | 🔴 97.3% | 9 | 13 | 310 | Ginger |
| `strIngredient3` | ✅ 0% | 332 | 0 | 0 | Tomatoes |
| `strIngredient4` | 🔵 0.3% | 331 | 0 | 1 | Garlic |
| `strIngredient5` | 🔵 0.9% | 329 | 0 | 3 | Ginger paste |
| `strIngredient6` | 🔵 3.9% | 319 | 0 | 13 | Vegetable oil |
| `strIngredient7` | 🔵 9.0% | 302 | 0 | 30 | Cumin seeds |
| `strIngredient8` | 🔵 18.7% | 270 | 0 | 62 | Coriander seeds |
| `strIngredient9` | 🟡 27.4% | 241 | 2 | 89 | Turmeric powder |
| `strInstructions` | ✅ 0% | 332 | 0 | 0 | Take a large pot or wok, big enough to cook all th |
| `strMeal` | ✅ 0% | 332 | 0 | 0 | Chicken Handi |
| `strMealAlternate` | 🔴 100.0% | 0 | 332 | 0 | — |
| `strMealThumb` | ✅ 0% | 332 | 0 | 0 | https://www.themealdb.com/images/media/meals/wyxws |
| `strMeasure1` | ✅ 0% | 332 | 0 | 0 | 1.2 kg |
| `strMeasure10` | 🔵 15.4% | 281 | 0 | 51 | 1 tsp |
| `strMeasure11` | 🔵 18.7% | 270 | 0 | 62 | 2 |
| `strMeasure12` | 🟡 21.1% | 262 | 0 | 70 | 1 cup |
| `strMeasure13` | 🟡 26.8% | 243 | 0 | 89 | ¾ cup |
| `strMeasure14` | 🟡 29.5% | 234 | 0 | 98 | 3 tsp Dried |
| `strMeasure15` | 🟡 31.3% | 228 | 0 | 104 | 1 tsp |
| `strMeasure16` | 🟡 34.9% | 216 | 6 | 110 | To taste |
| `strMeasure17` | 🟡 36.4% | 211 | 6 | 115 |   |
| `strMeasure18` | 🟡 38.9% | 203 | 6 | 123 |   |
| `strMeasure19` | 🟡 39.2% | 202 | 6 | 124 |   |
| `strMeasure2` | ✅ 0% | 332 | 0 | 0 | 5 thinly sliced |
| `strMeasure20` | 🟡 40.1% | 199 | 6 | 127 |   |
| `strMeasure3` | ✅ 0% | 332 | 0 | 0 | 2 finely chopped |
| `strMeasure4` | 🔵 0.3% | 331 | 0 | 1 | 8 cloves chopped |
| `strMeasure5` | ✅ 0% | 332 | 0 | 0 | 1 tbsp |
| `strMeasure6` | 🔵 1.8% | 326 | 0 | 6 | ¼ cup |
| `strMeasure7` | 🔵 3.9% | 319 | 0 | 13 | 2 tsp |
| `strMeasure8` | 🔵 7.5% | 307 | 0 | 25 | 3 tsp |
| `strMeasure9` | 🔵 11.7% | 293 | 0 | 39 | 1 tsp |
| `strSource` | 🔵 5.7% | 313 | 1 | 18 | https://www.bbcgoodfood.com/recipes/sticky-chicken |
| `strTags` | 🟠 65.4% | 115 | 217 | 0 | Spicy,Meat |
| `strYoutube` | 🔵 11.7% | 293 | 0 | 39 | https://www.youtube.com/watch?v=IO0issT0Rmc |

### 标准请求/响应样本

```json
{
  "meals": [
    {
      "idMeal": "52795",
      "strMeal": "Chicken Handi",
      "strMealAlternate": null,
      "strCategory": "Chicken",
      "strArea": "India",
      "strCountry": "India",
      "strInstructions": "Take a large pot or wok, big enough to cook all the chicken, and heat the oil in it. Once the oil is hot, add sliced onion and fry them until deep golden brown. Then take them out on a plate and set aside.\r\nTo the same pot, add the chopped garlic and sauté for a minute. Then add the chopped tomatoes and cook until tomatoes turn soft. This would take about 5 minutes.\r\nThen return the fried onion to the pot and stir. Add ginger paste and sauté well.\r\nNow add the cumin seeds, half of the coriander seeds and chopped green chillies. Give them a quick stir.\r\nNext goes in the spices – turmeric powder and red chilli powder. Sauté the spices well for couple of minutes.\r\nAdd the chicken pieces to the wok, season it with salt to taste and cook the chicken covered on medium-low heat until the chicken is almost cooked through. This would take about 15 minutes. Slowly sautéing the chicken will enhance the flavor, so do not expedite this step by putting it on high heat.\r\nWhen the oil separates from the spices, add the beaten yogurt keeping the heat on lowest so that the yogurt doesn’t split. Sprinkle the remaining coriander seeds and add half of the dried fenugreek leaves. Mix well.\r\nFinally add the cream and give a final mix to combine everything well.\r\
```

---

## 2. TheMealDB — filter.php?i={ingredient}

- **调用次数**: 30 种食材
- **去重后结果数**: 613
- **返回字段数**: 5
- **返回根 key**: `meals`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `idMeal` | ✅ 0% | 613 | 0 | 0 | 53453 |
| `strArea` | 🔵 10.3% | 550 | 63 | 0 | United States |
| `strCountry` | ✅ 0% | 613 | 0 | 0 | Bangladesh |
| `strMeal` | ✅ 0% | 613 | 0 | 0 | Bengali Chicken Curry with Potatoes |
| `strMealThumb` | ✅ 0% | 613 | 0 | 0 | https://www.themealdb.com/images/media/meals/9ya6o |

### 标准请求/响应样本

```json
{
  "meals": [
    {
      "strMeal": "Bengali Chicken Curry with Potatoes",
      "strMealThumb": "https://www.themealdb.com/images/media/meals/9ya6o71780262651.jpg",
      "idMeal": "53453",
      "strArea": null,
      "strCountry": "Bangladesh"
    }
  ]
}
```

---

## 3. TheMealDB — filter.php?c={category}

- **调用次数**: 14 个分类
- **去重后结果数**: 667
- **返回字段数**: 5
- **返回根 key**: `meals`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `idMeal` | ✅ 0% | 667 | 0 | 0 | 53281 |
| `strArea` | 🔵 9.9% | 601 | 66 | 0 | Algerian |
| `strCountry` | ✅ 0% | 667 | 0 | 0 | Algeria |
| `strMeal` | ✅ 0% | 667 | 0 | 0 | Algerian Kefta (Meatballs) |
| `strMealThumb` | ✅ 0% | 667 | 0 | 0 | https://www.themealdb.com/images/media/meals/8rfd4 |

### 标准请求/响应样本

```json
{
  "meals": [
    {
      "strMeal": "Algerian Kefta (Meatballs)",
      "strMealThumb": "https://www.themealdb.com/images/media/meals/8rfd4q1764112993.jpg",
      "idMeal": "53281",
      "strArea": "Algerian",
      "strCountry": "Algeria"
    }
  ]
}
```

---

## 4. TheMealDB — filter.php?a={area}

- **调用次数**: 30 个地区
- **去重后结果数**: 403
- **返回字段数**: 5
- **返回根 key**: `meals`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `idMeal` | ✅ 0% | 403 | 0 | 0 | 52885 |
| `strArea` | ✅ 0% | 403 | 0 | 0 | British |
| `strCountry` | ✅ 0% | 403 | 0 | 0 | United Kingdom |
| `strMeal` | ✅ 0% | 403 | 0 | 0 |  Bubble & Squeak |
| `strMealThumb` | ✅ 0% | 403 | 0 | 0 | https://www.themealdb.com/images/media/meals/xusqv |

### 标准请求/响应样本

```json
{
  "meals": [
    {
      "strMeal": " Bubble & Squeak",
      "strMealThumb": "https://www.themealdb.com/images/media/meals/xusqvw1511638311.jpg",
      "idMeal": "52885",
      "strArea": "British",
      "strCountry": "United Kingdom"
    }
  ]
}
```

---

## 5. TheMealDB — lookup.php?i={id}

- **调用次数**: 30 个 ID
- **去重后结果数**: 29
- **返回字段数**: 54
- **返回根 key**: `meals`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `dateModified` | 🔴 100.0% | 0 | 29 | 0 | — |
| `idMeal` | ✅ 0% | 29 | 0 | 0 | 52772 |
| `strArea` | ✅ 0% | 29 | 0 | 0 | Japanese |
| `strCategory` | ✅ 0% | 29 | 0 | 0 | Chicken |
| `strCountry` | ✅ 0% | 29 | 0 | 0 | Japan |
| `strCreativeCommonsConfirmed` | 🔴 100.0% | 0 | 29 | 0 | — |
| `strImageSource` | 🔴 100.0% | 0 | 29 | 0 | — |
| `strIngredient1` | ✅ 0% | 29 | 0 | 0 | soy sauce |
| `strIngredient10` | 🟡 27.6% | 21 | 0 | 8 | Chicken |
| `strIngredient11` | 🟡 34.5% | 19 | 0 | 10 | Egg |
| `strIngredient12` | 🟡 41.4% | 17 | 0 | 12 | Chinese broccoli |
| `strIngredient13` | 🟠 55.2% | 13 | 0 | 16 | Butter |
| `strIngredient14` | 🟠 65.5% | 10 | 0 | 19 | Salt |
| `strIngredient15` | 🟠 65.5% | 10 | 0 | 19 | Pepper |
| `strIngredient16` | 🟠 75.9% | 7 | 4 | 18 | Lemons |
| `strIngredient17` | 🔴 82.8% | 5 | 4 | 20 | Black Olives |
| `strIngredient18` | 🔴 89.7% | 3 | 4 | 22 | Salt |
| `strIngredient19` | 🔴 89.7% | 3 | 4 | 22 | Pepper |
| `strIngredient2` | ✅ 0% | 29 | 0 | 0 | water |
| `strIngredient20` | 🔴 93.1% | 2 | 4 | 23 | Kidney Beans |
| `strIngredient3` | ✅ 0% | 29 | 0 | 0 | brown sugar |
| `strIngredient4` | ✅ 0% | 29 | 0 | 0 | ground ginger |
| `strIngredient5` | ✅ 0% | 29 | 0 | 0 | minced garlic |
| `strIngredient6` | ✅ 0% | 29 | 0 | 0 | cornstarch |
| `strIngredient7` | 🔵 3.4% | 28 | 0 | 1 | chicken breasts |
| `strIngredient8` | 🔵 17.2% | 24 | 0 | 5 | stir-fry vegetables |
| `strIngredient9` | 🔵 17.2% | 24 | 0 | 5 | brown rice |
| `strInstructions` | ✅ 0% | 29 | 0 | 0 | Preheat oven to 350° F. Spray a 9x13-inch baking p |
| `strMeal` | ✅ 0% | 29 | 0 | 0 | Teriyaki Chicken Casserole |
| `strMealAlternate` | 🔴 100.0% | 0 | 29 | 0 | — |
| `strMealThumb` | ✅ 0% | 29 | 0 | 0 | https://www.themealdb.com/images/media/meals/wvpsx |
| `strMeasure1` | ✅ 0% | 29 | 0 | 0 | 3/4 cup |
| `strMeasure10` | 🟡 27.6% | 21 | 0 | 8 | 1 cup |
| `strMeasure11` | 🟡 34.5% | 19 | 0 | 10 | 1 |
| `strMeasure12` | 🟡 41.4% | 17 | 0 | 12 | 4 cups |
| `strMeasure13` | 🟠 55.2% | 13 | 0 | 16 | 25g |
| `strMeasure14` | 🟠 65.5% | 10 | 0 | 19 | pinch |
| `strMeasure15` | 🟠 65.5% | 10 | 0 | 19 | pinch |
| `strMeasure16` | 🟠 75.9% | 7 | 4 | 18 | 2 |
| `strMeasure17` | 🔴 82.8% | 5 | 4 | 20 | 100g  |
| `strMeasure18` | 🔴 89.7% | 3 | 4 | 22 | to serve |
| `strMeasure19` | 🔴 89.7% | 3 | 4 | 22 | to serve |
| `strMeasure2` | ✅ 0% | 29 | 0 | 0 | 1/2 cup |
| `strMeasure20` | 🔴 93.1% | 2 | 4 | 23 | 800g |
| `strMeasure3` | ✅ 0% | 29 | 0 | 0 | 1/4 cup |
| `strMeasure4` | ✅ 0% | 29 | 0 | 0 | 1/2 teaspoon |
| `strMeasure5` | ✅ 0% | 29 | 0 | 0 | 1/2 teaspoon |
| `strMeasure6` | ✅ 0% | 29 | 0 | 0 | 4 Tablespoons |
| `strMeasure7` | 🔵 3.4% | 28 | 0 | 1 | 2 |
| `strMeasure8` | 🔵 17.2% | 24 | 0 | 5 | 1 (12 oz.) |
| `strMeasure9` | 🔵 17.2% | 24 | 0 | 5 | 3 cups |
| `strSource` | 🔵 10.3% | 26 | 3 | 0 | http://www.goodtoknow.co.uk/recipes/536028/chocola |
| `strTags` | 🔵 6.9% | 27 | 2 | 0 | Meat,Casserole |
| `strYoutube` | ✅ 0% | 29 | 0 | 0 | https://www.youtube.com/watch?v=4aZr5hZXP_s |

### 标准请求/响应样本

```json
{
  "meals": [
    {
      "idMeal": "53038",
      "strMeal": "Mustard champ",
      "strMealAlternate": null,
      "strCategory": "Side",
      "strArea": "Irish",
      "strCountry": "Ireland",
      "strInstructions": "STEP 1\r\nBoil the potatoes for 15 mins or until tender. Drain, then mash.\r\n\r\nSTEP 2\r\nHeat the milk and half the butter in the corner of the pan, then beat into the mash, along with the wholegrain mustard.\r\n\r\nSTEP 3\r\nGently fry the spring onions in the remaining butter for 2 mins until just soft but still a perky green. Fold into the mash and serve. Great with gammon or to top a fish pie.",
      "strMealThumb": "https://www.themealdb.com/images/media/meals/o7p9581608589317.jpg",
      "strTags": null,
      "strYoutube": "https://www.youtube.com/watch?v=_iKllHSC978",
      "strIngredient1": "Potatoes",
      "strIngredient2": "Milk",
      "strIngredient3": "Butter",
      "strIngredient4": "Mustard",
      "strIngredient5": "Spring Onions",
      "strIngredient6": "Spring Onions",
      "strIngredient7": "",
      "strIngredient8": "",
      "strIngredient9": "",
      "strIngredient10": "",
      "strIngredient11": "",
      "strIngredient12": "",
      "strIngredient13": "",
      "strIngredient14": "",
      "strIngredient15": "",
      "strIngredient16": "",
      "strIngredient17": "",
      "strIngredient18": "",
      "strIngredient19": "",
      "strIngredient20": "",
      "strMeasure1": "1kg",
      "strMeasure2": "200ml",
      "st
```

---

## 6. TheMealDB — random.php

- **调用次数**: 30 次随机
- **去重后结果数**: 29
- **返回字段数**: 54
- **返回根 key**: `meals`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `dateModified` | 🟠 58.6% | 12 | 17 | 0 | 2025-11-29 20:22:39 |
| `idMeal` | ✅ 0% | 29 | 0 | 0 | 52817 |
| `strArea` | 🔵 3.4% | 28 | 1 | 0 | United States |
| `strCategory` | ✅ 0% | 29 | 0 | 0 | Vegetarian |
| `strCountry` | ✅ 0% | 29 | 0 | 0 | United States |
| `strCreativeCommonsConfirmed` | 🔴 100.0% | 0 | 29 | 0 | — |
| `strImageSource` | 🔴 100.0% | 0 | 29 | 0 | — |
| `strIngredient1` | ✅ 0% | 29 | 0 | 0 | Olive Oil |
| `strIngredient10` | 🟡 31.0% | 20 | 0 | 9 | Salt |
| `strIngredient11` | 🟡 44.8% | 16 | 0 | 13 | Black Pepper |
| `strIngredient12` | 🟠 51.7% | 14 | 0 | 15 | thyme |
| `strIngredient13` | 🟠 65.5% | 10 | 1 | 18 | Rosemary |
| `strIngredient14` | 🟠 72.4% | 8 | 0 | 21 | bay leaves |
| `strIngredient15` | 🟠 79.3% | 6 | 0 | 23 | parsley |
| `strIngredient16` | 🔴 93.1% | 2 | 0 | 27 | chestnut mushroom |
| `strIngredient17` | 🔴 93.1% | 2 | 0 | 27 | plain flour |
| `strIngredient18` | 🔴 93.1% | 2 | 0 | 27 | butter |
| `strIngredient19` | 🔴 96.6% | 1 | 0 | 28 | Ground Cumin |
| `strIngredient2` | ✅ 0% | 29 | 0 | 0 | Egg Plants |
| `strIngredient20` | 🔴 96.6% | 1 | 0 | 28 | Peanuts |
| `strIngredient3` | ✅ 0% | 29 | 0 | 0 | Harissa Spice |
| `strIngredient4` | 🔵 3.4% | 28 | 0 | 1 | Chickpeas |
| `strIngredient5` | 🔵 6.9% | 27 | 0 | 2 | Cherry Tomatoes |
| `strIngredient6` | 🔵 10.3% | 26 | 0 | 3 | Greek yogurt |
| `strIngredient7` | 🔵 10.3% | 26 | 0 | 3 | Ground cumin |
| `strIngredient8` | 🔵 17.2% | 24 | 0 | 5 | Parsley |
| `strIngredient9` | 🟡 20.7% | 23 | 0 | 6 | Butter |
| `strInstructions` | ✅ 0% | 29 | 0 | 0 | Heat the oil in a 12-inch skillet over high heat u |
| `strMeal` | ✅ 0% | 29 | 0 | 0 | Stovetop Eggplant With Harissa, Chickpeas, and Cum |
| `strMealAlternate` | 🔴 100.0% | 0 | 29 | 0 | — |
| `strMealThumb` | ✅ 0% | 29 | 0 | 0 | https://www.themealdb.com/images/media/meals/yqwtv |
| `strMeasure1` | ✅ 0% | 29 | 0 | 0 | 4 tablespoons |
| `strMeasure10` | 🟡 20.7% | 23 | 0 | 6 | 1/2 tsp |
| `strMeasure11` | 🟡 20.7% | 23 | 0 | 6 | 1/4 tsp |
| `strMeasure12` | 🟡 20.7% | 23 | 0 | 6 |   |
| `strMeasure13` | 🟡 27.6% | 21 | 0 | 8 |   |
| `strMeasure14` | 🟡 31.0% | 20 | 0 | 9 |   |
| `strMeasure15` | 🟡 31.0% | 20 | 0 | 9 |   |
| `strMeasure16` | 🟡 41.4% | 17 | 0 | 12 |   |
| `strMeasure17` | 🟡 41.4% | 17 | 0 | 12 |   |
| `strMeasure18` | 🟡 41.4% | 17 | 0 | 12 |   |
| `strMeasure19` | 🟡 44.8% | 16 | 0 | 13 |   |
| `strMeasure2` | ✅ 0% | 29 | 0 | 0 | 6 small |
| `strMeasure20` | 🟡 44.8% | 16 | 0 | 13 |   |
| `strMeasure3` | ✅ 0% | 29 | 0 | 0 | ½ tablespoon |
| `strMeasure4` | ✅ 0% | 29 | 0 | 0 | 1 can |
| `strMeasure5` | ✅ 0% | 29 | 0 | 0 | 2 cups halved |
| `strMeasure6` | 🔵 3.4% | 28 | 0 | 1 | 1 1/2 cups |
| `strMeasure7` | 🔵 3.4% | 28 | 0 | 1 | 1 tablespoon |
| `strMeasure8` | 🔵 10.3% | 26 | 0 | 3 | ½ cup  |
| `strMeasure9` | 🔵 13.8% | 25 | 0 | 4 | 1/2 cup |
| `strSource` | 🔵 6.9% | 27 | 0 | 2 | http://www.seriouseats.com/2014/09/one-pot-wonders |
| `strTags` | 🟠 65.5% | 10 | 19 | 0 | Vegetarian |
| `strYoutube` | 🔵 10.3% | 26 | 0 | 3 | https://www.youtube.com/watch?v=uYB-1xJp4lg |

### 标准请求/响应样本

```json
{
  "meals": [
    {
      "idMeal": "53102",
      "strMeal": "Squid, chickpea & chorizo salad",
      "strMealAlternate": null,
      "strCategory": "Seafood",
      "strArea": "Australian",
      "strCountry": "Australia",
      "strInstructions": "step 1\r\nCook the peppers whole under a grill, on a barbecue or griddle, until completely charred. Place the peppers in a bowl, cover with a plate until cool enough to handle, then peel, deseed and finely slice. In a large bowl mix the peppers and any juices with the chickpeas, parsley, chilli and garlic. Set aside.\r\n\r\nstep 2\r\nHeat a large frying pan until smoking. Working quickly and carefully, add a splash of oil to the pan, then the squid. Stir-fry for about 30 secs. Scatter the chorizo over the squid, continue to cook for 30 secs more, then tip into the bowl with the peppers. Season everything with salt and pepper, then dress with the remaining oil, lemon juice and lemon zest. Mix together, pile onto a platter and let everyone help themselves.",
      "strMealThumb": "https://www.themealdb.com/images/media/meals/wsu0rc1761848482.jpg",
      "strTags": null,
      "strYoutube": "https://www.bbcgoodfood.com/recipes/squid-chickpea-chorizo-salad",
      "strIngredient1": "Red Pepper",
      "strIngredient2": "Can of chickpeas",
      "strIngredient3": "Parsley",
      "strIngredient4": "Red Chilli",
      "strIngredient5": "Garlic Clove",
      "strIngredient6": "Olive Oil",
      "strIngredient7": "Squid",
      "strIngr
```

---

## 7. TheMealDB — categories.php

- **调用次数**: 1 次
- **去重后结果数**: 14
- **返回字段数**: 4
- **返回根 key**: `categories`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `idCategory` | ✅ 0% | 14 | 0 | 0 | 1 |
| `strCategory` | ✅ 0% | 14 | 0 | 0 | Beef |
| `strCategoryDescription` | ✅ 0% | 14 | 0 | 0 | Beef is the culinary name for meat from cattle, pa |
| `strCategoryThumb` | ✅ 0% | 14 | 0 | 0 | https://www.themealdb.com/images/category/beef.png |

### 标准请求/响应样本

```json
{
  "categories": [
    {
      "idCategory": "1",
      "strCategory": "Beef",
      "strCategoryThumb": "https://www.themealdb.com/images/category/beef.png",
      "strCategoryDescription": "Beef is the culinary name for meat from cattle, particularly skeletal muscle. Humans have been eating beef since prehistoric times.[1] Beef is a source of high-quality protein and essential nutrients.[2]"
    }
  ]
}
```

---

## 8. TheCocktailDB — search.php?s={name}

- **调用次数**: 30 词搜索
- **去重后结果数**: 162
- **返回字段数**: 51
- **返回根 key**: `drinks`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `dateModified` | 🔵 15.4% | 137 | 25 | 0 | 2015-08-18 14:42:59 |
| `idDrink` | ✅ 0% | 162 | 0 | 0 | 11007 |
| `strAlcoholic` | ✅ 0% | 162 | 0 | 0 | Alcoholic |
| `strCategory` | ✅ 0% | 162 | 0 | 0 | Ordinary Drink |
| `strCreativeCommonsConfirmed` | ✅ 0% | 162 | 0 | 0 | Yes |
| `strDrink` | ✅ 0% | 162 | 0 | 0 | Margarita |
| `strDrinkAlternate` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strDrinkThumb` | ✅ 0% | 162 | 0 | 0 | https://www.thecocktaildb.com/images/media/drink/5 |
| `strGlass` | ✅ 0% | 162 | 0 | 0 | Cocktail glass |
| `strIBA` | 🔴 86.4% | 22 | 140 | 0 | Contemporary Classics |
| `strImageAttribution` | 🔴 90.7% | 15 | 147 | 0 | Cocktailmarler |
| `strImageSource` | 🔴 84.0% | 26 | 136 | 0 | https://commons.wikimedia.org/wiki/File:Klassiche_ |
| `strIngredient1` | ✅ 0% | 162 | 0 | 0 | Tequila |
| `strIngredient10` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strIngredient11` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strIngredient12` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strIngredient13` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strIngredient14` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strIngredient15` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strIngredient2` | ✅ 0% | 162 | 0 | 0 | Triple sec |
| `strIngredient3` | 🔵 11.1% | 144 | 18 | 0 | Lime juice |
| `strIngredient4` | 🟡 29.6% | 114 | 48 | 0 | Salt |
| `strIngredient5` | 🟠 51.2% | 79 | 83 | 0 | Strawberries |
| `strIngredient6` | 🟠 74.7% | 41 | 121 | 0 | Salt |
| `strIngredient7` | 🔴 92.0% | 13 | 149 | 0 | Mint |
| `strIngredient8` | 🔴 97.5% | 4 | 158 | 0 | Fresca |
| `strIngredient9` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strInstructions` | ✅ 0% | 162 | 0 | 0 | Rub the rim of the glass with the lime slice to ma |
| `strInstructionsDE` | 🔵 4.9% | 154 | 8 | 0 | Reiben Sie den Rand des Glases mit der Limettensch |
| `strInstructionsES` | 🔵 19.1% | 131 | 31 | 0 | Frota el borde del vaso con la rodaja de lima para |
| `strInstructionsFR` | 🟡 24.1% | 123 | 39 | 0 | Frotter le bord du verre avec la tranche de citron |
| `strInstructionsIT` | ✅ 0% | 162 | 0 | 0 | Strofina il bordo del bicchiere con la fetta di li |
| `strInstructionsZH-HANS` | 🔴 99.4% | 1 | 161 | 0 | 将解冻的草莓放入一个大碗中。用叉子将它们捣碎，以确保没有大块。

在潘趣酒碗或水罐中，将捣碎的草 |
| `strInstructionsZH-HANT` | 🔴 99.4% | 1 | 161 | 0 | 將解凍的草莓放入大碗中。用叉子將它們搗碎，以確保沒有大塊。

在潘趣酒碗或水罐中，將搗碎的草莓、 |
| `strMeasure1` | 🔵 1.9% | 159 | 3 | 0 | 1 1/2 oz  |
| `strMeasure10` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strMeasure11` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strMeasure12` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strMeasure13` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strMeasure14` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strMeasure15` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strMeasure2` | 🔵 4.3% | 155 | 7 | 0 | 1/2 oz  |
| `strMeasure3` | 🔵 14.8% | 138 | 24 | 0 | 1 oz  |
| `strMeasure4` | 🟡 37.0% | 102 | 55 | 5 | Coarse  |
| `strMeasure5` | 🟠 58.6% | 67 | 83 | 12 | 1 oz  |
| `strMeasure6` | 🔴 81.5% | 30 | 118 | 14 | Garnish with |
| `strMeasure7` | 🔴 93.2% | 11 | 134 | 17 | Garnish with |
| `strMeasure8` | 🔴 98.1% | 3 | 159 | 0 | 3 oz |
| `strMeasure9` | 🔴 100.0% | 0 | 162 | 0 | — |
| `strTags` | 🟠 75.3% | 40 | 122 | 0 | IBA,ContemporaryClassic |
| `strVideo` | 🔴 95.1% | 8 | 154 | 0 | https://www.youtube.com/watch?v=ApMR3IWYZHI |

### 标准请求/响应样本

```json
{
  "drinks": [
    {
      "idDrink": "11007",
      "strDrink": "Margarita",
      "strDrinkAlternate": null,
      "strTags": "IBA,ContemporaryClassic",
      "strVideo": null,
      "strCategory": "Ordinary Drink",
      "strIBA": "Contemporary Classics",
      "strAlcoholic": "Alcoholic",
      "strGlass": "Cocktail glass",
      "strInstructions": "Rub the rim of the glass with the lime slice to make the salt stick to it. Take care to moisten only the outer rim and sprinkle the salt on it. The salt should present to the lips of the imbiber and never mix into the cocktail. Shake the other ingredients with ice, then carefully pour into the glass.",
      "strInstructionsES": "Frota el borde del vaso con la rodaja de lima para que la sal se adhiera a él. Procure humedecer sólo el borde exterior y espolvorear la sal sobre él. La sal debe presentarse en los labios del imbibidor y nunca mezclarse en el cóctel. Agite los demás ingredientes con hielo y viértalos con cuidado en el vaso.",
      "strInstructionsDE": "Reiben Sie den Rand des Glases mit der Limettenscheibe, damit das Salz daran haftet. Achten Sie darauf, dass nur der äußere Rand angefeuchtet wird und streuen Sie das Salz darauf. Das Salz sollte sich auf den Lippen des Genießers befinden und niemals in den Cocktail einmischen. Die anderen Zutaten mit Eis schütteln und vorsichtig in das Glas geben.",
      "strInstructionsFR": "Frotter le bord du verre avec la tranche de citron vert pour faire adhérer le sel. Veillez
```

---

## 9. TheCocktailDB — filter.php?i={ingredient}

- **调用次数**: 30 种食材
- **去重后结果数**: 22
- **返回字段数**: 3
- **返回根 key**: `drinks`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `idDrink` | ✅ 0% | 22 | 0 | 0 | 15300 |
| `strDrink` | ✅ 0% | 22 | 0 | 0 | 3-Mile Long Island Iced Tea |
| `strDrinkThumb` | ✅ 0% | 22 | 0 | 0 | https://www.thecocktaildb.com/images/media/drink/r |

### 标准请求/响应样本

```json
{
  "drinks": [
    {
      "strDrink": "3-Mile Long Island Iced Tea",
      "strDrinkThumb": "https://www.thecocktaildb.com/images/media/drink/rrtssw1472668972.jpg",
      "idDrink": "15300"
    }
  ]
}
```

---

## 10. TheCocktailDB — lookup.php?i={id}

- **调用次数**: 30 个 ID
- **去重后结果数**: 20
- **返回字段数**: 51
- **返回根 key**: `drinks`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `dateModified` | ✅ 0% | 20 | 0 | 0 | 2015-08-18 14:42:59 |
| `idDrink` | ✅ 0% | 20 | 0 | 0 | 11007 |
| `strAlcoholic` | ✅ 0% | 20 | 0 | 0 | Alcoholic |
| `strCategory` | ✅ 0% | 20 | 0 | 0 | Ordinary Drink |
| `strCreativeCommonsConfirmed` | ✅ 0% | 20 | 0 | 0 | Yes |
| `strDrink` | ✅ 0% | 20 | 0 | 0 | Margarita |
| `strDrinkAlternate` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strDrinkThumb` | ✅ 0% | 20 | 0 | 0 | https://www.thecocktaildb.com/images/media/drink/5 |
| `strGlass` | ✅ 0% | 20 | 0 | 0 | Cocktail glass |
| `strIBA` | 🟠 75.0% | 5 | 15 | 0 | Contemporary Classics |
| `strImageAttribution` | 🟠 55.0% | 9 | 11 | 0 | Cocktailmarler |
| `strImageSource` | 🟠 55.0% | 9 | 11 | 0 | https://commons.wikimedia.org/wiki/File:Klassiche_ |
| `strIngredient1` | ✅ 0% | 20 | 0 | 0 | Tequila |
| `strIngredient10` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strIngredient11` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strIngredient12` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strIngredient13` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strIngredient14` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strIngredient15` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strIngredient2` | ✅ 0% | 20 | 0 | 0 | Triple sec |
| `strIngredient3` | 🔵 10.0% | 18 | 2 | 0 | Lime juice |
| `strIngredient4` | 🟠 60.0% | 8 | 12 | 0 | Salt |
| `strIngredient5` | 🔴 90.0% | 2 | 18 | 0 | Maraschino cherry |
| `strIngredient6` | 🔴 95.0% | 1 | 19 | 0 | Orange peel |
| `strIngredient7` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strIngredient8` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strIngredient9` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strInstructions` | ✅ 0% | 20 | 0 | 0 | Rub the rim of the glass with the lime slice to ma |
| `strInstructionsDE` | ✅ 0% | 20 | 0 | 0 | Reiben Sie den Rand des Glases mit der Limettensch |
| `strInstructionsES` | ✅ 0% | 20 | 0 | 0 | Frota el borde del vaso con la rodaja de lima para |
| `strInstructionsFR` | ✅ 0% | 20 | 0 | 0 | Frotter le bord du verre avec la tranche de citron |
| `strInstructionsIT` | ✅ 0% | 20 | 0 | 0 | Strofina il bordo del bicchiere con la fetta di li |
| `strInstructionsZH-HANS` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strInstructionsZH-HANT` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure1` | ✅ 0% | 20 | 0 | 0 | 1 1/2 oz  |
| `strMeasure10` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure11` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure12` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure13` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure14` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure15` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure2` | ✅ 0% | 20 | 0 | 0 | 1/2 oz  |
| `strMeasure3` | 🔵 15.0% | 17 | 3 | 0 | 1 oz  |
| `strMeasure4` | 🟠 75.0% | 5 | 15 | 0 | 2 or 3  |
| `strMeasure5` | 🔴 90.0% | 2 | 18 | 0 | 1  |
| `strMeasure6` | 🔴 95.0% | 1 | 19 | 0 | 1 twist of  |
| `strMeasure7` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure8` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strMeasure9` | 🔴 100.0% | 0 | 20 | 0 | — |
| `strTags` | 🟠 50.0% | 10 | 10 | 0 | IBA,ContemporaryClassic |
| `strVideo` | 🔴 85.0% | 3 | 17 | 0 | https://www.youtube.com/watch?v=TFWPtkNoF4Y |

### 标准请求/响应样本

```json
{
  "drinks": [
    {
      "idDrink": "178312",
      "strDrink": "Bloody Punch",
      "strDrinkAlternate": null,
      "strTags": "Halloween",
      "strVideo": null,
      "strCategory": "Punch / Party Drink",
      "strIBA": null,
      "strAlcoholic": "Alcoholic",
      "strGlass": "Punch bowl",
      "strInstructions": "Place the thawed strawberries in a large bowl. Mash them with a fork to ensure no large chunks.\r\n\r\nIn a punch bowl or pitcher, combine mashed strawberries, lime pulp and soda. Mix well.\r\n\r\nAdd blueberries and raisins. They will float and look like bugs in the punch.",
      "strInstructionsES": "Coloque las fresas descongeladas en un bol grande. Machácalas con un tenedor para que no queden trozos grandes.\r\n\r\nPaso\r\n2\r\n\r\n \r\nEn una ponchera o jarra, mezcla el puré de fresas, la pulpa de lima y la soda. Mezcle bien.\r\n\r\nPaso\r\n3\r\n\r\n \r\nAñade los arándanos y las pasas. Flotarán y parecerán bichos en el ponche.",
      "strInstructionsDE": "Die aufgetauten Erdbeeren in eine große Schüssel geben. Zerdrücken Sie sie mit einer Gabel, um sicherzustellen, dass keine großen Stücke entstehen.\r\n\r\nIn einer Bowle oder einem Krug zerdrückte Erdbeeren, Limettenmark und Soda vermischen. Gut mischen.\r\n\r\nBlaubeeren und Rosinen hinzufügen. Sie schweben und sehen aus wie Käfer im Loch.",
      "strInstructionsFR": "Placer les fraises décongelées dans un grand bol. Les écraser à l'aide d'une fourchette pour qu'il n'y ait pas de gros morceau
```

---

## 11. TheCocktailDB — random.php

- **调用次数**: 30 次随机
- **去重后结果数**: 28
- **返回字段数**: 51
- **返回根 key**: `drinks`

### 字段缺失分析

| 字段 | 缺失率 | 有值 | null | 空串 | 样本值 |
|------|--------|------|------|------|--------|
| `dateModified` | 🔵 14.3% | 24 | 4 | 0 | 2015-09-06 16:51:14 |
| `idDrink` | ✅ 0% | 28 | 0 | 0 | 12442 |
| `strAlcoholic` | ✅ 0% | 28 | 0 | 0 | Alcoholic |
| `strCategory` | ✅ 0% | 28 | 0 | 0 | Ordinary Drink |
| `strCreativeCommonsConfirmed` | ✅ 0% | 28 | 0 | 0 | No |
| `strDrink` | ✅ 0% | 28 | 0 | 0 | Vermouth Cassis |
| `strDrinkAlternate` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strDrinkThumb` | ✅ 0% | 28 | 0 | 0 | https://www.thecocktaildb.com/images/media/drink/t |
| `strGlass` | ✅ 0% | 28 | 0 | 0 | Highball glass |
| `strIBA` | 🔴 85.7% | 4 | 24 | 0 | Contemporary Classics |
| `strImageAttribution` | 🔴 96.4% | 1 | 27 | 0 | Cocktailmarler |
| `strImageSource` | 🔴 89.3% | 3 | 25 | 0 | https://commons.wikimedia.org/wiki/File:Klassiche_ |
| `strIngredient1` | ✅ 0% | 28 | 0 | 0 | Dry Vermouth |
| `strIngredient10` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strIngredient11` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strIngredient12` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strIngredient13` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strIngredient14` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strIngredient15` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strIngredient2` | ✅ 0% | 28 | 0 | 0 | Creme de Cassis |
| `strIngredient3` | 🔵 3.6% | 27 | 1 | 0 | Carbonated water |
| `strIngredient4` | 🟡 35.7% | 18 | 10 | 0 | Cucumber |
| `strIngredient5` | 🟠 64.3% | 10 | 18 | 0 | lemon |
| `strIngredient6` | 🔴 85.7% | 4 | 24 | 0 | Red wine |
| `strIngredient7` | 🔴 96.4% | 1 | 27 | 0 | Brandy |
| `strIngredient8` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strIngredient9` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strInstructions` | ✅ 0% | 28 | 0 | 0 | Stir vermouth and creme de cassis in a highball gl |
| `strInstructionsDE` | 🔵 10.7% | 25 | 3 | 0 | Wermut und Creme de Cassis in einem Highball-Glas  |
| `strInstructionsES` | 🟡 28.6% | 20 | 8 | 0 | Llenar el vaso con hielo
Vierta la ginebra y el z |
| `strInstructionsFR` | 🟡 39.3% | 17 | 11 | 0 | Remplir le verre de glace
Verser le Gin et le jus |
| `strInstructionsIT` | ✅ 0% | 28 | 0 | 0 | Mescolare il vermouth e la creme de cassis in un b |
| `strInstructionsZH-HANS` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strInstructionsZH-HANT` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strMeasure1` | 🔵 3.6% | 27 | 1 | 0 | 1 1/2 oz  |
| `strMeasure10` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strMeasure11` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strMeasure12` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strMeasure13` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strMeasure14` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strMeasure15` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strMeasure2` | ✅ 0% | 28 | 0 | 0 | 3/4 oz  |
| `strMeasure3` | 🔵 10.7% | 25 | 3 | 0 | 10 cl |
| `strMeasure4` | 🟡 46.4% | 15 | 13 | 0 | Chopped |
| `strMeasure5` | 🟠 64.3% | 10 | 17 | 1 | Chopped |
| `strMeasure6` | 🔴 92.9% | 2 | 24 | 2 | 750 ml  |
| `strMeasure7` | 🔴 96.4% | 1 | 25 | 2 | 1/4 cup  |
| `strMeasure8` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strMeasure9` | 🔴 100.0% | 0 | 28 | 0 | — |
| `strTags` | 🟠 71.4% | 8 | 20 | 0 | German |
| `strVideo` | 🔴 96.4% | 1 | 27 | 0 | https://www.youtube.com/watch?v=obGhGNUKx30 |

### 标准请求/响应样本

```json
{
  "drinks": [
    {
      "idDrink": "17215",
      "strDrink": "Spritz",
      "strDrinkAlternate": null,
      "strTags": null,
      "strVideo": null,
      "strCategory": "Ordinary Drink",
      "strIBA": "New Era Drinks",
      "strAlcoholic": "Alcoholic",
      "strGlass": "Old-Fashioned glass",
      "strInstructions": "Build into glass over ice, garnish and serve.",
      "strInstructionsES": "Servir en un vaso con hielo, decorar y servir.",
      "strInstructionsDE": "Über Eis in Glas einfüllen, garnieren und servieren.",
      "strInstructionsFR": "Verser dans un verre avec des glaçons, garnir et servir.",
      "strInstructionsIT": "Build into glass over ice, garnish and serve.",
      "strInstructionsZH-HANS": null,
      "strInstructionsZH-HANT": null,
      "strDrinkThumb": "https://www.thecocktaildb.com/images/media/drink/j9evx11504373665.jpg",
      "strIngredient1": "Prosecco",
      "strIngredient2": "Campari",
      "strIngredient3": "Soda Water",
      "strIngredient4": null,
      "strIngredient5": null,
      "strIngredient6": null,
      "strIngredient7": null,
      "strIngredient8": null,
      "strIngredient9": null,
      "strIngredient10": null,
      "strIngredient11": null,
      "strIngredient12": null,
      "strIngredient13": null,
      "strIngredient14": null,
      "strIngredient15": null,
      "strMeasure1": "6 cl",
      "strMeasure2": "4 cl",
      "strMeasure3": "splash",
      "strMeasure4": null,
      "strMeasure5": null,
      "s
```

---

## 🔍 跨接口关键发现

### 1. filter 接口 vs 详情接口的字段差异

| 接口类型 | TheMealDB 字段数 | TheCocktailDB 字段数 |
|---------|-----------------|---------------------|
| search / lookup / random（详情） | 54 | 51 |
| filter（摘要） | **5** | **3** |
| categories | 4 | — |

filter 接口只返回摘要信息，需配合 lookup 获取完整数据。

### 2. strCountry vs strArea（TheMealDB）

| 接口 | strArea 缺失率 | strCountry 缺失率 |
|------|---------------|------------------|
| search (332 条) | 8.1% | **0%** |
| filter_i (613 条) | 10.3% | **0%** |
| filter_c (667 条) | 9.9% | **0%** |
| filter_a (403 条) | 0% | **0%** |
| lookup (29 条) | 0% | **0%** |
| random (29 条) | 3.4% | **0%** |

**结论**: `strCountry` 在所有接口中零缺失，`strArea` 在 filter_i/filter_c 中有 ~10% 缺失。推荐用 `strCountry`。

### 3. 无结果返回格式不一致

| 接口 | 无结果返回 |
|------|-----------|
| TheMealDB 所有接口 | `{"meals": null}` |
| TheCocktailDB search/lookup | `{"drinks": null}` |
| TheCocktailDB filter | `{"drinks": "no data found"}` ⚠️ |

### 4. TheCocktailDB 中文翻译未实现

- `strInstructionsZH-HANS`（简体中文）：162 条中仅 1 条有值（99.4% 缺失）
- `strInstructionsZH-HANT`（繁体中文）：同上
- 其他语言覆盖率：英文 100% > 意大利文 100% > 德文 95% > 西班牙文 81% > 法文 76%

### 5. 永远为空的字段

| 字段 | 数据源 | 说明 |
|------|--------|------|
| `strMealAlternate` | TheMealDB | 永远 null，疑似废弃 |
| `strImageSource` | TheMealDB | 永远 null |
| `strCreativeCommonsConfirmed` | TheMealDB | 永远 null |
| `strDrinkAlternate` | TheCocktailDB | 永远 null |
| `strInstructionsZH-HANS` | TheCocktailDB | 永远 null（中文翻译未实现） |
| `strInstructionsZH-HANT` | TheCocktailDB | 永远 null |
| `strIngredient10~15` | TheCocktailDB | 永远 null（只用到 9 种食材） |

### 6. TheCocktailDB 特有字段

| 字段 | 说明 | 缺失率 |
|------|------|--------|
| `strAlcoholic` | 含酒精类型（Alcoholic / Non alcoholic / Optional alcohol） | 0% |
| `strGlass` | 推荐杯型（如 Cocktail glass） | 0% |
| `strIBA` | 国际调酒师协会官方分类 | 75~86% |
| `strVideo` | 视频链接（几乎全空） | 85~96% |
| `strCreativeCommonsConfirmed` | CC 协议确认（TheMealDB 永远 null，TheCocktailDB 有值） | 0% |

### 7. 食材槽位数差异

| | TheMealDB | TheCocktailDB |
|--|-----------|---------------|
| 最大食材数 | 20 | 15 |
| 实际常用上限 | ~12 | ~6 |
| 99% 使用的槽位 | 1~11 | 1~5 |

### 8. 空搜索行为

- TheMealDB `search.php?s=`（空参数）→ 返回 25 条默认数据（可当推荐接口）
- TheCocktailDB `search.php?s=` → 返回 null

### 9. 参数大小写

- 两个 API 的 filter 参数均**不区分大小写**
- `?i=Chicken_Breast` 和 `?i=chicken_breast` 返回相同结果

---

## 🛠️ 前端最佳实践

```js
// 统一判空（处理 null / "" / "null" / "no data found"）
const isEmpty = (v) => !v || v.trim() === '' || v === 'null' || v === 'no data found';

// 检查是否有结果
const hasResults = (data, key = 'meals') => Array.isArray(data[key]) && data[key].length > 0;

// TheMealDB: filter → lookup 典型流程
async function getFullMeals(filterUrl) {
  const res = await fetch(filterUrl);
  const data = await res.json();
  if (!hasResults(data, 'meals')) return [];
  return Promise.all(
    data.meals.map(m =>
      fetch(`/api/json/v1/1/lookup.php?i=${m.idMeal}`)
        .then(r => r.json())
        .then(d => d.meals?.[0])
    )
  ).then(results => results.filter(Boolean));
}

// TheMealDB: 获取归属地（优先 strCountry）
const getCountry = (meal) => meal.strCountry || meal.strArea || 'Unknown';

// TheCocktailDB: 获取饮品信息
const getDrinkInfo = (drink) => ({
  name: drink.strDrink,
  category: drink.strCategory,
  alcoholic: drink.strAlcoholic,
  glass: drink.strGlass,
  iba: drink.strIBA || null,
  tags: isEmpty(drink.strTags) ? [] : drink.strTags.split(',').map(t => t.trim()),
});
```