# 🍽️ TheMealDB Random API 分析报告

> **接口**: `https://www.themealdb.com/api/json/v1/1/random.php`
> **采样**: 100 次 | **日期**: 2026-06-14

---

## 📊 总览

| 指标 | 数值 |
|------|------|
| 总字段数 | 54 |
| 从未缺失 | 12 |
| 有时缺失 | 39 |
| 永远缺失 | 3 |
| 唯一 ID 数 | 95 / 100（5 个重复） |

---

## 💀 永远缺失的字段（100% 为空）

| 字段 | 缺失类型 | 中文说明 |
|------|---------|---------|
| `strMealAlternate` | null | 菜品别名 / 替代名称，疑似废弃字段 |
| `strImageSource` | null | 图片来源 URL，永远为 null |
| `strCreativeCommonsConfirmed` | null | Creative Commons 协议确认标志，永远为 null |

---

## 📉 高频缺失字段

| 字段 | 缺失率 | 缺失形式 | 中文说明 |
|------|--------|---------|---------|
| `strIngredient17~20` | 96~98% | null + 空字符串混合 | 第 17~20 种食材名称，几乎不使用 |
| `strIngredient14~16` | 83~92% | null + 空字符串混合 | 第 14~16 种食材名称 |
| `strIngredient13` | 77% | null + 空字符串 | 第 13 种食材名称 |
| `strIngredient12` | 66% | null + 空字符串 | 第 12 种食材名称 |
| `strTags` | 65% | null | 菜品标签，逗号分隔 |
| `strIngredient11` | 57% | null + 空字符串 | 第 11 种食材名称 |
| `dateModified` | 49% | null | 记录最后修改时间 |
| `strMeasure17~20` | 44~46% | null + 空字符串 | 第 17~20 种食材用量 |
| `strIngredient10` | 43% | null + 空字符串 | 第 10 种食材名称 |
| `strIngredient9` | 34% | null + 空字符串 | 第 9 种食材名称 |
| `strIngredient8` | 24% | 空字符串 | 第 8 种食材名称 |
| `strYoutube` | 14% | 空字符串 | YouTube 视频链接 |
| `strArea` | 13% | null | 菜系风格标签（形容词形式） |
| `strSource` | 9% | null + 空字符串 | 菜谱原始来源 URL |

---

## 📊 strIngredient 缺失率分布

```
strIngredient1~3   ▏                              0%  ✅
strIngredient4     ▏                              1%  ✅
strIngredient5     ▏██                            6%  ✅
strIngredient6     ▏████                         12%  ✅
strIngredient7     ▏██████                       17%  ✅
strIngredient8     ▏█████████                    24%  ⚠️
strIngredient9     ▏████████████                 34%  ⚠️
strIngredient10    ▏████████████████             43%  ⚠️
strIngredient11    ▏█████████████████████        57%  🟠
strIngredient12    ▏████████████████████████     66%  🔴
strIngredient13    ▏███████████████████████████  77%  🔴
strIngredient14    ▏████████████████████████████████  83%  🔴
strIngredient15    ▏██████████████████████████████████  89%  🔴
strIngredient16    ▏████████████████████████████████████  92%  🔴
strIngredient17    ▏██████████████████████████████████████  96%  🔴
strIngredient18~20 ▏███████████████████████████████████████  98%  🔴
```

---

## 🗺️ 分类 & 地区分布

### strCategory（菜系分类）

| 分类 | 数量 |
|------|------|
| Dessert 甜点 | 24 |
| Chicken 鸡肉 | 13 |
| Beef 牛肉 | 11 |
| Vegetarian 素食 | 11 |
| Seafood 海鲜 | 10 |
| Side 配菜 | 9 |
| Pork 猪肉 | 6 |
| Miscellaneous 其他 | 6 |
| Breakfast 早餐 | 5 |
| Lamb 羊肉 | 3 |
| Vegan 纯素 | 2 |

### strCountry（国家归属）— 零缺失

| 国家 | 数量 |
|------|------|
| United Kingdom 英国 | 13 |
| Jamaica 牙买加 | 9 |
| United States 美国 | 6 |
| China 中国 | 6 |
| Turkey 土耳其 | 6 |
| France 法国 | 5 |
| Cambodia 柬埔寨 | 3 |
| 其他（33 个国家） | 52 |

> **💡 strCountry 始终有值（100/100）**，而 strArea 有 13 条为 null。两者值**不相同**：strArea 是菜系风格形容词（如 British），strCountry 是国家名（如 United Kingdom）。**建议用 strCountry 做筛选。**

---

## ⚠️ 特别值得注意的问题

### 1. 空值类型不一致

