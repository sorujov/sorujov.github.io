---
title: "Internet in the CIS region"
excerpt: "Broadband and mobile speeds, rankings, projections and adoption across twelve post-Soviet countries, with Azerbaijan city by city, updated monthly from public Ookla, ITU and APNIC data."
collection: portfolio
share: false
ict_page: true
---

<p class="ict-lead">How fast is the internet in Azerbaijan and its neighbours, how is it changing, and where is it heading? This page compares twelve countries of the former Soviet Union, looks inside Azerbaijan city by city, and is refreshed automatically from public sources.</p>

<p class="ict-disclaimer">A personal project. The figures are Ookla's, the ITU's and APNIC's, not official statistics of the Information and Communication Technologies Agency, and the views are my own.</p>

<nav class="ict-toc" aria-label="On this page">
  <a href="#ict-now">At a glance</a>
  <a href="#ict-map-h">Region</a>
  <a href="#ict-trend-h">Monthly trend</a>
  <a href="#ict-fc-h">Projection</a>
  <a href="#ict-rank-h">Rankings</a>
  <a href="#ict-az-h">Azerbaijan by city</a>
  <a href="#ict-adopt-h">Adoption</a>
  <a href="#ict-v6-h">IPv6</a>
  <a href="#ict-sources">Sources</a>
</nav>

<div class="ict" id="ict" data-src="{{ '/assets/data/ict/ict.json' | relative_url }}" data-map="{{ '/assets/data/ict/countries.json' | relative_url }}" data-az-src="{{ '/assets/data/ict/az_regions.json' | relative_url }}" data-az-map="{{ '/assets/data/ict/az_map.json' | relative_url }}" data-fc-src="{{ '/assets/data/ict/forecast.json' | relative_url }}">

<noscript><p>The charts on this page need JavaScript. The underlying data is linked under <a href="#ict-sources">Sources</a>.</p></noscript>

<section class="ict-section" aria-labelledby="ict-now">
  <div class="ict-section__head">
    <h2 id="ict-now">Azerbaijan at a glance</h2>
    <p class="ict-meta" data-slot="asof"></p>
  </div>
  <ul class="ict-tiles" data-slot="tiles"></ul>
</section>

<section class="ict-section" aria-labelledby="ict-map-h">
  <div class="ict-section__head">
    <h2 id="ict-map-h">Where the region stands</h2>
  </div>
  <div class="ict-toolbar">
    <div class="ict-group" role="group" aria-label="Network"><span class="ict-group__label">Network</span>
      <button type="button" data-ctl="map-net" data-value="fixed">Fixed</button>
      <button type="button" data-ctl="map-net" data-value="mobile">Mobile</button>
    </div>
    <div class="ict-group" role="group" aria-label="Statistic"><span class="ict-group__label">Statistic</span>
      <button type="button" data-ctl="map-stat" data-value="median">Median</button>
      <button type="button" data-ctl="map-stat" data-value="mean">Mean</button>
    </div>
    <div class="ict-group" role="group" aria-label="Measure"><span class="ict-group__label">Measure</span>
      <button type="button" data-ctl="map-measure" data-value="download">Download</button>
      <button type="button" data-ctl="map-measure" data-value="upload">Upload</button>
      <button type="button" data-ctl="map-measure" data-value="latency">Latency</button>
    </div>
    <label class="ict-select"><span class="ict-group__label">Month</span>
      <select data-ctl="map-month"></select>
    </label>
  </div>
  <p class="ict-note">Speedtest Global Index, any month since June 2023. Darker means better, for latency as for speed. Countries without a figure for the chosen month are hatched; Belarus and Russia appear up to April 2025.</p>
  <div class="ict-split">
    <figure class="ict-figure ict-figure--map" data-chart="map"></figure>
    <figure class="ict-figure" data-chart="bars"></figure>
  </div>
</section>

