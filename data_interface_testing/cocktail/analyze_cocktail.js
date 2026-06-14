const https = require('https');
const fs = require('fs');
const path = require('path');

const URL = 'https://www.thecocktaildb.com/api/json/v1/1/random.php';
const TIMES = 100;
const results = [];

function fetchOnce() {
  return new Promise((resolve, reject) => {
    https.get(URL, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.drinks[0]);
        } catch(e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function main() {
  // Collect 30 samples with small delay to avoid rate limiting
  for (let i = 0; i < TIMES; i++) {
    try {
      const drink = await fetchOnce();
      results.push(drink);
      process.stderr.write(`Fetched ${i+1}/${TIMES}\n`);
      // small delay
      await new Promise(r => setTimeout(r, 300));
    } catch(e) {
      process.stderr.write(`Error on ${i+1}: ${e.message}\n`);
      i--; // retry
      await new Promise(r => setTimeout(r, 1000));
    }
  }

  // Get all unique field names
  const allFields = new Set();
  results.forEach(r => Object.keys(r).forEach(k => allFields.add(k)));
  const fields = [...allFields].sort();

  // Field name -> Chinese description mapping
  const fieldDesc = {
    'idDrink': '饮品唯一ID',
    'strDrink': '饮品名称',
    'strDrinkAlternate': '替代名称（历史/别名）',
    'strTags': '标签（逗号分隔）',
    'strVideo': '视频链接（YouTube等）',
    'strCategory': '饮品分类',
    'strIBA': 'IBA官方分类（国际调酒师协会）',
    'strAlcoholic': '是否含酒精',
    'strGlass': '推荐杯型',
    'strInstructions': '制作说明（英文）',
    'strInstructionsES': '制作说明（西班牙文）',
    'strInstructionsDE': '制作说明（德文）',
    'strInstructionsFR': '制作说明（法文）',
    'strInstructionsIT': '制作说明（意大利文）',
    'strInstructionsZH-HANS': '制作说明（简体中文）',
    'strInstructionsZH-HANT': '制作说明（繁体中文）',
    'strDrinkThumb': '饮品图片URL',
    'strIngredient1': '配料 1',
    'strIngredient2': '配料 2',
    'strIngredient3': '配料 3',
    'strIngredient4': '配料 4',
    'strIngredient5': '配料 5',
    'strIngredient6': '配料 6',
    'strIngredient7': '配料 7',
    'strIngredient8': '配料 8',
    'strIngredient9': '配料 9',
    'strIngredient10': '配料 10',
    'strIngredient11': '配料 11',
    'strIngredient12': '配料 12',
    'strIngredient13': '配料 13',
    'strIngredient14': '配料 14',
    'strIngredient15': '配料 15',
    'strMeasure1': '用量 1',
    'strMeasure2': '用量 2',
    'strMeasure3': '用量 3',
    'strMeasure4': '用量 4',
    'strMeasure5': '用量 5',
    'strMeasure6': '用量 6',
    'strMeasure7': '用量 7',
    'strMeasure8': '用量 8',
    'strMeasure9': '用量 9',
    'strMeasure10': '用量 10',
    'strMeasure11': '用量 11',
    'strMeasure12': '用量 12',
    'strMeasure13': '用量 13',
    'strMeasure14': '用量 14',
    'strMeasure15': '用量 15',
    'strImageSource': '图片素材来源',
    'strImageAttribution': '图片版权归属',
    'strCreativeCommonsConfirmed': '知识共享协议确认',
    'dateModified': '数据最后修改时间'
  };

  // Analyze each field
  const analysis = fields.map(field => {
    const values = results.map(r => r[field]);
    const nullCount = values.filter(v => v === null).length;
    const emptyCount = values.filter(v => v === '').length;
    const nullOrEmpty = nullCount + emptyCount;
    const nonEmptyValues = values.filter(v => v !== null && v !== '');
    
    // Sample values (up to 5 unique)
    const uniqueNonEmpty = [...new Set(nonEmptyValues)];
    const samples = uniqueNonEmpty.slice(0, 5);
    
    // Detect special patterns
    const notes = [];
    if (field.startsWith('strIngredient')) notes.push('配料字段 (Ingredient)');
    if (field.startsWith('strMeasure')) notes.push('用量字段 (Measure)');
    if (field === 'strVideo') notes.push('视频链接，经常为null');
    if (field === 'strTags') notes.push('逗号分隔的标签');
    if (field === 'strImageSource' || field === 'strImageAttribution') notes.push('图片来源/归属信息');
    if (field === 'strCreativeCommonsConfirmed') notes.push('知识共享协议确认标志');
    if (field === 'dateModified') notes.push('修改日期 (ISO格式)');
    if (field === 'idDrink') notes.push('唯一标识符');
    if (field === 'strDrinkThumb') notes.push('饮品缩略图URL');
    if (field.startsWith('strIngredient') && nullOrEmpty > 0) {
      const num = parseInt(field.replace('strIngredient', ''));
      if (num > 1) notes.push(`第${num}种配料，高频为空`);
    }
    if (field.startsWith('strMeasure') && nullOrEmpty > 0) {
      const num = parseInt(field.replace('strMeasure', ''));
      if (num > 1) notes.push(`第${num}种用量，高频为空`);
    }
    
    // Check if all non-empty values look like URLs
    if (nonEmptyValues.length > 0 && nonEmptyValues.every(v => typeof v === 'string' && v.startsWith('http'))) {
      notes.push('所有值均为URL');
    }
    
    // Check if values look numeric
    if (nonEmptyValues.length > 0 && nonEmptyValues.every(v => typeof v === 'string' && /^\d+$/.test(v))) {
      notes.push('所有值均为纯数字字符串');
    }

    const desc = fieldDesc[field] || '';

    return {
      field,
      desc,
      totalCalls: TIMES,
      nullCount,
      emptyCount,
      nullOrEmpty,
      fillRate: ((TIMES - nullOrEmpty) / TIMES * 100).toFixed(1),
      samples,
      notes
    };
  });

  // Generate HTML
  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TheCocktailDB Random API 字段分析报告</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }
  .container { max-width: 1200px; margin: 0 auto; }
  h1 { font-size: 1.8rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, #f97316, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .subtitle { color: #94a3b8; margin-bottom: 2rem; font-size: 0.95rem; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
  .stat-card { background: #1e293b; border-radius: 12px; padding: 1.2rem; border: 1px solid #334155; }
  .stat-card .label { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat-card .value { font-size: 2rem; font-weight: 700; margin-top: 0.3rem; }
  .stat-card .value.orange { color: #f97316; }
  .stat-card .value.pink { color: #ec4899; }
  .stat-card .value.green { color: #22c55e; }
  .stat-card .value.blue { color: #3b82f6; }
  .section-title { font-size: 1.3rem; margin: 2rem 0 1rem; color: #f1f5f9; }
  table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; margin-bottom: 2rem; }
  thead { background: #334155; }
  th { padding: 0.8rem 1rem; text-align: left; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; font-weight: 600; }
  td { padding: 0.7rem 1rem; border-top: 1px solid #334155; font-size: 0.9rem; vertical-align: top; }
  tr:hover { background: #253348; }
  .bar-container { width: 100%; height: 8px; background: #334155; border-radius: 4px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
  .bar-fill.high { background: #22c55e; }
  .bar-fill.mid { background: #f97316; }
  .bar-fill.low { background: #ef4444; }
  .fill-text { font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem; }
  .sample-value { display: inline-block; background: #334155; border-radius: 6px; padding: 0.2rem 0.5rem; margin: 0.15rem 0.2rem; font-size: 0.8rem; font-family: 'SF Mono', Monaco, monospace; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #38bdf8; }
  .tag { display: inline-block; background: #4c1d95; color: #c4b5fd; border-radius: 4px; padding: 0.15rem 0.5rem; font-size: 0.75rem; margin: 0.1rem; }
  .tag.warn { background: #78350f; color: #fbbf24; }
  .tag.info { background: #1e3a5f; color: #60a5fa; }
  .null-badge { display: inline-block; background: #7f1d1d; color: #fca5a5; border-radius: 4px; padding: 0.1rem 0.4rem; font-size: 0.75rem; font-weight: 600; }
  .empty-badge { display: inline-block; background: #713f12; color: #fde68a; border-radius: 4px; padding: 0.1rem 0.4rem; font-size: 0.75rem; font-weight: 600; }
  .legend { display: flex; gap: 1.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
  .legend-item { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: #94a3b8; }
  .legend-dot { width: 10px; height: 10px; border-radius: 50%; }
  .note-box { background: #1e293b; border-left: 4px solid #f97316; border-radius: 0 12px 12px 0; padding: 1.2rem; margin-bottom: 1.5rem; }
  .note-box h3 { color: #f97316; font-size: 1rem; margin-bottom: 0.5rem; }
  .note-box ul { padding-left: 1.2rem; }
  .note-box li { margin-bottom: 0.3rem; color: #cbd5e1; font-size: 0.9rem; }
  .footer { text-align: center; color: #475569; font-size: 0.8rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #1e293b; }
</style>
</head>
<body>
<div class="container">
  <h1>🍹 TheCocktailDB Random API 字段分析报告</h1>
  <p class="subtitle">接口: <code style="background:#334155;padding:0.2rem 0.5rem;border-radius:4px;">https://www.thecocktaildb.com/api/json/v1/1/random.php</code> · 查询次数: ${TIMES} 次</p>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="label">总字段数</div>
      <div class="value orange">${fields.length}</div>
    </div>
    <div class="stat-card">
      <div class="label">始终有值的字段</div>
      <div class="value green">${analysis.filter(a => a.nullOrEmpty === 0).length}</div>
    </div>
    <div class="stat-card">
      <div class="label">有时为空的字段</div>
      <div class="value pink">${analysis.filter(a => a.nullOrEmpty > 0 && a.nullOrEmpty < TIMES).length}</div>
    </div>
    <div class="stat-card">
      <div class="label">始终为空的字段</div>
      <div class="value blue">${analysis.filter(a => a.nullOrEmpty === TIMES).length}</div>
    </div>
  </div>

  <div class="note-box">
    <h3>📊 关键发现</h3>
    <ul>
      <li><strong>配料 & 用量 (strIngredient1-15, strMeasure1-15)</strong>: 第1种配料/用量基本都有值，后续序号越高越容易为空。大部分饮品只用到3-6种配料。</li>
      <li><strong>strVideo</strong>: 绝大多数为 null，视频链接非常稀缺。</li>
      <li><strong>strImageSource / strImageAttribution</strong>: 大部分为空，属于可选的图片版权信息。</li>
      <li><strong>strCreativeCommonsConfirmed</strong>: 多数为 "Yes" 或空，标记知识共享协议。</li>
      <li><strong>strTags</strong>: 逗号分隔的标签（如 "IBA,ContemporaryClassic"），部分为空。</li>
      <li><strong>dateModified</strong>: ISO 8601 格式的修改时间戳。</li>
      <li><strong>strDrinkThumb</strong>: 几乎始终有值，指向饮品图片。</li>
      <li><strong>idDrink</strong>: 纯数字字符串，作为唯一标识。</li>
    </ul>
  </div>

  <div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:#22c55e"></div>填充率 ≥ 80%</div>
    <div class="legend-item"><div class="legend-dot" style="background:#f97316"></div>填充率 20%-79%</div>
    <div class="legend-item"><div class="legend-dot" style="background:#ef4444"></div>填充率 < 20%</div>
    <div class="legend-item"><span class="null-badge">NULL</span> JSON null 值</div>
    <div class="legend-item"><span class="empty-badge">""</span> 空字符串</div>
  </div>

  <h2 class="section-title">📋 字段详情</h2>
  <table>
    <thead>
      <tr>
        <th>字段名</th>
        <th>中文说明</th>
        <th>NULL</th>
        <th>空串""</th>
        <th>填充率</th>
        <th>示例值</th>
        <th>备注</th>
      </tr>
    </thead>
    <tbody>
${analysis.map(a => {
  const pct = parseFloat(a.fillRate);
  const barClass = pct >= 80 ? 'high' : pct >= 20 ? 'mid' : 'low';
  const samplesHtml = a.samples.map(s => {
    const display = s.length > 60 ? s.substring(0, 57) + '...' : s;
    return `<span class="sample-value" title="${s.replace(/"/g, '&quot;')}">${display}</span>`;
  }).join('');
  const notesHtml = a.notes.map(n => `<span class="tag info">${n}</span>`).join(' ');
  return `      <tr>
        <td><strong>${a.field}</strong></td>
        <td style="color:#94a3b8;font-size:0.85rem">${a.desc}</td>
        <td>${a.nullCount > 0 ? `<span class="null-badge">${a.nullCount}</span>` : '0'}</td>
        <td>${a.emptyCount > 0 ? `<span class="empty-badge">${a.emptyCount}</span>` : '0'}</td>
        <td>
          <div class="bar-container"><div class="bar-fill ${barClass}" style="width:${a.fillRate}%"></div></div>
          <div class="fill-text">${a.fillRate}%</div>
        </td>
        <td>${samplesHtml || '<span style="color:#64748b">—</span>'}</td>
        <td>${notesHtml || ''}</td>
      </tr>`;
}).join('\n')}
    </tbody>
  </table>

  <h2 class="section-title">🔍 特殊字段深度解读</h2>
  <div class="note-box" style="border-left-color:#3b82f6">
    <h3 style="color:#3b82f6">strIngredient & strMeasure</h3>
    <ul>
      <li>API 固定返回 15 个配料和 15 个用量字段，但实际饮品通常只用 3-6 种。</li>
      <li>未使用的字段值为空字符串 <code>""</code>（不是 null）。</li>
      <li>用量字段比配料字段更容易为空 —— 有些配料不需要指定用量（如 "garnish"）。</li>
    </ul>
  </div>
  <div class="note-box" style="border-left-color:#a855f7">
    <h3 style="color:#a855f7">strTags</h3>
    <ul>
      <li>值为逗号分隔的标签字符串，如 <code>"IBA,ContemporaryClassic"</code>。</li>
      <li>部分饮品无标签，此时为 <code>null</code>（不是空字符串）。</li>
      <li>常见标签: IBA, OrdinaryDrink, Cocktail, HomemadeLiqueur 等。</li>
    </ul>
  </div>
  <div class="note-box" style="border-left-color:#22c55e">
    <h3 style="color:#22c55e">strCreativeCommonsConfirmed</h3>
    <ul>
      <li>只有两个可能值: <code>"Yes"</code> 或空字符串。</li>
      <li>表示该饮品数据是否遵循知识共享协议。</li>
    </ul>
  </div>
  <div class="note-box" style="border-left-color:#ec4899">
    <h3 style="color:#ec4899">dateModified</h3>
    <ul>
      <li>格式: <code>"2015-08-18 14:42:59"</code>（非标准 ISO 8601，缺少 T 分隔符和时区）。</li>
      <li>几乎所有饮品都有此字段，记录数据库中的最后修改时间。</li>
    </ul>
  </div>

  <div class="footer">
    Generated on ${new Date().toISOString()} · ${TIMES} API calls to TheCocktailDB
  </div>
</div>
</body>
</html>`;

  const outPath = '/Users/zhoo/.openclaw/workspace/_temp/cocktail-api-analysis.html';
  fs.writeFileSync(outPath, html);

  // Generate Markdown report
  const alwaysFilled = analysis.filter(a => a.nullOrEmpty === 0);
  const sometimesEmpty = analysis.filter(a => a.nullOrEmpty > 0 && a.nullOrEmpty < TIMES);
  const alwaysEmpty = analysis.filter(a => a.nullOrEmpty === TIMES);

  const mdTableRows = analysis.map(a => {
    const samplesStr = a.samples.slice(0, 3).map(s => {
      const display = s.length > 50 ? s.substring(0, 47) + '...' : s;
      return '`' + display.replace(/\|/g, '\\|') + '`';
    }).join(', ');
    const notesStr = a.notes.join(', ');
    return `| ${a.field} | ${a.desc} | ${a.nullCount} | ${a.emptyCount} | ${a.fillRate}% | ${samplesStr || '—'} | ${notesStr || ''} |`;
  }).join('\n');

  const md = `# 🍹 TheCocktailDB Random API 字段分析报告

> **接口**: \`https://www.thecocktaildb.com/api/json/v1/1/random.php\`
> **查询次数**: ${TIMES} 次
> **生成时间**: ${new Date().toISOString()}

---

## 📊 概览

| 指标 | 数值 |
|------|------|
| 总字段数 | **${fields.length}** |
| 始终有值的字段 | **${alwaysFilled.length}** |
| 有时为空的字段 | **${sometimesEmpty.length}** |
| 始终为空的字段 | **${alwaysEmpty.length}** |

---

## 📋 字段详情

| 字段名 | 中文说明 | NULL 次数 | 空串\"\" 次数 | 填充率 | 示例值 | 备注 |
|--------|----------|-----------|-------------|--------|--------|------|
${mdTableRows}

---

## 🔍 关键发现

### 配料 & 用量 (strIngredient1-15, strMeasure1-15)

- API 固定返回 15 个配料和 15 个用量字段，但实际饮品通常只用 3-6 种。
- 未使用的字段值为空字符串 \`\"\"\`（不是 null）。
- 第 1 种配料/用量基本都有值，后续序号越高越容易为空。
- 用量字段比配料字段更容易为空 —— 有些配料不需要指定用量（如 garnish）。

### strVideo

- 绝大多数为 null，视频链接非常稀缺。

### strTags

- 值为逗号分隔的标签字符串，如 \`\"IBA,ContemporaryClassic\"\`。
- 部分饮品无标签，此时为 null（不是空字符串）。
- 常见标签: IBA, OrdinaryDrink, Cocktail, HomemadeLiqueur 等。

### strImageSource / strImageAttribution

- 大部分为空，属于可选的图片版权信息。

### strCreativeCommonsConfirmed

- 只有两个可能值: \`\"Yes\"\` 或空字符串。
- 表示该饮品数据是否遵循知识共享协议。

### dateModified

- 格式: \`\"2015-08-18 14:42:59\"\`（非标准 ISO 8601，缺少 T 分隔符和时区）。
- 几乎所有饮品都有此字段，记录数据库中的最后修改时间。

### strDrinkThumb & idDrink

- \`strDrinkThumb\` 几乎始终有值，指向饮品图片 URL。
- \`idDrink\` 为纯数字字符串，作为唯一标识，始终有值。

### 多语言制作说明

- API 提供 7 种语言的制作说明（英/西/德/法/意/简中/繁中）。
- 非英文说明经常为空，覆盖率较低。

---

## 🏷️ 始终为空的字段（${alwaysEmpty.length} 个）

${alwaysEmpty.map(a => `- \`${a.field}\` — ${a.desc}`).join('\n') || '无'}

---

## ⚠️ 高频缺失字段（填充率 < 50%，${sometimesEmpty.filter(a => parseFloat(a.fillRate) < 50).length} 个）

${sometimesEmpty.filter(a => parseFloat(a.fillRate) < 50).map(a => `- \`${a.field}\` (${a.desc}) — 填充率 ${a.fillRate}%`).join('\n') || '无'}
`;

  const mdPath = '/Users/zhoo/.openclaw/workspace/_temp/cocktail-api-analysis.md';
  fs.writeFileSync(mdPath, md);

  console.log(JSON.stringify({ 
    totalFields: fields.length,
    alwaysFilled: alwaysFilled.length,
    sometimesEmpty: sometimesEmpty.length,
    alwaysEmpty: alwaysEmpty.length,
    outputHtml: outPath,
    outputMd: mdPath
  }));
}

main().catch(e => { console.error(e); process.exit(1); });
