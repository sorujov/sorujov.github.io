/* ICT data page (/portfolio/cis-internet/).
   Charts are drawn with D3 from the JSON files in assets/data/ict/. Colours come
   from CSS custom properties, so the charts follow the site's light and dark
   themes; every chart is redrawn when the theme, the width or a control changes. */
(function () {
  "use strict";

  const root = document.getElementById("ict");
  if (!root || typeof d3 === "undefined") return;

  const AZ = "AZE";
  const STROKE = { key: 3, ref: 2.5, bg: 1.6, bgHover: 2.6 };

  const state = {
    compare: "KAZ",
    map: { net: "fixed", stat: "median", measure: "download", month: null },
    rankMonth: null,
    trend: { net: "fixed", stat: "median", measure: "download", range: "all" },
    fc: { country: AZ, net: "fixed", stat: "median", measure: "download", horizon: 12, level: 95 },
    adopt: "internet_share",
    v6: "capable",
    az: { net: "fixed", measure: "download", quarter: null, region: "C-baku" },
  };

  let DATA = null, GEO = null, AZD = null, AZGEO = null, FC = null;
  const NAME = {};

  const MEASURE = {
    download: { idx: 1, label: "Download speed", unit: "Mbps", higherBetter: true },
    upload: { idx: 2, label: "Upload speed", unit: "Mbps", higherBetter: true },
    latency: { idx: 3, label: "Latency", unit: "ms", higherBetter: false },
  };
  const STAT = { median: "Median", mean: "Mean" };
  const NET = { fixed: "fixed broadband", mobile: "mobile" };

  // ------------------------------------------------------------------ helpers
  const css = (name) => getComputedStyle(root).getPropertyValue(name).trim();
  const colours = () => ({
    az: css("--ict-az"), cmp: css("--ict-cmp"), other: css("--ict-other"), otherHover: css("--ict-other-hover"),
    ref: css("--ict-ref"), band: css("--ict-band"), ink: css("--ink"), soft: css("--ink-soft"),
    muted: css("--ink-muted"), rule: css("--rule"), surface: css("--paper-raised"),
    paper: css("--paper"), seqLo: css("--ict-seq-lo"), seqHi: css("--ict-seq-hi"),
  });

  const num = (v, unit = "") => {
    if (v == null || Number.isNaN(v)) return "–";
    const s = Math.abs(v) >= 100 ? Math.round(v).toLocaleString("en") : v.toFixed(1);
    return unit ? `${s} ${unit}` : s;
  };
  const parseMonth = d3.timeParse("%Y-%m");
  const monthLabel = (m) => d3.timeFormat("%b %Y")(parseMonth(m));
  const shiftMonth = (m, k) => d3.timeFormat("%Y-%m")(d3.timeMonth.offset(parseMonth(m), k));
  const monthGrid = (a, b) =>
    d3.timeMonth.range(parseMonth(a), d3.timeMonth.offset(parseMonth(b), 1)).map(d3.timeFormat("%Y-%m"));
  const qLabel = (k) => k.replace("-", " ");
  const ordinal = (n) => {
    const s = ["th", "st", "nd", "rd"], v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
  };

  function el(tag, attrs, text) {
    const n = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => n.setAttribute(k, v));
    if (text != null) n.textContent = text;
    return n;
  }
  const slot = (name) => document.querySelector(`[data-slot="${name}"]`);

  /** Clear a figure and give it a legend row, a plot holder with tooltip, and an optional caption. */
  function frame(fig, { legend = [], caption = "", title = "" } = {}) {
    const open = fig.querySelector("details")?.open;
    fig.innerHTML = "";
    if (title) fig.append(el("p", { class: "ict-figure__title" }, title));
    if (legend.length) {
      const ul = el("ul", { class: "ict-legend" });
      legend.forEach((l) => {
        const li = el("li");
        const sw = el("span", { class: `ict-swatch ict-swatch--${l.kind || "line"}` });
        sw.style.setProperty("--sw", l.colour);
        li.append(sw, document.createTextNode(l.label));
        if (l.onRemove) {
          const b = el("button", { type: "button", class: "ict-legend__x", "aria-label": `Remove ${l.label}` }, "×");
          b.addEventListener("click", l.onRemove);
          li.append(b);
        }
        ul.append(li);
      });
      fig.append(ul);
    }
    const plot = el("div", { class: "ict-plot" });
    const tip = el("div", { class: "ict-tip", role: "status", "aria-live": "polite" });
    tip.hidden = true;
    plot.append(tip);
    fig.append(plot);
    if (caption) fig.append(el("figcaption", {}, caption));
    const width = Math.max(280, Math.floor(plot.getBoundingClientRect().width || fig.clientWidth));
    return { plot, tip, width, open };
  }

  function addTable(fig, headers, rows, open) {
    const det = el("details", { class: "ict-table" });
    if (open) det.open = true;
    det.append(el("summary", {}, "Show the data"));
    const wrap = el("div", { class: "ict-table__wrap" });
    const t = el("table");
    const thead = el("thead"), tr = el("tr");
    headers.forEach((h) => tr.append(el("th", { scope: "col" }, h)));
    thead.append(tr);
    const tb = el("tbody");
    rows.forEach((r) => {
      const row = el("tr");
      r.forEach((v, i) => {
        const text = v == null || Number.isNaN(v) ? "–" : typeof v === "number" ? num(v) : String(v);
        row.append(el(i ? "td" : "th", i ? {} : { scope: "row" }, text));
      });
      tb.append(row);
    });
    t.append(thead, tb);
    wrap.append(t);
    det.append(wrap);
    fig.append(det);
  }

  function showTip(tip, plot, html, x, y) {
    tip.innerHTML = html;
    tip.hidden = false;
    const pw = plot.clientWidth, tw = tip.offsetWidth, th = tip.offsetHeight;
    let left = x + 16;
    if (left + tw > pw) left = x - tw - 16;
    tip.style.left = `${Math.max(0, left)}px`;
    tip.style.top = `${Math.max(0, y - th - 12)}px`;
  }
  const hideTip = (tip) => { tip.hidden = true; };

  function axisStyle(g, c) {
    g.selectAll("path.domain").remove();
    g.selectAll("line").attr("stroke", c.rule);
    g.selectAll("text").attr("fill", c.muted).attr("font-size", 12.5);
  }

  /** Spread label y-positions at least `gap` apart inside [lo, hi]. */
  function dodge(items, gap, lo, hi) {
    items.sort((a, b) => a.y - b.y);
    for (let i = 1; i < items.length; i++)
      if (items[i].y - items[i - 1].y < gap) items[i].y = items[i - 1].y + gap;
    const over = items.length ? items[items.length - 1].y - hi : 0;
    if (over > 0) items.forEach((d) => (d.y -= over));
    for (let i = items.length - 2; i >= 0; i--)
      if (items[i + 1].y - items[i].y < gap) items[i].y = items[i + 1].y - gap;
    items.forEach((d) => (d.y = Math.max(lo, d.y)));
    return items;
  }

  /** Wire a group of segmented buttons: data-ctl="name" data-value="…". */
  function segmented(name, current, onChange) {
    const buttons = root.querySelectorAll(`button[data-ctl="${name}"]`);
    buttons.forEach((b) => {
      b.setAttribute("aria-pressed", String(b.dataset.value === String(current)));
      b.addEventListener("click", () => {
        buttons.forEach((o) => o.setAttribute("aria-pressed", String(o === b)));
        onChange(b.dataset.value);
      });
    });
  }
  function setDisabled(name, value, disabled) {
    const b = root.querySelector(`button[data-ctl="${name}"][data-value="${value}"]`);
    if (b) b.disabled = disabled;
  }

  // Emphasis: the subject (accent) and one comparison (blue); all else is grey.
  let focus = { primary: AZ, secondary: "KAZ" };
  const countryFocus = () => { focus = { primary: AZ, secondary: state.compare }; };
  const colourOf = (id, c) => (id === focus.primary ? c.az : id === focus.secondary ? c.cmp : c.other);
  const weightOf = (id) => (id === focus.primary ? 2 : id === focus.secondary ? 1 : 0);

  function setCompare(iso) {
    if (iso === AZ) return;
    state.compare = iso || "";
    const sel = root.querySelector('select[data-ctl="compare"]');
    if (sel) sel.value = state.compare;
    renderCountryCharts();
  }

  // ------------------------------------------------------------- data access
  const gi = (iso, net, stat) => DATA.global_index[iso]?.[net]?.[stat] || [];

  function allMonths() {
    const set = new Set();
    Object.values(DATA.global_index).forEach((nets) => Object.values(nets).forEach((stats) =>
      Object.values(stats).forEach((rows) => rows.forEach((r) => set.add(r[0])))));
    return Array.from(set).sort();
  }

  function latest({ net, stat, measure, month }) {
    const m = month || DATA.latest_month, idx = MEASURE[measure].idx;
    const rows = DATA.countries.map((cc) => {
      const r = gi(cc.iso3, net, stat).find((p) => p[0] === m);
      return r ? { iso: cc.iso3, name: cc.name, value: r[idx], down: r[1], up: r[2], lat: r[3], rank: r[4] } : null;
    }).filter(Boolean);
    const dir = MEASURE[measure].higherBetter ? -1 : 1;
    return rows.sort((a, b) => dir * (a.value - b.value));
  }

  // ------------------------------------------------------------------- tiles
  function renderTiles() {
    const ul = slot("tiles");
    const m = DATA.latest_month, prev = shiftMonth(m, -12);
    ul.innerHTML = "";
    const tile = (label, value, sub) => {
      const li = el("li");
      li.append(el("span", { class: "ict-tile__label" }, label), el("span", { class: "ict-tile__value" }, value));
      if (sub) li.append(el("span", { class: "ict-tile__sub" }, sub));
      ul.append(li);
    };
    ["fixed", "mobile"].forEach((net) => {
      const s = gi(AZ, net, "median");
      const now = s.find((r) => r[0] === m), then = s.find((r) => r[0] === prev);
      const change = now && then ? (now[1] / then[1] - 1) * 100 : null;
      tile(net === "fixed" ? "Fixed download, median" : "Mobile download, median",
        now ? `${now[1].toFixed(1)} Mbps` : "–",
        change == null ? "" : `${change >= 0 ? "+" : "−"}${Math.abs(change).toFixed(0)}% on ${monthLabel(prev)}`);
    });
    ["fixed", "mobile"].forEach((net) => {
      const list = latest({ net, stat: "median", measure: "download" });
      const pos = list.findIndex((d) => d.iso === AZ);
      tile(net === "fixed" ? "Fixed, CIS rank" : "Mobile, CIS rank",
        pos >= 0 ? `${ordinal(pos + 1)} of ${list.length}` : "–",
        pos >= 0 ? `${ordinal(list[pos].rank)} in the world` : "");
    });
    slot("asof").textContent = `Speedtest Global Index, ${monthLabel(m)}`;
    slot("rolling").textContent = DATA.rolling_from ? monthLabel(DATA.rolling_from) : "mid-2024";
  }

  // --------------------------------------------------------------- choropleth
  function choropleth(fig, opt) {
    const c = colours();
    const { plot, tip, width } = frame(fig, { caption: opt.caption });
    const height = Math.round(Math.min(opt.maxHeight || 440, width * opt.aspect));
    const projection = opt.projection().fitExtent([[8, 8], [width - 8, height - 56]], opt.fit);
    const path = d3.geoPath(projection);
    const shown = opt.rows.filter((d) => d.value != null && d.reliable !== false);
    const ext = d3.extent(shown, (d) => d.value);
    const good = opt.higherBetter ? ext : [ext[1], ext[0]];
    const scale = (opt.log && ext[0] > 0 ? d3.scaleSequentialLog() : d3.scaleSequential())
      .domain(good).interpolator(d3.interpolateLab(c.seqLo, c.seqHi));
    const byId = new Map(opt.rows.map((d) => [d.id, d]));

    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height).attr("role", "img").attr("aria-label", opt.aria);
    const uid = Math.random().toString(36).slice(2, 8);
    const defs = svg.append("defs");
    const pat = defs.append("pattern").attr("id", `hatch-${uid}`).attr("width", 6).attr("height", 6)
      .attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)");
    pat.append("rect").attr("width", 6).attr("height", 6).attr("fill", c.surface);
    pat.append("line").attr("y2", 6).attr("stroke", c.rule).attr("stroke-width", 2);

    const selected = (f) => opt.selected && opt.selected.includes(f.id);
    const strokeOf = (f) => (selected(f) ? c.ink : c.surface);
    const widthOf = (f) => (selected(f) ? 2.25 : opt.thin ? 0.75 : 1);
    const paths = svg.append("g").selectAll("path").data(opt.geo.features).join("path")
      .attr("d", path)
      .attr("fill", (f) => { const d = byId.get(f.id); return d && d.value != null && d.reliable !== false ? scale(d.value) : `url(#hatch-${uid})`; })
      .attr("stroke", strokeOf).attr("stroke-width", widthOf)
      .style("cursor", opt.onPick ? "pointer" : "default")
      .on("pointermove", function (ev, f) {
        const [x, y] = d3.pointer(ev, plot);
        showTip(tip, plot, opt.tip(f, byId.get(f.id)), x, y);
        d3.select(this).attr("stroke", c.ink).attr("stroke-width", 2.25).raise();
      })
      .on("pointerleave", function (ev, f) {
        hideTip(tip);
        d3.select(this).attr("stroke", strokeOf(f)).attr("stroke-width", widthOf(f));
        paths.filter(selected).raise();
      })
      .on("click", (ev, f) => opt.onPick && opt.onPick(f.id));
    paths.filter(selected).raise();

    // Scale legend: darker always means better.
    const lw = Math.min(240, width - 170), lx = 10, ly = height - 38;
    const gid = `grad-${uid}`;
    const grad = defs.append("linearGradient").attr("id", gid);
    d3.range(0, 1.001, 0.1).forEach((t) => {
      const v = opt.log && ext[0] > 0 ? good[0] * Math.pow(good[1] / good[0], t) : good[0] + t * (good[1] - good[0]);
      grad.append("stop").attr("offset", t).attr("stop-color", scale(v));
    });
    svg.append("rect").attr("x", lx).attr("y", ly).attr("width", lw).attr("height", 10).attr("rx", 2).attr("fill", `url(#${gid})`);
    const lg = svg.append("g").attr("font-size", 12).attr("fill", c.muted);
    lg.append("text").attr("x", lx).attr("y", ly + 26).text(num(good[0], opt.unit));
    lg.append("text").attr("x", lx + lw).attr("y", ly + 26).attr("text-anchor", "end").text(num(good[1], opt.unit));
    svg.append("rect").attr("x", lx + lw + 18).attr("y", ly - 1).attr("width", 14).attr("height", 12)
      .attr("fill", `url(#hatch-${uid})`).attr("stroke", c.rule);
    lg.append("text").attr("x", lx + lw + 38).attr("y", ly + 9).text(opt.missingLabel);
    return scale;
  }

  // -------------------------------------------------------------- ranked bars
  function bars(fig, opt) {
    const c = colours();
    const { plot, tip, width, open } = frame(fig, { title: opt.title, legend: opt.legend || [] });
    const rowH = 32, m = { t: 6, r: 84, b: 6, l: opt.labelWidth || 108 };
    const height = m.t + m.b + rowH * opt.rows.length;
    const max = d3.max(opt.rows, (d) => d.value) || 1;
    const x = d3.scaleLinear().domain([0, Math.max(max, opt.reference || 0)]).nice().range([m.l, width - m.r]);
    const y = d3.scaleBand().domain(opt.rows.map((d) => d.id)).range([m.t, height - m.b]).padding(0.3);
    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height).attr("role", "img").attr("aria-label", opt.aria);
    svg.append("line").attr("x1", m.l).attr("x2", m.l).attr("y1", m.t).attr("y2", height - m.b).attr("stroke", c.rule);
    const fillOf = (d) => (opt.primary === d.id ? c.az : opt.secondary === d.id ? c.cmp : c.other);

    // bars, then the reference line, then the labels, so the line never covers text
    svg.append("g").selectAll("rect").data(opt.rows).join("rect").attr("class", "ict-bar")
      .attr("x", m.l).attr("y", (d) => y(d.id))
      .attr("width", (d) => Math.max(2, x(d.value) - m.l)).attr("height", y.bandwidth())
      .attr("rx", 4).attr("fill", fillOf);
    if (opt.reference != null) {
      const rx = x(opt.reference);
      svg.append("line").attr("x1", rx).attr("x2", rx).attr("y1", m.t - 4).attr("y2", height - m.b + 4)
        .attr("stroke", c.ink).attr("stroke-width", 1.5);
    }
    const barSel = svg.selectAll("rect.ict-bar");
    const row = svg.append("g").selectAll("g").data(opt.rows).join("g");
    row.append("text").attr("x", m.l - 10).attr("y", (d) => y(d.id) + y.bandwidth() / 2).attr("dy", "0.35em")
      .attr("text-anchor", "end").attr("font-size", 13.5)
      .attr("fill", (d) => (fillOf(d) === c.other ? c.soft : c.ink))
      .attr("font-weight", (d) => (opt.primary === d.id ? 600 : 400)).text((d) => d.name);
    row.append("text").attr("class", "ict-halo").attr("x", (d) => x(d.value) + 7)
      .attr("y", (d) => y(d.id) + y.bandwidth() / 2).attr("dy", "0.35em")
      .attr("font-size", 12.5).attr("fill", c.soft).text((d) => num(d.value, opt.unit));
    row.append("rect").attr("x", 0).attr("width", width).attr("y", (d) => y(d.id) - (y.step() - y.bandwidth()) / 2)
      .attr("height", y.step()).attr("fill", "transparent").style("cursor", opt.onPick ? "pointer" : "default")
      .on("pointerenter", (ev, d) => barSel.filter((b) => b.id === d.id).attr("opacity", 0.8))
      .on("pointermove", (ev, d) => {
        const [px, py] = d3.pointer(ev, plot);
        showTip(tip, plot, opt.tip(d), px, py);
      })
      .on("pointerleave", () => { hideTip(tip); barSel.attr("opacity", 1); })
      .on("click", (ev, d) => opt.onPick && opt.onPick(d.id));
    if (opt.table) addTable(fig, opt.table.headers, opt.table.rows, open);
  }

  // -------------------------------------------------------------- line chart
  /**
   * opt.series: [{id, name, points: [[key, value], ...]}]; opt.refs: labelled
   * reference lines; opt.keys: ordered x domain. Grey lines light up on hover
   * and, with opt.onPick, become the comparison on click.
   */
  function lineChart(fig, opt) {
    const c = colours();
    const refs = opt.refs || [];
    const nameOf = (id) => opt.series.find((s) => s.id === id)?.name;
    const legend = [];
    if (nameOf(focus.primary)) legend.push({ label: nameOf(focus.primary), colour: c.az });
    if (nameOf(focus.secondary)) legend.push({
      label: nameOf(focus.secondary), colour: c.cmp,
      onRemove: opt.onClearSecondary || null,
    });
    refs.forEach((r) => legend.push({ label: r.name, colour: c.ref }));
    if (opt.series.some((s) => weightOf(s.id) === 0))
      legend.push({ label: opt.otherLabel || "Other countries", colour: c.other, kind: "thin" });
    const { plot, tip, width, open } = frame(fig, { legend, caption: opt.caption });

    const narrow = width < 560;
    const height = Math.round(Math.max(280, Math.min(430, width * 0.52)));
    const labelChars = d3.max(opt.series.filter((s) => weightOf(s.id) > 0).concat(refs), (s) => s.name.length + 10) || 12;
    const m = { t: 24, r: narrow ? 14 : Math.min(200, Math.max(120, labelChars * 7.4)), b: 34, l: 52 };
    const keys = opt.keys;
    const x = d3.scalePoint().domain(keys).range([m.l, width - m.r]);
    const inRange = (p) => x(p[0]) != null && p[1] != null;
    const series = opt.series.map((s) => ({ ...s, points: s.points.filter(inRange) })).filter((s) => s.points.length);
    const refSeries = refs.map((s) => ({ ...s, points: s.points.filter(inRange) })).filter((s) => s.points.length);
    const all = series.concat(refSeries);

    const emph = all.filter((s) => weightOf(s.id) > 0 || refSeries.includes(s));
    const keyVals = emph.flatMap((s) => s.points.map((p) => p[1]));
    const bgVals = series.filter((s) => weightOf(s.id) === 0).flatMap((s) => s.points.map((p) => p[1])).sort(d3.ascending);
    const fullMax = d3.max(all, (s) => d3.max(s.points, (p) => p[1])) || 1;
    const ymax = opt.clipOutliers
      ? Math.max(d3.max(keyVals) || 0, bgVals.length ? d3.quantile(bgVals, 0.98) : 0) || fullMax
      : fullMax;
    const y = d3.scaleLinear().domain([0, ymax]).nice().range([height - m.b, m.t]);

    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height).attr("role", "img").attr("aria-label", opt.aria);
    svg.append("g").attr("transform", `translate(${m.l},0)`)
      .call(d3.axisLeft(y).ticks(5).tickSize(-(width - m.l - m.r)).tickPadding(8))
      .call((g) => axisStyle(g, c));
    const maxTicks = Math.max(3, Math.floor((width - m.l - m.r) / 80));
    let tickKeys = keys.filter((k, i) => (opt.tickFilter ? opt.tickFilter(k, i) : true));
    if (tickKeys.length > maxTicks) {
      const step = Math.ceil(tickKeys.length / maxTicks);
      tickKeys = tickKeys.filter((k, i) => i % step === 0);
    }
    svg.append("g").attr("transform", `translate(0,${height - m.b})`)
      .call(d3.axisBottom(x).tickValues(tickKeys).tickFormat((k) => opt.tickFormat(k, false)).tickSize(0).tickPadding(12))
      .call((g) => axisStyle(g, c));
    svg.append("text").attr("x", m.l).attr("y", 10).attr("font-size", 12).attr("fill", c.muted).text(opt.unit);

    if (opt.marker && x(opt.marker.key) != null) {
      const mx = x(opt.marker.key);
      svg.append("line").attr("x1", mx).attr("x2", mx).attr("y1", m.t).attr("y2", height - m.b)
        .attr("stroke", c.rule).attr("stroke-width", 1.5);
      const label = narrow ? "Rolling 3-month" : opt.marker.label;
      const flip = mx + 8 + label.length * 6.6 > width - m.r;
      svg.append("text").attr("x", flip ? mx - 6 : mx + 6).attr("y", m.t + 12).attr("font-size", 12)
        .attr("text-anchor", flip ? "end" : "start").attr("fill", c.muted).text(label);
    }

    const line = d3.line().defined((p) => p[1] != null).x((p) => x(p[0])).y((p) => y(p[1])).curve(d3.curveMonotoneX);
    const dense = (s) => {
      const map = new Map(s.points);
      const a = keys.indexOf(s.points[0][0]), b = keys.indexOf(s.points[s.points.length - 1][0]);
      return keys.slice(a, b + 1).map((k) => [k, map.has(k) ? map.get(k) : null]);
    };

    const clipId = `clip-${Math.random().toString(36).slice(2, 8)}`;
    svg.append("clipPath").attr("id", clipId).append("rect")
      .attr("x", 0).attr("y", m.t - 4).attr("width", width).attr("height", height - m.t - m.b + 8);
    const g = svg.append("g").attr("fill", "none").attr("stroke-linejoin", "round").attr("stroke-linecap", "round")
      .attr("clip-path", `url(#${clipId})`);
    if (opt.clipOutliers && fullMax > y.domain()[1]) {
      svg.append("text").attr("x", width - m.r).attr("y", 10).attr("text-anchor", "end")
        .attr("font-size", 12).attr("fill", c.muted).text("Some grey lines run above the chart");
    }

    const bgPaths = new Map();
    const ordered = series.slice().sort((a, b) => weightOf(a.id) - weightOf(b.id));
    ordered.forEach((s) => {
      const w = weightOf(s.id);
      const pts = dense(s);
      const p = g.append("path").datum(pts).attr("d", line)
        .attr("stroke", colourOf(s.id, c)).attr("stroke-width", w ? STROKE.key : STROKE.bg);
      if (!w) bgPaths.set(s.id, p);
      pts.forEach((q, i) => {
        if (q[1] != null && pts[i - 1]?.[1] == null && pts[i + 1]?.[1] == null)
          g.append("circle").attr("cx", x(q[0])).attr("cy", y(q[1])).attr("r", w ? 3.5 : 2.5).attr("fill", colourOf(s.id, c));
      });
    });
    refSeries.forEach((r) => g.append("path").datum(dense(r)).attr("d", line).attr("stroke", c.ref).attr("stroke-width", STROKE.ref));

    // End dots and direct labels for the emphasised and reference lines
    const endpoints = ordered.filter((s) => weightOf(s.id) > 0).map((s) => ({ s, colour: colourOf(s.id, c), ink: c.ink }))
      .concat(refSeries.map((s) => ({ s, colour: c.ref, ink: c.muted })))
      .map((d) => {
        const last = d.s.points[d.s.points.length - 1];
        return { ...d, x: x(last[0]), y: y(last[1]), y0: y(last[1]), v: last[1] };
      });
    endpoints.forEach((d) => svg.append("circle").attr("cx", d.x).attr("cy", d.y0).attr("r", 4.5)
      .attr("fill", d.colour).attr("stroke", c.surface).attr("stroke-width", 2));
    if (!narrow) {
      dodge(endpoints, 17, m.t, height - m.b).forEach((d) => {
        svg.append("text").attr("class", "ict-halo").attr("x", width - m.r + 12).attr("y", d.y).attr("dy", "0.35em")
          .attr("font-size", 13).attr("fill", d.ink).attr("font-weight", d.s.id === focus.primary ? 600 : 500)
          .text(`${d.s.name} ${opt.short(d.v)}`);
      });
    }

    // Hover layer: crosshair, nearest-line highlight, tooltip, click to compare
    const cross = svg.append("line").attr("y1", m.t).attr("y2", height - m.b).attr("stroke", c.muted)
      .attr("stroke-width", 1).attr("visibility", "hidden");
    const dots = svg.append("g");
    const hoverLabel = svg.append("text").attr("class", "ict-halo").attr("font-size", 12.5)
      .attr("font-weight", 600).attr("fill", c.ink).attr("visibility", "hidden");
    let hovered = null;
    const unhover = () => {
      if (hovered && bgPaths.has(hovered)) bgPaths.get(hovered).attr("stroke", c.other).attr("stroke-width", STROKE.bg);
      hovered = null;
      hoverLabel.attr("visibility", "hidden");
    };
    const lookup = all.map((s) => ({ s, map: new Map(s.points) }));
    svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", width - m.l - m.r).attr("height", height - m.t - m.b)
      .attr("fill", "transparent")
      .on("pointermove", (ev) => {
        const [px, py] = d3.pointer(ev, plot);
        const [sx, sy] = d3.pointer(ev, svg.node());
        const i = Math.round((sx - m.l) / (x.step() || 1));
        const key = keys[Math.max(0, Math.min(keys.length - 1, i))];
        cross.attr("x1", x(key)).attr("x2", x(key)).attr("visibility", "visible");
        const rows = lookup.map((d) => ({ s: d.s, v: d.map.get(key) })).filter((d) => d.v != null);
        // nearest grey line to the pointer
        let near = null, best = 14;
        rows.forEach((d) => {
          if (weightOf(d.s.id) === 0 && bgPaths.has(d.s.id)) {
            const dist = Math.abs(y(d.v) - sy);
            if (dist < best) { best = dist; near = d; }
          }
        });
        if ((near && near.s.id) !== hovered) {
          unhover();
          if (near) {
            hovered = near.s.id;
            bgPaths.get(hovered).attr("stroke", c.otherHover).attr("stroke-width", STROKE.bgHover).raise();
          }
        }
        if (near) {
          hoverLabel.attr("x", Math.min(x(key) + 8, width - m.r - 4)).attr("y", y(near.v) - 8)
            .attr("text-anchor", x(key) + 120 > width - m.r ? "end" : "start")
            .text(near.s.name).attr("visibility", "visible");
        }
        svg.select("rect.ict-hit").style("cursor", near && opt.onPick ? "pointer" : "crosshair");
        dots.selectAll("*").remove();
        rows.filter((d) => weightOf(d.s.id) > 0 || refSeries.includes(d.s)).forEach((d) => {
          dots.append("circle").attr("cx", x(key)).attr("cy", y(d.v)).attr("r", 5)
            .attr("fill", refSeries.includes(d.s) ? c.ref : colourOf(d.s.id, c))
            .attr("stroke", c.surface).attr("stroke-width", 2);
        });
        const sorted = rows.slice().sort((a, b) => (opt.lowerBetter ? a.v - b.v : b.v - a.v));
        const body = sorted.map((d) => {
          const cls = weightOf(d.s.id) > 0 || d.s.id === hovered ? " is-strong" : "";
          return `<div class="ict-tip__row${cls}"><span>${d.s.name}</span><span>${opt.short(d.v)}</span></div>`;
        }).join("");
        const hint = near && opt.onPick ? `<div class="ict-tip__hint">Click to compare with ${near.s.name}</div>` : "";
        showTip(tip, plot, `<div class="ict-tip__head">${opt.tickFormat(key, true)}</div>${body}${hint}`, px, py);
      })
      .on("click", () => { if (hovered && opt.onPick) opt.onPick(hovered); })
      .on("pointerleave", () => {
        cross.attr("visibility", "hidden");
        dots.selectAll("*").remove();
        unhover();
        hideTip(tip);
      })
      .attr("class", "ict-hit").style("cursor", "crosshair");

    if (opt.table) addTable(fig, opt.table.headers, opt.table.rows, open);
  }

  // ------------------------------------------------------ CIS map and ranking
  function renderMap() {
    const s = state.map, meas = MEASURE[s.measure];
    const rows = latest(s);
    const byIso = new Map(rows.map((d) => [d.iso, d]));
    const tipFor = (d) => `<strong>${d.name}</strong><br>Download ${num(d.down, "Mbps")}<br>Upload ${num(d.up, "Mbps")}<br>Latency ${num(d.lat, "ms")}<br><span>${ordinal(d.rank)} in the world</span>`;
    choropleth(root.querySelector('[data-chart="map"]'), {
      geo: GEO, fit: { type: "FeatureCollection", features: GEO.features.filter((f) => f.id !== "RUS") },
      projection: () => d3.geoConicEqualArea().parallels([38, 50]).rotate([-58, 0]),
      aspect: 0.72, maxHeight: 440, unit: meas.unit, higherBetter: meas.higherBetter,
      rows: DATA.countries.map((cc) => ({ id: cc.iso3, value: byIso.get(cc.iso3)?.value ?? null })),
      selected: [AZ, state.compare].filter(Boolean),
      missingLabel: "No figure this month",
      aria: `Map of ${STAT[s.stat].toLowerCase()} ${meas.label.toLowerCase()}, ${NET[s.net]}`,
      caption: "Click a country to compare it with Azerbaijan in the charts below.",
      tip: (f, d) => (byIso.has(f.id) ? tipFor(byIso.get(f.id)) : `<strong>${f.properties.name}</strong><br><span>No Global Index figure for ${monthLabel(s.month)}</span>`),
      onPick: (id) => byIso.has(id) && setCompare(id),
    });
    const fig = root.querySelector('[data-chart="bars"]');
    bars(fig, {
      title: `${STAT[s.stat]} ${meas.label.toLowerCase()}, ${monthLabel(s.month)}${meas.higherBetter ? "" : " (lower is better)"}`,
      rows: rows.map((d) => ({ ...d, id: d.iso })), unit: meas.unit,
      primary: AZ, secondary: state.compare,
      aria: `Countries ranked by ${STAT[s.stat].toLowerCase()} ${meas.label.toLowerCase()}`,
      tip: tipFor, onPick: (id) => setCompare(id),
      table: {
        headers: ["Country", "Download (Mbps)", "Upload (Mbps)", "Latency (ms)", "World rank"],
        rows: rows.map((d) => [d.name, d.down, d.up, d.lat, d.rank]),
      },
    });
    const missing = DATA.countries.filter((cc) => !byIso.has(cc.iso3)).map((cc) => cc.name);
    if (missing.length) fig.append(el("figcaption", {}, `No figures for ${monthLabel(s.month)}: ${missing.join(", ")}.${s.month > "2025-04" && missing.some((n) => n === "Russia" || n === "Belarus") ? " Belarus and Russia left the index after April 2025; choose an earlier month to see them." : ""}`));
  }

  // ------------------------------------------------------------ monthly trend
  function renderTrend() {
    countryFocus();
    const s = state.trend, meas = MEASURE[s.measure];
    const series = DATA.countries.map((cc) => ({
      id: cc.iso3, name: cc.name,
      points: gi(cc.iso3, s.net, s.stat).map((r) => [r[0], r[meas.idx]]).filter((p) => p[1] != null),
    })).filter((x) => x.points.length);
    const first = d3.min(series, (x) => x.points[0][0]);
    const span = { "1y": 12, "3y": 36 }[s.range];
    const start = span ? shiftMonth(DATA.latest_month, -(span - 1)) : first;
    const months = monthGrid(start < first ? first : start, DATA.latest_month);
    const az = new Map(gi(AZ, s.net, s.stat).map((r) => [r[0], r[meas.idx]]));
    const cmp = new Map(gi(state.compare, s.net, s.stat).map((r) => [r[0], r[meas.idx]]));
    lineChart(root.querySelector('[data-chart="trend"]'), {
      series, keys: months, lowerBetter: !meas.higherBetter,
      unit: `${STAT[s.stat]} ${meas.label.toLowerCase()}, ${meas.unit}${meas.higherBetter ? "" : " (lower is better)"}`,
      aria: `${STAT[s.stat]} ${meas.label.toLowerCase()} by month, ${NET[s.net]}`,
      tickFormat: (k, long) => (long || months.length <= 18 ? monthLabel(k) : k.endsWith("-01") ? k.slice(0, 4) : monthLabel(k)),
      tickFilter: months.length <= 18 ? (k, i) => i % 2 === 0 : (k) => k.endsWith("-01") || k.endsWith("-07"),
      short: (v) => num(v, meas.unit),
      marker: DATA.rolling_from ? { key: DATA.rolling_from, label: "Rolling three-month figures from here" } : null,
      onPick: setCompare, onClearSecondary: () => setCompare(""),
      table: {
        headers: ["Month", "Azerbaijan", NAME[state.compare] || "Comparison"],
        rows: months.slice().reverse().filter((k) => az.has(k) || cmp.has(k)).map((k) => [monthLabel(k), az.get(k), cmp.get(k)]),
      },
    });
  }

  // ----------------------------------------------------------------- forecast
  function fcKey() {
    const f = state.fc;
    return `${f.country}|${f.net}|${f.stat}|${f.measure}`;
  }

  function renderForecast() {
    const fig = root.querySelector('[data-chart="forecast"]');
    const panel = slot("fc-summary");
    const f = state.fc, meas = MEASURE[f.measure];
    const entry = FC?.series?.[fcKey()];
    const c = colours();
    const name = NAME[f.country];
    if (!entry) {
      frame(fig).plot.append(el("p", { class: "ict-note" }, `No projection is available for ${name} with these settings; the series is too short.`));
      panel.innerHTML = "";
      return;
    }
    const li = FC.levels.indexOf(f.level);
    const fc = entry.forecast.slice(0, f.horizon).map((r) => ({ key: r[0], mean: r[1], lo: r[2 + 2 * li], hi: r[3 + 2 * li] }));
    const hist = gi(f.country, f.net, f.stat).map((r) => [r[0], r[meas.idx]]).filter((p) => p[1] != null && p[0] >= entry.start);
    const shownHist = hist.slice(-Math.max(18, f.horizon * 2));
    const keys = monthGrid(shownHist[0][0], fc[fc.length - 1].key);
    const lastObs = hist[hist.length - 1];

    const gone = DATA.countries.find((cc) => cc.iso3 === f.country)?.discontinued;
    const legend = [
      { label: `${name}, observed`, colour: f.country === AZ ? c.az : c.cmp },
      { label: "Projection", colour: f.country === AZ ? c.az : c.cmp, kind: "dash" },
      { label: `${f.level}% interval`, colour: c.band, kind: "band" },
    ];
    const { plot, tip, width, open } = frame(fig, {
      legend,
      caption: gone ? `${name} left the Global Index after ${monthLabel(lastObs[0])}; this projection runs on from that last figure, not from today.` : "",
    });
    const narrow = width < 560;
    const height = Math.round(Math.max(280, Math.min(420, width * 0.55)));
    const m = { t: 24, r: narrow ? 14 : 96, b: 34, l: 52 };
    const x = d3.scalePoint().domain(keys).range([m.l, width - m.r]);
    const hiMax = d3.max(fc, (d) => d.hi), obsMax = d3.max(shownHist, (p) => p[1]);
    const y = d3.scaleLinear().domain([0, Math.max(hiMax, obsMax)]).nice().range([height - m.b, m.t]);
    const tone = f.country === AZ ? c.az : c.cmp;

    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height).attr("role", "img")
      .attr("aria-label", `${name}: ${meas.label.toLowerCase()} with a ${f.horizon}-month ARIMA projection`);
    svg.append("g").attr("transform", `translate(${m.l},0)`)
      .call(d3.axisLeft(y).ticks(5).tickSize(-(width - m.l - m.r)).tickPadding(8)).call((g) => axisStyle(g, c));
    const maxTicks = Math.max(3, Math.floor((width - m.l - m.r) / 80));
    let ticks = keys.filter((k) => k.endsWith("-01") || k.endsWith("-07"));
    if (ticks.length > maxTicks) ticks = keys.filter((k) => k.endsWith("-01"));
    svg.append("g").attr("transform", `translate(0,${height - m.b})`)
      .call(d3.axisBottom(x).tickValues(ticks).tickFormat(monthLabel).tickSize(0).tickPadding(12)).call((g) => axisStyle(g, c));
    svg.append("text").attr("x", m.l).attr("y", 10).attr("font-size", 12).attr("fill", c.muted)
      .text(`${STAT[f.stat]} ${meas.label.toLowerCase()}, ${meas.unit}`);

    // shaded future region
    const x0 = x(lastObs[0]);
    svg.insert("rect", ":first-child").attr("x", x0).attr("y", m.t).attr("width", width - m.r - x0).attr("height", height - m.t - m.b)
      .attr("fill", c.band).attr("opacity", 0.25);
    svg.append("text").attr("x", x0 + 8).attr("y", m.t + 14).attr("font-size", 12).attr("fill", c.muted).text("Projection");

    const band = [{ key: lastObs[0], lo: lastObs[1], hi: lastObs[1] }, ...fc];
    svg.append("path").datum(band).attr("fill", c.band).attr("opacity", 0.9)
      .attr("d", d3.area().x((d) => x(d.key)).y0((d) => y(d.lo)).y1((d) => y(d.hi)).curve(d3.curveMonotoneX));
    const lineGen = d3.line().x((p) => x(p[0])).y((p) => y(p[1])).curve(d3.curveMonotoneX);
    svg.append("path").datum(shownHist).attr("d", lineGen).attr("fill", "none").attr("stroke", tone)
      .attr("stroke-width", STROKE.key).attr("stroke-linejoin", "round").attr("stroke-linecap", "round");
    svg.append("path").datum([[lastObs[0], lastObs[1]], ...fc.map((d) => [d.key, d.mean])]).attr("d", lineGen)
      .attr("fill", "none").attr("stroke", tone).attr("stroke-width", STROKE.key).attr("stroke-dasharray", "7 5")
      .attr("stroke-linecap", "round");
    svg.append("circle").attr("cx", x0).attr("cy", y(lastObs[1])).attr("r", 5).attr("fill", tone)
      .attr("stroke", c.surface).attr("stroke-width", 2);
    const end = fc[fc.length - 1];
    svg.append("circle").attr("cx", x(end.key)).attr("cy", y(end.mean)).attr("r", 5).attr("fill", c.surface)
      .attr("stroke", tone).attr("stroke-width", 2.5);
    if (!narrow) {
      svg.append("text").attr("class", "ict-halo").attr("x", width - m.r + 12).attr("y", y(end.mean)).attr("dy", "0.35em")
        .attr("font-size", 13).attr("font-weight", 600).attr("fill", c.ink).text(num(end.mean, meas.unit));
      svg.append("text").attr("class", "ict-halo").attr("x", width - m.r + 12).attr("y", y(end.mean) + 17).attr("dy", "0.35em")
        .attr("font-size", 12).attr("fill", c.muted).text(`${num(end.lo)}–${num(end.hi)}`);
    }

    const cross = svg.append("line").attr("y1", m.t).attr("y2", height - m.b).attr("stroke", c.muted).attr("visibility", "hidden");
    const dot = svg.append("circle").attr("r", 5).attr("fill", tone).attr("stroke", c.surface).attr("stroke-width", 2).attr("visibility", "hidden");
    const obsMap = new Map(shownHist), fcMap = new Map(fc.map((d) => [d.key, d]));
    svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", width - m.l - m.r).attr("height", height - m.t - m.b)
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("pointermove", (ev) => {
        const [px, py] = d3.pointer(ev, plot);
        const [sx] = d3.pointer(ev, svg.node());
        const i = Math.round((sx - m.l) / (x.step() || 1));
        const key = keys[Math.max(0, Math.min(keys.length - 1, i))];
        cross.attr("x1", x(key)).attr("x2", x(key)).attr("visibility", "visible");
        let html = `<div class="ict-tip__head">${monthLabel(key)}</div>`;
        if (obsMap.has(key)) {
          dot.attr("cx", x(key)).attr("cy", y(obsMap.get(key))).attr("visibility", "visible");
          html += `<div class="ict-tip__row is-strong"><span>Observed</span><span>${num(obsMap.get(key), meas.unit)}</span></div>`;
        } else if (fcMap.has(key)) {
          const d = fcMap.get(key);
          dot.attr("cx", x(key)).attr("cy", y(d.mean)).attr("visibility", "visible");
          html += `<div class="ict-tip__row is-strong"><span>Projected</span><span>${num(d.mean, meas.unit)}</span></div>`
            + `<div class="ict-tip__row"><span>${f.level}% interval</span><span>${num(d.lo)}–${num(d.hi)}</span></div>`;
        }
        showTip(tip, plot, html, px, py);
      })
      .on("pointerleave", () => { cross.attr("visibility", "hidden"); dot.attr("visibility", "hidden"); hideTip(tip); });

    addTable(fig, ["Month", "Projected", `Lower ${f.level}%`, `Upper ${f.level}%`],
      fc.map((d) => [monthLabel(d.key), d.mean, d.lo, d.hi]), open);

    // Summary panel
    const [p, dd, q] = entry.order;
    const change = (end.mean / lastObs[1] - 1) * 100;
    const facts = [
      ["Model", `ARIMA(${p}, ${dd}, ${q}) with trend`],
      ["Fitted on", `${entry.obs} months, ${monthLabel(entry.start)} to ${monthLabel(lastObs[0])}`],
      ["AIC", entry.aic.toFixed(1)],
      ["Trend term", entry.slope == null ? "–" : `${entry.slope >= 0 ? "+" : "−"}${Math.abs(entry.slope).toFixed(2)} ${meas.unit} a month`],
      [`Latest, ${monthLabel(lastObs[0])}`, num(lastObs[1], meas.unit)],
      [`Projected, ${monthLabel(end.key)}`, `${num(end.mean, meas.unit)} (${change >= 0 ? "+" : "−"}${Math.abs(change).toFixed(0)}%)`],
      [`${f.level}% interval`, `${num(end.lo)} to ${num(end.hi)} ${meas.unit}`],
    ];
    panel.innerHTML = "";
    const dl = el("dl", { class: "ict-facts" });
    facts.forEach(([k, v]) => { dl.append(el("dt", {}, k), el("dd", {}, v)); });
    panel.append(dl);
  }

  function fillForecastCountries() {
    const sel = root.querySelector('select[data-ctl="fc-country"]');
    const available = new Set(Object.keys(FC?.series || {}).map((k) => k.split("|")[0]));
    sel.innerHTML = "";
    DATA.countries.filter((cc) => available.has(cc.iso3)).forEach((cc) => {
      const o = el("option", { value: cc.iso3 }, cc.name + (cc.discontinued ? " (to Apr 2025)" : ""));
      if (cc.iso3 === state.fc.country) o.selected = true;
      sel.append(o);
    });
    sel.addEventListener("change", () => { state.fc.country = sel.value; syncForecastButtons(); renderForecast(); });
  }
  function syncForecastButtons() {
    const f = state.fc;
    ["fixed", "mobile"].forEach((net) =>
      setDisabled("fc-net", net, !FC.series[`${f.country}|${net}|${f.stat}|${f.measure}`]));
    if (!FC.series[fcKey()]) {
      const alt = ["fixed", "mobile"].find((net) => FC.series[`${f.country}|${net}|${f.stat}|${f.measure}`]);
      if (alt) {
        f.net = alt;
        root.querySelectorAll('button[data-ctl="fc-net"]').forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.value === alt)));
      }
    }
  }

  // -------------------------------------------------------------------- slope
  function renderSlope(net) {
    countryFocus();
    const fig = root.querySelector(`[data-chart="slope-${net}"]`);
    const c = colours();
    const end = state.rankMonth || DATA.latest_month, start = shiftMonth(end, -12);
    const rows = DATA.countries.map((cc) => {
      const s = new Map(gi(cc.iso3, net, "median").map((r) => [r[0], r[4]]));
      return s.has(end) && s.has(start) ? { iso: cc.iso3, name: cc.name, a: s.get(start), b: s.get(end) } : null;
    }).filter(Boolean);
    const { plot, tip, width, open } = frame(fig, { title: net === "fixed" ? "Fixed broadband" : "Mobile" });
    const height = 340, m = { t: 34, r: Math.min(160, width * 0.42), b: 14, l: 56 };
    const ext = d3.extent(rows.flatMap((d) => [d.a, d.b]));
    const y = d3.scaleLinear().domain([ext[0] - 3, ext[1] + 3]).range([m.t, height - m.b]);
    const xa = m.l, xb = width - m.r;
    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`).attr("width", width).attr("height", height)
      .attr("role", "img").attr("aria-label", `World rank by ${NET[net]} median download, ${monthLabel(start)} and ${monthLabel(end)}`);
    [[xa, monthLabel(start), "middle"], [xb, monthLabel(end), "middle"]].forEach(([xx, t, anchor]) => {
      svg.append("line").attr("x1", xx).attr("x2", xx).attr("y1", m.t - 8).attr("y2", height - m.b).attr("stroke", c.rule).attr("stroke-width", 1.5);
      svg.append("text").attr("x", xx).attr("y", 14).attr("text-anchor", anchor).attr("font-size", 12.5).attr("fill", c.muted).text(t);
    });
    rows.sort((p, q) => weightOf(p.iso) - weightOf(q.iso)).forEach((d) => {
      const w = weightOf(d.iso), col = colourOf(d.iso, c);
      const g = svg.append("g").style("cursor", w === 2 ? "default" : "pointer");
      const ln = g.append("line").attr("x1", xa).attr("x2", xb).attr("y1", y(d.a)).attr("y2", y(d.b))
        .attr("stroke", col).attr("stroke-width", w ? STROKE.key : STROKE.bg).attr("stroke-linecap", "round");
      [[xa, d.a], [xb, d.b]].forEach(([xx, v]) =>
        g.append("circle").attr("cx", xx).attr("cy", y(v)).attr("r", w ? 5 : 3.5).attr("fill", col)
          .attr("stroke", c.surface).attr("stroke-width", 2));
      if (w) g.append("text").attr("class", "ict-halo").attr("x", xa - 12).attr("y", y(d.a)).attr("dy", "0.35em")
        .attr("text-anchor", "end").attr("font-size", 13).attr("fill", c.ink).text(d.a);
      g.append("line").attr("x1", xa).attr("x2", xb).attr("y1", y(d.a)).attr("y2", y(d.b))
        .attr("stroke", "transparent").attr("stroke-width", 16)
        .on("pointerenter", () => { if (!w) ln.attr("stroke", c.otherHover).attr("stroke-width", STROKE.bgHover); })
        .on("pointermove", (ev) => {
          const [px, py] = d3.pointer(ev, plot);
          const delta = d.a - d.b;
          const hint = w ? "" : `<div class="ict-tip__hint">Click to compare</div>`;
          showTip(tip, plot, `<strong>${d.name}</strong><br>${ordinal(d.a)} → ${ordinal(d.b)}<br><span>${delta === 0 ? "No change" : `${Math.abs(delta)} places ${delta > 0 ? "up" : "down"}`}</span>${hint}`, px, py);
        })
        .on("pointerleave", () => { hideTip(tip); if (!w) ln.attr("stroke", col).attr("stroke-width", STROKE.bg); })
        .on("click", () => setCompare(d.iso));
    });
    dodge(rows.map((d) => ({ d, y: y(d.b) })), 16, m.t, height - m.b).forEach(({ d, y: ly }) => {
      svg.append("text").attr("x", xb + 12).attr("y", ly).attr("dy", "0.35em").attr("font-size", 13)
        .attr("fill", weightOf(d.iso) ? c.ink : c.muted).attr("font-weight", d.iso === AZ ? 600 : 400)
        .text(`${d.b}  ${d.name}`);
    });
    addTable(fig, ["Country", `Rank ${monthLabel(start)}`, `Rank ${monthLabel(end)}`],
      rows.slice().sort((p, q) => p.b - q.b).map((d) => [d.name, d.a, d.b]), open);
  }

  // ----------------------------------------------------------------- adoption
  function renderAdopt() {
    countryFocus();
    const ds = DATA.adoption[state.adopt];
    const pts = (code) => (ds.series[code] || []).map((r) => [String(r[0]), r[1]]).filter((p) => p[1] != null);
    const series = DATA.countries.map((cc) => ({ id: cc.iso3, name: cc.name, points: pts(cc.iso3) })).filter((s) => s.points.length);
    const refs = [{ id: "WLD", name: "World", points: pts("WLD") }].filter((s) => s.points.length);
    const keys = Array.from(new Set(series.concat(refs).flatMap((s) => s.points.map((p) => p[0])))).sort();
    const pct = ds.unit.startsWith("%");
    const short = (v) => (pct ? `${Math.round(v)}%` : v.toFixed(1));
    slot("adopt-note").textContent = `${ds.label}, ${ds.unit}. Annual ITU and World Bank figures; the latest year is usually one or two years behind.`;
    const m = (code) => new Map(pts(code));
    const [az, cmp, wld] = [m(AZ), m(state.compare), m("WLD")];
    lineChart(root.querySelector('[data-chart="adopt"]'), {
      series, refs, keys, unit: `${ds.label}, ${ds.unit}`, aria: `${ds.label} since 2000`,
      tickFormat: (k) => k, tickFilter: (k) => Number(k) % 5 === 0, short,
      onPick: setCompare, onClearSecondary: () => setCompare(""),
      table: {
        headers: ["Year", "Azerbaijan", NAME[state.compare] || "Comparison", "World"],
        rows: keys.slice().reverse().map((k) => [k, az.get(k), cmp.get(k), wld.get(k)]),
      },
    });
  }

  // --------------------------------------------------------------------- IPv6
  function renderIpv6() {
    countryFocus();
    const v6 = DATA.ipv6 || {}, col = state.v6 === "capable" ? 1 : 2;
    const pts = (code) => (v6[code] || []).map((r) => [r[0], r[col]]);
    const series = DATA.countries.map((cc) => ({ id: cc.iso3, name: cc.name, points: pts(cc.iso3) })).filter((s) => s.points.length);
    const refs = v6.WLD ? [{ id: "WLD", name: "World", points: pts("WLD") }] : [];
    const all = series.concat(refs);
    const months = monthGrid(d3.min(all, (s) => s.points[0][0]), d3.max(all, (s) => s.points[s.points.length - 1][0]));
    const pctFmt = (v) => (v == null ? "–" : `${v < 10 ? v.toFixed(1) : Math.round(v)}%`);
    const m = (code) => new Map(pts(code));
    const [az, cmp, wld] = [m(AZ), m(state.compare), m("WLD")];
    const label = state.v6 === "capable" ? "Users able to use IPv6" : "Users who prefer IPv6 when offered both";
    lineChart(root.querySelector('[data-chart="ipv6"]'), {
      series, refs, keys: months, unit: `${label}, %`, aria: `${label}, by month`,
      tickFormat: (k, long) => (long ? monthLabel(k) : k.slice(0, 4)),
      tickFilter: (k) => k.endsWith("-01"), short: pctFmt,
      onPick: setCompare, onClearSecondary: () => setCompare(""),
      table: {
        headers: ["Month", "Azerbaijan (%)", `${NAME[state.compare] || "Comparison"} (%)`, "World (%)"],
        rows: months.slice().reverse().map((k) => [monthLabel(k), az.get(k), cmp.get(k), wld.get(k)]),
      },
    });
  }

  // ------------------------------------------------------ Azerbaijan regions
  const AZM = {
    download: { col: 1, label: "Average download", unit: "Mbps", higherBetter: true },
    median: { col: 4, label: "Median tile download", unit: "Mbps", higherBetter: true },
    upload: { col: 2, label: "Average upload", unit: "Mbps", higherBetter: true },
    latency: { col: 3, label: "Average latency", unit: "ms", higherBetter: false },
  };
  const azSeries = (id, net) => AZD.series[id]?.[net] || []; // [q, down, up, lat, median, tests]
  const azName = (id) => AZD.regions.find((r) => r.id === id)?.name || id;

  function fillQuarters() {
    const sel = root.querySelector('select[data-ctl="az-quarter"]');
    const quarters = AZD.quarters[state.az.net];
    if (!state.az.quarter || !quarters.includes(state.az.quarter)) state.az.quarter = quarters[quarters.length - 1];
    sel.innerHTML = "";
    quarters.slice().reverse().forEach((q) => {
      const o = el("option", { value: q }, qLabel(q));
      if (q === state.az.quarter) o.selected = true;
      sel.append(o);
    });
  }

  function azRows() {
    const a = state.az, col = AZM[a.measure].col;
    return AZD.regions.map((r) => {
      const row = azSeries(r.id, a.net).find((p) => p[0] === a.quarter);
      return {
        id: r.id, name: r.name, kind: r.kind, tests: row ? row[5] : 0,
        value: row ? row[col] : null, down: row?.[1], up: row?.[2], lat: row?.[3], median: row?.[4],
        reliable: !!row && row[5] >= AZD.min_tests,
      };
    });
  }

  function national(net, measure) {
    // Test-weighted national figure for the chosen measure, from the unit rows.
    const col = AZM[measure].col;
    const out = new Map();
    AZD.quarters[net].forEach((q) => {
      let wsum = 0, tsum = 0;
      AZD.regions.forEach((r) => {
        const row = azSeries(r.id, net).find((p) => p[0] === q);
        if (row && row[col] != null) { wsum += row[col] * row[5]; tsum += row[5]; }
      });
      if (tsum) out.set(q, wsum / tsum);
    });
    return out;
  }

  function selectRegion(id) {
    state.az.region = id;
    root.querySelector('select[data-ctl="az-region"]').value = id;
    renderAzMap();
    renderAzTrend();
  }

  function azTip(d) {
    const kind = d.kind === "city" ? "city" : "district";
    if (!d.reliable) {
      return `<strong>${d.name}</strong> <span>${kind}</span><br><span>${d.tests ? `Only ${d.tests} tests this quarter` : "No tests this quarter"}</span>`;
    }
    return `<strong>${d.name}</strong> <span>${kind}</span><br>Download ${num(d.down, "Mbps")}<br>Median tile ${num(d.median, "Mbps")}<br>Upload ${num(d.up, "Mbps")}<br>Latency ${num(d.lat, "ms")}<br><span>${d.tests.toLocaleString("en")} tests</span>`;
  }

  function renderAzMap() {
    const a = state.az, meas = AZM[a.measure];
    const rows = azRows();
    const byId = new Map(rows.map((d) => [d.id, d]));
    choropleth(root.querySelector('[data-chart="az-map"]'), {
      geo: AZGEO, fit: AZGEO, projection: () => d3.geoMercator(), aspect: 0.8, maxHeight: 460,
      unit: meas.unit, higherBetter: meas.higherBetter, log: a.measure !== "latency", thin: true,
      rows: rows.map((d) => ({ id: d.id, value: d.value, reliable: d.reliable })),
      selected: [a.region], missingLabel: "Too few tests",
      aria: `Map of ${meas.label.toLowerCase()} by city and district, ${qLabel(a.quarter)}`,
      caption: "Click a city or district to follow it over time below.",
      tip: (f) => azTip(byId.get(f.id)), onPick: selectRegion,
    });
    const nat = national(a.net, a.measure).get(a.quarter);
    const cities = rows.filter((d) => d.kind === "city" && d.reliable)
      .sort((p, q) => (meas.higherBetter ? q.value - p.value : p.value - q.value));
    const legend = nat == null ? [] : [{ label: `Azerbaijan overall, ${num(nat, meas.unit)}`, colour: colours().ink, kind: "rule" }];
    const all = rows.slice().sort((p, q) => (q.down ?? -1) - (p.down ?? -1));
    bars(root.querySelector('[data-chart="az-bars"]'), {
      title: `Cities, ${meas.label.toLowerCase()}, ${qLabel(a.quarter)}`, legend,
      rows: cities, unit: meas.unit, reference: nat, primary: a.region, labelWidth: 112,
      aria: `Cities of Azerbaijan ranked by ${meas.label.toLowerCase()}`,
      tip: azTip, onPick: selectRegion,
      table: {
        headers: ["City or district", "Download (Mbps)", "Median tile (Mbps)", "Upload (Mbps)", "Latency (ms)", "Tests"],
        rows: all.map((d) => [d.name + (d.kind === "city" ? " (city)" : ""), d.down, d.median, d.up, d.lat, d.tests]),
      },
    });
  }

  function renderAzTrend() {
    const a = state.az, meas = AZM[a.measure];
    focus = { primary: a.region, secondary: null };
    const ok = (r) => r[5] >= AZD.min_tests && r[meas.col] != null;
    const places = AZD.regions.filter((r) => r.kind === "city" || r.id === a.region);
    const series = places.map((r) => ({
      id: r.id, name: r.name, points: azSeries(r.id, a.net).filter(ok).map((p) => [p[0], p[meas.col]]),
    })).filter((s) => s.points.length);
    const nat = national(a.net, a.measure);
    const refs = [{ id: "AZE", name: "Azerbaijan overall", points: Array.from(nat.entries()) }];
    const keys = AZD.quarters[a.net];
    const sel = new Map(azSeries(a.region, a.net).map((p) => [p[0], p]));
    lineChart(root.querySelector('[data-chart="az-trend"]'), {
      series, refs, keys, otherLabel: "Other cities", clipOutliers: true, lowerBetter: !meas.higherBetter,
      unit: `${meas.label}, ${meas.unit}${meas.higherBetter ? "" : " (lower is better)"}`,
      aria: `${meas.label} by quarter in ${azName(a.region)} since 2019`,
      tickFormat: (k, long) => (long ? qLabel(k) : k.slice(0, 4)), tickFilter: (k) => k.endsWith("Q1"),
      short: (v) => num(v, meas.unit),
      onPick: selectRegion,
      table: {
        headers: ["Quarter", `${azName(a.region)} (${meas.unit})`, "Tests", `Azerbaijan overall (${meas.unit})`],
        rows: keys.slice().reverse().map((k) => {
          const p = sel.get(k);
          return [qLabel(k), p && p[5] >= AZD.min_tests ? p[meas.col] : null, p ? p[5] : 0, nat.get(k)];
        }),
      },
    });
    slot("az-place").textContent = azName(a.region);
    countryFocus();
  }

  // ------------------------------------------------------------------ wiring
  function renderCountryCharts() {
    renderMap();
    renderTrend();
    renderSlope("fixed");
    renderSlope("mobile");
    renderAdopt();
    renderIpv6();
  }
  function renderAll() {
    renderTiles();
    renderCountryCharts();
    if (FC) renderForecast();
    renderAzMap();
    renderAzTrend();
  }

  function bindControls() {
    segmented("map-net", state.map.net, (v) => { state.map.net = v; renderMap(); });
    segmented("map-stat", state.map.stat, (v) => { state.map.stat = v; renderMap(); });
    segmented("map-measure", state.map.measure, (v) => { state.map.measure = v; renderMap(); });
    segmented("trend-net", state.trend.net, (v) => { state.trend.net = v; renderTrend(); });
    segmented("trend-stat", state.trend.stat, (v) => { state.trend.stat = v; renderTrend(); });
    segmented("trend-measure", state.trend.measure, (v) => { state.trend.measure = v; renderTrend(); });
    segmented("trend-range", state.trend.range, (v) => { state.trend.range = v; renderTrend(); });
    segmented("adopt", state.adopt, (v) => { state.adopt = v; renderAdopt(); });
    segmented("v6", state.v6, (v) => { state.v6 = v; renderIpv6(); });

    const months = allMonths();
    state.map.month = DATA.latest_month;
    const msel = root.querySelector('select[data-ctl="map-month"]');
    months.slice().reverse().forEach((mm) => {
      const o = el("option", { value: mm }, monthLabel(mm));
      if (mm === state.map.month) o.selected = true;
      msel.append(o);
    });
    msel.addEventListener("change", () => { state.map.month = msel.value; renderMap(); });
    const rsel0 = root.querySelector('select[data-ctl="rank-month"]');
    months.filter((mm) => months.includes(shiftMonth(mm, -12))).reverse().forEach((mm) => {
      const o = el("option", { value: mm }, `${monthLabel(shiftMonth(mm, -12))} → ${monthLabel(mm)}`);
      if (mm === DATA.latest_month) o.selected = true;
      rsel0.append(o);
    });
    state.rankMonth = DATA.latest_month;
    rsel0.addEventListener("change", () => { state.rankMonth = rsel0.value; renderSlope("fixed"); renderSlope("mobile"); });

    const sel = root.querySelector('select[data-ctl="compare"]');
    sel.append(el("option", { value: "" }, "No comparison"));
    DATA.countries.filter((cc) => cc.iso3 !== AZ).forEach((cc) => {
      const o = el("option", { value: cc.iso3 }, cc.name + (cc.discontinued ? " (to Apr 2025)" : ""));
      if (cc.iso3 === state.compare) o.selected = true;
      sel.append(o);
    });
    sel.addEventListener("change", () => setCompare(sel.value));

    if (FC) {
      fillForecastCountries();
      segmented("fc-net", state.fc.net, (v) => { state.fc.net = v; renderForecast(); });
      segmented("fc-stat", state.fc.stat, (v) => { state.fc.stat = v; syncForecastButtons(); renderForecast(); });
      segmented("fc-measure", state.fc.measure, (v) => { state.fc.measure = v; syncForecastButtons(); renderForecast(); });
      segmented("fc-horizon", state.fc.horizon, (v) => { state.fc.horizon = Number(v); renderForecast(); });
      segmented("fc-level", state.fc.level, (v) => { state.fc.level = Number(v); renderForecast(); });
      syncForecastButtons();
    }

    // Azerbaijan
    fillQuarters();
    segmented("az-net", state.az.net, (v) => { state.az.net = v; fillQuarters(); renderAzMap(); renderAzTrend(); });
    segmented("az-measure", state.az.measure, (v) => { state.az.measure = v; renderAzMap(); renderAzTrend(); });
    root.querySelector('select[data-ctl="az-quarter"]').addEventListener("change", (e) => {
      state.az.quarter = e.target.value;
      renderAzMap();
    });
    const rsel = root.querySelector('select[data-ctl="az-region"]');
    [["city", "Cities"], ["district", "Districts"]].forEach(([kind, label]) => {
      const og = el("optgroup", { label });
      AZD.regions.filter((r) => r.kind === kind).sort((p, q) => p.name.localeCompare(q.name))
        .forEach((r) => og.append(el("option", { value: r.id }, r.name)));
      rsel.append(og);
    });
    rsel.value = state.az.region;
    rsel.addEventListener("change", () => selectRegion(rsel.value));
    slot("min-tests").textContent = AZD.min_tests;
    const qs = AZD.quarters.fixed;
    if (slot("od-latest") && qs.length) slot("od-latest").textContent = qLabel(qs[qs.length - 1]);

    let w = root.clientWidth, timer;
    new ResizeObserver(() => {
      if (Math.abs(root.clientWidth - w) < 8) return;
      w = root.clientWidth;
      clearTimeout(timer);
      timer = setTimeout(renderAll, 150);
    }).observe(root);
    new MutationObserver(() => renderAll())
      .observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", renderAll);
  }

  const optional = (url) => (url ? d3.json(url).catch(() => null) : Promise.resolve(null));
  Promise.all([
    d3.json(root.dataset.src), d3.json(root.dataset.map),
    d3.json(root.dataset.azSrc), d3.json(root.dataset.azMap), optional(root.dataset.fcSrc),
  ])
    .then(([data, geo, az, azgeo, fc]) => {
      DATA = data; GEO = geo; AZD = az; AZGEO = azgeo; FC = fc;
      DATA.countries.forEach((cc) => (NAME[cc.iso3] = cc.name));
      root.classList.add("is-ready");
      bindControls();
      renderAll();
    })
    .catch((err) => {
      console.error(err);
      root.prepend(el("p", { class: "ict-error" }, "The data could not be loaded. Please try again later."));
    });
})();
