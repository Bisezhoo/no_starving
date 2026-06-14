# 🍹 TheCocktailDB Random API 分析报告

> **接口**: `https://www.thecocktaildb.com/api/json/v1/1/random.php`
> **采样**: 100 次
> **唯一 ID**: 95 个（5 个重复）
> **日期**: 2026-06-14

---

## 📊 概览

| 指标 | 数值 |
|------|------|
| 总字段数 | **51** |
| 从未缺失 | **11** |
| 有时缺失 | **25** |
| 永远缺失 | **15** |
| 唯一 ID 数 | **95/100** |

---

## 💀 永远缺失的字段（100% 为空）

| 字段 | 缺失类型 | 中文说明 |
|------|----------|----------|
| `strDrinkAlternate` | null | 饮品别名 / 替代名称（疑似废弃） |
| `strIngredient10` | null | 第 10 种配料名称 |
| `strIngredient11` | null | 第 11 种配料名称 |
| `strIngredient12` | null | 第 12 种配料名称 |
| `strIngredient13` | null | 第 13 种配料名称 |
| `strIngredient14` | null | 第 14 种配料名称 |
| `strIngredient15` | null | 第 15 种配料名称 |
| `strInstructionsZH-HANS` | null | 制作说明（简体中文） |
| `strInstructionsZH-HANT` | null | 制作说明（繁体中文） |
| `strMeasure10` | null | 第 10 种配料用量 |
| `strMeasure11` | null | 第 11 种配料用量 |
| `strMeasure12` | null | 第 12 种配料用量 |
| `strMeasure13` | null | 第 13 种配料用量 |
| `strMeasure14` | null | 第 14 种配料用量 |
| `strMeasure15` | null | 第 15 种配料用量 |

---

## 📉 高频缺失字段（填充率 < 50%）

| 字段 | 缺失率 | 缺失形式 | 中文说明 |
|------|--------|----------|----------|
| `strDrinkAlternate` | 100.0% | null | 饮品别名 / 替代名称（疑似废弃） |
| `strIngredient10` | 100.0% | null | 第 10 种配料名称 |
| `strIngredient11` | 100.0% | null | 第 11 种配料名称 |
| `strIngredient12` | 100.0% | null | 第 12 种配料名称 |
| `strIngredient13` | 100.0% | null | 第 13 种配料名称 |
| `strIngredient14` | 100.0% | null | 第 14 种配料名称 |
| `strIngredient15` | 100.0% | null | 第 15 种配料名称 |
| `strInstructionsZH-HANS` | 100.0% | null | 制作说明（简体中文） |
| `strInstructionsZH-HANT` | 100.0% | null | 制作说明（繁体中文） |
| `strMeasure10` | 100.0% | null | 第 10 种配料用量 |
| `strMeasure11` | 100.0% | null | 第 11 种配料用量 |
| `strMeasure12` | 100.0% | null | 第 12 种配料用量 |
| `strMeasure13` | 100.0% | null | 第 13 种配料用量 |
| `strMeasure14` | 100.0% | null | 第 14 种配料用量 |
| `strMeasure15` | 100.0% | null | 第 15 种配料用量 |
| `strIngredient9` | 99.0% | null | 第 9 种配料名称 |
| `strMeasure9` | 99.0% | null | 第 9 种配料用量 |
| `strVideo` | 99.0% | null | 视频链接（YouTube 等） |
| `strIngredient8` | 98.0% | null | 第 8 种配料名称 |
| `strMeasure8` | 98.0% | null | 第 8 种配料用量 |
| `strIngredient7` | 93.0% | null + "" 混合 | 第 7 种配料名称 |
| `strMeasure7` | 93.0% | null + "" 混合 | 第 7 种配料用量 |
| `strIBA` | 92.0% | null | IBA 官方分类（国际调酒师协会） |
| `strImageAttribution` | 90.0% | null | 图片版权归属 |
| `strImageSource` | 85.0% | null | 图片来源 URL |
| `strMeasure6` | 83.0% | null + "" 混合 | 第 6 种配料用量 |
| `strIngredient6` | 81.0% | null + "" 混合 | 第 6 种配料名称 |
| `strTags` | 76.0% | null | 标签，逗号分隔（如 "IBA,ContemporaryClassic"） |
| `strMeasure5` | 67.0% | null + "" 混合 | 第 5 种配料用量 |
| `strIngredient5` | 62.0% | null | 第 5 种配料名称 |

