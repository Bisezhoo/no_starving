const https = require('https');
const fs = require('fs');

const URL = 'https://www.thecocktaildb.com/api/json/v1/1/random.php';
const TIMES = 100;
const results = [];

const fieldDesc = {
  'idDrink': '饮品唯一 ID（数字字符串）',
  'strDrink': '饮品英文名称',
  'strDrinkAlternate': '饮品别名 / 替代名称（疑似废弃）',
  'strTags': '标签，逗号分隔（如 "IBA,ContemporaryClassic"）',
  'strVideo': '视频链接（YouTube 等）',
  'strCategory': '饮品分类',
  'strIBA': 'IBA 官方分类（国际调酒师协会）',
  'strAlcoholic': '是否含酒精',
  'strGlass': '推荐杯型',
  'strInstructions': '制作说明（英文）',
  'strInstructionsES': '制作说明（西班牙文）',
  'strInstructionsDE': '制作说明（德文）',
  'strInstructionsFR': '制作说明（法文）',
  'strInstructionsIT': '制作说明（意大利文）',
  'strInstructionsZH-HANS': '制作说明（简体中文）',
  'strInstructionsZH-HANT': '制作说明（繁体中文）',
  'strDrinkThumb': '饮品缩略图 URL',
  'strImageSource': '图片来源 URL',
  'strImageAttribution': '图片版权归属',
  'strCreativeCommonsConfirmed': '知识共享协议确认标志',
  'dateModified': '数据最后修改时间'
};
for (let i = 1; i <= 15; i++) {
  fieldDesc[`strIngredient${i}`] = `第 ${i} 种配料名称`;
  fieldDesc[`strMeasure${i}`] = `第 ${i} 种配料用量`;
}

function fetchOnce() {
  return new Promise((resolve, reject) => {
    https.get(URL, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data).drinks[0]); }
        catch(e) { reject(e); }
      });
    }).on('error', reject);
  });
}

