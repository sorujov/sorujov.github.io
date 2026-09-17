---
title: "Internet in the CIS region"
excerpt: "Broadband and mobile speeds, rankings and adoption across twelve post-Soviet countries, updated monthly from Ookla and ITU data."
collection: portfolio
share: false
ict_page: true
---

<p class="ict-lead">How fast is the internet in Azerbaijan and its neighbours, how is it changing, and how many people use it? This page compares twelve countries of the former Soviet Union, looks inside Azerbaijan city by city, and is refreshed automatically from public sources.</p>

<p class="ict-disclaimer">A personal project. The figures are Ookla's and the ITU's, not official statistics of the Information and Communication Technologies Agency, and the views are my own.</p>

<div class="ict" id="ict" data-src="{{ '/assets/data/ict/ict.json' | relative_url }}" data-map="{{ '/assets/data/ict/countries.json' | relative_url }}" data-az-src="{{ '/assets/data/ict/az_regions.json' | relative_url }}" data-az-map="{{ '/assets/data/ict/az_map.json' | relative_url }}">

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
    <div class="ict-controls" role="group" aria-label="Network">
      <button type="button" data-ctl="map-net" data-value="fixed" aria-pressed="true">Fixed broadband</button>
      <button type="button" data-ctl="map-net" data-value="mobile" aria-pressed="false">Mobile</button>
    </div>
  </div>
  <p class="ict-note">Median download speed in the latest month of the Speedtest Global Index. Countries outside the index are shown hatched.</p>
  <div class="ict-split">
    <figure class="ict-figure ict-figure--map" data-chart="map"></figure>
    <figure class="ict-figure" data-chart="bars"></figure>
  </div>
</section>

<section class="ict-section" aria-labelledby="ict-trend-h">
  <div class="ict-section__head">
    <h2 id="ict-trend-h">Speeds month by month</h2>
    <div class="ict-controls">
      <div role="group" aria-label="Network">
        <button type="button" data-ctl="trend-net" data-value="fixed" aria-pressed="true">Fixed</button>
        <button type="button" data-ctl="trend-net" data-value="mobile" aria-pressed="false">Mobile</button>
      </div>
      <div role="group" aria-label="Measure">
        <button type="button" data-ctl="trend-metric" data-value="download" aria-pressed="true">Download</button>
        <button type="button" data-ctl="trend-metric" data-value="upload" aria-pressed="false">Upload</button>
        <button type="button" data-ctl="trend-metric" data-value="latency" aria-pressed="false">Latency</button>
      </div>
      <label class="ict-select">Compare with
        <select data-ctl="compare"></select>
      </label>
    </div>
  </div>
  <p class="ict-note">Median values from the Speedtest Global Index. From <span data-slot="rolling"></span> Ookla reports each month as a rolling three-month figure, which smooths the series. May and June 2025 were never archived and appear as a break.</p>
  <figure class="ict-figure" data-chart="trend"></figure>
</section>

<section class="ict-section" aria-labelledby="ict-rank-h">
  <div class="ict-section__head">
    <h2 id="ict-rank-h">Global rank, a year apart</h2>
  </div>
  <p class="ict-note">Position in Ookla's worldwide ranking by median download speed; a line rising to the right is an improvement.</p>
  <div class="ict-split ict-split--even">
    <figure class="ict-figure" data-chart="slope-fixed"></figure>
    <figure class="ict-figure" data-chart="slope-mobile"></figure>
  </div>
</section>

<section class="ict-section" aria-labelledby="ict-az-h">
  <div class="ict-section__head">
    <h2 id="ict-az-h">Azerbaijan, city by city</h2>
    <div class="ict-controls">
      <div role="group" aria-label="Network">
        <button type="button" data-ctl="az-net" data-value="fixed" aria-pressed="true">Fixed</button>
        <button type="button" data-ctl="az-net" data-value="mobile" aria-pressed="false">Mobile</button>
      </div>
      <label class="ict-select">Quarter
        <select data-ctl="az-quarter"></select>
      </label>
    </div>
  </div>
  <p class="ict-note">Average download speed in each of Azerbaijan's 78 cities and districts, from Ookla Open Data. Ookla publishes these data as roughly 600-metre map tiles; each tile is placed in the city or district that contains it, and tiles are averaged with the number of tests as weights. Areas with fewer than <span data-slot="min-tests"></span> tests in the quarter are hatched, because their figures are too uncertain to compare.</p>
  <div class="ict-split">
    <figure class="ict-figure ict-figure--map" data-chart="az-map"></figure>
    <figure class="ict-figure" data-chart="az-bars"></figure>
  </div>
