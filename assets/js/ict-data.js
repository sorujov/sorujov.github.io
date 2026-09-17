/* ICT data page: charts drawn with D3 from the JSON files in assets/data/ict/.
   Colours come from CSS custom properties, so the charts follow the site's
   light and dark themes; everything is redrawn when the theme or width changes. */
(function () {
  "use strict";

  const root = document.getElementById("ict");
  if (!root || typeof d3 === "undefined") return;

  const AZ = "AZE";
  const state = {
    mapNet: "fixed",
    trendNet: "fixed",
    trendMetric: "download",
    adopt: "internet_share",
    compare: "KAZ",
    azNet: "fixed",
    azQuarter: null,
    azRegion: "C-baku",
  };
  let DATA = null;
  let GEO = null;
  let AZD = null;
  let AZGEO = null;
  const NAME = {};

  const METRIC = {
    download: { idx: 1, label: "Download speed", unit: "Mbps", better: "higher" },
    upload: { idx: 2, label: "Upload speed", unit: "Mbps", better: "higher" },
    latency: { idx: 3, label: "Latency", unit: "ms", better: "lower" },
  };

  // ------------------------------------------------------------------ helpers
  const css = (name) => getComputedStyle(root).getPropertyValue(name).trim();
  const colours = () => ({
    az: css("--ict-az"),
    cmp: css("--ict-cmp"),
    other: css("--ict-other"),
    ref: css("--ict-ref"),
    ink: css("--ink"),
    soft: css("--ink-soft"),
    muted: css("--ink-muted"),
    rule: css("--rule"),
    surface: css("--paper-raised"),
    seqLo: css("--ict-seq-lo"),
    seqHi: css("--ict-seq-hi"),
  });

  const fmt = (v, unit) =>
    v == null || Number.isNaN(v) ? "–" : `${v >= 100 ? Math.round(v) : v.toFixed(1)} ${unit}`;
  const monthLabel = (m) => d3.timeFormat("%b %Y")(d3.timeParse("%Y-%m")(m));
  const ordinal = (n) => {
    const s = ["th", "st", "nd", "rd"], v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
  };
  const shiftMonth = (m, k) => {
    const d = d3.timeParse("%Y-%m")(m);
    return d3.timeFormat("%Y-%m")(d3.timeMonth.offset(d, k));
  };
  const monthGrid = (a, b) =>
    d3.timeMonth
      .range(d3.timeParse("%Y-%m")(a), d3.timeMonth.offset(d3.timeParse("%Y-%m")(b), 1))
      .map(d3.timeFormat("%Y-%m"));

  function el(tag, attrs, text) {
    const n = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => n.setAttribute(k, v));
    if (text != null) n.textContent = text;
    return n;
  }

  /** Prepare a figure: clear it, add legend row, svg holder, tooltip, table. */
  function frame(fig, { legend = [], caption = "" } = {}) {
    const open = fig.querySelector("details")?.open;
    fig.innerHTML = "";
    if (legend.length) {
      const ul = el("ul", { class: "ict-legend" });
      legend.forEach((l) => {
        const li = el("li");
        const sw = el("span", { class: `ict-swatch ict-swatch--${l.kind || "line"}` });
        sw.style.setProperty("--sw", l.colour);
        li.append(sw, document.createTextNode(l.label));
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
    return { plot, tip, width: Math.max(280, plot.clientWidth || fig.clientWidth), open };
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
      r.forEach((c, i) => row.append(el(i ? "td" : "th", i ? {} : { scope: "row" }, c == null ? "–" : String(c))));
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
    let left = x + 14;
    if (left + tw > pw) left = x - tw - 14;
    tip.style.left = `${Math.max(0, left)}px`;
    tip.style.top = `${Math.max(0, y - th - 10)}px`;
  }
  const hideTip = (tip) => { tip.hidden = true; };

  function axisStyle(g, c) {
    g.selectAll("path.domain").remove();
    g.selectAll("line").attr("stroke", c.rule);
    g.selectAll("text").attr("fill", c.muted).attr("font-size", 12);
  }

  /** Spread label y-positions so they are at least `gap` apart, within [lo, hi]. */
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

  // Which series are emphasised: the subject (accent) and one comparison.
  let focus = { primary: AZ, secondary: "KAZ" };
  const seriesColour = (id, c) => (id === focus.primary ? c.az : id === focus.secondary ? c.cmp : c.other);
  const rankOf = (id) => (id === focus.primary ? 2 : id === focus.secondary ? 1 : 0);
  const highlightOrder = (a, b) => rankOf(a) - rankOf(b);
  const countryFocus = () => { focus = { primary: AZ, secondary: state.compare }; };

  // -------------------------------------------------------------- data access
  const gi = (iso, net, stat = "median") => DATA.global_index[iso]?.[net]?.[stat] || [];

  function latestFor(net) {
    const m = DATA.latest_month;
    return DATA.countries
      .map((c) => {
        const row = gi(c.iso3, net).find((r) => r[0] === m);
        return row ? { iso: c.iso3, name: c.name, value: row[1], up: row[2], lat: row[3], rank: row[4] } : null;
      })
      .filter(Boolean)
      .sort((a, b) => b.value - a.value);
  }

  // -------------------------------------------------------------------- tiles
  function renderTiles() {
    const ul = root.querySelector('[data-slot="tiles"]');
    const m = DATA.latest_month, prev = shiftMonth(m, -12);
    ul.innerHTML = "";
    const tile = (label, value, sub) => {
      const li = el("li");
      li.append(el("span", { class: "ict-tile__label" }, label), el("span", { class: "ict-tile__value" }, value));
      if (sub) li.append(el("span", { class: "ict-tile__sub" }, sub));
      ul.append(li);
    };
    ["fixed", "mobile"].forEach((net) => {
      const s = gi(AZ, net);
      const now = s.find((r) => r[0] === m), then = s.find((r) => r[0] === prev);
      const change = now && then ? ((now[1] / then[1] - 1) * 100) : null;
      tile(
        net === "fixed" ? "Fixed download" : "Mobile download",
        now ? `${now[1].toFixed(1)} Mbps` : "–",
        change == null ? "" : `${change >= 0 ? "+" : "−"}${Math.abs(change).toFixed(0)}% on ${monthLabel(prev)}`
      );
    });
    ["fixed", "mobile"].forEach((net) => {
      const list = latestFor(net);
      const pos = list.findIndex((d) => d.iso === AZ);
      const me = list[pos];
      tile(
        net === "fixed" ? "Fixed, CIS rank" : "Mobile, CIS rank",
        pos >= 0 ? `${ordinal(pos + 1)} of ${list.length}` : "–",
        me ? `${ordinal(me.rank)} in the world` : ""
      );
    });
    root.querySelector('[data-slot="asof"]').textContent = `Speedtest Global Index, ${monthLabel(m)}`;
    root.querySelector('[data-slot="rolling"]').textContent = DATA.rolling_from ? monthLabel(DATA.rolling_from) : "mid-2024";
  }

  // ---------------------------------------------------------------------- map
  function renderMap() {
    const fig = root.querySelector('[data-chart="map"]');
    const c = colours();
    const { plot, tip, width } = frame(fig);
    const list = latestFor(state.mapNet);
    const byIso = new Map(list.map((d) => [d.iso, d]));
    const height = Math.round(Math.min(420, width * 0.72));

    const focus = { type: "FeatureCollection", features: GEO.features.filter((f) => f.id !== "RUS") };
    const projection = d3.geoConicEqualArea().parallels([38, 50]).rotate([-58, 0])
      .fitExtent([[8, 8], [width - 8, height - 44]], focus);
    const path = d3.geoPath(projection);
    const ext = d3.extent(list, (d) => d.value);
    const colour = d3.scaleSequential(d3.interpolateLab(c.seqLo, c.seqHi)).domain(ext);

    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height)
      .attr("role", "img").attr("aria-label", `Map of median ${state.mapNet} download speed by country`);
    const pid = `ict-hatch-${state.mapNet}`;
    const pat = svg.append("defs").append("pattern").attr("id", pid).attr("width", 6).attr("height", 6)
      .attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)");
    pat.append("rect").attr("width", 6).attr("height", 6).attr("fill", c.surface);
    pat.append("line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 6).attr("stroke", c.rule).attr("stroke-width", 2);

    svg.append("g").selectAll("path").data(GEO.features).join("path")
      .attr("d", path)
      .attr("fill", (f) => (byIso.has(f.id) ? colour(byIso.get(f.id).value) : `url(#${pid})`))
      .attr("stroke", c.surface).attr("stroke-width", 1)
      .style("cursor", "default")
      .on("pointermove", function (ev, f) {
        const d = byIso.get(f.id);
        const [x, y] = d3.pointer(ev, plot);
        showTip(tip, plot, d
          ? `<strong>${d.name}</strong><br>${fmt(d.value, "Mbps")}<br><span>${ordinal(d.rank)} in the world</span>`
          : `<strong>${f.properties.name}</strong><br><span>Not in the latest Global Index</span>`, x, y);
        d3.select(this).attr("stroke", c.ink).attr("stroke-width", 1.5).raise();
      })
      .on("pointerleave", function (ev, f) {
        hideTip(tip);
        d3.select(this).attr("stroke", f.id === AZ ? c.ink : c.surface).attr("stroke-width", f.id === AZ ? 1.5 : 1);
      });
    svg.selectAll("path").filter((f) => f.id === AZ).attr("stroke", c.ink).attr("stroke-width", 1.5).raise();

    // Scale legend
    const lw = Math.min(220, width - 40), lx = 12, ly = height - 26;
    const gid = `ict-grad-${state.mapNet}`;
    const grad = svg.select("defs").append("linearGradient").attr("id", gid);
    d3.range(0, 1.01, 0.25).forEach((t) =>
      grad.append("stop").attr("offset", t).attr("stop-color", colour(ext[0] + t * (ext[1] - ext[0]))));
    svg.append("rect").attr("x", lx).attr("y", ly).attr("width", lw).attr("height", 8).attr("rx", 2).attr("fill", `url(#${gid})`);
    const lg = svg.append("g").attr("font-size", 11).attr("fill", c.muted);
    lg.append("text").attr("x", lx).attr("y", ly + 22).text(fmt(ext[0], "Mbps"));
    lg.append("text").attr("x", lx + lw).attr("y", ly + 22).attr("text-anchor", "end").text(fmt(ext[1], "Mbps"));
    lg.append("text").attr("x", lx + lw + 12).attr("y", ly + 8).text("Not in index").attr("dx", 16);
    svg.append("rect").attr("x", lx + lw + 12).attr("y", ly - 1).attr("width", 12).attr("height", 10)
      .attr("fill", `url(#${pid})`).attr("stroke", c.rule);
  }

  // --------------------------------------------------------------------- bars
  function renderBars() {
    const fig = root.querySelector('[data-chart="bars"]');
    const c = colours();
    const list = latestFor(state.mapNet);
    const { plot, tip, width, open } = frame(fig);
    const rowH = 30, m = { t: 4, r: 72, b: 8, l: 96 };
    const height = m.t + m.b + rowH * list.length;
    const x = d3.scaleLinear().domain([0, d3.max(list, (d) => d.value)]).nice().range([m.l, width - m.r]);
    const y = d3.scaleBand().domain(list.map((d) => d.iso)).range([m.t, height - m.b]).padding(0.38);

    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height)
      .attr("role", "img").attr("aria-label", `Countries ranked by median ${state.mapNet} download speed`);
    svg.append("line").attr("x1", m.l).attr("x2", m.l).attr("y1", m.t).attr("y2", height - m.b).attr("stroke", c.rule);

    const row = svg.append("g").selectAll("g").data(list).join("g");
    row.append("rect").attr("x", m.l).attr("y", (d) => y(d.iso))
      .attr("width", (d) => Math.max(1, x(d.value) - m.l)).attr("height", y.bandwidth())
      .attr("rx", 3).attr("fill", (d) => (d.iso === AZ ? c.az : c.other));
    row.append("text").attr("x", m.l - 10).attr("y", (d) => y(d.iso) + y.bandwidth() / 2).attr("dy", "0.35em")
      .attr("text-anchor", "end").attr("font-size", 13)
      .attr("fill", (d) => (d.iso === AZ ? c.ink : c.soft)).attr("font-weight", (d) => (d.iso === AZ ? 600 : 400))
      .text((d) => d.name);
    row.append("text").attr("x", (d) => x(d.value) + 6).attr("y", (d) => y(d.iso) + y.bandwidth() / 2).attr("dy", "0.35em")
      .attr("font-size", 12).attr("fill", c.muted).text((d) => fmt(d.value, "Mbps"));
    row.append("rect").attr("x", 0).attr("width", width).attr("y", (d) => y(d.iso) - (y.step() - y.bandwidth()) / 2)
      .attr("height", y.step()).attr("fill", "transparent")
      .on("pointermove", (ev, d) => {
        const [px, py] = d3.pointer(ev, plot);
        showTip(tip, plot, `<strong>${d.name}</strong><br>Download ${fmt(d.value, "Mbps")}<br>Upload ${fmt(d.up, "Mbps")}<br>Latency ${fmt(d.lat, "ms")}<br><span>${ordinal(d.rank)} in the world</span>`, px, py);
      })
      .on("pointerleave", () => hideTip(tip));

    const missing = DATA.countries.filter((cc) => !list.some((d) => d.iso === cc.iso3)).map((cc) => cc.name);
    if (missing.length) fig.append(el("figcaption", {}, `Not in ${monthLabel(DATA.latest_month)}: ${missing.join(", ")}.`));
    addTable(fig, ["Country", "Download (Mbps)", "Upload (Mbps)", "Latency (ms)", "World rank"],
      list.map((d) => [d.name, d.value, d.up, d.lat, d.rank]), open);
  }

  // -------------------------------------------------------- generic line chart
  /**
   * series: [{iso, name, points: [[xKey, value]...]}], xKeys: ordered domain,
   * refs: extra labelled reference series drawn in the reference ink.
   */
  function lineChart(fig, opt) {
    const c = colours();
    const nameOf = (id) => opt.series.find((s) => s.iso === id)?.name;
    const legend = [];
    if (nameOf(focus.primary)) legend.push({ label: nameOf(focus.primary), colour: c.az });
    if (nameOf(focus.secondary)) legend.push({ label: nameOf(focus.secondary), colour: c.cmp });
    (opt.refs || []).forEach((r) => legend.push({ label: r.name, colour: c.ref }));
    if (opt.series.some((s) => rankOf(s.iso) === 0))
      legend.push({ label: opt.otherLabel || "Other countries", colour: c.other, kind: "thin" });
    const { plot, tip, width, open } = frame(fig, { legend, caption: opt.caption });

    const height = Math.round(Math.max(260, Math.min(400, width * 0.5)));
    const m = { t: 16, r: width < 560 ? 16 : 118, b: 30, l: 48 };
    const keys = opt.xKeys;
    const x = d3.scalePoint().domain(keys).range([m.l, width - m.r]);
    const all = opt.series.concat(opt.refs || []);
    // Emphasised and reference series always fit; the grey background series
    // may be clipped above their 95th percentile so one sparse outlier does not
    // flatten everything else.
    const keyMax = d3.max(all.filter((s) => rankOf(s.iso) > 0 || (opt.refs || []).includes(s)),
      (s) => d3.max(s.points, (p) => p[1])) || 0;
    const background = opt.series.filter((s) => rankOf(s.iso) === 0).flatMap((s) => s.points.map((p) => p[1]));
    const bgMax = background.length ? d3.quantile(background.sort(d3.ascending), 0.95) : 0;
    const fullMax = d3.max(all, (s) => d3.max(s.points, (p) => p[1])) || 1;
    const ymax = opt.clipOutliers ? Math.max(keyMax, bgMax) || fullMax : fullMax;
    const y = d3.scaleLinear().domain([0, ymax]).nice().range([height - m.b, m.t]);
    const clipped = opt.clipOutliers && fullMax > y.domain()[1];

    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height).attr("role", "img").attr("aria-label", opt.aria);

    svg.append("g").attr("transform", `translate(${m.l},0)`)
      .call(d3.axisLeft(y).ticks(5).tickSize(-(width - m.l - m.r)).tickPadding(8))
      .call((g) => axisStyle(g, c));
    const every = Math.max(1, Math.ceil(keys.length / Math.max(3, Math.floor((width - m.l - m.r) / 90))));
    const tickKeys = keys.filter((k, i) => opt.tickFilter ? opt.tickFilter(k, i) : i % every === 0);
    svg.append("g").attr("transform", `translate(0,${height - m.b})`)
      .call(d3.axisBottom(x).tickValues(tickKeys).tickFormat((k) => opt.tickFormat(k, false)).tickSize(0).tickPadding(10))
      .call((g) => axisStyle(g, c));
    svg.append("text").attr("x", m.l).attr("y", m.t - 4).attr("font-size", 11).attr("fill", c.muted).text(opt.unit);

    if (opt.marker && x(opt.marker.key) != null) {
      const mx = x(opt.marker.key);
      svg.append("line").attr("x1", mx).attr("x2", mx).attr("y1", m.t).attr("y2", height - m.b)
        .attr("stroke", c.muted).attr("stroke-width", 1);
      svg.append("text").attr("x", mx + 6).attr("y", m.t + 10).attr("font-size", 11).attr("fill", c.muted)
        .text(opt.marker.label);
    }

    const line = d3.line().defined((p) => p[1] != null).x((p) => x(p[0])).y((p) => y(p[1]));
    const dense = (s) => {
      const map = new Map(s.points);
      const first = keys.indexOf(s.points[0]?.[0]);
      const last = keys.indexOf(s.points[s.points.length - 1]?.[0]);
      return keys.slice(first, last + 1).map((k) => [k, map.has(k) ? map.get(k) : null]);
    };

    const ordered = opt.series.slice().sort((a, b) => highlightOrder(a.iso, b.iso));
    const clipId = `ict-clip-${Math.random().toString(36).slice(2, 8)}`;
    svg.append("clipPath").attr("id", clipId).append("rect")
      .attr("x", 0).attr("y", m.t - 2).attr("width", width).attr("height", height - m.t - m.b + 4);
    const g = svg.append("g").attr("fill", "none").attr("stroke-linejoin", "round").attr("stroke-linecap", "round")
      .attr("clip-path", `url(#${clipId})`);
    if (clipped) {
      svg.append("text").attr("x", width - m.r).attr("y", m.t - 4).attr("text-anchor", "end")
        .attr("font-size", 11).attr("fill", c.muted).text("Some grey lines run above the chart");
    }
    ordered.forEach((s) => {
      const hi = rankOf(s.iso) > 0;
      const pts = dense(s);
      g.append("path").datum(pts).attr("d", line)
        .attr("stroke", seriesColour(s.iso, c)).attr("stroke-width", hi ? 2.25 : 1.1)
        .attr("opacity", hi ? 1 : 0.9);
      // isolated points (a lone month between gaps) would otherwise vanish
      pts.forEach((p, i) => {
        if (p[1] != null && (pts[i - 1]?.[1] == null) && (pts[i + 1]?.[1] == null))
          g.append("circle").attr("cx", x(p[0])).attr("cy", y(p[1])).attr("r", hi ? 3 : 2).attr("fill", seriesColour(s.iso, c));
      });
    });
    (opt.refs || []).forEach((r) => {
      g.append("path").datum(dense(r)).attr("d", line).attr("stroke", c.ref).attr("stroke-width", 1.75);
    });

    // Direct labels at the right-hand ends for highlighted and reference series
    if (m.r > 40) {
      const labels = ordered.filter((s) => rankOf(s.iso) > 0).map((s) => ({ s, colour: c.ink }))
        .concat((opt.refs || []).map((r) => ({ s: r, colour: c.muted })))
        .map((d) => {
          const lastP = d.s.points[d.s.points.length - 1];
          return lastP ? { ...d, x: x(lastP[0]), y: y(lastP[1]), y0: y(lastP[1]), v: lastP[1] } : null;
        })
        .filter(Boolean);
      dodge(labels, 15, m.t, height - m.b).forEach((d) => {
        svg.append("text").attr("x", width - m.r + 8).attr("y", d.y).attr("dy", "0.35em")
          .attr("font-size", 12).attr("fill", d.colour).attr("font-weight", d.s.iso === focus.primary ? 600 : 400)
          .text(`${d.s.name} ${opt.short(d.v)}`);
        svg.append("line").attr("x1", d.x + 4).attr("x2", width - m.r + 4).attr("y1", d.y0).attr("y2", d.y)
          .attr("stroke", c.rule);
      });
    }

    // Crosshair and tooltip
    const cross = svg.append("line").attr("y1", m.t).attr("y2", height - m.b).attr("stroke", c.muted)
      .attr("stroke-width", 1).attr("visibility", "hidden");
    const dots = svg.append("g");
    svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", width - m.l - m.r).attr("height", height - m.t - m.b)
      .attr("fill", "transparent")
      .on("pointermove", (ev) => {
        const [px, py] = d3.pointer(ev, plot);
        const i = Math.round((px - m.l) / (x.step() || 1));
        const key = keys[Math.max(0, Math.min(keys.length - 1, i))];
        cross.attr("x1", x(key)).attr("x2", x(key)).attr("visibility", "visible");
        const rows = all
          .map((s) => ({ s, v: new Map(s.points).get(key) }))
          .filter((d) => d.v != null)
          .sort((a, b) => b.v - a.v);
        dots.selectAll("*").remove();
        rows.filter((d) => rankOf(d.s.iso) > 0 || (opt.refs || []).includes(d.s)).forEach((d) => {
          dots.append("circle").attr("cx", x(key)).attr("cy", y(d.v)).attr("r", 4)
            .attr("fill", (opt.refs || []).includes(d.s) ? c.ref : seriesColour(d.s.iso, c))
            .attr("stroke", c.surface).attr("stroke-width", 2);
        });
        const body = rows.map((d) => {
          const strong = rankOf(d.s.iso) > 0;
          return `<div class="ict-tip__row${strong ? " is-strong" : ""}"><span>${d.s.name}</span><span>${opt.short(d.v)}</span></div>`;
        }).join("");
        showTip(tip, plot, `<div class="ict-tip__head">${opt.tickFormat(key, true)}</div>${body || "<span>No data</span>"}`, px, py);
      })
      .on("pointerleave", () => { cross.attr("visibility", "hidden"); dots.selectAll("*").remove(); hideTip(tip); });

    if (opt.table) addTable(fig, opt.table.headers, opt.table.rows, open);
  }

  // -------------------------------------------------------------------- trend
  function renderTrend() {
    countryFocus();
    const fig = root.querySelector('[data-chart="trend"]');
    const met = METRIC[state.trendMetric];
    const series = DATA.countries.map((cc) => ({
      iso: cc.iso3, name: cc.name,
      points: gi(cc.iso3, state.trendNet).map((r) => [r[0], r[met.idx]]).filter((p) => p[1] != null),
    })).filter((s) => s.points.length);
    const months = monthGrid(d3.min(series, (s) => s.points[0][0]), DATA.latest_month);
    const tableKeys = months.slice().reverse();
    const az = new Map(series.find((s) => s.iso === AZ)?.points || []);
    const cmp = new Map(series.find((s) => s.iso === state.compare)?.points || []);
    lineChart(fig, {
      series, xKeys: months,
      unit: `${met.label}, ${met.unit}${met.better === "lower" ? " (lower is better)" : ""}`,
      aria: `${met.label} by month, ${state.trendNet} networks`,
      tickFormat: (k, long) => (long || k.endsWith("-07") ? monthLabel(k) : k.slice(0, 4)),
      tickFilter: (k) => k.endsWith("-01") || k.endsWith("-07"),
      short: (v) => fmt(v, met.unit),
      marker: DATA.rolling_from ? { key: DATA.rolling_from, label: "Rolling three-month figures" } : null,
      caption: "",
      table: {
        headers: ["Month", "Azerbaijan", NAME[state.compare] || "Comparison"],
        rows: tableKeys.filter((k) => az.has(k) || cmp.has(k)).map((k) => [monthLabel(k), az.get(k), cmp.get(k)]),
      },
    });
  }

  // -------------------------------------------------------------------- slope
  function renderSlope(net) {
    countryFocus();
    const fig = root.querySelector(`[data-chart="slope-${net}"]`);
    const c = colours();
    const end = DATA.latest_month, start = shiftMonth(end, -12);
    const rows = DATA.countries.map((cc) => {
      const s = new Map(gi(cc.iso3, net).map((r) => [r[0], r[4]]));
      return s.has(end) && s.has(start) ? { iso: cc.iso3, name: cc.name, a: s.get(start), b: s.get(end) } : null;
    }).filter(Boolean);
    const { plot, tip, width, open } = frame(fig);
    const title = el("p", { class: "ict-figure__title" }, net === "fixed" ? "Fixed broadband" : "Mobile");
    fig.prepend(title);
    const height = 320, m = { t: 30, r: Math.min(150, width * 0.42), b: 12, l: 52 };
    const ext = d3.extent(rows.flatMap((d) => [d.a, d.b]));
    const y = d3.scaleLinear().domain([ext[0] - 3, ext[1] + 3]).range([m.t, height - m.b]);
    const xa = m.l, xb = width - m.r;
    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`).attr("width", width).attr("height", height)
      .attr("role", "img").attr("aria-label", `World rank by ${net} median download, ${monthLabel(start)} and ${monthLabel(end)}`);
    [[xa, monthLabel(start), "start"], [xb, monthLabel(end), "end"]].forEach(([xx, t, anchor]) => {
      svg.append("line").attr("x1", xx).attr("x2", xx).attr("y1", m.t - 6).attr("y2", height - m.b).attr("stroke", c.rule);
      svg.append("text").attr("x", xx).attr("y", 12).attr("text-anchor", anchor).attr("font-size", 11).attr("fill", c.muted).text(t);
    });
    rows.sort((p, q) => highlightOrder(p.iso, q.iso)).forEach((d) => {
      const hi = rankOf(d.iso) > 0, col = seriesColour(d.iso, c);
      const g = svg.append("g");
      g.append("line").attr("x1", xa).attr("x2", xb).attr("y1", y(d.a)).attr("y2", y(d.b))
        .attr("stroke", col).attr("stroke-width", hi ? 2.25 : 1.1);
      [[xa, d.a], [xb, d.b]].forEach(([xx, v]) =>
        g.append("circle").attr("cx", xx).attr("cy", y(v)).attr("r", hi ? 4 : 2.5).attr("fill", col)
          .attr("stroke", c.surface).attr("stroke-width", 2));
      if (hi) g.append("text").attr("x", xa - 8).attr("y", y(d.a)).attr("dy", "0.35em").attr("text-anchor", "end")
        .attr("font-size", 12).attr("fill", c.ink).text(d.a);
      g.append("line").attr("x1", xa).attr("x2", xb).attr("y1", y(d.a)).attr("y2", y(d.b))
        .attr("stroke", "transparent").attr("stroke-width", 12)
        .on("pointermove", (ev) => {
          const [px, py] = d3.pointer(ev, plot);
          const delta = d.a - d.b;
          showTip(tip, plot, `<strong>${d.name}</strong><br>${ordinal(d.a)} → ${ordinal(d.b)}<br><span>${delta === 0 ? "no change" : `${Math.abs(delta)} places ${delta > 0 ? "up" : "down"}`}</span>`, px, py);
        })
        .on("pointerleave", () => hideTip(tip));
    });
    const labels = dodge(rows.map((d) => ({ d, y: y(d.b) })), 14, m.t, height - m.b);
    labels.forEach(({ d, y: ly }) => {
      svg.append("text").attr("x", xb + 10).attr("y", ly).attr("dy", "0.35em").attr("font-size", 12)
        .attr("fill", rankOf(d.iso) > 0 ? c.ink : c.muted).attr("font-weight", d.iso === AZ ? 600 : 400)
        .text(`${d.b}  ${d.name}`);
    });
    addTable(fig, ["Country", `Rank ${monthLabel(start)}`, `Rank ${monthLabel(end)}`],
      rows.slice().sort((p, q) => p.b - q.b).map((d) => [d.name, d.a, d.b]), open);
  }

  // ------------------------------------------------------ Azerbaijan regions
  const qLabel = (k) => k.replace("-", " ");
  const azSeries = (id, net) => AZD.series[id]?.[net] || [];   // [q, down, up, lat, median, tests]
  const azRow = (id, net, q) => azSeries(id, net).find((r) => r[0] === q);
  const azName = (id) => AZD.regions.find((r) => r.id === id)?.name || id;

  function fillQuarters() {
    const sel = root.querySelector('select[data-ctl="az-quarter"]');
    const quarters = AZD.quarters[state.azNet];
    if (!state.azQuarter || !quarters.includes(state.azQuarter)) state.azQuarter = quarters[quarters.length - 1];
    sel.innerHTML = "";
    quarters.slice().reverse().forEach((q) => {
      const o = el("option", { value: q }, qLabel(q));
      if (q === state.azQuarter) o.selected = true;
      sel.append(o);
    });
  }

  function azRows() {
    return AZD.regions.map((r) => {
      const row = azRow(r.id, state.azNet, state.azQuarter);
      return {
        id: r.id, name: r.name, kind: r.kind,
        value: row ? row[1] : null, up: row?.[2], lat: row?.[3], median: row?.[4], tests: row ? row[5] : 0,
        reliable: !!row && row[5] >= AZD.min_tests,
      };
    });
  }

  function renderAzMap() {
    const fig = root.querySelector('[data-chart="az-map"]');
    const c = colours();
    const { plot, tip, width } = frame(fig);
    const rows = azRows();
    const byId = new Map(rows.map((d) => [d.id, d]));
    const shown = rows.filter((d) => d.reliable);
    const height = Math.round(Math.min(440, width * 0.78));
    const projection = d3.geoMercator().fitExtent([[8, 8], [width - 8, height - 48]], AZGEO);
    const path = d3.geoPath(projection);
    const ext = d3.extent(shown, (d) => d.value);
    const colour = d3.scaleSequentialLog(d3.interpolateLab(c.seqLo, c.seqHi)).domain(ext);

    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height).attr("role", "img")
      .attr("aria-label", `Map of average ${state.azNet} download speed by city and district, ${qLabel(state.azQuarter)}`);
    const pid = `az-hatch-${state.azNet}`;
    const pat = svg.append("defs").append("pattern").attr("id", pid).attr("width", 6).attr("height", 6)
      .attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)");
    pat.append("rect").attr("width", 6).attr("height", 6).attr("fill", c.surface);
    pat.append("line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 6).attr("stroke", c.rule).attr("stroke-width", 2);

    const stroke = (f) => (f.id === state.azRegion ? c.ink : c.surface);
    svg.append("g").selectAll("path").data(AZGEO.features).join("path")
      .attr("d", path)
      .attr("fill", (f) => { const d = byId.get(f.id); return d?.reliable ? colour(d.value) : `url(#${pid})`; })
      .attr("stroke", stroke).attr("stroke-width", (f) => (f.id === state.azRegion ? 1.75 : 0.75))
      .style("cursor", "pointer")
      .on("pointermove", function (ev, f) {
        const d = byId.get(f.id);
        const [x, y] = d3.pointer(ev, plot);
        const kind = d.kind === "city" ? "city" : "district";
        const body = d.reliable
          ? `${fmt(d.value, "Mbps")} average download<br><span>${d.tests.toLocaleString("en")} tests</span>`
          : `<span>${d.tests ? `Only ${d.tests} tests this quarter` : "No tests this quarter"}</span>`;
        showTip(tip, plot, `<strong>${d.name}</strong> <span>${kind}</span><br>${body}`, x, y);
        d3.select(this).attr("stroke", c.ink).attr("stroke-width", 1.75).raise();
      })
      .on("pointerleave", function (ev, f) {
        hideTip(tip);
        d3.select(this).attr("stroke", stroke(f)).attr("stroke-width", f.id === state.azRegion ? 1.75 : 0.75);
        svg.selectAll("path").filter((g) => g.id === state.azRegion).raise();
      })
      .on("click", (ev, f) => selectRegion(f.id));
    svg.selectAll("path").filter((f) => f.id === state.azRegion).raise();

    // Scale legend (logarithmic, since city and rural speeds differ by an order of magnitude)
    const lw = Math.min(220, width - 150), lx = 12, ly = height - 30;
    const gid = `az-grad-${state.azNet}`;
    const grad = svg.select("defs").append("linearGradient").attr("id", gid);
    d3.range(0, 1.01, 0.25).forEach((t) =>
      grad.append("stop").attr("offset", t).attr("stop-color", colour(ext[0] * Math.pow(ext[1] / ext[0], t))));
    svg.append("rect").attr("x", lx).attr("y", ly).attr("width", lw).attr("height", 8).attr("rx", 2).attr("fill", `url(#${gid})`);
    const lg = svg.append("g").attr("font-size", 11).attr("fill", c.muted);
    lg.append("text").attr("x", lx).attr("y", ly + 22).text(fmt(ext[0], "Mbps"));
    lg.append("text").attr("x", lx + lw).attr("y", ly + 22).attr("text-anchor", "end").text(fmt(ext[1], "Mbps"));
    svg.append("rect").attr("x", lx + lw + 16).attr("y", ly - 1).attr("width", 12).attr("height", 10)
      .attr("fill", `url(#${pid})`).attr("stroke", c.rule);
    lg.append("text").attr("x", lx + lw + 34).attr("y", ly + 8).text("Too few tests");
    fig.append(el("figcaption", {}, "Select a city or district on the map to follow it over time below."));
  }

  function renderAzBars() {
    const fig = root.querySelector('[data-chart="az-bars"]');
    const c = colours();
    const rows = azRows();
    const cities = rows.filter((d) => d.kind === "city" && d.reliable).sort((a, b) => b.value - a.value);
    const national = AZD.national[state.azNet].find((r) => r[0] === state.azQuarter);
    const { plot, tip, width, open } = frame(fig);
    fig.prepend(el("p", { class: "ict-figure__title" }, `Cities, ${qLabel(state.azQuarter)}`));
    const rowH = 28, m = { t: 4, r: 72, b: 8, l: 104 };
    const height = m.t + m.b + rowH * cities.length;
    const max = d3.max(cities, (d) => d.value) || 1;
    const x = d3.scaleLinear().domain([0, Math.max(max, national ? national[1] : 0)]).nice().range([m.l, width - m.r]);
    const y = d3.scaleBand().domain(cities.map((d) => d.id)).range([m.t, height - m.b]).padding(0.38);
    const svg = d3.select(plot).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width).attr("height", height).attr("role", "img")
      .attr("aria-label", `Cities of Azerbaijan ranked by average ${state.azNet} download speed`);
    svg.append("line").attr("x1", m.l).attr("x2", m.l).attr("y1", m.t).attr("y2", height - m.b).attr("stroke", c.rule);
    if (national) {
      const nx = x(national[1]);
      svg.append("line").attr("x1", nx).attr("x2", nx).attr("y1", m.t).attr("y2", height - m.b)
        .attr("stroke", c.ref).attr("stroke-width", 1.25);
    }
    const row = svg.append("g").selectAll("g").data(cities).join("g");
    row.append("rect").attr("x", m.l).attr("y", (d) => y(d.id))
      .attr("width", (d) => Math.max(1, x(d.value) - m.l)).attr("height", y.bandwidth())
      .attr("rx", 3).attr("fill", (d) => (d.id === state.azRegion ? c.az : c.other));
    row.append("text").attr("x", m.l - 10).attr("y", (d) => y(d.id) + y.bandwidth() / 2).attr("dy", "0.35em")
      .attr("text-anchor", "end").attr("font-size", 13)
      .attr("fill", (d) => (d.id === state.azRegion ? c.ink : c.soft))
      .attr("font-weight", (d) => (d.id === state.azRegion ? 600 : 400)).text((d) => d.name);
    row.append("text").attr("class", "ict-halo").attr("x", (d) => x(d.value) + 6).attr("y", (d) => y(d.id) + y.bandwidth() / 2).attr("dy", "0.35em")
      .attr("font-size", 12).attr("fill", c.muted).text((d) => fmt(d.value, "Mbps"));
    row.append("rect").attr("x", 0).attr("width", width).attr("y", (d) => y(d.id) - (y.step() - y.bandwidth()) / 2)
      .attr("height", y.step()).attr("fill", "transparent").style("cursor", "pointer")
      .on("pointermove", (ev, d) => {
        const [px, py] = d3.pointer(ev, plot);
        showTip(tip, plot, `<strong>${d.name}</strong><br>Download ${fmt(d.value, "Mbps")}<br>Upload ${fmt(d.up, "Mbps")}<br>Latency ${fmt(d.lat, "ms")}<br><span>${d.tests.toLocaleString("en")} tests</span>`, px, py);
      })
      .on("pointerleave", () => hideTip(tip))
      .on("click", (ev, d) => selectRegion(d.id));
    if (national) {
      const leg = el("ul", { class: "ict-legend" });
      const li = el("li");
      const sw = el("span", { class: "ict-swatch ict-swatch--rule" });
      sw.style.setProperty("--sw", c.ref);
      li.append(sw, document.createTextNode(`Azerbaijan overall, ${fmt(national[1], "Mbps")}`));
      leg.append(li);
      fig.insertBefore(leg, plot);
    }
    const all = rows.slice().sort((a, b) => (b.value ?? -1) - (a.value ?? -1));
    addTable(fig, ["City or district", "Download (Mbps)", "Upload (Mbps)", "Latency (ms)", "Median tile (Mbps)", "Tests"],
      all.map((d) => [d.name + (d.kind === "city" ? " (city)" : ""), d.value, d.up, d.lat, d.median, d.tests]), open);
  }

  function renderAzTrend() {
    const fig = root.querySelector('[data-chart="az-trend"]');
    focus = { primary: state.azRegion, secondary: null };
    const net = state.azNet;
    const cities = AZD.regions.filter((r) => r.kind === "city" || r.id === state.azRegion);
    const ok = (r) => r[5] >= AZD.min_tests;
    const series = cities.map((r) => ({
      iso: r.id, name: r.name, points: azSeries(r.id, net).filter(ok).map((p) => [p[0], p[1]]),
    })).filter((s) => s.points.length);
    const refs = [{ iso: "AZE", name: "Azerbaijan overall", points: AZD.national[net].map((p) => [p[0], p[1]]) }];
    const keys = AZD.quarters[net];
    const sel = new Map(azSeries(state.azRegion, net).map((p) => [p[0], p]));
    lineChart(fig, {
      series, refs, xKeys: keys,
      otherLabel: "Other cities",
      clipOutliers: true,
      unit: `Average ${net} download speed, Mbps`,
      aria: `Quarterly average ${net} download speed in ${azName(state.azRegion)} since 2019`,
      tickFormat: (k, long) => (long ? qLabel(k) : k.slice(0, 4)),
      tickFilter: (k) => k.endsWith("Q1"),
      short: (v) => fmt(v, "Mbps"),
      table: {
        headers: ["Quarter", `${azName(state.azRegion)} (Mbps)`, "Tests", "Azerbaijan overall (Mbps)"],
        rows: keys.slice().reverse().map((k) => {
          const p = sel.get(k), n = AZD.national[net].find((r) => r[0] === k);
          return [qLabel(k), p ? p[1] : null, p ? p[5] : 0, n ? n[1] : null];
        }),
      },
    });
    countryFocus();
  }

  function selectRegion(id) {
    state.azRegion = id;
    root.querySelector('select[data-ctl="az-region"]').value = id;
    renderAzMap();
    renderAzBars();
    renderAzTrend();
  }

  function bindAzControls() {
    fillQuarters();
    root.querySelector('select[data-ctl="az-quarter"]').addEventListener("change", (e) => {
      state.azQuarter = e.target.value;
      renderAzMap();
      renderAzBars();
    });
    const sel = root.querySelector('select[data-ctl="az-region"]');
    const groups = [["city", "Cities"], ["district", "Districts"]];
    groups.forEach(([kind, label]) => {
      const og = el("optgroup", { label });
      AZD.regions.filter((r) => r.kind === kind).sort((a, b) => a.name.localeCompare(b.name))
        .forEach((r) => og.append(el("option", { value: r.id }, r.name)));
      sel.append(og);
    });
    sel.value = state.azRegion;
    sel.addEventListener("change", () => selectRegion(sel.value));
    root.querySelector('[data-slot="min-tests"]').textContent = AZD.min_tests;
    const odl = document.querySelector('[data-slot="od-latest"]');
    const qs = AZD.quarters.fixed;
    if (odl && qs.length) odl.textContent = qLabel(qs[qs.length - 1]);
  }

  // ----------------------------------------------------------------- adoption
  function renderAdopt() {
    countryFocus();
    const fig = root.querySelector('[data-chart="adopt"]');
    const ds = DATA.adoption[state.adopt];
    const series = DATA.countries.map((cc) => ({
      iso: cc.iso3, name: cc.name, points: (ds.series[cc.iso3] || []).map((r) => [String(r[0]), r[1]]).filter((p) => p[1] != null),
    })).filter((s) => s.points.length);
    const refs = [["WLD", "World"]].map(([code, name]) => ({
      iso: code, name, points: (ds.series[code] || []).map((r) => [String(r[0]), r[1]]).filter((p) => p[1] != null),
    })).filter((s) => s.points.length);
    const keys = Array.from(new Set(series.concat(refs).flatMap((s) => s.points.map((p) => p[0])))).sort();
    const unitShort = ds.unit.startsWith("%") ? "%" : "";
    const short = (v) => (unitShort ? `${Math.round(v)}%` : v.toFixed(1));
    root.querySelector('[data-slot="adopt-note"]').textContent =
      `${ds.label}, ${ds.unit}. Annual ITU and World Bank figures; the latest year is usually one or two years behind.`;
    const az = new Map(series.find((s) => s.iso === AZ)?.points || []);
    const cmp = new Map(series.find((s) => s.iso === state.compare)?.points || []);
    const wld = new Map(refs[0]?.points || []);
    lineChart(fig, {
      series, refs, xKeys: keys,
      unit: `${ds.label}, ${ds.unit}`,
      aria: `${ds.label} since 2000`,
      tickFormat: (k) => k,
      tickFilter: (k) => Number(k) % 5 === 0,
      short,
      table: {
        headers: ["Year", "Azerbaijan", NAME[state.compare] || "Comparison", "World"],
        rows: keys.slice().reverse().map((k) => [k, az.get(k), cmp.get(k), wld.get(k)]),
      },
    });
  }

  // --------------------------------------------------------------------- IPv6
  function renderIpv6() {
    countryFocus();
    const fig = root.querySelector('[data-chart="ipv6"]');
    const v6 = DATA.ipv6 || {};
    const series = DATA.countries.map((cc) => ({
      iso: cc.iso3, name: cc.name, points: (v6[cc.iso3] || []).map((r) => [r[0], r[1]]),
    })).filter((s) => s.points.length);
    const refs = v6.WLD ? [{ iso: "WLD", name: "World", points: v6.WLD.map((r) => [r[0], r[1]]) }] : [];
    const first = d3.min(series.concat(refs), (s) => s.points[0][0]);
    const last = d3.max(series.concat(refs), (s) => s.points[s.points.length - 1][0]);
    const months = monthGrid(first, last);
    const az = new Map(v6[AZ] || []), cmp = new Map(v6[state.compare] || []), wld = new Map(v6.WLD || []);
    const pct = (v) => (v == null ? "–" : `${v < 10 ? v.toFixed(1) : Math.round(v)}%`);
    lineChart(fig, {
      series, refs, xKeys: months,
      unit: "IPv6-capable users, % of all measured",
      aria: "Share of users able to use IPv6, by month",
      tickFormat: (k, long) => (long ? monthLabel(k) : k.slice(0, 4)),
      tickFilter: (k) => k.endsWith("-01") && Number(k.slice(0, 4)) % 2 === 1,
      short: pct,
      table: {
        headers: ["Month", "Azerbaijan (%)", `${NAME[state.compare] || "Comparison"} (%)`, "World (%)"],
        rows: months.slice().reverse().map((k) => [monthLabel(k), az.get(k), cmp.get(k), wld.get(k)]),
      },
    });
  }

  // ------------------------------------------------------------------ wiring
  function renderAll() {
    renderTiles();
    renderMap();
    renderBars();
    renderTrend();
    renderSlope("fixed");
    renderSlope("mobile");
    renderAdopt();
    renderIpv6();
    renderAzMap();
    renderAzBars();
    renderAzTrend();
  }

  function bindControls() {
    const map = {
      "map-net": (v) => { state.mapNet = v; renderMap(); renderBars(); },
      "trend-net": (v) => { state.trendNet = v; renderTrend(); },
      "trend-metric": (v) => { state.trendMetric = v; renderTrend(); },
      "az-net": (v) => { state.azNet = v; fillQuarters(); renderAzMap(); renderAzBars(); renderAzTrend(); },
      adopt: (v) => { state.adopt = v; renderAdopt(); },
    };
    root.querySelectorAll("button[data-ctl]").forEach((b) => {
      b.addEventListener("click", () => {
        root.querySelectorAll(`button[data-ctl="${b.dataset.ctl}"]`).forEach((o) =>
          o.setAttribute("aria-pressed", String(o === b)));
        map[b.dataset.ctl](b.dataset.value);
      });
    });
    const sel = root.querySelector('select[data-ctl="compare"]');
    sel.append(el("option", { value: "" }, "No comparison"));
    DATA.countries.filter((cc) => cc.iso3 !== AZ).forEach((cc) => {
      const o = el("option", { value: cc.iso3 }, cc.name + (cc.discontinued ? " (to 2025)" : ""));
      if (cc.iso3 === state.compare) o.selected = true;
      sel.append(o);
    });
    sel.addEventListener("change", () => {
      state.compare = sel.value;
      renderTrend(); renderSlope("fixed"); renderSlope("mobile"); renderAdopt(); renderIpv6();
    });

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

  Promise.all([
    d3.json(root.dataset.src), d3.json(root.dataset.map),
    d3.json(root.dataset.azSrc), d3.json(root.dataset.azMap),
  ])
    .then(([data, geo, az, azgeo]) => {
      DATA = data;
      GEO = geo;
      AZD = az;
      AZGEO = azgeo;
      DATA.countries.forEach((cc) => (NAME[cc.iso3] = cc.name));
      root.classList.add("is-ready");
      bindControls();
      bindAzControls();
      renderAll();
    })
    .catch((err) => {
      console.error(err);
      root.prepend(el("p", { class: "ict-error" }, "The data could not be loaded. Please try again later."));
    });
})();