<section class="ict-section" aria-labelledby="ict-trend-h">
  <div class="ict-section__head">
    <h2 id="ict-trend-h">Speeds month by month</h2>
  </div>
  <div class="ict-toolbar">
    <div class="ict-group" role="group" aria-label="Network"><span class="ict-group__label">Network</span>
      <button type="button" data-ctl="trend-net" data-value="fixed">Fixed</button>
      <button type="button" data-ctl="trend-net" data-value="mobile">Mobile</button>
    </div>
    <div class="ict-group" role="group" aria-label="Statistic"><span class="ict-group__label">Statistic</span>
      <button type="button" data-ctl="trend-stat" data-value="median">Median</button>
      <button type="button" data-ctl="trend-stat" data-value="mean">Mean</button>
    </div>
    <div class="ict-group" role="group" aria-label="Measure"><span class="ict-group__label">Measure</span>
      <button type="button" data-ctl="trend-measure" data-value="download">Download</button>
      <button type="button" data-ctl="trend-measure" data-value="upload">Upload</button>
      <button type="button" data-ctl="trend-measure" data-value="latency">Latency</button>
    </div>
    <div class="ict-group" role="group" aria-label="Period"><span class="ict-group__label">Period</span>
      <button type="button" data-ctl="trend-range" data-value="1y">1 year</button>
      <button type="button" data-ctl="trend-range" data-value="3y">3 years</button>
      <button type="button" data-ctl="trend-range" data-value="all">All</button>
    </div>
    <label class="ict-select"><span class="ict-group__label">Compare with</span>
      <select data-ctl="compare"></select>
    </label>
  </div>
  <p class="ict-note">From <span data-slot="rolling"></span> Ookla reports each month as a rolling three-month figure, which smooths the series. Hover a grey line to see which country it is, and click it to compare.</p>
  <figure class="ict-figure" data-chart="trend"></figure>
</section>

<section class="ict-section" aria-labelledby="ict-fc-h">
  <div class="ict-section__head">
    <h2 id="ict-fc-h">Where the trend points</h2>
  </div>
  <div class="ict-toolbar">
    <label class="ict-select"><span class="ict-group__label">Country</span>
      <select data-ctl="fc-country"></select>
    </label>
    <div class="ict-group" role="group" aria-label="Network"><span class="ict-group__label">Network</span>
      <button type="button" data-ctl="fc-net" data-value="fixed">Fixed</button>
      <button type="button" data-ctl="fc-net" data-value="mobile">Mobile</button>
    </div>
    <div class="ict-group" role="group" aria-label="Statistic"><span class="ict-group__label">Statistic</span>
      <button type="button" data-ctl="fc-stat" data-value="median">Median</button>
      <button type="button" data-ctl="fc-stat" data-value="mean">Mean</button>
    </div>
    <div class="ict-group" role="group" aria-label="Measure"><span class="ict-group__label">Measure</span>
      <button type="button" data-ctl="fc-measure" data-value="download">Download</button>
      <button type="button" data-ctl="fc-measure" data-value="upload">Upload</button>
      <button type="button" data-ctl="fc-measure" data-value="latency">Latency</button>
    </div>
    <div class="ict-group" role="group" aria-label="Horizon"><span class="ict-group__label">Horizon</span>
      <button type="button" data-ctl="fc-horizon" data-value="6">6 months</button>
      <button type="button" data-ctl="fc-horizon" data-value="12">12</button>
      <button type="button" data-ctl="fc-horizon" data-value="24">24</button>
    </div>
    <div class="ict-group" role="group" aria-label="Interval"><span class="ict-group__label">Interval</span>
      <button type="button" data-ctl="fc-level" data-value="80">80%</button>
      <button type="button" data-ctl="fc-level" data-value="90">90%</button>
      <button type="button" data-ctl="fc-level" data-value="95">95%</button>
    </div>
  </div>
  <p class="ict-note">An ARIMA model with a linear trend, chosen by AIC and refitted every month. The shaded band is the model's interval; with only a few years of data, read the band rather than the central line.</p>
  <div class="ict-split ict-split--aside">
    <figure class="ict-figure" data-chart="forecast"></figure>
    <aside class="ict-aside" data-slot="fc-summary" aria-live="polite"></aside>
  </div>
