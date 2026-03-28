from fastapi.responses import HTMLResponse


def render_dashboard_html() -> HTMLResponse:
    html = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Aslan Energy Risk Dashboard</title>
  <style>
    :root {
      --bg: #f3efe5;
      --surface: rgba(255, 252, 245, 0.82);
      --ink: #182126;
      --muted: #5b676d;
      --line: rgba(24, 33, 38, 0.12);
      --accent: #0d6c63;
      --accent-soft: rgba(13, 108, 99, 0.14);
      --warning: #c26a1b;
      --danger: #ad3f34;
      --shadow: 0 20px 60px rgba(32, 44, 48, 0.08);
      --up: #0d6c63;
      --down: #ad3f34;
      --deep: #132a2e;
    }

    * { box-sizing: border-box; }
    body { margin: 0; font-family: "Segoe UI Variable Display", "Aptos", "Trebuchet MS", sans-serif; color: var(--ink); background: radial-gradient(circle at top left, rgba(13, 108, 99, 0.16), transparent 32%), radial-gradient(circle at top right, rgba(194, 106, 27, 0.18), transparent 28%), linear-gradient(180deg, #f7f1e5 0%, var(--bg) 55%, #ebe5d8 100%); min-height: 100vh; }
    button { font: inherit; cursor: pointer; border: none; background: none; }
    .shell { max-width: 1280px; margin: 0 auto; padding: 32px 20px 48px; }
    .hero { display: grid; grid-template-columns: 1.4fr 0.9fr; gap: 18px; margin-bottom: 18px; }
    .hero-panel, .panel, .metric-card { background: var(--surface); backdrop-filter: blur(12px); border: 1px solid var(--line); border-radius: 24px; box-shadow: var(--shadow); }
    .hero-panel { padding: 28px; min-height: 220px; position: relative; overflow: hidden; }
    .hero-panel::after { content: ""; position: absolute; inset: auto -40px -60px auto; width: 220px; height: 220px; background: radial-gradient(circle, rgba(13, 108, 99, 0.18), transparent 70%); border-radius: 50%; }
    .eyebrow { text-transform: uppercase; letter-spacing: 0.16em; font-size: 12px; color: var(--muted); margin-bottom: 10px; }
    h1, h2, h3 { margin: 0; font-family: Georgia, "Times New Roman", serif; font-weight: 600; }
    h1 { font-size: clamp(32px, 5vw, 56px); line-height: 0.96; max-width: 10ch; }
    .hero-copy { margin-top: 14px; max-width: 52ch; color: var(--muted); line-height: 1.6; font-size: 15px; }
    .hero-meta, .controls, .compare-grid, .legend { display: flex; flex-wrap: wrap; gap: 10px; }
    .hero-meta { margin-top: 20px; }
    .controls { margin-top: 18px; align-items: center; }
    .pill { border-radius: 999px; padding: 9px 14px; background: rgba(255,255,255,0.68); border: 1px solid var(--line); font-size: 12px; color: var(--muted); }
    .segment { display: inline-flex; padding: 4px; background: rgba(255,255,255,0.72); border: 1px solid var(--line); border-radius: 999px; }
    .segment button { padding: 9px 14px; border-radius: 999px; color: var(--muted); transition: background 180ms ease, color 180ms ease, transform 180ms ease; }
    .segment button.active { background: var(--accent); color: white; transform: translateY(-1px); }
    .action { padding: 10px 14px; border-radius: 999px; background: var(--ink); color: white; box-shadow: var(--shadow); }
    .action.secondary { background: rgba(255,255,255,0.76); color: var(--ink); border: 1px solid var(--line); box-shadow: none; }
    .status-board { display: grid; gap: 14px; padding: 20px; }
    .status-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 14px 16px; border-radius: 18px; background: rgba(255,255,255,0.56); border: 1px solid var(--line); }
    .status-label, .metric-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); }
    .status-value { font-size: 22px; font-weight: 600; }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }
    .metric-card { padding: 20px; min-height: 170px; display: flex; flex-direction: column; justify-content: space-between; grid-column: span 3; }
    .metric-value { font-size: clamp(28px, 4vw, 44px); font-weight: 650; line-height: 1; margin-top: 10px; }
    .metric-sub, .panel-copy, .small, .meta-note { color: var(--muted); font-size: 14px; line-height: 1.5; }
    .panel { padding: 22px; grid-column: span 6; }
    .panel.wide { grid-column: span 8; }
    .panel.narrow { grid-column: span 4; }
    .panel-head { display: flex; justify-content: space-between; align-items: end; gap: 12px; margin-bottom: 18px; }
    .chart { height: 220px; width: 100%; background: linear-gradient(180deg, rgba(255,255,255,0.65), rgba(255,255,255,0.25)); border: 1px solid var(--line); border-radius: 18px; padding: 16px; }
    .chart svg { width: 100%; height: 100%; overflow: visible; }
    .chart-note { margin-top: 10px; color: var(--muted); font-size: 12px; }
    .legend { margin-top: 14px; color: var(--muted); font-size: 13px; }
    .legend span { display: inline-flex; align-items: center; gap: 8px; }
    .legend i { width: 12px; height: 12px; border-radius: 999px; display: inline-block; }
    .feed, .driver-list, .table-stack, .evidence-stack, .action-list, .summary-grid { display: grid; gap: 12px; }
    .feed-item, .driver-item, .compare-card, .evidence-item, .detail-shell { padding: 14px 16px; border-radius: 16px; background: rgba(255,255,255,0.58); border: 1px solid var(--line); }
    .summary-band { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 18px; margin-bottom: 18px; }
    .summary-card { padding: 22px; border-radius: 24px; background: linear-gradient(180deg, rgba(19,42,46,0.96), rgba(31,54,59,0.96)); color: #eef5f5; border: 1px solid rgba(19,42,46,0.24); box-shadow: var(--shadow); }
    .summary-card .eyebrow, .summary-card .small, .summary-card .meta-note { color: rgba(238,245,245,0.72); }
    .summary-head { display: flex; justify-content: space-between; gap: 12px; align-items: start; }
    .summary-title { font-size: clamp(26px, 3vw, 38px); line-height: 1.04; max-width: 12ch; }
    .summary-copy { margin-top: 14px; color: rgba(238,245,245,0.9); line-height: 1.7; font-size: 15px; max-width: 60ch; }
    .summary-grid { margin-top: 18px; grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .summary-metric { padding: 14px; border-radius: 16px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.08); }
    .summary-metric-value { margin-top: 8px; font-size: 24px; font-weight: 650; }
    .summary-metric-copy { margin-top: 6px; color: rgba(238,245,245,0.72); font-size: 13px; line-height: 1.5; }
    .action-card { padding: 22px; border-radius: 24px; background: rgba(255,252,245,0.86); border: 1px solid var(--line); box-shadow: var(--shadow); }
    .action-item { padding: 14px 16px; border-radius: 16px; background: rgba(255,255,255,0.72); border: 1px solid var(--line); }
    .action-kicker { font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); }
    .action-title { margin-top: 6px; font-size: 18px; font-weight: 650; }
    .action-copy { margin-top: 6px; color: var(--muted); line-height: 1.6; font-size: 14px; }
    .change-strip { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }
    .change-card { padding: 16px; border-radius: 18px; background: rgba(255,255,255,0.6); border: 1px solid var(--line); }
    .change-main { margin-top: 8px; font-size: 28px; font-weight: 650; }
    .change-copy { margin-top: 6px; color: var(--muted); line-height: 1.5; font-size: 13px; }
    .feed-top { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 8px; align-items: center; }
    .badge { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 10px; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; background: var(--accent-soft); color: var(--accent); }
    .badge.medium { background: rgba(194, 106, 27, 0.12); color: var(--warning); }
    .badge.high { background: rgba(173, 63, 52, 0.12); color: var(--danger); }
    .mono { font-family: Consolas, "SFMono-Regular", monospace; }
    .compare-grid { margin-top: 18px; }
    .compare-card { min-width: 190px; }
    .compare-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); }
    .compare-main { font-size: 26px; font-weight: 650; margin-top: 8px; }
    .delta { margin-top: 10px; font-size: 13px; font-weight: 600; }
    .delta.up { color: var(--up); }
    .delta.down { color: var(--down); }
    .table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,0.46); }
    table { width: 100%; border-collapse: collapse; min-width: 520px; }
    th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--line); font-size: 14px; }
    th { color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; font-size: 11px; }
    tr:last-child td { border-bottom: none; }
    .evidence-item { display: flex; justify-content: space-between; gap: 10px; align-items: start; width: 100%; text-align: left; transition: border-color 160ms ease, background 160ms ease; overflow: hidden; }
    .evidence-item:hover { border-color: rgba(19,42,46,0.22); background: rgba(255,255,255,0.8); }
    .evidence-item.selected { border-color: rgba(13,108,99,0.45); background: rgba(13,108,99,0.10); }
    .evidence-meta { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .evidence-item > div:first-child { min-width: 0; }
    .evidence-item strong, .detail-value, .detail-summary, .summary-metric-value { overflow-wrap: anywhere; word-break: break-word; }
    .source-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
    .source-column { min-width: 0; padding: 0; background: transparent; border: none; box-shadow: none; }
    .source-column .feed-item, .source-column .detail-shell { height: 100%; }

    .detail-shell { background: linear-gradient(180deg, rgba(19,42,46,0.96), rgba(30,54,59,0.96)); color: #eef5f5; min-height: 100%; }
    .detail-shell .muted, .detail-shell .small, .detail-shell .evidence-meta { color: rgba(238,245,245,0.72); }
    .detail-summary { margin-top: 14px; color: rgba(238,245,245,0.92); line-height: 1.6; font-size: 14px; }
    .detail-grid { display: grid; gap: 10px; margin-top: 16px; }
    .detail-field { padding: 12px 14px; border-radius: 14px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.08); }
    .detail-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(238,245,245,0.6); margin-bottom: 6px; }
    .detail-value { font-size: 14px; line-height: 1.5; color: #eef5f5; }
    .detail-toggle { margin-top: 16px; padding: 10px 14px; border-radius: 999px; background: rgba(255,255,255,0.08); color: #eef5f5; border: 1px solid rgba(255,255,255,0.12); }
    .detail-pre { margin-top: 12px; padding: 14px; border-radius: 14px; background: rgba(255,255,255,0.06); overflow: auto; max-height: 360px; font-size: 12px; line-height: 1.6; }
    .loading { display: grid; place-items: center; min-height: 60vh; color: var(--muted); font-size: 15px; letter-spacing: 0.08em; text-transform: uppercase; }

    @media (max-width: 980px) {
      .hero { grid-template-columns: 1fr; }
      .summary-band, .summary-grid, .change-strip { grid-template-columns: 1fr; }
      .metric-card { grid-column: span 6; }
      .panel, .panel.wide, .panel.narrow { grid-column: span 12; }
      .source-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 640px) {
      .shell { padding: 18px 14px 32px; }
      .metric-card { grid-column: span 12; }
      .hero-panel { padding: 22px; }
      .status-row, .evidence-item { align-items: start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <div id=\"app\" class=\"loading\">Loading dashboard...</div>
  <script>
    const currency = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 });
    let selectedHorizon = 30;
    let latestRunMeta = { mode: 'persisted', timestamp: null };
    let selectedDetail = null;

    function metric(value) { return value == null ? 'n/a' : currency.format(value); }
    function isoDate(value) {
      if (!value) return 'n/a';
      return new Date(value).toLocaleString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }
    function riskBadge(level) {
      const normalized = String(level || '').toLowerCase();
      if (normalized === 'high') return 'badge high';
      if (normalized === 'medium' || normalized === 'watchlist') return 'badge medium';
      return 'badge';
    }
    function deltaClass(delta) { if (delta > 0) return 'delta up'; if (delta < 0) return 'delta down'; return 'delta'; }
    function deltaText(current, previous) {
      if (current == null || previous == null) return { text: 'No prior comparison', className: 'delta' };
      const delta = current - previous;
      const direction = delta > 0 ? 'up' : delta < 0 ? 'down' : 'flat';
      const prefix = delta > 0 ? '+' : '';
      return { text: `${prefix}${delta.toFixed(2)} vs previous (${direction})`, className: deltaClass(delta) };
    }
    function buildLinePath(values, width, height, padding) {
      if (!values.length) return '';
      const max = Math.max(...values);
      const min = Math.min(...values);
      const range = Math.max(max - min, 1);
      return values.map((value, index) => {
        const x = padding + ((width - padding * 2) * index / Math.max(values.length - 1, 1));
        const y = height - padding - ((value - min) / range) * (height - padding * 2);
        return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`;
      }).join(' ');
    }
    function areaPath(values, width, height, padding) {
      if (!values.length) return '';
      const line = buildLinePath(values, width, height, padding);
      const startX = padding;
      const endX = width - padding;
      const baseline = height - padding;
      return `${line} L ${endX} ${baseline} L ${startX} ${baseline} Z`;
    }
    function pointMarkup(values, width, height, padding, color) {
      if (!values.length) return '';
      const max = Math.max(...values);
      const min = Math.min(...values);
      const range = Math.max(max - min, 1);
      return values.map((value, index) => {
        const x = padding + ((width - padding * 2) * index / Math.max(values.length - 1, 1));
        const y = height - padding - ((value - min) / range) * (height - padding * 2);
        return `<circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="5.5" fill="${color}" stroke="rgba(255,255,255,0.9)" stroke-width="2"></circle>`;
      }).join('');
    }
    function chartMarkup(values, color) {
      const width = 620;
      const height = 220;
      const padding = 14;
      const safeValues = values.length ? values : [0];
      const pointCountText = safeValues.length === 1 ? '1 persisted point' : `${safeValues.length} persisted points`;
      return `
        <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
          <defs>
            <linearGradient id="fill-${color.replace('#','')}" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stop-color="${color}" stop-opacity="0.28"></stop>
              <stop offset="100%" stop-color="${color}" stop-opacity="0.02"></stop>
            </linearGradient>
          </defs>
          <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="rgba(24,33,38,0.16)" stroke-width="2"></line>
          <path d="${areaPath(safeValues, width, height, padding)}" fill="url(#fill-${color.replace('#','')})"></path>
          <path d="${buildLinePath(safeValues, width, height, padding)}" fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round"></path>
          ${pointMarkup(safeValues, width, height, padding, color)}
        </svg>
        <div class="chart-note">${pointCountText}</div>`;
    }
    function refreshStatusLine() {
      if (!latestRunMeta.timestamp) return 'Using persisted history';
      if (latestRunMeta.mode === 'full-refresh') return `Full refresh completed at ${isoDate(latestRunMeta.timestamp)}`;
      if (latestRunMeta.mode === 'live-refresh') return `Fresh run completed at ${isoDate(latestRunMeta.timestamp)}`;
      return `Viewing persisted artifacts as of ${isoDate(latestRunMeta.timestamp)}`;
    }
    function compactRows(rows, renderer, emptyMessage = 'No persisted rows yet.') {
      if (!rows.length) return `<div class="feed-item">${emptyMessage}</div>`;
      return rows.map(renderer).join('');
    }
    async function fetchJsonOrThrow(url, options) {
      const response = await fetch(url, options);
      const text = await response.text();
      let payload = null;
      try {
        payload = text ? JSON.parse(text) : null;
      } catch (error) {
        payload = text;
      }
      if (!response.ok) {
        const detail = typeof payload === 'string' ? payload : payload?.detail || JSON.stringify(payload);
        throw new Error(`${url} failed: ${detail}`);
      }
      return payload;
    }
    async function runMaterializationSuite(horizon) {
      await Promise.all([
        fetchJsonOrThrow(`/demand-forecast?horizon=${horizon}`),
        fetchJsonOrThrow(`/supply-forecast?horizon=${horizon}`),
        fetchJsonOrThrow(`/risk-score?horizon=${horizon}`),
        fetchJsonOrThrow(`/alerts?horizon=${horizon}`),
      ]);
    }
    async function runFullRefresh() {
      await fetchJsonOrThrow('/ingestion/ppac', { method: 'POST' });
      await fetchJsonOrThrow('/ingestion/eia', { method: 'POST' });
      await runMaterializationSuite(30);
      await runMaterializationSuite(60);
    }
    function ensureDefaultDetail(domestic, market) {
      if (selectedDetail) return;
      const first = domestic[0] ? { sourceType: 'domestic', id: domestic[0].id } : market[0] ? { sourceType: 'market', id: market[0].id } : null;
      if (!first) return;
      selectedDetail = {
        id: first.id,
        sourceType: first.sourceType,
        loading: true,
        metric_name: 'Loading source detail...',
        source_name: first.sourceType === 'domestic' ? 'PPAC' : 'EIA',
        observation_date: '',
        value: null,
        unit: '',
        source_record: { message: 'Loading raw source record...' },
      };
      loadObservationDetail(first.sourceType, first.id);
    }
    function renderEvidence(rows, sourceType) {
      if (!rows.length) return '<div class="feed-item">No source observations available yet.</div>';
      return rows.map(item => {
        const isSelected = selectedDetail && selectedDetail.id === item.id && selectedDetail.sourceType === sourceType;
        return `
          <button class=\"evidence-item ${isSelected ? 'selected' : ''}\" data-source-type=\"${sourceType}\" data-observation-id=\"${item.id}\">
            <div>
              <div><strong>${item.metric_name}</strong></div>
              <div class=\"evidence-meta\">${item.source_name} • ${item.observation_date}</div>
            </div>
            <div><strong>${metric(item.value)}</strong> <span class=\"muted\">${item.unit || ''}</span></div>
          </button>`;
      }).join('');
    }
    function titleCase(value) {
      return String(value || '')
        .replace(/[_-]+/g, ' ')
        .replace(/\\b\\w/g, char => char.toUpperCase());
    }
    function readableLabel(key) {
      const labels = {
        title: 'Source row',
        field: 'Period field',
        modified_date: 'Last modified',
        period: 'Period',
        product: 'Product code',
        'product-name': 'Product',
        process: 'Process code',
        'process-name': 'Process',
        series: 'Series code',
        'series-description': 'Series description',
        duoarea: 'Area code',
        'area-name': 'Area',
        units: 'Original units',
        value: 'Source value'
      };
      return labels[key] || titleCase(key);
    }
    function summarizeDetail(detail) {
      const source = detail.source_record || {};
      if (detail.source_name === 'PPAC') {
        const month = source.field ? titleCase(source.field) : 'the reported period';
        const modified = source.modified_date ? ` Last modified: ${source.modified_date}.` : '';
        return `${detail.source_name} reports ${titleCase(detail.metric_name)} at ${metric(detail.value)} ${detail.unit || ''} for ${month}.${modified}`.trim();
      }
      if (detail.source_name === 'EIA') {
        const product = source['product-name'] || titleCase(detail.metric_name);
        const period = source.period || detail.observation_date || 'the latest available date';
        const process = source['process-name'] ? ` via ${source['process-name']}` : '';
        return `${detail.source_name} reports ${product} at ${metric(detail.value)} ${detail.unit || ''} for ${period}${process}.`.trim();
      }
      return `${detail.source_name} reports ${titleCase(detail.metric_name)} at ${metric(detail.value)} ${detail.unit || ''}.`.trim();
    }
    function detailFieldsMarkup(detail) {
      const source = detail.source_record || {};
      const fields = [
        ['Source', detail.source_name],
        ['Observation date', detail.observation_date],
        ['Metric', titleCase(detail.metric_name)],
        ['Reported value', `${metric(detail.value)} ${detail.unit || ''}`.trim()],
      ];
      Object.entries(source).forEach(([key, value]) => {
        if (value == null || value === '') return;
        if (typeof value === 'object') return;
        fields.push([readableLabel(key), String(value)]);
      });
      return fields.map(([label, value]) => `
        <div class="detail-field">
          <div class="detail-label">${label}</div>
          <div class="detail-value">${value}</div>
        </div>`).join('');
    }
    function changeDescriptor(current, previous, label, formatter = metric) {
      if (current == null || previous == null) {
        return `No previous ${label.toLowerCase()} snapshot is available yet.`;
      }
      const delta = current - previous;
      if (delta === 0) {
        return `Current ${label.toLowerCase()} remains ${formatter(current)} versus the previous run.`;
      }
      const direction = delta > 0 ? 'up' : 'down';
      return `${label} moved ${direction} by ${formatter(Math.abs(delta))} versus the previous run.`;
    }
    function recommendationItems(latestRisk, latestDemand, latestSupply, latestAlert) {
      if (!latestRisk) {
        return [{
          title: 'Load source data first',
          copy: 'Run PPAC and EIA ingestion, then materialize the latest snapshot so the cockpit can produce a real outlook.',
          kicker: 'Setup',
        }];
      }
      const actions = [];
      if (latestRisk.risk_score >= 70) {
        actions.push({
          title: 'Escalate supply review now',
          copy: `Risk is ${latestRisk.risk_level}. Pull procurement, operations, and leadership into a same-day review of the next ${selectedHorizon} days.`,
          kicker: 'Immediate',
        });
      }
      if (latestRisk.supply_gap_score >= 20) {
        actions.push({
          title: 'Protect LPG availability',
          copy: `Demand is outrunning the LPG proxy by ${latestRisk.supply_gap_score.toFixed(2)} points. Review import cover, buffer stock, and alternate sourcing options.`,
          kicker: 'Supply gap',
        });
      }
      if (latestRisk.disruption_score >= 20) {
        actions.push({
          title: 'Monitor market stress daily',
          copy: 'Price pressure or inventory tightness is now materially contributing to the outlook. Tighten watch frequency on Brent, WTI, and inventory prints.',
          kicker: 'Market watch',
        });
      }
      if (latestAlert) {
        actions.push({
          title: 'Work the latest alert',
          copy: `${latestAlert.title}: ${latestAlert.message}`,
          kicker: 'Alert',
        });
      }
      if (latestSupply && latestDemand && actions.length < 3) {
        actions.push({
          title: 'Track the next scheduled run',
          copy: 'Use the next scheduler cycle as the operating checkpoint and compare whether demand, supply, and risk are converging or diverging.',
          kicker: 'Cadence',
        });
      }
      return actions.slice(0, 4);
    }
    function executiveSummary(latestRisk, latestDemand, latestSupply, latestAlert) {
      if (!latestRisk || !latestDemand || !latestSupply) {
        return {
          title: 'Decision support is not ready yet',
          copy: 'This cockpit needs at least one successful ingestion and one persisted snapshot before it can generate a usable outlook.',
        };
      }
      const pressure = latestRisk.risk_score >= 70 ? 'high' : latestRisk.risk_score >= 40 ? 'elevated' : 'contained';
      const alertSentence = latestAlert ? ` Latest alert: ${latestAlert.title}.` : '';
      return {
        title: `${selectedHorizon}-day outlook is ${pressure}`,
        copy: `Current risk is ${latestRisk.risk_score.toFixed(2)} at ${latestRisk.risk_level}. Demand is forecast at ${metric(latestDemand.predicted_lpg_demand)} while supply is running at ${metric(latestSupply.expected_crude_arrival_volume)}. The main operator question is whether price pressure and supply tightness are starting to outrun the recent import baseline.${alertSentence}`,
      };
    }
    function whatChangedCards(latestDemand, priorDemand, latestSupply, priorSupply, latestRisk, priorRisk) {
      return [
        {
          label: 'Demand',
          value: metric(latestDemand?.predicted_lpg_demand),
          note: changeDescriptor(latestDemand?.predicted_lpg_demand, priorDemand?.predicted_lpg_demand, 'Demand forecast'),
        },
        {
          label: 'Supply',
          value: metric(latestSupply?.expected_crude_arrival_volume),
          note: changeDescriptor(latestSupply?.expected_crude_arrival_volume, priorSupply?.expected_crude_arrival_volume, 'Supply forecast'),
        },
        {
          label: 'Risk',
          value: latestRisk ? latestRisk.risk_score.toFixed(2) : 'n/a',
          note: changeDescriptor(latestRisk?.risk_score, priorRisk?.risk_score, 'Risk score', value => Number(value).toFixed(2)),
        },
      ];
    }
    function detailMarkup() {
      if (!selectedDetail) {
        return '<div class="feed-item">No source record available yet.</div>';
      }
      const isRawOpen = Boolean(selectedDetail.showRaw);
      return `
        <div class="detail-shell">
          <div class="evidence-meta">Traceability</div>
          <h3 style="font-size:26px; margin-top:8px;">What This Input Says</h3>
          <div class="small">${selectedDetail.metric_name} • ${selectedDetail.source_name}</div>
          <div class="detail-summary">${summarizeDetail(selectedDetail)}</div>
          <div class="detail-grid">${detailFieldsMarkup(selectedDetail)}</div>
          <button class="detail-toggle" data-raw-toggle="true">${isRawOpen ? 'Hide raw payload' : 'Show raw payload'}</button>
          ${isRawOpen ? `<div class="detail-pre mono">${JSON.stringify(selectedDetail.source_record || {}, null, 2)}</div>` : ''}
        </div>`;
    }
    async function loadObservationDetail(sourceType, observationId) {
      const endpoint = sourceType === 'domestic' ? `/source/domestic-observations/${observationId}` : `/source/market-observations/${observationId}`;
      const response = await fetch(endpoint);
      const detail = await response.json();
      selectedDetail = { ...detail, sourceType };
      await loadDashboard(false);
    }
    function bindDashboardEvents() {
      document.querySelectorAll('[data-horizon]').forEach(button => {
        button.addEventListener('click', () => {
          selectedHorizon = Number(button.dataset.horizon);
          latestRunMeta = { mode: 'persisted', timestamp: null };
          selectedDetail = null;
          loadDashboard(true);
        });
      });
      document.getElementById('reload-history').addEventListener('click', async () => {
        latestRunMeta = { mode: 'persisted', timestamp: new Date().toISOString() };
        selectedDetail = null;
        await loadDashboard(true);
      });
      document.getElementById('run-refresh').addEventListener('click', async () => {
        const runButton = document.getElementById('run-refresh');
        runButton.disabled = true;
        runButton.textContent = 'Running...';
        try {
          await runMaterializationSuite(selectedHorizon);
          latestRunMeta = { mode: 'live-refresh', timestamp: new Date().toISOString() };
          selectedDetail = null;
          await loadDashboard(true);
        } catch (error) {
          window.alert(error.message || 'Latest snapshot failed.');
        } finally {
          runButton.disabled = false;
          runButton.textContent = 'Run latest snapshot';
        }
      });
      const refreshAllButton = document.getElementById('refresh-all');
      if (refreshAllButton) {
        refreshAllButton.addEventListener('click', async () => {
          refreshAllButton.disabled = true;
          refreshAllButton.textContent = 'Refreshing...';
          try {
            await runFullRefresh();
            latestRunMeta = { mode: 'full-refresh', timestamp: new Date().toISOString() };
            selectedDetail = null;
            await loadDashboard(true);
          } catch (error) {
            window.alert(error.message || 'Full refresh failed.');
          } finally {
            refreshAllButton.disabled = false;
            refreshAllButton.textContent = 'Refresh all data';
          }
        });
      }
      document.querySelectorAll('[data-observation-id]').forEach(button => {
        button.addEventListener('click', async () => {
          const sourceType = button.dataset.sourceType;
          const observationId = Number(button.dataset.observationId);
          selectedDetail = {
            id: observationId,
            sourceType,
            loading: true,
            metric_name: 'Loading source detail...',
            source_name: sourceType === 'domestic' ? 'PPAC' : 'EIA',
            observation_date: '',
            value: null,
            unit: '',
            source_record: { message: 'Loading raw source record...' },
          };
          await loadDashboard(false);
          await loadObservationDetail(sourceType, observationId);
        });
      });
      const rawToggle = document.querySelector('[data-raw-toggle]');
      if (rawToggle) {
        rawToggle.addEventListener('click', async () => {
          selectedDetail = { ...selectedDetail, showRaw: !selectedDetail.showRaw };
          await loadDashboard(false);
        });
      }
    }
    function render(data) {
      const demand = data.demand.items || [];
      const supply = data.supply.items || [];
      const risks = data.risk.items || [];
      const alerts = data.alerts.items || [];
      const domestic = data.domestic.items || [];
      const market = data.market.items || [];
      const scheduler = data.scheduler;
      ensureDefaultDetail(domestic, market);
      const latestDemand = demand[0];
      const priorDemand = demand[1];
      const latestSupply = supply[0];
      const priorSupply = supply[1];
      const latestRisk = risks[0];
      const priorRisk = risks[1];
      const latestAlert = alerts[0];
      if (!latestRunMeta.timestamp) latestRunMeta.timestamp = latestRisk?.as_of || latestAlert?.as_of || new Date().toISOString();
      const demandValues = [...demand].reverse().map(item => item.predicted_lpg_demand);
      const supplyValues = [...supply].reverse().map(item => item.expected_crude_arrival_volume);
      const riskValues = [...risks].reverse().map(item => item.risk_score);
      const demandDelta = deltaText(latestDemand?.predicted_lpg_demand, priorDemand?.predicted_lpg_demand);
      const supplyDelta = deltaText(latestSupply?.expected_crude_arrival_volume, priorSupply?.expected_crude_arrival_volume);
      const riskDelta = deltaText(latestRisk?.risk_score, priorRisk?.risk_score);
      const schedulerLabel = scheduler.enabled ? `${scheduler.last_status} • every ${scheduler.interval_seconds}s` : 'disabled';
      const summary = executiveSummary(latestRisk, latestDemand, latestSupply, latestAlert);
      const actions = recommendationItems(latestRisk, latestDemand, latestSupply, latestAlert);
      const changed = whatChangedCards(latestDemand, priorDemand, latestSupply, priorSupply, latestRisk, priorRisk);
      const app = document.getElementById('app');
      app.className = 'shell';
      app.innerHTML = `
        <section class=\"hero\">
          <div class=\"hero-panel\">
            <div class=\"eyebrow\">Aslan Technologies</div>
            <h1>Energy risk cockpit for India-focused supply stress.</h1>
            <div class=\"hero-copy\">This dashboard reads persisted forecast, risk, alert, and source-input artifacts from the API. It is designed as an operator view: latest state first, trend context second, with conclusions, drivers, and actions surfaced clearly.</div>
            <div class=\"controls\">
              <div class=\"segment\"><button class=\"${selectedHorizon === 30 ? 'active' : ''}\" data-horizon=\"30\">30 day</button><button class=\"${selectedHorizon === 60 ? 'active' : ''}\" data-horizon=\"60\">60 day</button></div>
              <button id=\"run-refresh\" class=\"action\">Run latest snapshot</button>
              <button id=\"refresh-all\" class=\"action secondary\">Refresh all data</button>
              <button id=\"reload-history\" class=\"action secondary\">Reload persisted history</button>
            </div>
            <div class=\"hero-meta\">
              <div class=\"pill\">PPAC + EIA backed</div>
              <div class=\"pill\">Live API source: <span class=\"mono\">/history/* + /source/*</span></div>
              <div class=\"pill\">Horizon: ${selectedHorizon} days</div>
              <div class=\"pill\">Scheduler: ${schedulerLabel}</div>
            </div>
            <div class=\"meta-note\">${refreshStatusLine()} • last scheduled finish: ${isoDate(scheduler.last_run_finished_at)}</div>
            <div class=\"compare-grid\">
              <div class=\"compare-card\"><div class=\"compare-label\">Demand delta</div><div class=\"compare-main\">${metric(latestDemand?.predicted_lpg_demand)}</div><div class=\"${demandDelta.className}\">${demandDelta.text}</div></div>
              <div class=\"compare-card\"><div class=\"compare-label\">Supply delta</div><div class=\"compare-main\">${metric(latestSupply?.expected_crude_arrival_volume)}</div><div class=\"${supplyDelta.className}\">${supplyDelta.text}</div></div>
              <div class=\"compare-card\"><div class=\"compare-label\">Risk delta</div><div class=\"compare-main\">${latestRisk ? latestRisk.risk_score.toFixed(2) : 'n/a'}</div><div class=\"${riskDelta.className}\">${riskDelta.text}</div></div>
            </div>
          </div>
          <div class=\"hero-panel status-board\">
            <div class=\"status-row\"><div><div class=\"status-label\">Latest Risk</div><div class=\"small muted\">${selectedHorizon}-day horizon</div></div><div><div class=\"status-value\">${latestRisk ? latestRisk.risk_score.toFixed(2) : 'n/a'}</div><div class=\"${riskBadge(latestRisk?.risk_level)}\">${latestRisk?.risk_level || 'No data'}</div></div></div>
            <div class=\"status-row\"><div><div class=\"status-label\">Demand vs LPG Proxy</div><div class=\"small muted\">Latest computed gap</div></div><div class=\"status-value\">${latestRisk ? latestRisk.supply_gap_score.toFixed(2) : 'n/a'}</div></div>
            <div class=\"status-row\"><div><div class=\"status-label\">Scheduler Runs</div><div class=\"small muted\">Automatic materialization count</div></div><div class=\"status-value\">${scheduler.run_count}</div></div>
          </div>
        </section>

        <section class=\"grid\" style=\"margin-bottom:18px;\">
          <article class=\"metric-card\"><div><div class=\"metric-label\">Demand Forecast</div><div class=\"metric-value\">${metric(latestDemand?.predicted_lpg_demand)}</div></div><div class=\"metric-sub\">${selectedHorizon}-day LPG demand forecast with interval ${latestDemand ? `${metric(latestDemand.lower_bound)} to ${metric(latestDemand.upper_bound)}` : 'n/a'}.</div></article>
          <article class=\"metric-card\"><div><div class=\"metric-label\">Crude Supply Forecast</div><div class=\"metric-value\">${metric(latestSupply?.expected_crude_arrival_volume)}</div></div><div class=\"metric-sub\">Market-adjusted crude arrivals with confidence band ${latestSupply?.confidence_band || 'n/a'}.</div></article>
          <article class=\"metric-card\"><div><div class=\"metric-label\">Disruption Score</div><div class=\"metric-value\">${latestRisk ? latestRisk.disruption_score.toFixed(2) : 'n/a'}</div></div><div class=\"metric-sub\">Derived from Brent, WTI, inventory tightness, and short-window price volatility.</div></article>
          <article class=\"metric-card\"><div><div class=\"metric-label\">Artifacts Loaded</div><div class=\"metric-value\">${demand.length + supply.length + risks.length + alerts.length + domestic.length + market.length}</div></div><div class=\"metric-sub\">Visible across persisted history and source-input endpoints for the selected view.</div></article>
        </section>

        <section class=\"grid\">
          <article class=\"panel wide\"><div class=\"panel-head\"><div><h2>Demand vs Supply Trend</h2><div class=\"panel-copy\">Persisted forecast history for demand and supply. The shapes become more useful as repeated scheduled runs accumulate.</div></div></div><div class=\"chart\">${chartMarkup(demandValues.length ? demandValues : [0], '#0d6c63')}</div><div class=\"legend\"><span><i style=\"background:#0d6c63\"></i>Demand forecast</span><span><i style=\"background:#c26a1b\"></i>Supply forecast</span></div><div class=\"chart\" style=\"margin-top:14px;\">${chartMarkup(supplyValues.length ? supplyValues : [0], '#c26a1b')}</div></article>
          <article class=\"panel narrow\"><div class=\"panel-head\"><div><h2>Recommended Actions</h2><div class=\"panel-copy\">Concrete next steps generated from the current risk, alert, and supply-demand picture.</div></div></div><div class=\"driver-list\">${actions.map(item => `<div class=\"driver-item\"><strong>${item.title}</strong><div class=\"small\" style=\"margin-top:8px;\">${item.copy}</div></div>`).join('')}</div></article>
          <article class=\"panel narrow\"><div class=\"panel-head\"><div><h2>Risk Trend</h2><div class=\"panel-copy\">Persisted risk snapshots from the API, useful for auditability and dashboard history.</div></div></div><div class=\"chart\">${chartMarkup(riskValues.length ? riskValues : [0], '#ad3f34')}</div></article>
          <article class="panel wide"><div class="panel-head"><div><h2>Alert Feed</h2><div class="panel-copy">Most recent persisted alerts, newest first.</div></div></div><div class="feed">${compactRows(alerts, item => `<div class="feed-item"><div class="feed-top"><div><div class="${riskBadge(item.level)}">${item.level}</div><h3 style="margin-top:10px; font-size:24px;">${item.title}</h3></div><div class="small muted">${isoDate(item.as_of)}</div></div><div class="small" style="line-height:1.6; margin-bottom:10px;">${item.message}</div><div class="small muted">${item.drivers.join(' | ')}</div></div>`, 'No active alerts for the current snapshot. Thresholds were not crossed in the latest persisted run.')}</div></article>
          <article class=\"panel wide\"><div class=\"panel-head\"><div><h2>Source Inputs</h2><div class=\"panel-copy\">The selected source input is explained in the same card style as the rest of the dashboard. Raw payload is available only when needed.</div></div></div><div class=\"source-grid\"><div class=\"source-column\"><div class=\"feed-item\"><h3 style=\"font-size:24px; margin-bottom:10px;\">Domestic PPAC Inputs</h3><div class=\"evidence-stack\">${renderEvidence(domestic, 'domestic')}</div></div></div><div class=\"source-column\"><div class=\"feed-item\"><h3 style=\"font-size:24px; margin-bottom:10px;\">EIA Market Inputs</h3><div class=\"evidence-stack\">${renderEvidence(market, 'market')}</div></div></div><div class=\"source-column\">${detailMarkup()}</div></div></article>
          <article class=\"panel wide\"><div class=\"panel-head\"><div><h2>Forecast History Table</h2><div class=\"panel-copy\">Compact persisted rows for quick operator comparison.</div></div></div><div class=\"table-stack\"><div class=\"table-wrap\"><table><thead><tr><th>Forecast Date</th><th>Demand</th><th>Interval</th><th>Model</th></tr></thead><tbody>${demand.length ? demand.slice(0, 5).map(item => `<tr><td>${item.forecast_date}</td><td>${metric(item.predicted_lpg_demand)}</td><td>${metric(item.lower_bound)} to ${metric(item.upper_bound)}</td><td>${item.model_version}</td></tr>`).join('') : '<tr><td colspan="4">No demand history yet.</td></tr>'}</tbody></table></div><div class=\"table-wrap\"><table><thead><tr><th>Forecast Date</th><th>Supply</th><th>Confidence Band</th><th>Model</th></tr></thead><tbody>${supply.length ? supply.slice(0, 5).map(item => `<tr><td>${item.forecast_date}</td><td>${metric(item.expected_crude_arrival_volume)}</td><td>${item.confidence_band}</td><td>${item.model_version}</td></tr>`).join('') : '<tr><td colspan="4">No supply history yet.</td></tr>'}</tbody></table></div></div></article>
          <article class="panel narrow"><div class="panel-head"><div><h2>Latest Drivers</h2><div class="panel-copy">Top factors feeding the most recent risk snapshot.</div></div></div><div class="driver-list">${(latestRisk?.top_risk_drivers || ['No drivers available yet.']).map(driver => `<div class="driver-item">${driver}</div>`).join('')}</div></article>
        </section>`;
      bindDashboardEvents();
    }
    async function loadDashboard(resetDetail = false) {
      if (resetDetail) selectedDetail = null;
      const [demand, supply, risk, alerts, domestic, market, scheduler] = await Promise.all([
        fetch(`/history/demand-forecasts?limit=12&horizon=${selectedHorizon}`).then(r => r.json()),
        fetch(`/history/supply-forecasts?limit=12&horizon=${selectedHorizon}`).then(r => r.json()),
        fetch(`/history/risk-snapshots?limit=12&horizon=${selectedHorizon}`).then(r => r.json()),
        fetch('/history/alerts?limit=8').then(r => r.json()),
        fetch('/source/domestic-observations?limit=6').then(r => r.json()),
        fetch('/source/market-observations?limit=6').then(r => r.json()),
        fetch('/scheduler/status').then(r => r.json()),
      ]);
      render({ demand, supply, risk, alerts, domestic, market, scheduler });
    }
    async function boot() { try { await loadDashboard(true); } catch (error) { document.getElementById('app').innerHTML = 'Dashboard failed to load persisted history, source endpoints, or scheduler status.'; } }
    boot();
  </script>
</body>
</html>"""
    return HTMLResponse(content=html)