---

## 📊 strIngredient 缺失率分布

| 字段 | 填充率 | 缺失率 |
|------|--------|--------|
| `strIngredient1` | 100.0% | 0.0% |
| `strIngredient2` | 100.0% | 0.0% |
| `strIngredient3` | 90.0% | 10.0% |
| `strIngredient4` | 62.0% | 38.0% |
| `strIngredient5` | 38.0% | 62.0% |
| `strIngredient6` | 19.0% | 81.0% |
| `strIngredient7` | 7.0% | 93.0% |
| `strIngredient8` | 2.0% | 98.0% |
| `strIngredient9` | 1.0% | 99.0% |
| `strIngredient10` | 0.0% | 100.0% |
| `strIngredient11` | 0.0% | 100.0% |
| `strIngredient12` | 0.0% | 100.0% |
| `strIngredient13` | 0.0% | 100.0% |
| `strIngredient14` | 0.0% | 100.0% |
| `strIngredient15` | 0.0% | 100.0% |

## 📊 strMeasure 缺失率分布

| 字段 | 填充率 | 缺失率 |
|------|--------|--------|
| `strMeasure1` | 98.0% | 2.0% |
| `strMeasure2` | 97.0% | 3.0% |
| `strMeasure3` | 86.0% | 14.0% |
| `strMeasure4` | 56.0% | 44.0% |
| `strMeasure5` | 33.0% | 67.0% |
| `strMeasure6` | 17.0% | 83.0% |
| `strMeasure7` | 7.0% | 93.0% |
| `strMeasure8` | 2.0% | 98.0% |
| `strMeasure9` | 1.0% | 99.0% |
| `strMeasure10` | 0.0% | 100.0% |
| `strMeasure11` | 0.0% | 100.0% |
| `strMeasure12` | 0.0% | 100.0% |
| `strMeasure13` | 0.0% | 100.0% |
| `strMeasure14` | 0.0% | 100.0% |
| `strMeasure15` | 0.0% | 100.0% |

---

## 🗺️ 分类 & 枚举分布

### strCategory（饮品分类）

| 分类 | 次数 |
|------|------|
| Ordinary Drink | 43 |
| Cocktail | 28 |
| Shot | 12 |
| Other / Unknown | 5 |
| Punch / Party Drink | 4 |
| Coffee / Tea | 2 |
| Homemade Liqueur | 2 |
| Beer | 2 |
| Shake | 1 |
| Cocoa | 1 |

### strAlcoholic（酒精类型）

| 类型 | 次数 |
|------|------|
| Alcoholic | 92 |
| Non alcoholic | 7 |
| Optional alcohol | 1 |

### strGlass（推荐杯型 Top 12）

| 杯型 | 次数 |
|------|------|
| Cocktail glass | 20 |
| Old-fashioned glass | 17 |
| Highball glass | 14 |
| Shot glass | 9 |
| Collins glass | 8 |
| Collins Glass | 7 |
| Hurricane glass | 3 |
| Champagne flute | 2 |
| Martini Glass | 2 |
| Nick and Nora Glass | 2 |
| Highball Glass | 2 |
| Pitcher | 2 |

### strIBA（IBA 官方分类）

| 分类 | 次数 |
|------|------|
| Contemporary Classics | 4 |
| New Era Drinks | 3 |
| Unforgettables | 1 |

> ⚠️ 92/100 条为空 — 非所有饮品都有 IBA 分类


### strTags 高频标签 Top 15