</section>

<section class="ict-section" aria-labelledby="ict-rank-h">
  <div class="ict-section__head">
    <h2 id="ict-rank-h">Global rank, a year apart</h2>
  </div>
  <div class="ict-toolbar">
    <label class="ict-select"><span class="ict-group__label">Period</span>
      <select data-ctl="rank-month"></select>
    </label>
  </div>
  <p class="ict-note">Position in Ookla's worldwide ranking by median download speed; a line rising to the right is an improvement. Click a line to compare that country.</p>
  <div class="ict-split ict-split--even">
    <figure class="ict-figure" data-chart="slope-fixed"></figure>
    <figure class="ict-figure" data-chart="slope-mobile"></figure>
  </div>
</section>

<section class="ict-section" aria-labelledby="ict-az-h">
  <div class="ict-section__head">
    <h2 id="ict-az-h">Azerbaijan, city by city</h2>
  </div>
  <div class="ict-toolbar">
    <div class="ict-group" role="group" aria-label="Network"><span class="ict-group__label">Network</span>
      <button type="button" data-ctl="az-net" data-value="fixed">Fixed</button>
      <button type="button" data-ctl="az-net" data-value="mobile">Mobile</button>
    </div>
    <div class="ict-group" role="group" aria-label="Measure"><span class="ict-group__label">Measure</span>
      <button type="button" data-ctl="az-measure" data-value="download">Average download</button>
      <button type="button" data-ctl="az-measure" data-value="median">Median tile</button>
      <button type="button" data-ctl="az-measure" data-value="upload">Upload</button>
      <button type="button" data-ctl="az-measure" data-value="latency">Latency</button>
    </div>
    <label class="ict-select"><span class="ict-group__label">Quarter</span>
      <select data-ctl="az-quarter"></select>
    </label>
  </div>
  <p class="ict-note">Azerbaijan's 78 cities and districts, from Ookla Open Data. Ookla publishes these data as map tiles of roughly 600 metres; each tile is placed in the city or district that contains it. The average weights tiles by their number of tests; the median tile is the middle of the tile averages, which a handful of very fast tiles cannot pull up. Areas with fewer than <span data-slot="min-tests"></span> tests in the quarter are hatched.</p>
  <div class="ict-split">
    <figure class="ict-figure ict-figure--map" data-chart="az-map"></figure>
    <figure class="ict-figure" data-chart="az-bars"></figure>
  </div>

  <div class="ict-subhead">
    <h3>How <span data-slot="az-place">each place</span> has changed since 2019</h3>
    <label class="ict-select"><span class="ict-group__label">Place</span>
      <select data-ctl="az-region"></select>
    </label>
  </div>
  <p class="ict-note">Quarterly figures for the chosen city or district, against the national figure computed the same way. These tile-based figures come from a different source from the Global Index above and run higher than its medians, so the two should not be compared directly.</p>
  <figure class="ict-figure" data-chart="az-trend"></figure>
</section>

<section class="ict-section" aria-labelledby="ict-adopt-h">
  <div class="ict-section__head">
    <h2 id="ict-adopt-h">Who is connected</h2>
  </div>
  <div class="ict-toolbar">
    <div class="ict-group" role="group" aria-label="Indicator"><span class="ict-group__label">Indicator</span>
      <button type="button" data-ctl="adopt" data-value="internet_share">Internet users</button>
      <button type="button" data-ctl="adopt" data-value="fixed_broadband_per100">Fixed broadband</button>
      <button type="button" data-ctl="adopt" data-value="mobile_subscriptions_per100">Mobile subscriptions</button>
    </div>
  </div>
  <p class="ict-note" data-slot="adopt-note"></p>
  <figure class="ict-figure" data-chart="adopt"></figure>