`strIngredient` / `strMeasure` 的空值有时是 JSON `null`，有时是空字符串 `""`，两种形式随机出现。前端判空必须同时处理：

```js
const isEmpty = (v) => !v || v.trim() === "" || v === "null";
```

### 2. strInstructions 几乎全部含换行符

99/100 条记录含 `\n`。步骤格式不统一：`step 1`、`1)`、`0.`、直接文字等。

### 3. strMeasure 值带前后空格

如 `" 2 tablespoons "`、`"  250g"`，需 `trim()`。

### 4. strTags 格式不规范

逗号分隔：`"Meat,Stew"`、`"Soup,Warm,Seafood,Shellfish"`，大小写混用，65% 缺失。

### 5. idMeal 会出现重复（真随机）

100 次调用出现 5 个重复 ID（各重复 2 次），唯一 ID 95 个。**接口是真随机，不保证不重复。**

### 6. strArea ≠ strCountry

- `strArea` = 菜系风格（形容词）：`British`、`Turkish`、`Chinese`
- `strCountry` = 国家名（名词）：`United Kingdom`、`Turkey`、`China`
- 100 条中 82 条值不同，13 条 strArea 为 null 但 strCountry 有值
- **strCountry 更可靠**

### 7. strSource 缺失率比预期高

100 次采样中 9 条缺失（9%），主要是空字符串（8 条）而非 null（1 条）。

---

## ✅ 从未缺失的字段（12 个核心字段）

| 字段 | 类型 | 中文说明 |
|------|------|---------|
| `idMeal` | string | 菜品唯一 ID（数字字符串，如 "53274"） |
| `strMeal` | string | 菜品英文名称 |
| `strMealThumb` | string | 菜品缩略图 URL（始终有效，指向 themealdb.com CDN） |
| `strInstructions` | string | 烹饪步骤详细说明（含 \n 换行符） |
| `strCategory` | string | 菜品分类（如 Dessert、Beef、Vegetarian） |
| `strCountry` | string | 所属国家（名词形式，零缺失，如 "United Kingdom"） |
| `strIngredient1` | string | 第 1 种食材名称 |
| `strIngredient2` | string | 第 2 种食材名称 |
| `strIngredient3` | string | 第 3 种食材名称 |
| `strMeasure1` | string | 第 1 种食材用量 |
| `strMeasure2` | string | 第 2 种食材用量 |
| `strMeasure3` | string | 第 3 种食材用量 |

---

## 📖 全字段中文参考（54 个字段）

### 基础信息（7 个）

| 字段 | 类型 | 中文说明 | 示例值 |
|------|------|---------|--------|
| `idMeal` | string | 菜品唯一 ID（数字字符串） | "53274" |
| `strMeal` | string | 菜品英文名称 | "Griddled aubergines with sesame dressing" |
| `strMealAlternate` | null | 菜品别名（永远为 null，疑似废弃） | null |
| `strCategory` | string | 菜品分类：Beef / Chicken / Dessert / Lamb / Miscellaneous / Pork / Seafood / Side / Starter / Vegan / Vegetarian / Breakfast | "Vegetarian" |
| `strArea` | string\|null | 菜系风格标签（形容词，如 British / Turkish），约 13% 缺失 | "Turkish" |
| `strCountry` | string | 所属国家（名词，零缺失，如 United Kingdom / Turkey） | "Turkey" |
| `strTags` | string\|null | 标签，逗号分隔（如 "Meat,Stew"），约 65% 缺失 | "Vegetarian,Nutty" |

### 媒体链接（4 个）

| 字段 | 类型 | 中文说明 | 示例值 |
|------|------|---------|--------|
| `strMealThumb` | string | 菜品缩略图 URL（始终有值，指向 themealdb.com CDN） | "https://www.themealdb.com/images/media/meals/...jpg" |
| `strImageSource` | null | 图片来源 URL（永远为 null，从未使用） | null |
| `strSource` | string\|null | 菜谱原始来源 URL（如 BBC Good Food），约 9% 缺失 | "https://www.bbcgoodfood.com/recipes/..." |
| `strYoutube` | string | YouTube 视频链接，约 14% 缺失（空字符串） | "https://www.youtube.com/watch?v=..." |

### 烹饪步骤（1 个）

| 字段 | 类型 | 中文说明 |
|------|------|---------|
| `strInstructions` | string | 烹饪步骤详细说明（始终有值，99/100 含 \n 换行。格式不统一：有的用 "step 1"，有的用 "1)"，有的用 "0."，有的直接文字） |

### 食材 & 用量（40 个：strIngredient1~20 + strMeasure1~20）

`strIngredient` 和 `strMeasure` 是 1~20 编号配对的。前端遍历用 `meal["strIngredient" + i]` 取值。