| 标签 | 次数 |
|------|------|
| IBA | 8 |
| ContemporaryClassic | 5 |
| Sweet | 3 |
| NewEra | 3 |
| Alcoholic | 3 |
| Brunch | 3 |
| DateNight | 2 |
| USA | 2 |
| Breakfast | 2 |
| Hangover | 2 |
| Summer | 2 |
| StrongFlavor | 2 |
| Winter | 2 |
| Fruity | 1 |
| Classic | 1 |

> ⚠️ 76/100 条无标签（null）


---

## ⚠️ 特别值得注意的问题

### 1. 空值类型不一致
`strIngredient` / `strMeasure` 的空值有时是 JSON `null`，有时是空字符串 `""`，两种形式随机出现。前端判空必须同时处理：

```javascript
const isEmpty = (v) => !v || v.trim() === "" || v === "null";
```

### 2. strInstructions 含换行符
11/100 条记录含 `\n`。步骤格式不统一，需注意渲染处理。

### 3. strMeasure 值带前后空格
281 处用量值带多余空格（如 `" 2 oz "`），需 `trim()`。

### 4. strTags 格式不规范
逗号分隔，大小写混用，76% 缺失。

### 5. idDrink 会出现重复（真随机）
100 次调用出现 5 个重复 ID，唯一 ID 95 个。接口是真随机，不保证不重复。


### 6. strIBA 经常为空
并非所有饮品都有 IBA（国际调酒师协会）分类，92/100 条为空。只有经典鸡尾酒才有 IBA 归类。

### 7. 多语言制作说明覆盖率低
英文 strInstructions 始终有值，但 ES/DE/FR/IT/ZH-HANS/ZH-HANT 六种语言版本经常为空，不可依赖。

---

## ✅ 从未缺失的字段（11 个核心字段）

| 字段 | 类型 | 中文说明 |
|------|------|----------|
| `idDrink` | string | 饮品唯一 ID（数字字符串） |
| `strAlcoholic` | string | 是否含酒精 |
| `strCategory` | string | 饮品分类 |
| `strCreativeCommonsConfirmed` | string | 知识共享协议确认标志 |
| `strDrink` | string | 饮品英文名称 |
| `strDrinkThumb` | string | 饮品缩略图 URL |
| `strGlass` | string | 推荐杯型 |
| `strIngredient1` | string | 第 1 种配料名称 |
| `strIngredient2` | string | 第 2 种配料名称 |
| `strInstructions` | string | 制作说明（英文） |
| `strInstructionsIT` | string | 制作说明（意大利文） |

---

## 📖 全字段中文参考（51 个字段）

### 基础信息

| 字段 | 类型 | 中文说明 | 示例值 |
|------|------|----------|--------|
| `idDrink` | string | 饮品唯一 ID（数字字符串） | `13405` |
| `strAlcoholic` | string | 是否含酒精 | `Alcoholic` |
| `strCategory` | string | 饮品分类 | `Shot` |
| `strDrink` | string | 饮品英文名称 | `Brainteaser` |
| `strDrinkAlternate` | null | 饮品别名 / 替代名称（疑似废弃） | `null` |
| `strGlass` | string | 推荐杯型 | `Shot Glass` |
| `strIBA` | string\|null | IBA 官方分类（国际调酒师协会） | `New Era Drinks` |
| `strTags` | string\|null | 标签，逗号分隔（如 "IBA,ContemporaryClassic"） | `Fruity` |

### 媒体链接

| 字段 | 类型 | 中文说明 |
|------|------|----------|
| `strDrinkThumb` | string | 饮品缩略图 URL |
| `strImageAttribution` | string\|null | 图片版权归属 |
| `strImageSource` | string\|null | 图片来源 URL |
| `strVideo` | string\|null | 视频链接（YouTube 等） |

### 制作说明（多语言）