</section>

<section class="ict-section" aria-labelledby="ict-aztrend-h">
  <div class="ict-section__head">
    <h2 id="ict-aztrend-h">How each place has changed since 2019</h2>
    <div class="ict-controls">
      <label class="ict-select">Place
        <select data-ctl="az-region"></select>
      </label>
    </div>
  </div>
  <p class="ict-note">Quarterly average download speed for the chosen city or district, set against the national figure computed the same way. These tile-based averages come from a different source from the Global Index figures above and run higher than its medians, so the two should not be compared directly.</p>
  <figure class="ict-figure" data-chart="az-trend"></figure>
</section>

<section class="ict-section" aria-labelledby="ict-adopt-h">
  <div class="ict-section__head">
    <h2 id="ict-adopt-h">Who is connected</h2>
    <div class="ict-controls" role="group" aria-label="Indicator">
      <button type="button" data-ctl="adopt" data-value="internet_share" aria-pressed="true">Internet users</button>
      <button type="button" data-ctl="adopt" data-value="fixed_broadband_per100" aria-pressed="false">Fixed broadband</button>
      <button type="button" data-ctl="adopt" data-value="mobile_subscriptions_per100" aria-pressed="false">Mobile subscriptions</button>
    </div>
  </div>
  <p class="ict-note" data-slot="adopt-note"></p>
  <figure class="ict-figure" data-chart="adopt"></figure>
</section>

<section class="ict-section" aria-labelledby="ict-v6-h">
  <div class="ict-section__head">
    <h2 id="ict-v6-h">Ready for IPv6?</h2>
  </div>
  <p class="ict-note">Share of internet users whose connection can reach a website over IPv6, the successor to the exhausted IPv4 address space. Monthly figures from APNIC Labs, which measures this with test objects placed in online advertisements; hover the lines for exact values.</p>
  <figure class="ict-figure" data-chart="ipv6"></figure>
</section>

</div>

<section class="ict-section ict-methods" aria-labelledby="ict-sources">
  <h2 id="ict-sources">Sources and method</h2>

  <p><strong>Speedtest Global Index</strong> (Ookla), monthly. Ookla publishes only the last thirteen months, so every earlier month on this page comes from an archive kept since June 2023. Belarus and Russia were withdrawn from the index in 2025, so their series end in April 2025. The series for Georgia and Ukraine begin in July 2025, the earliest month Ookla still published when they were added, and Turkmenistan appears only in the months Ookla reports it.</p>

  <p><strong>Ookla Open Data</strong>, quarterly, from 2019, used here only for the cities and districts of Azerbaijan. Each tile is assigned to the city or district containing its centre, using the second-level boundaries published by <a href="https://www.geoboundaries.org/">geoBoundaries</a> (derived from Wikipedia, CC BY-SA 3.0). A unit's figure is the mean of its tile averages, weighted by the number of tests. Speedtest users are a self-selected sample, and tests cluster where people live and where connections are being checked, so these are indicators rather than measurements of every connection.</p>

  <p><strong>APNIC Labs IPv6 measurement</strong>, daily, aggregated here to months as the number of IPv6-capable samples divided by all samples; months with fewer than 20 days of data are left out. Data &copy; APNIC, re-used with attribution.</p>

  <p><strong>ITU and World Bank indicators</strong>, annual, as republished by Our World in Data under CC BY 4.0.</p>

  <p>A scheduled job fetches all four sources each month and refuses to save a refresh in which any country would lose months of history. The data and code are in the <a href="https://github.com/sorujov/sorujov.github.io/tree/master/data-pipeline/ict">site repository</a>; the tables behind the charts are <a href="https://github.com/sorujov/sorujov.github.io/blob/master/data-pipeline/ict/archive/global_index.csv">global_index.csv</a> (countries, monthly) and <a href="https://github.com/sorujov/sorujov.github.io/blob/master/data-pipeline/ict/archive/azerbaijan_regions.csv">azerbaijan_regions.csv</a> (cities and districts, quarterly).</p>

  <p class="ict-attribution">Speedtest&reg; by Ookla&reg; Global Fixed and Mobile Network Performance Maps, accessed from AWS; based on Samir Orujov's analysis of these maps for 2019 Q1 to <span data-slot="od-latest">the latest quarter</span>. Licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>. Ookla trademarks used under license and reprinted with permission.</p>
</section>

<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js" defer></script>
<script src="{{ '/assets/js/ict-data.js' | relative_url }}" defer></script>