</section>

<section class="ict-section" aria-labelledby="ict-v6-h">
  <div class="ict-section__head">
    <h2 id="ict-v6-h">Ready for IPv6?</h2>
  </div>
  <div class="ict-toolbar">
    <div class="ict-group" role="group" aria-label="Measure"><span class="ict-group__label">Share of users</span>
      <button type="button" data-ctl="v6" data-value="capable">Able to use IPv6</button>
      <button type="button" data-ctl="v6" data-value="preferred">Preferring IPv6</button>
    </div>
  </div>
  <p class="ict-note">IPv6 is the successor to the exhausted IPv4 address space. Monthly figures from APNIC Labs, which measures this with test objects placed in online advertisements.</p>
  <figure class="ict-figure" data-chart="ipv6"></figure>
</section>

</div>

<section class="ict-section ict-methods" aria-labelledby="ict-sources">
  <h2 id="ict-sources">Sources and method</h2>

  <p><strong>Speedtest Global Index</strong> (Ookla), monthly. Ookla publishes only the last thirteen months, so every earlier month on this page comes from an archive kept since June 2023; the few months absent from that archive are filled by linear interpolation. Belarus and Russia were withdrawn from the index in 2025, so their series end in April 2025. The series for Georgia and Ukraine begin in July 2025, the earliest month Ookla still published when they were added, and Turkmenistan appears only in the months Ookla reports it.</p>

  <p><strong>Ookla Open Data</strong>, quarterly, from 2019, used here only for the cities and districts of Azerbaijan. Each tile is assigned to the city or district containing its centre, using the second-level boundaries published by <a href="https://www.geoboundaries.org/">geoBoundaries</a> (derived from Wikipedia, CC BY-SA 3.0). A unit's figure is the mean of its tile averages, weighted by the number of tests. Speedtest users are a self-selected sample, and tests cluster where people live and where connections are being checked, so these are indicators rather than measurements of every connection.</p>

  <p><strong>Projections</strong> are fitted to the Global Index series each month: for every country, network, statistic and measure, the ARIMA model with a linear trend that has the lowest AIC among orders up to (3, 1, 3) is projected up to 24 months ahead. The intervals are the model's own. With about three years of monthly data, and a change in Ookla's method in mid-2024, the uncertainty about the model itself is larger than those intervals show; read the projections as a continuation of the recent trend, not as a prediction.</p>

  <p><strong>APNIC Labs IPv6 measurement</strong>, daily, aggregated here to months as the number of IPv6-capable samples divided by all samples; months with fewer than 20 days of data are left out. Data &copy; APNIC, re-used with attribution.</p>

  <p><strong>ITU and World Bank indicators</strong>, annual, as republished by Our World in Data under CC BY 4.0.</p>

  <p>A scheduled job fetches all four sources each month and refuses to save a refresh in which any country would lose months of history. The data and code are in the <a href="https://github.com/sorujov/sorujov.github.io/tree/master/data-pipeline/ict">site repository</a>; the tables behind the charts are <a href="https://github.com/sorujov/sorujov.github.io/blob/master/data-pipeline/ict/archive/global_index.csv">global_index.csv</a> (countries, monthly) and <a href="https://github.com/sorujov/sorujov.github.io/blob/master/data-pipeline/ict/archive/azerbaijan_regions.csv">azerbaijan_regions.csv</a> (cities and districts, quarterly).</p>

  <p class="ict-attribution">Speedtest&reg; by Ookla&reg; Global Fixed and Mobile Network Performance Maps, accessed from AWS; based on Samir Orujov's analysis of these maps for 2019 Q1 to <span data-slot="od-latest">the latest quarter</span>. Licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>. Ookla trademarks used under license and reprinted with permission.</p>
</section>

<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js" defer></script>
<script src="{{ '/assets/js/ict-data.js' | relative_url }}" defer></script>