| 字段 | 缺失率 | 中文说明 |
|------|--------|----------|
| `strInstructions` | 0.0% | 制作说明（英文） |
| `strInstructionsDE` | 8.0% | 制作说明（德文） |
| `strInstructionsES` | 19.0% | 制作说明（西班牙文） |
| `strInstructionsFR` | 25.0% | 制作说明（法文） |
| `strInstructionsIT` | 0.0% | 制作说明（意大利文） |
| `strInstructionsZH-HANS` | 100.0% | 制作说明（简体中文） |
| `strInstructionsZH-HANT` | 100.0% | 制作说明（繁体中文） |

### 配料 & 用量

| 字段 | 缺失率 | 中文说明 |
|------|--------|----------|
| `strIngredient1` | 0.0% | 第 1 种配料名称 |
| `strIngredient10` | 100.0% | 第 10 种配料名称 |
| `strIngredient11` | 100.0% | 第 11 种配料名称 |
| `strIngredient12` | 100.0% | 第 12 种配料名称 |
| `strIngredient13` | 100.0% | 第 13 种配料名称 |
| `strIngredient14` | 100.0% | 第 14 种配料名称 |
| `strIngredient15` | 100.0% | 第 15 种配料名称 |
| `strIngredient2` | 0.0% | 第 2 种配料名称 |
| `strIngredient3` | 10.0% | 第 3 种配料名称 |
| `strIngredient4` | 38.0% | 第 4 种配料名称 |
| `strIngredient5` | 62.0% | 第 5 种配料名称 |
| `strIngredient6` | 81.0% | 第 6 种配料名称 |
| `strIngredient7` | 93.0% | 第 7 种配料名称 |
| `strIngredient8` | 98.0% | 第 8 种配料名称 |
| `strIngredient9` | 99.0% | 第 9 种配料名称 |
| `strMeasure1` | 2.0% | 第 1 种配料用量 |
| `strMeasure10` | 100.0% | 第 10 种配料用量 |
| `strMeasure11` | 100.0% | 第 11 种配料用量 |
| `strMeasure12` | 100.0% | 第 12 种配料用量 |
| `strMeasure13` | 100.0% | 第 13 种配料用量 |
| `strMeasure14` | 100.0% | 第 14 种配料用量 |
| `strMeasure15` | 100.0% | 第 15 种配料用量 |
| `strMeasure2` | 3.0% | 第 2 种配料用量 |
| `strMeasure3` | 14.0% | 第 3 种配料用量 |
| `strMeasure4` | 44.0% | 第 4 种配料用量 |
| `strMeasure5` | 67.0% | 第 5 种配料用量 |
| `strMeasure6` | 83.0% | 第 6 种配料用量 |
| `strMeasure7` | 93.0% | 第 7 种配料用量 |
| `strMeasure8` | 98.0% | 第 8 种配料用量 |
| `strMeasure9` | 99.0% | 第 9 种配料用量 |

### 元数据

| 字段 | 类型 | 中文说明 | 示例值 |
|------|------|----------|--------|
| `dateModified` | string\|null | 数据最后修改时间 | `2016-04-28 18:54:26` |
| `strCreativeCommonsConfirmed` | string | 知识共享协议确认标志 | `No` |

---

## 🛠️ 前端最佳实践代码

```javascript
// 安全判空 — 同时处理 null / "" / " "
const isEmpty = (v) => !v || v.trim() === "" || v === "null";

// 提取有效配料列表
const getIngredients = (drink) => {
  const items = [];
  for (let i = 1; i <= 15; i++) {
    const name = drink[`strIngredient${i}`];
    const amount = drink[`strMeasure${i}`];
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
const getTags = (drink) => {
  if (isEmpty(drink.strTags)) return [];
  return drink.strTags.split(",").map(t => t.trim()).filter(Boolean);
};

// 获取酒精类型
const isAlcoholic = (drink) => drink.strAlcoholic === "Alcoholic";

// 去重：接口是真随机，可能返回重复 ID
const seen = new Set();
if (seen.has(drink.idDrink)) {
  console.warn(`重复饮品: ${drink.strDrink}`);
}
seen.add(drink.idDrink);
```

---

*Generated 2026-06-14T02:12:33.689Z · TheCocktailDB Random API · 100 samples*