| 字段 | 缺失率 | 中文说明 |
|------|--------|---------|
| `strIngredient1` | 0% | 第 1 种食材名称（始终有值） |
| `strIngredient2` | 0% | 第 2 种食材名称（始终有值） |
| `strIngredient3` | 0% | 第 3 种食材名称（始终有值） |
| `strIngredient4` | 1% | 第 4 种食材名称 |
| `strIngredient5` | 6% | 第 5 种食材名称 |
| `strIngredient6` | 12% | 第 6 种食材名称 |
| `strIngredient7` | 17% | 第 7 种食材名称 |
| `strIngredient8` | 24% | 第 8 种食材名称 |
| `strIngredient9` | 34% | 第 9 种食材名称 |
| `strIngredient10` | 43% | 第 10 种食材名称 |
| `strIngredient11` | 57% | 第 11 种食材名称 |
| `strIngredient12` | 66% | 第 12 种食材名称 |
| `strIngredient13` | 77% | 第 13 种食材名称 |
| `strIngredient14` | 83% | 第 14 种食材名称 |
| `strIngredient15` | 89% | 第 15 种食材名称 |
| `strIngredient16` | 92% | 第 16 种食材名称 |
| `strIngredient17` | 96% | 第 17 种食材名称 |
| `strIngredient18` | 98% | 第 18 种食材名称 |
| `strIngredient19` | 98% | 第 19 种食材名称 |
| `strIngredient20` | 98% | 第 20 种食材名称 |
| `strMeasure1` | 0% | 第 1 种食材用量（如 "2 tablespoons"），值常带前后空格 |
| `strMeasure2` | 0% | 第 2 种食材用量 |
| `strMeasure3` | 0% | 第 3 种食材用量 |
| `strMeasure4` | 2% | 第 4 种食材用量 |
| `strMeasure5` | 2% | 第 5 种食材用量 |
| `strMeasure6` | 5% | 第 6 种食材用量 |
| `strMeasure7` | 9% | 第 7 种食材用量 |
| `strMeasure8` | 13% | 第 8 种食材用量 |
| `strMeasure9` | 18% | 第 9 种食材用量 |
| `strMeasure10` | 21% | 第 10 种食材用量 |
| `strMeasure11` | 27% | 第 11 种食材用量 |
| `strMeasure12` | 32% | 第 12 种食材用量 |
| `strMeasure13` | 37% | 第 13 种食材用量 |
| `strMeasure14` | 40% | 第 14 种食材用量 |
| `strMeasure15` | 41% | 第 15 种食材用量 |
| `strMeasure16` | 43% | 第 16 种食材用量 |
| `strMeasure17` | 44% | 第 17 种食材用量 |
| `strMeasure18` | 46% | 第 18 种食材用量 |
| `strMeasure19` | 46% | 第 19 种食材用量 |
| `strMeasure20` | 46% | 第 20 种食材用量 |

> **💡 空值可能是 `null`、`""` 或 `" "`（纯空格），建议统一用 `!v || v.trim() === ""` 判空。**

### 元数据（2 个）

| 字段 | 类型 | 中文说明 | 示例值 |
|------|------|---------|--------|
| `dateModified` | string\|null | 记录最后修改时间（格式 "YYYY-MM-DD HH:mm:ss"），约 49% 缺失 | "2025-11-22 13:09:15" |
| `strCreativeCommonsConfirmed` | null | Creative Commons 协议确认标志（永远为 null，从未使用） | null |

---

## 🛠️ 前端最佳实践代码

```js
// 安全判空 — 同时处理 null / "" / "null" / " "
const isEmpty = (v) => !v || v.trim() === "" || v === "null";

// 提取有效食材列表
const getIngredients = (meal) => {
  const items = [];
  for (let i = 1; i <= 20; i++) {
    const name = meal[`strIngredient${i}`];
    const amount = meal[`strMeasure${i}`];
    if (!isEmpty(name)) {
      items.push({
        name: name.trim(),
        measure: isEmpty(amount) ? "" : amount.trim(),
      });
    }
  }
  return items;
};

// 安全获取标签
const getTags = (meal) => {
  if (isEmpty(meal.strTags)) return [];
  return meal.strTags.split(",").map(t => t.trim()).filter(Boolean);
};

// 获取归属地（优先 strCountry，零缺失）
const getCountry = (meal) => meal.strCountry || meal.strArea || "Unknown";

// 去重：接口是真随机，100 次出现 5 个重复 ID
const seen = new Set();
if (seen.has(meal.idMeal)) {
  console.warn(`重复菜品: ${meal.strMeal}`);
}
seen.add(meal.idMeal);
```