async function main() {
  const ids = new Set();
  let duplicateCount = 0;

  for (let i = 0; i < TIMES; i++) {
    try {
      const drink = await fetchOnce();
      results.push(drink);
      if (ids.has(drink.idDrink)) duplicateCount++;
      ids.add(drink.idDrink);
      process.stderr.write(`Fetched ${i+1}/${TIMES}\n`);
      await new Promise(r => setTimeout(r, 300));
    } catch(e) {
      process.stderr.write(`Error ${i+1}: ${e.message}\n`);
      i--;
      await new Promise(r => setTimeout(r, 1000));
    }
  }

  const allFields = new Set();
  results.forEach(r => Object.keys(r).forEach(k => allFields.add(k)));
  const fields = [...allFields].sort();

  const analysis = fields.map(field => {
    const values = results.map(r => r[field]);
    const nullCount = values.filter(v => v === null).length;
    const emptyCount = values.filter(v => v === '').length;
    const nullOrEmpty = nullCount + emptyCount;
    const nonEmpty = values.filter(v => v !== null && v !== '');
    const uniqueNonEmpty = [...new Set(nonEmpty)];
    const samples = uniqueNonEmpty.slice(0, 5);
    const fillRate = ((TIMES - nullOrEmpty) / TIMES * 100).toFixed(1);
    const desc = fieldDesc[field] || '';

    // Detect patterns
    const notes = [];
    if (field.startsWith('strIngredient')) notes.push('配料字段');
    if (field.startsWith('strMeasure')) notes.push('用量字段');
    if (field === 'strVideo') notes.push('视频链接，绝大多数为 null');
    if (field === 'strTags') notes.push('逗号分隔标签');
    if (field === 'strImageSource' || field === 'strImageAttribution') notes.push('图片版权信息');
    if (field === 'strCreativeCommonsConfirmed') notes.push('CC 协议标志');
    if (field === 'dateModified') notes.push('ISO 时间戳');
    if (field === 'idDrink') notes.push('唯一标识');
    if (field === 'strDrinkThumb') notes.push('饮品图片 URL');
    if (field === 'strIBA') notes.push('IBA 官方分类');
    if (field === 'strAlcoholic') notes.push('酒精类型枚举');
    if (field === 'strGlass') notes.push('杯型枚举');
    if (field === 'strCategory') notes.push('分类枚举');
    if (field.startsWith('strInstructions') && field !== 'strInstructions') notes.push('多语言制作说明');
    if (nonEmpty.length > 0 && nonEmpty.every(v => typeof v === 'string' && v.startsWith('http'))) notes.push('所有值均为 URL');
    if (nonEmpty.length > 0 && nonEmpty.every(v => typeof v === 'string' && /^\d+$/.test(v))) notes.push('纯数字字符串');
    if (nonEmpty.some(v => typeof v === 'string' && v.includes('\n'))) notes.push('含换行符');

    // Special values enumeration
    let enumValues = null;
    if (['strCategory', 'strAlcoholic', 'strGlass', 'strIBA'].includes(field)) {
      const counts = {};
      nonEmpty.forEach(v => { counts[v] = (counts[v] || 0) + 1; });
      enumValues = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    }

    return { field, desc, nullCount, emptyCount, nullOrEmpty, fillRate, samples, notes, enumValues };
  });

  // Category distribution
  const categoryField = analysis.find(a => a.field === 'strCategory');
  const alcoholicField = analysis.find(a => a.field === 'strAlcoholic');
  const glassField = analysis.find(a => a.field === 'strGlass');
  const ibaField = analysis.find(a => a.field === 'strIBA');
  const tagValues = results.map(r => r.strTags).filter(v => v !== null && v !== '');
  const allTags = tagValues.flatMap(v => v.split(',').map(t => t.trim())).filter(Boolean);
  const tagCounts = {};
  allTags.forEach(t => { tagCounts[t] = (tagCounts[t] || 0) + 1; });
  const topTags = Object.entries(tagCounts).sort((a, b) => b[1] - a[1]).slice(0, 15);

  // Check instructions newline
  const instrWithNewline = results.filter(r => r.strInstructions && r.strInstructions.includes('\n')).length;

  // Check measure trim issues
  const measureTrimIssues = results.reduce((acc, r) => {
    for (let i = 1; i <= 15; i++) {
      const v = r[`strMeasure${i}`];
      if (v && v !== '' && (v !== v.trim())) acc++;
    }
    return acc;
  }, 0);

  // Always missing
  const alwaysEmpty = analysis.filter(a => a.nullOrEmpty === TIMES);
  // High frequency missing (< 50% fill)
  const highFreqMissing = analysis.filter(a => parseFloat(a.fillRate) < 50 && a.nullOrEmpty > 0).sort((a, b) => parseFloat(a.fillRate) - parseFloat(b.fillRate));
  // Always filled
  const alwaysFilled = analysis.filter(a => a.nullOrEmpty === 0);
  // Sometimes missing
  const sometimesEmpty = analysis.filter(a => a.nullOrEmpty > 0 && a.nullOrEmpty < TIMES);

  // Ingredient missing rates for bar chart
  const ingredientBars = [];
  for (let i = 1; i <= 15; i++) {
    const field = `strIngredient${i}`;
    const a = analysis.find(x => x.field === field);
    if (a) ingredientBars.push({ label: field, rate: parseFloat(a.fillRate), missing: a.nullOrEmpty });
  }
  const measureBars = [];
  for (let i = 1; i <= 15; i++) {
    const field = `strMeasure${i}`;
    const a = analysis.find(x => x.field === field);
    if (a) measureBars.push({ label: field, rate: parseFloat(a.fillRate), missing: a.nullOrEmpty });
  }

  // Helper
  const tagColor = (rate) => {
    if (rate >= 80) return 'tag-green';
    if (rate >= 50) return 'tag-yellow';
    if (rate >= 20) return 'tag-orange';
    return 'tag-red';
  };
  const barColor = (rate) => {
    if (rate >= 80) return 'green';
    if (rate >= 50) return 'yellow';
    if (rate >= 20) return 'orange';
    return 'red';
  };

  // ========== Generate HTML ==========
  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TheCocktailDB Random API 分析报告（100 次采样）</title>
<style>
  :root {
    --bg: #0f172a; --card: #1e293b; --border: #334155; --text: #e2e8f0;
    --muted: #94a3b8; --accent: #38bdf8; --green: #4ade80; --yellow: #fbbf24;
    --red: #f87171; --orange: #fb923c; --purple: #a78bfa; --pink: #f472b6;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'SF Mono','Cascadia Code','Fira Code','JetBrains Mono',monospace; background:var(--bg); color:var(--text); line-height:1.6; padding:2rem; min-height:100vh; }
  .container { max-width:1200px; margin:0 auto; }
  h1 { font-size:1.8rem; font-weight:700; margin-bottom:0.5rem; background:linear-gradient(135deg,var(--orange),var(--pink)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  .subtitle { color:var(--muted); font-size:0.9rem; margin-bottom:2.5rem; padding-bottom:1.5rem; border-bottom:1px solid var(--border); }
  .subtitle code { background:var(--card); padding:2px 8px; border-radius:4px; color:var(--accent); font-size:0.85rem; }
  h2 { font-size:1.2rem; font-weight:600; margin:2.5rem 0 1rem; display:flex; align-items:center; gap:0.5rem; }
  h2 .icon { font-size:1.3rem; }
  h3 { font-size:1rem; font-weight:600; margin:1.5rem 0 0.75rem; color:var(--muted); }
  .stats-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:1rem; margin-bottom:2rem; }
  .stat-card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:1.25rem; text-align:center; }
  .stat-card .value { font-size:1.8rem; font-weight:700; line-height:1.2; }
  .stat-card .label { font-size:0.78rem; color:var(--muted); margin-top:0.25rem; }
  .stat-card.blue .value { color:var(--accent); }
  .stat-card.green .value { color:var(--green); }
  .stat-card.yellow .value { color:var(--yellow); }
  .stat-card.red .value { color:var(--red); }
  .stat-card.purple .value { color:var(--purple); }
  .stat-card.orange .value { color:var(--orange); }
  .stat-card.pink .value { color:var(--pink); }
  .table-wrap { background:var(--card); border:1px solid var(--border); border-radius:10px; overflow:hidden; margin-bottom:1.5rem; }
  table { width:100%; border-collapse:collapse; font-size:0.85rem; }
  thead th { background:rgba(56,189,248,0.08); text-align:left; padding:0.75rem 1rem; font-weight:600; color:var(--accent); border-bottom:1px solid var(--border); white-space:nowrap; }
  tbody td { padding:0.6rem 1rem; border-bottom:1px solid rgba(51,65,85,0.5); vertical-align:top; }
  tbody tr:last-child td { border-bottom:none; }
  tbody tr:hover { background:rgba(56,189,248,0.04); }
  .tag { display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:600; white-space:nowrap; }
  .tag-red { background:rgba(248,113,113,0.15); color:var(--red); }
  .tag-orange { background:rgba(251,146,60,0.15); color:var(--orange); }
  .tag-yellow { background:rgba(251,191,36,0.15); color:var(--yellow); }
  .tag-green { background:rgba(74,222,128,0.15); color:var(--green); }
  .tag-blue { background:rgba(56,189,248,0.15); color:var(--accent); }
  .tag-purple { background:rgba(167,139,250,0.15); color:var(--purple); }
  .mono { font-family:inherit; font-size:0.82rem; color:var(--accent); }
  .bar-row { display:flex; align-items:center; gap:0.75rem; margin-bottom:0.5rem; font-size:0.82rem; }
  .bar-label { width:170px; text-align:right; color:var(--muted); flex-shrink:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .bar-track { flex:1; height:22px; background:rgba(51,65,85,0.4); border-radius:4px; overflow:hidden; }
  .bar-fill { height:100%; border-radius:4px; transition:width 0.6s ease; min-width:2px; }
  .bar-fill.blue { background:linear-gradient(90deg,var(--accent),#818cf8); }
  .bar-fill.green { background:linear-gradient(90deg,var(--green),#34d399); }
  .bar-fill.yellow { background:linear-gradient(90deg,var(--yellow),#f59e0b); }
  .bar-fill.red { background:linear-gradient(90deg,var(--red),#ef4444); }
  .bar-fill.purple { background:linear-gradient(90deg,var(--purple),#c084fc); }
  .bar-fill.pink { background:linear-gradient(90deg,var(--pink),#f9a8d4); }
  .bar-fill.orange { background:linear-gradient(90deg,var(--orange),#fdba74); }
  .bar-value { width:55px; text-align:right; font-weight:600; flex-shrink:0; }
  .alert { background:var(--card); border:1px solid var(--border); border-left:4px solid var(--yellow); border-radius:0 10px 10px 0; padding:1rem 1.25rem; margin-bottom:1rem; font-size:0.85rem; }
  .alert.red { border-left-color:var(--red); }
  .alert.green { border-left-color:var(--green); }
  .alert.blue { border-left-color:var(--accent); }
  .alert.orange { border-left-color:var(--orange); }
  .alert strong { color:var(--yellow); }
  .alert.red strong { color:var(--red); }
  .alert.green strong { color:var(--green); }
  .alert.blue strong { color:var(--accent); }
  .alert.orange strong { color:var(--orange); }
  .code-block { background:#0c1222; border:1px solid var(--border); border-radius:8px; padding:1rem 1.25rem; font-size:0.82rem; line-height:1.7; overflow-x:auto; margin-bottom:1.5rem; color:var(--muted); }
  .code-block .kw { color:var(--purple); }
  .code-block .fn { color:var(--accent); }
  .code-block .str { color:var(--green); }
  .code-block .cm { color:#64748b; }
  .code-block .num { color:var(--orange); }
  .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:1.5rem; }
  @media (max-width:700px) { .grid-2 { grid-template-columns:1fr; } .bar-label { width:120px; font-size:0.75rem; } }
  .footer { margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--border); text-align:center; color:var(--muted); font-size:0.78rem; }
</style>
</head>
<body>
<div class="container">

  <h1>🍹 TheCocktailDB Random API 分析报告</h1>
  <p class="subtitle">
    接口: <code>https://www.thecocktaildb.com/api/json/v1/1/random.php</code> &nbsp;|&nbsp;
    采样: <code>${TIMES} 次</code> &nbsp;|&nbsp;
    日期: ${new Date().toISOString().split('T')[0]}
  </p>

  <div class="stats-row">
    <div class="stat-card blue"><div class="value">${fields.length}</div><div class="label">总字段数</div></div>
    <div class="stat-card green"><div class="value">${alwaysFilled.length}</div><div class="label">从未缺失</div></div>
    <div class="stat-card yellow"><div class="value">${sometimesEmpty.length}</div><div class="label">有时缺失</div></div>
    <div class="stat-card red"><div class="value">${alwaysEmpty.length}</div><div class="label">永远缺失</div></div>
    <div class="stat-card purple"><div class="value">${ids.size}/${TIMES}</div><div class="label">唯一 ID 数</div></div>
  </div>

  <!-- 永远缺失 -->
  <h2><span class="icon">💀</span> 永远缺失的字段（100% 为空）</h2>
  <div class="table-wrap">
    <table>
      <thead><tr><th>字段</th><th>缺失类型</th><th>中文说明</th></tr></thead>
      <tbody>
${alwaysEmpty.map(a => `        <tr><td class="mono">${a.field}</td><td><span class="tag tag-red">${a.nullCount > 0 ? 'null' : '""'}</span></td><td>${a.desc}</td></tr>`).join('\n')}
      </tbody>
    </table>
  </div>

  <!-- 高频缺失 -->
  <h2><span class="icon">📉</span> 高频缺失字段（填充率 < 50%）</h2>
  <div class="table-wrap">
    <table>
      <thead><tr><th>字段</th><th>缺失率</th><th>缺失形式</th><th>中文说明</th></tr></thead>
      <tbody>
${highFreqMissing.map(a => {
  const missingRate = (100 - parseFloat(a.fillRate)).toFixed(1);
  const missingForm = a.nullCount > 0 && a.emptyCount > 0 ? 'null + 空字符串混合' : a.nullCount > 0 ? 'null' : '空字符串';
  return `        <tr><td class="mono">${a.field}</td><td><span class="tag ${tagColor(parseFloat(a.fillRate))}">${missingRate}%</span></td><td>${missingForm}</td><td>${a.desc}</td></tr>`;
}).join('\n')}
      </tbody>
    </table>
  </div>

  <!-- 配料缺失率可视化 -->
  <h2><span class="icon">📊</span> strIngredient 缺失率分布（${TIMES} 次采样）</h2>
  <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1.25rem;margin-bottom:1.5rem;">
${ingredientBars.map(b => `    <div class="bar-row"><div class="bar-label">${b.label}</div><div class="bar-track"><div class="bar-fill ${barColor(b.rate)}" style="width:${b.rate}%"></div></div><div class="bar-value" style="color:var(--${barColor(b.rate)})">${(100 - b.rate).toFixed(0)}%</div></div>`).join('\n')}
  </div>

  <h2><span class="icon">📊</span> strMeasure 缺失率分布（${TIMES} 次采样）</h2>
  <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1.25rem;margin-bottom:1.5rem;">
${measureBars.map(b => `    <div class="bar-row"><div class="bar-label">${b.label}</div><div class="bar-track"><div class="bar-fill ${barColor(b.rate)}" style="width:${b.rate}%"></div></div><div class="bar-value" style="color:var(--${barColor(b.rate)})">${(100 - b.rate).toFixed(0)}%</div></div>`).join('\n')}
  </div>

  <!-- 分类 & 枚举分布 -->
  <h2><span class="icon">🗺️</span> 分类 & 枚举字段分布</h2>
  <div class="grid-2">
    <div>
      <h3>strCategory（饮品分类）</h3>
      <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem;">
${(categoryField.enumValues || []).map(([val, cnt], i) => {
  const max = categoryField.enumValues[0][1];
  const pct = (cnt / max * 100).toFixed(0);
  const colors = ['purple','yellow','red','green','blue','pink','orange'];
  return `        <div class="bar-row"><div class="bar-label">${val}</div><div class="bar-track"><div class="bar-fill ${colors[i % colors.length]}" style="width:${pct}%"></div></div><div class="bar-value">${cnt}</div></div>`;
}).join('\n')}
      </div>
    </div>
    <div>
      <h3>strAlcoholic（酒精类型）</h3>
      <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem;">
${(alcoholicField.enumValues || []).map(([val, cnt], i) => {
  const max = alcoholicField.enumValues[0][1];
  const pct = (cnt / max * 100).toFixed(0);
  const colors = ['green','blue','purple','orange'];
  return `        <div class="bar-row"><div class="bar-label">${val}</div><div class="bar-track"><div class="bar-fill ${colors[i % colors.length]}" style="width:${pct}%"></div></div><div class="bar-value">${cnt}</div></div>`;
}).join('\n')}
      </div>
    </div>
  </div>

  <div class="grid-2">
    <div>
      <h3>strGlass（推荐杯型）</h3>
      <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem;">
${(glassField.enumValues || []).slice(0, 12).map(([val, cnt], i) => {
  const max = glassField.enumValues[0][1];
  const pct = (cnt / max * 100).toFixed(0);
  const colors = ['blue','purple','green','yellow','pink','orange','red'];
  return `        <div class="bar-row"><div class="bar-label">${val}</div><div class="bar-track"><div class="bar-fill ${colors[i % colors.length]}" style="width:${pct}%"></div></div><div class="bar-value">${cnt}</div></div>`;
}).join('\n')}
${glassField.enumValues && glassField.enumValues.length > 12 ? `        <div style="color:var(--muted);font-size:0.8rem;padding:0.5rem 0;">... 还有 ${glassField.enumValues.length - 12} 种杯型` : ''}
      </div>
    </div>
    <div>
      <h3>strIBA（IBA 官方分类）</h3>
      <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem;">
${(ibaField.enumValues || []).map(([val, cnt], i) => {
  const max = ibaField.enumValues[0][1];
  const pct = (cnt / max * 100).toFixed(0);
  const colors = ['orange','purple','blue','green','yellow','pink','red'];
  return `        <div class="bar-row"><div class="bar-label">${val}</div><div class="bar-track"><div class="bar-fill ${colors[i % colors.length]}" style="width:${pct}%"></div></div><div class="bar-value">${cnt}</div></div>`;
}).join('\n')}
${ibaField.nullOrEmpty > 0 ? `        <div class="alert orange" style="margin-top:0.5rem;font-size:0.8rem;"><strong>⚠️ ${ibaField.nullOrEmpty}/${TIMES} 条为空</strong> — 非所有饮品都有 IBA 分类</div>` : ''}
      </div>
    </div>
  </div>

  <h3>strTags 高频标签 Top 15</h3>
  <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem;margin-bottom:1.5rem;">
${topTags.map(([tag, cnt], i) => {
  const max = topTags[0][1];
  const pct = (cnt / max * 100).toFixed(0);
  const colors = ['pink','purple','blue','green','yellow','orange','red'];
  return `    <div class="bar-row"><div class="bar-label">${tag}</div><div class="bar-track"><div class="bar-fill ${colors[i % colors.length]}" style="width:${pct}%"></div></div><div class="bar-value">${cnt}</div></div>`;
}).join('\n')}
${analysis.find(a => a.field === 'strTags').nullOrEmpty > 0 ? `    <div class="alert orange" style="margin-top:0.5rem;font-size:0.8rem;"><strong>⚠️ ${analysis.find(a => a.field === 'strTags').nullOrEmpty}/${TIMES} 条无标签（null）</strong></div>` : ''}
  </div>

  <!-- 特别注意 -->
  <h2><span class="icon">⚠️</span> 特别值得注意的问题</h2>

  <div class="alert red">
    <strong>1. 空值类型不一致</strong><br>
    <code>strIngredient</code> / <code>strMeasure</code> 的空值有时是 JSON <code>null</code>，有时是空字符串 <code>""</code>，两种形式随机出现。前端判空必须同时处理：
  </div>
  <div class="code-block">
<span class="kw">const</span> <span class="fn">isEmpty</span> = (v) =&gt; !v || v.<span class="fn">trim</span>() === <span class="str">""</span> || v === <span class="str">"null"</span>;
</div>

  <div class="alert">
    <strong>2. strInstructions 含换行符</strong><br>
    ${instrWithNewline}/${TIMES} 条记录含 <code>\\n</code>。步骤格式不统一，需注意渲染处理。
  </div>

  <div class="alert">
    <strong>3. strMeasure 值带前后空格</strong><br>
    ${measureTrimIssues} 处用量值带多余空格（如 <code>" 2 oz "</code>），需 <code>trim()</code>。
  </div>

  <div class="alert">
    <strong>4. strTags 格式不规范</strong><br>
    逗号分隔：<code>"IBA,OrdinaryDrink"</code>、<code>"Shot,Vodka"</code>，大小写混用，${analysis.find(a => a.field === 'strTags').nullOrEmpty}% 缺失。
  </div>

  ${duplicateCount > 0 ? `<div class="alert red">
    <strong>5. idDrink 会出现重复（真随机）</strong><br>
    ${TIMES} 次调用出现 ${duplicateCount} 个重复 ID，唯一 ID ${ids.size} 个。<strong>接口是真随机，不保证不重复。</strong>
  </div>` : `<div class="alert green">
    <strong>5. idDrink 无重复</strong><br>
    本次 ${TIMES} 次调用全部返回不同 ID（共 ${ids.size} 个唯一值）。
  </div>`}

  <div class="alert blue">
    <strong>6. strIBA 经常为空</strong><br>
    并非所有饮品都有 IBA（国际调酒师协会）分类，${ibaField.nullOrEmpty}/${TIMES} 条为空。只有经典鸡尾酒才有 IBA 归类。
  </div>

  <div class="alert blue">
    <strong>7. 多语言制作说明覆盖率低</strong><br>
    英文 strInstructions 始终有值，但 ES/DE/FR/IT/ZH-HANS/ZH-HANT 六种语言版本经常为空，不可依赖。
  </div>

  <!-- 从未缺失 -->
  <h2><span class="icon">✅</span> 从未缺失的字段（${alwaysFilled.length} 个核心字段）</h2>
  <div class="table-wrap">
    <table>
      <thead><tr><th>字段</th><th>类型</th><th>中文说明</th></tr></thead>
      <tbody>
${alwaysFilled.map(a => `        <tr><td class="mono">${a.field}</td><td><span class="tag tag-green">string</span></td><td>${a.desc}</td></tr>`).join('\n')}
      </tbody>
    </table>
  </div>

  <!-- 全字段参考 -->
  <h2><span class="icon">📖</span> 全字段中文参考（${fields.length} 个字段）</h2>

  <h3>基础信息</h3>
  <div class="table-wrap">
    <table>
      <thead><tr><th>字段</th><th>类型</th><th>中文说明</th><th>示例值</th></tr></thead>
      <tbody>
${analysis.filter(a => ['idDrink','strDrink','strDrinkAlternate','strCategory','strIBA','strAlcoholic','strGlass','strTags'].includes(a.field)).map(a => {
  const typeTag = a.nullOrEmpty === TIMES ? 'tag-red' : a.nullOrEmpty === 0 ? 'tag-green' : 'tag-yellow';
  const typeText = a.nullOrEmpty === TIMES ? 'null' : a.nullOrEmpty === 0 ? 'string' : 'string|null';
  const sample = a.samples[0] || 'null';
  const sampleStr = typeof sample === 'string' && sample.length > 60 ? sample.substring(0,57) + '...' : sample;
  return `        <tr><td class="mono">${a.field}</td><td><span class="tag ${typeTag}">${typeText}</span></td><td>${a.desc}</td><td class="mono">${JSON.stringify(sampleStr)}</td></tr>`;
}).join('\n')}
      </tbody>
    </table>
  </div>

  <h3>媒体链接</h3>
  <div class="table-wrap">
    <table>
      <thead><tr><th>字段</th><th>类型</th><th>中文说明</th><th>示例值</th></tr></thead>
      <tbody>
${analysis.filter(a => ['strDrinkThumb','strImageSource','strImageAttribution','strVideo'].includes(a.field)).map(a => {
  const typeTag = a.nullOrEmpty === TIMES ? 'tag-red' : a.nullOrEmpty === 0 ? 'tag-green' : 'tag-yellow';
  const typeText = a.nullOrEmpty === TIMES ? 'null' : a.nullOrEmpty === 0 ? 'string' : 'string|null';
  const sample = a.samples[0] || 'null';
  const sampleStr = typeof sample === 'string' && sample.length > 60 ? sample.substring(0,57) + '...' : sample;
  return `        <tr><td class="mono">${a.field}</td><td><span class="tag ${typeTag}">${typeText}</span></td><td>${a.desc}</td><td class="mono">${JSON.stringify(sampleStr)}</td></tr>`;
}).join('\n')}
      </tbody>
    </table>
  </div>

  <h3>制作说明（多语言）</h3>
  <div class="table-wrap">
    <table>
      <thead><tr><th>字段</th><th>缺失率</th><th>中文说明</th></tr></thead>
      <tbody>
${analysis.filter(a => a.field.startsWith('strInstructions')).map(a => {
  const missingRate = (100 - parseFloat(a.fillRate)).toFixed(1);
  return `        <tr><td class="mono">${a.field}</td><td><span class="tag ${tagColor(parseFloat(a.fillRate))}">${missingRate}% 缺失</span></td><td>${a.desc}</td></tr>`;
}).join('\n')}
      </tbody>
    </table>
  </div>

  <h3>配料 & 用量（strIngredient1~15 + strMeasure1~15）</h3>
  <div class="table-wrap">
    <table>
      <thead><tr><th>字段</th><th>缺失率</th><th>中文说明</th></tr></thead>
      <tbody>
${analysis.filter(a => a.field.startsWith('strIngredient') || a.field.startsWith('strMeasure')).map(a => {
  const missingRate = (100 - parseFloat(a.fillRate)).toFixed(1);
  return `        <tr><td class="mono">${a.field}</td><td><span class="tag ${tagColor(parseFloat(a.fillRate))}">${missingRate}% 缺失</span></td><td>${a.desc}</td></tr>`;
}).join('\n')}
      </tbody>
    </table>
  </div>

  <div class="alert blue">
    <strong>💡 配料/用量命名规律：</strong><code>strIngredient</code> 和 <code>strMeasure</code> 是 1~15 编号配对。前端遍历用 <code>drink["strIngredient" + i]</code> 取值。<br>
    空值可能是 <code>null</code> 或 <code>""</code>，建议统一用 <code>!v || v.trim() === ""</code> 判空。
  </div>

  <h3>元数据</h3>
  <div class="table-wrap">
    <table>
      <thead><tr><th>字段</th><th>类型</th><th>中文说明</th><th>示例值</th></tr></thead>
      <tbody>
${analysis.filter(a => ['dateModified','strCreativeCommonsConfirmed'].includes(a.field)).map(a => {
  const typeTag = a.nullOrEmpty === TIMES ? 'tag-red' : a.nullOrEmpty === 0 ? 'tag-green' : 'tag-yellow';
  const typeText = a.nullOrEmpty === TIMES ? 'null' : a.nullOrEmpty === 0 ? 'string' : 'string|null';
  const sample = a.samples[0] || 'null';
  return `        <tr><td class="mono">${a.field}</td><td><span class="tag ${typeTag}">${typeText}</span></td><td>${a.desc}</td><td class="mono">${JSON.stringify(sample)}</td></tr>`;
}).join('\n')}
      </tbody>
    </table>
  </div>

  <!-- 最佳实践 -->
  <h2><span class="icon">🛠️</span> 前端最佳实践代码</h2>
  <div class="code-block">
<span class="cm">// 安全判空 — 同时处理 null / "" / " "</span>
<span class="kw">const</span> <span class="fn">isEmpty</span> = (v) =&gt; !v || v.<span class="fn">trim</span>() === <span class="str">""</span> || v === <span class="str">"null"</span>;

<span class="cm">// 提取有效配料列表</span>
<span class="kw">const</span> <span class="fn">getIngredients</span> = (drink) =&gt; {
  <span class="kw">const</span> items = [];
  <span class="kw">for</span> (<span class="kw">let</span> i = <span class="num">1</span>; i &lt;= <span class="num">15</span>; i++) {
    <span class="kw">const</span> name = drink[<span class="str">\`strIngredient\${i}\`</span>];
    <span class="kw">const</span> amount = drink[<span class="str">\`strMeasure\${i}\`</span>];
    <span class="kw">if</span> (!<span class="fn">isEmpty</span>(name)) {
      items.<span class="fn">push</span>({
        name: name.<span class="fn">trim</span>(),
        measure: <span class="fn">isEmpty</span>(amount) ? <span class="str">""</span> : amount.<span class="fn">trim</span>(),
      });
    }
  }
  <span class="kw">return</span> items;
};

<span class="cm">// 安全获取标签</span>
<span class="kw">const</span> <span class="fn">getTags</span> = (drink) =&gt; {
  <span class="kw">if</span> (<span class="fn">isEmpty</span>(drink.strTags)) <span class="kw">return</span> [];
  <span class="kw">return</span> drink.strTags.<span class="fn">split</span>(<span class="str">","</span>).<span class="fn">map</span>(t =&gt; t.<span class="fn">trim</span>()).<span class="fn">filter</span>(Boolean);
};

<span class="cm">// 获取酒精类型</span>
<span class="kw">const</span> <span class="fn">isAlcoholic</span> = (drink) =&gt; drink.strAlcoholic === <span class="str">"Alcoholic"</span>;

<span class="cm">// 去重：接口是真随机，可能返回重复 ID</span>
<span class="kw">const</span> seen = <span class="kw">new</span> <span class="fn">Set</span>();
<span class="kw">if</span> (seen.<span class="fn">has</span>(drink.idDrink)) {
  console.<span class="fn">warn</span>(<span class="str">\`重复饮品: \${drink.strDrink}\`</span>);
}
seen.<span class="fn">add</span>(drink.idDrink);
</div>

  <div class="footer">
    Generated ${new Date().toISOString()} &nbsp;·&nbsp; TheCocktailDB Random API &nbsp;·&nbsp; ${TIMES} samples
  </div>

</div>
</body>
</html>`;

  fs.writeFileSync('/Users/zhoo/.openclaw/workspace/_temp/cocktail-api-analysis.html', html);

  // ========== Generate Markdown ==========
  const alwaysFilledMd = analysis.filter(a => a.nullOrEmpty === 0);
  const sometimesEmptyMd = analysis.filter(a => a.nullOrEmpty > 0 && a.nullOrEmpty < TIMES);
  const alwaysEmptyMd = analysis.filter(a => a.nullOrEmpty === TIMES);
  const highFreqMd = analysis.filter(a => parseFloat(a.fillRate) < 50 && a.nullOrEmpty > 0).sort((a, b) => parseFloat(a.fillRate) - parseFloat(b.fillRate));

  const md = `# 🍹 TheCocktailDB Random API 分析报告

> **接口**: \`https://www.thecocktaildb.com/api/json/v1/1/random.php\`
> **采样**: ${TIMES} 次
> **唯一 ID**: ${ids.size} 个${duplicateCount > 0 ? `（${duplicateCount} 个重复）` : ''}
> **日期**: ${new Date().toISOString().split('T')[0]}

---

## 📊 概览

| 指标 | 数值 |
|------|------|
| 总字段数 | **${fields.length}** |
| 从未缺失 | **${alwaysFilledMd.length}** |
| 有时缺失 | **${sometimesEmptyMd.length}** |
| 永远缺失 | **${alwaysEmptyMd.length}** |
| 唯一 ID 数 | **${ids.size}/${TIMES}** |

---

## 💀 永远缺失的字段（100% 为空）

| 字段 | 缺失类型 | 中文说明 |
|------|----------|----------|
${alwaysEmptyMd.map(a => `| \`${a.field}\` | ${a.nullCount > 0 ? 'null' : '""'} | ${a.desc} |`).join('\n')}

---

## 📉 高频缺失字段（填充率 < 50%）

| 字段 | 缺失率 | 缺失形式 | 中文说明 |
|------|--------|----------|----------|
${highFreqMd.map(a => {
  const missingRate = (100 - parseFloat(a.fillRate)).toFixed(1);
  const form = a.nullCount > 0 && a.emptyCount > 0 ? 'null + "" 混合' : a.nullCount > 0 ? 'null' : '""';
  return `| \`${a.field}\` | ${missingRate}% | ${form} | ${a.desc} |`;
}).join('\n')}

---

## 📊 strIngredient 缺失率分布

| 字段 | 填充率 | 缺失率 |
|------|--------|--------|
${ingredientBars.map(b => `| \`${b.label}\` | ${b.rate.toFixed(1)}% | ${(100 - b.rate).toFixed(1)}% |`).join('\n')}

## 📊 strMeasure 缺失率分布

| 字段 | 填充率 | 缺失率 |
|------|--------|--------|
${measureBars.map(b => `| \`${b.label}\` | ${b.rate.toFixed(1)}% | ${(100 - b.rate).toFixed(1)}% |`).join('\n')}

---

## 🗺️ 分类 & 枚举分布

### strCategory（饮品分类）

| 分类 | 次数 |
|------|------|
${(categoryField.enumValues || []).map(([val, cnt]) => `| ${val} | ${cnt} |`).join('\n')}

### strAlcoholic（酒精类型）

| 类型 | 次数 |
|------|------|
${(alcoholicField.enumValues || []).map(([val, cnt]) => `| ${val} | ${cnt} |`).join('\n')}

### strGlass（推荐杯型 Top 12）

| 杯型 | 次数 |
|------|------|
${(glassField.enumValues || []).slice(0, 12).map(([val, cnt]) => `| ${val} | ${cnt} |`).join('\n')}

### strIBA（IBA 官方分类）

| 分类 | 次数 |
|------|------|
${(ibaField.enumValues || []).map(([val, cnt]) => `| ${val} | ${cnt} |`).join('\n')}
${ibaField.nullOrEmpty > 0 ? `\n> ⚠️ ${ibaField.nullOrEmpty}/${TIMES} 条为空 — 非所有饮品都有 IBA 分类\n` : ''}

### strTags 高频标签 Top 15

| 标签 | 次数 |
|------|------|
${topTags.map(([tag, cnt]) => `| ${tag} | ${cnt} |`).join('\n')}
${analysis.find(a => a.field === 'strTags').nullOrEmpty > 0 ? `\n> ⚠️ ${analysis.find(a => a.field === 'strTags').nullOrEmpty}/${TIMES} 条无标签（null）\n` : ''}

---

## ⚠️ 特别值得注意的问题

### 1. 空值类型不一致
\`strIngredient\` / \`strMeasure\` 的空值有时是 JSON \`null\`，有时是空字符串 \`""\`，两种形式随机出现。前端判空必须同时处理：

\`\`\`javascript
const isEmpty = (v) => !v || v.trim() === "" || v === "null";
\`\`\`

### 2. strInstructions 含换行符
${instrWithNewline}/${TIMES} 条记录含 \`\\n\`。步骤格式不统一，需注意渲染处理。

### 3. strMeasure 值带前后空格
${measureTrimIssues} 处用量值带多余空格（如 \`" 2 oz "\`），需 \`trim()\`。

### 4. strTags 格式不规范
逗号分隔，大小写混用，${analysis.find(a => a.field === 'strTags').nullOrEmpty}% 缺失。

${duplicateCount > 0 ? `### 5. idDrink 会出现重复（真随机）\n${TIMES} 次调用出现 ${duplicateCount} 个重复 ID，唯一 ID ${ids.size} 个。接口是真随机，不保证不重复。\n` : `### 5. idDrink 无重复\n本次 ${TIMES} 次调用全部返回不同 ID（共 ${ids.size} 个唯一值）。\n`}

### 6. strIBA 经常为空
并非所有饮品都有 IBA（国际调酒师协会）分类，${ibaField.nullOrEmpty}/${TIMES} 条为空。只有经典鸡尾酒才有 IBA 归类。

### 7. 多语言制作说明覆盖率低
英文 strInstructions 始终有值，但 ES/DE/FR/IT/ZH-HANS/ZH-HANT 六种语言版本经常为空，不可依赖。

---

## ✅ 从未缺失的字段（${alwaysFilledMd.length} 个核心字段）

| 字段 | 类型 | 中文说明 |
|------|------|----------|
${alwaysFilledMd.map(a => `| \`${a.field}\` | string | ${a.desc} |`).join('\n')}

---

## 📖 全字段中文参考（${fields.length} 个字段）

### 基础信息

| 字段 | 类型 | 中文说明 | 示例值 |
|------|------|----------|--------|
${analysis.filter(a => ['idDrink','strDrink','strDrinkAlternate','strCategory','strIBA','strAlcoholic','strGlass','strTags'].includes(a.field)).map(a => {
  const type = a.nullOrEmpty === TIMES ? 'null' : a.nullOrEmpty === 0 ? 'string' : 'string\\|null';
  const sample = a.samples[0] || 'null';
  const s = typeof sample === 'string' && sample.length > 40 ? sample.substring(0,37) + '...' : sample;
  return `| \`${a.field}\` | ${type} | ${a.desc} | \`${s}\` |`;
}).join('\n')}

### 媒体链接

| 字段 | 类型 | 中文说明 |
|------|------|----------|
${analysis.filter(a => ['strDrinkThumb','strImageSource','strImageAttribution','strVideo'].includes(a.field)).map(a => {
  const type = a.nullOrEmpty === TIMES ? 'null' : a.nullOrEmpty === 0 ? 'string' : 'string\\|null';
  return `| \`${a.field}\` | ${type} | ${a.desc} |`;
}).join('\n')}

### 制作说明（多语言）

| 字段 | 缺失率 | 中文说明 |
|------|--------|----------|
${analysis.filter(a => a.field.startsWith('strInstructions')).map(a => {
  const missingRate = (100 - parseFloat(a.fillRate)).toFixed(1);
  return `| \`${a.field}\` | ${missingRate}% | ${a.desc} |`;
}).join('\n')}

### 配料 & 用量

| 字段 | 缺失率 | 中文说明 |
|------|--------|----------|
${analysis.filter(a => a.field.startsWith('strIngredient') || a.field.startsWith('strMeasure')).map(a => {
  const missingRate = (100 - parseFloat(a.fillRate)).toFixed(1);
  return `| \`${a.field}\` | ${missingRate}% | ${a.desc} |`;
}).join('\n')}

### 元数据

| 字段 | 类型 | 中文说明 | 示例值 |
|------|------|----------|--------|
${analysis.filter(a => ['dateModified','strCreativeCommonsConfirmed'].includes(a.field)).map(a => {
  const type = a.nullOrEmpty === TIMES ? 'null' : a.nullOrEmpty === 0 ? 'string' : 'string\\|null';
  const sample = a.samples[0] || 'null';
  return `| \`${a.field}\` | ${type} | ${a.desc} | \`${sample}\` |`;
}).join('\n')}

---

## 🛠️ 前端最佳实践代码

\`\`\`javascript
// 安全判空 — 同时处理 null / "" / " "
const isEmpty = (v) => !v || v.trim() === "" || v === "null";

// 提取有效配料列表
const getIngredients = (drink) => {
  const items = [];
  for (let i = 1; i <= 15; i++) {
    const name = drink[\`strIngredient\${i}\`];
    const amount = drink[\`strMeasure\${i}\`];
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
  console.warn(\`重复饮品: \${drink.strDrink}\`);
}
seen.add(drink.idDrink);
\`\`\`

---

*Generated ${new Date().toISOString()} · TheCocktailDB Random API · ${TIMES} samples*
`;

  fs.writeFileSync('/Users/zhoo/.openclaw/workspace/_temp/cocktail-api-analysis.md', md);

  console.log(JSON.stringify({
    totalFields: fields.length,
    alwaysFilled: alwaysFilledMd.length,
    sometimesEmpty: sometimesEmptyMd.length,
    alwaysEmpty: alwaysEmptyMd.length,
    uniqueIds: ids.size,
    duplicates: duplicateCount
  }));
}

main().catch(e => { console.error(e); process.exit(1); });
