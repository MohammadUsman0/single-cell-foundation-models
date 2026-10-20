/* Single-cell foundation model catalogue: a static, dependency-free viewer for data.json.
 *
 * Routes (hash based, so every view has a shareable URL):
 *   #/models?q=..&cat=a,b&tag=x,y&y0=2023&y1=2026&st=published&code=1&view=table&sort=year&dir=desc
 *   #/resources?type=benchmark&...
 *   #/model/<id>   #/resource/<id>
 */
(function () {
  "use strict";

  const LINK_LABELS = {
    paper: "Paper", preprint: "Preprint", code: "Code", weights: "Weights",
    project: "Project", dataset: "Dataset", docs: "Docs", video: "Video",
  };
  const CONFERENCES = new Set(["NeurIPS", "ICML", "ICLR", "AAAI", "ACL", "RECOMB", "WSDM", "ICDM Workshops"]);
  const PREPRINT_VENUES = new Set(["arxiv", "biorxiv", "medrxiv", "research square", "chemrxiv", "ssrn"]);

  let DATA = null;
  const V = { cat: {}, tag: {}, type: {}, card: [] };   // vocabulary lookups
  // field -> {id: label}, filled from data.json's vocab (inputs, outputs, architecture family, ...)
  const L = { inputs: {}, outputs: {}, architecture_family: {}, code_status: {}, review_basis: {},
              perturbation_type: {}, generalization: {} };
  // model filters for "what it takes / gives / is": [url param, field, heading]
  const IO = [["in", "inputs", "Takes"], ["out", "outputs", "Gives"], ["fam", "architecture_family", "Architecture"]];
  const asList = (v) => (v == null ? [] : Array.isArray(v) ? v : [v]);
  const lab = (field, v) => L[field][v] || v;
  const app = document.getElementById("app");
  const qInput = document.getElementById("q");

  // ------------------------------------------------------------ helpers

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
  const norm = (s) => String(s ?? "").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "");
  const doiOf = (url) => {
    const m = /(10\.\d{4,9}\/[^\s?#]+)/.exec(url || "");
    return m ? m[1].replace(/v\d+$/, "").replace(/\.$/, "") : null;
  };
  const entryDoi = (e) => doiOf((e.links || {}).paper) || doiOf((e.links || {}).preprint);
  const label = (e) => e.name || e.title;
  const prettyField = (f) => f.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());

  function parseHash() {
    const raw = location.hash.replace(/^#\/?/, "");
    const [path, query] = raw.split("?");
    const parts = path.split("/").filter(Boolean);
    const params = Object.fromEntries(new URLSearchParams(query || ""));
    return { route: parts[0] || "models", id: parts[1] ? decodeURIComponent(parts[1]) : null, params };
  }

  function setParams(route, params, push) {
    const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v != null));
    const qs = new URLSearchParams(clean).toString();
    const url = `#/${route}${qs ? "?" + qs : ""}`;
    if (push) location.hash = url;
    else { history.replaceState(null, "", url); render(); }
  }

  const list = (v) => (v ? v.split(",").filter(Boolean) : []);
  const toggleIn = (csv, val) => {
    const s = new Set(list(csv));
    s.has(val) ? s.delete(val) : s.add(val);
    return [...s].join(",");
  };

  // ------------------------------------------------------------ filtering

  function matchesSearch(e, q) {
    if (!q) return true;
    const hay = norm([e.id, e.name, e.title, e.key, e.venue, (e.aliases || []).join(" "),
      e.modality, e.architecture].join(" "));
    return norm(q).split(/\s+/).every((w) => hay.includes(w));
  }

  // Each filter is [param, test(entry, value)]; facet counts apply every filter except their own.
  function filtersFor(kind) {
    const f = [
      ["q", (e, v) => matchesSearch(e, v)],
      ["tag", (e, v) => list(v).every((t) => (e.tags || []).includes(t))],
      ["y0", (e, v) => e.year != null && e.year >= +v],
      ["y1", (e, v) => e.year != null && e.year <= +v],
      ["st", (e, v) => e.status === v],
    ];
    if (kind === "models") {
      f.push(["cat", (e, v) => list(v).includes(e.category)]);
      f.push(["code", (e) => !!(e.links || {}).code]);
      for (const [param, field] of IO) {
        f.push([param, field === "architecture_family"
          ? (e, v) => list(v).includes(e[field])
          : (e, v) => list(v).every((x) => asList(e[field]).includes(x))]);
      }
      for (const field of V.card) {
        f.push([`mc_${field}`, (e, v) => list(v).includes(String((e.model_card || {})[field] ?? ""))]);
      }
    } else {
      f.push(["type", (e, v) => list(v).includes(e.type)]);
    }
    return f;
  }

  function applyFilters(items, kind, params, skip) {
    const fs = filtersFor(kind).filter(([p]) => p !== skip && params[p]);
    return items.filter((e) => fs.every(([p, test]) => test(e, params[p])));
  }

  function countBy(items, fn) {
    const c = {};
    for (const e of items) for (const v of [].concat(fn(e) ?? [])) if (v !== "" && v != null) c[v] = (c[v] || 0) + 1;
    return c;
  }

  const SORTS = {
    year: (e) => e.year ?? -1,
    name: (e) => norm(label(e)),
    venue: (e) => norm(e.venue || "~"),
    category: (e) => norm(V.cat[e.category] || e.category || V.type[e.type] || e.type || "~"),
  };

  function sortItems(items, params) {
    const key = SORTS[params.sort] ? params.sort : "year";
    const dir = params.dir === "asc" ? 1 : params.dir === "desc" ? -1 : (key === "year" ? -1 : 1);
    return [...items].sort((a, b) => {
      const x = SORTS[key](a), y = SORTS[key](b);
      if (x < y) return -dir;
      if (x > y) return dir;
      return norm(label(a)) < norm(label(b)) ? -1 : 1;
    });
  }

  // ------------------------------------------------------------ list view

  function renderList(kind, params) {
    const items = DATA[kind];
    const result = sortItems(applyFilters(items, kind, params), params);
    const view = kind === "models" && params.view === "table" ? "table" : "list";
    app.innerHTML = `
      <div class="layout">
        ${filterPanel(kind, params)}
        <section aria-label="Results">
          <div class="toolbar">
            <div class="count" aria-live="polite">${result.length} <small>of ${items.length} ${kind}</small></div>
            ${kind === "models" ? `
              <div class="seg" role="group" aria-label="Layout">
                <button type="button" data-view="list" aria-pressed="${view === "list"}">List</button>
                <button type="button" data-view="table" aria-pressed="${view === "table"}">Compare</button>
              </div>` : ""}
            <label class="visually-hidden" for="sort">Sort by</label>
            <select id="sort" class="btn">
              ${[["year", "Newest first"], ["name", "Name A–Z"], ["venue", "Venue"]]
                .map(([k, l]) => `<option value="${k}" ${(params.sort || "year") === k ? "selected" : ""}>${l}</option>`).join("")}
            </select>
            <button type="button" class="btn" data-export="csv" title="Download the filtered list">CSV</button>
            <button type="button" class="btn" data-export="json">JSON</button>
            <button type="button" class="btn" data-export="bib">BibTeX</button>
          </div>
          ${activeChips(kind, params)}
          ${result.length === 0
            ? `<div class="empty">No ${kind} match these filters. <a href="#/${kind}">Clear all filters</a></div>`
            : view === "table" ? tableView(result, params) : `<div class="cards">${result.map((e) => card(e, kind)).join("")}</div>`}
        </section>
      </div>`;
    wireList(kind, params, result);
  }

  function filterPanel(kind, params) {
    const items = DATA[kind];
    const facet = (param, fn) => countBy(applyFilters(items, kind, params, param), fn);
    const checks = (param, counts, entries) => entries
      .filter(([id]) => counts[id] || list(params[param]).includes(id))
      .map(([id, text]) => `
        <label class="check"><input type="checkbox" data-param="${param}" value="${esc(id)}"
          ${list(params[param]).includes(id) ? "checked" : ""}> <span>${esc(text)}</span><span class="n">${counts[id] || 0}</span></label>`)
      .join("");

    const groups = [];
    if (kind === "models") {
      const c = facet("cat", (e) => e.category);
      groups.push(["Category", checks("cat", c, DATA.vocab.categories.map((x) => [x.id, x.label]))]);
      for (const [param, field, head] of IO) {
        const cnt = facet(param, (e) => asList(e[field]));
        const html = checks(param, cnt, Object.entries(L[field]));
        if (html) groups.push([head, html]);
      }
    } else {
      const c = facet("type", (e) => e.type);
      groups.push(["Type", checks("type", c, DATA.vocab.resource_types.map((x) => [x.id, x.label]))]);
    }
    const tc = facet("tag", (e) => e.tags || []);
    for (const g of ["modality", "task", "approach"]) {
      const html = checks("tag", tc, DATA.vocab.tags.filter((t) => t.group === g).map((t) => [t.id, t.label]));
      if (html) groups.push([g[0].toUpperCase() + g.slice(1), html]);
    }
    if (kind === "models") {
      for (const field of V.card) {
        const c = facet(`mc_${field}`, (e) => String((e.model_card || {})[field] ?? ""));
        const html = checks(`mc_${field}`, c, Object.keys(c).sort().map((v) => [v, v]));
        if (html) groups.push([prettyField(field), html]);
      }
    }

    const years = [...new Set(items.map((e) => e.year).filter(Boolean))].sort();
    const opt = (v, sel) => `<option value="${v}" ${String(sel) === String(v) ? "selected" : ""}>${v || "Any"}</option>`;
    const st = params.st || "";
    const codeCount = kind === "models" ? facet("code", (e) => ((e.links || {}).code ? "yes" : "")).yes || 0 : 0;

    return `
      <aside class="filters" aria-label="Filters">
        <div class="filters-head">
          <h2>Filters</h2>
          <button type="button" class="btn small filters-toggle" aria-expanded="false">Show</button>
          <a class="btn small" href="#/${kind}">Reset</a>
        </div>
        <div class="filter-body">
          <div class="filter-group">
            <h3>Status</h3>
            <div class="seg" role="group" aria-label="Publication status">
              ${[["", "All"], ["published", "Published"], ["preprint", "Preprint"]]
                .map(([v, l]) => `<button type="button" data-st="${v}" aria-pressed="${st === v}">${l}</button>`).join("")}
            </div>
          </div>
          ${kind === "models" ? `
          <div class="filter-group">
            <label class="check"><input type="checkbox" data-flag="code" ${params.code ? "checked" : ""}>
              <span>Has code</span><span class="n">${codeCount}</span></label>
          </div>` : ""}
          <div class="filter-group">
            <h3>Year</h3>
            <div class="year-range">
              <label class="visually-hidden" for="y0">From year</label>
              <select id="y0">${opt("", params.y0)}${years.map((y) => opt(y, params.y0)).join("")}</select>
              <span>–</span>
              <label class="visually-hidden" for="y1">To year</label>
              <select id="y1">${opt("", params.y1)}${years.map((y) => opt(y, params.y1)).join("")}</select>
            </div>
          </div>
          ${groups.map(([h, html]) => `<div class="filter-group"><h3>${esc(h)}</h3>${html}</div>`).join("")}
        </div>
      </aside>`;
  }

  function activeChips(kind, params) {
    const chips = [];
    const add = (param, value, text) => chips.push(
      `<button type="button" class="chip" data-remove="${param}" data-value="${esc(value)}" aria-label="Remove filter ${esc(text)}">${esc(text)} ✕</button>`);
    if (params.q) add("q", "", `“${params.q}”`);
    for (const v of list(params.cat)) add("cat", v, V.cat[v] || v);
    for (const v of list(params.type)) add("type", v, V.type[v] || v);
    for (const v of list(params.tag)) add("tag", v, V.tag[v] || v);
    if (params.st) add("st", "", params.st === "published" ? "Published" : "Preprint");
    if (params.code) add("code", "", "Has code");
    if (params.y0 || params.y1) add("year", "", `${params.y0 || "…"}–${params.y1 || "…"}`);
    for (const f of V.card) for (const v of list(params[`mc_${f}`])) add(`mc_${f}`, v, `${prettyField(f)}: ${v}`);
    for (const [param, field, head] of IO) for (const v of list(params[param])) add(param, v, `${head}: ${lab(field, v)}`);
    return chips.length ? `<div class="chips">${chips.join("")}</div>` : "";
  }

  function statusBadge(e) {
    if (e.status === "published") return `<span class="badge published">Published</span>`;
    if (e.status === "preprint") return `<span class="badge preprint">Preprint</span>`;
    return "";
  }

  function linkButtons(e) {
    const links = e.links || {};
    return Object.keys(LINK_LABELS).filter((k) => links[k])
      .map((k) => `<a href="${esc(links[k])}" target="_blank" rel="noopener">${LINK_LABELS[k]}</a>`).join("");
  }

  function card(e, kind) {
    const href = `#/${kind === "models" ? "model" : "resource"}/${encodeURIComponent(e.id)}`;
    const group = kind === "models" ? V.cat[e.category] : V.type[e.type];
    const venue = [e.venue, e.year].filter(Boolean).join(" ");
    return `
      <article class="card">
        <div class="card-top">
          <a class="card-name" href="${href}">${esc(label(e))}</a>
          ${venue ? `<span class="card-meta">${esc(venue)}</span>` : ""}
          ${statusBadge(e)}
        </div>
        ${e.name ? `<p class="card-title">${esc(e.title)}</p>` : ""}
        ${e.key ? `<p class="card-key">${esc(e.key)}</p>` : ""}
        ${ioLine(e)}
        <div class="card-foot">
          ${group ? `<span class="tag cat">${esc(group)}</span>` : ""}
          ${(e.tags || []).map((t) => `<button type="button" class="tag" data-addtag="${esc(t)}">${esc(V.tag[t] || t)}</button>`).join("")}
          <span class="links">${linkButtons(e)}</span>
        </div>
      </article>`;
  }

  function ioLine(e) {
    const ins = asList(e.inputs).map((v) => lab("inputs", v)), outs = asList(e.outputs).map((v) => lab("outputs", v));
    if (!ins.length && !outs.length) return "";
    return `<p class="card-io"><span class="io-label">Takes</span> ${esc(ins.join(", ") || "—")}
      <span class="io-arrow" aria-hidden="true">→</span> <span class="io-label">Gives</span> ${esc(outs.join(", ") || "—")}</p>`;
  }

  function tableView(rows, params) {
    const cols = [
      ["name", "Model"], ["year", "Year"], ["venue", "Venue"], ["category", "Category"],
    ];
    const cardCols = V.card.filter((f) => !["weights_url"].includes(f));
    const sortKey = SORTS[params.sort] ? params.sort : "year";
    const dir = params.dir || (sortKey === "year" ? "desc" : "asc");
    const th = ([k, l]) => `<th scope="col"><button type="button" data-sort="${k}">${l}<span class="arrow">${
      sortKey === k ? (dir === "asc" ? "▲" : "▼") : ""}</span></button></th>`;
    return `
      <div class="table-wrap">
        <table>
          <thead><tr>${cols.map(th).join("")}<th scope="col">Takes</th><th scope="col">Gives</th>
            <th scope="col">Architecture</th><th scope="col">Tags</th>
            ${cardCols.map((f) => `<th scope="col">${esc(prettyField(f))}</th>`).join("")}
            <th scope="col">Paper</th><th scope="col">Code</th></tr></thead>
          <tbody>
            ${rows.map((e) => {
              const l = e.links || {};
              return `<tr>
                <td class="model-col"><a href="#/model/${encodeURIComponent(e.id)}"><strong>${esc(e.name)}</strong></a><span class="t">${esc(e.title)}</span></td>
                <td class="num">${esc(e.year ?? "")}</td>
                <td>${esc(e.venue || "")} ${statusBadge(e)}</td>
                <td class="wide">${esc(V.cat[e.category] || "")}</td>
                <td class="wide">${asList(e.inputs).map((v) => esc(lab("inputs", v))).join(", ")}</td>
                <td class="wide">${asList(e.outputs).map((v) => esc(lab("outputs", v))).join(", ")}</td>
                <td>${esc(e.architecture_family ? lab("architecture_family", e.architecture_family) : "")}</td>
                <td class="wide">${(e.tags || []).map((t) => esc(V.tag[t] || t)).join(", ")}</td>
                ${cardCols.map((f) => `<td>${esc((e.model_card || {})[f] ?? "")}</td>`).join("")}
                <td class="nowrap">${l.paper ? `<a href="${esc(l.paper)}" target="_blank" rel="noopener">paper</a>` : ""}</td>
                <td>${l.code ? `<a href="${esc(l.code)}" target="_blank" rel="noopener">${esc(e.github || "code")}</a>` : ""}</td>
              </tr>`;
            }).join("")}
          </tbody>
        </table>
      </div>`;
  }

  function wireList(kind, params, result) {
    const update = (patch) => setParams(kind, { ...params, ...patch }, false);
    app.querySelectorAll("input[data-param]").forEach((el) =>
      el.addEventListener("change", () => update({ [el.dataset.param]: toggleIn(params[el.dataset.param], el.value) })));
    app.querySelectorAll("[data-st]").forEach((el) => el.addEventListener("click", () => update({ st: el.dataset.st })));
    app.querySelectorAll("[data-flag]").forEach((el) =>
      el.addEventListener("change", () => update({ [el.dataset.flag]: el.checked ? "1" : "" })));
    app.querySelectorAll("[data-view]").forEach((el) => el.addEventListener("click", () => update({ view: el.dataset.view })));
    app.querySelectorAll("[data-addtag]").forEach((el) => el.addEventListener("click", () => {
      if (!list(params.tag).includes(el.dataset.addtag)) update({ tag: toggleIn(params.tag, el.dataset.addtag) });
    }));
    app.querySelectorAll("[data-remove]").forEach((el) => el.addEventListener("click", () => {
      const p = el.dataset.remove;
      if (p === "year") update({ y0: "", y1: "" });
      else update({ [p]: el.dataset.value ? toggleIn(params[p], el.dataset.value) : "" });
    }));
    app.querySelectorAll("[data-sort]").forEach((el) => el.addEventListener("click", () => {
      const k = el.dataset.sort;
      const cur = SORTS[params.sort] ? params.sort : "year";
      const curDir = params.dir || (cur === "year" ? "desc" : "asc");
      update({ sort: k, dir: cur === k ? (curDir === "asc" ? "desc" : "asc") : (k === "year" ? "desc" : "asc") });
    }));
    const sort = app.querySelector("#sort");
    if (sort) sort.addEventListener("change", () => update({ sort: sort.value, dir: "" }));
    for (const id of ["y0", "y1"]) {
      const s = app.querySelector("#" + id);
      if (s) s.addEventListener("change", () => update({ [id]: s.value }));
    }
    const panel = app.querySelector(".filters");
    const tog = app.querySelector(".filters-toggle");
    if (tog) tog.addEventListener("click", () => {
      const open = panel.classList.toggle("open");
      tog.textContent = open ? "Hide" : "Show";
      tog.setAttribute("aria-expanded", String(open));
    });
    app.querySelectorAll("[data-export]").forEach((el) =>
      el.addEventListener("click", () => exportList(el.dataset.export, kind, result)));
  }

  // ------------------------------------------------------------ export

  function download(name, text, type) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type }));
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  function exportList(fmt, kind, rows) {
    const stamp = DATA.generated;
    if (fmt === "json") {
      download(`${kind}-${stamp}.json`, JSON.stringify(rows, null, 2), "application/json");
      return;
    }
    if (fmt === "csv") {
      const cols = ["id", "name", "title", "year", "venue", "status", kind === "models" ? "category" : "type", "tags",
        "paper", "preprint", "code"];
      const val = (e, c) => (["paper", "preprint", "code"].includes(c) ? (e.links || {})[c]
        : Array.isArray(e[c]) ? e[c].join("; ") : e[c]) ?? "";
      const cell = (v) => /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v);
      const csv = [cols.join(",")].concat(rows.map((e) => cols.map((c) => cell(val(e, c))).join(","))).join("\n");
      download(`${kind}-${stamp}.csv`, csv, "text/csv");
      return;
    }
    download(`${kind}-${stamp}.bib`, rows.map(bibtex).join("\n\n") + "\n", "application/x-bibtex");
  }

  // BibTeX built only from catalogue fields (no guessed authors or pages).
  function bibtex(e) {
    const doi = entryDoi(e);
    const venue = e.venue || "";
    const pre = PREPRINT_VENUES.has(venue.toLowerCase());
    const type = pre ? "misc" : CONFERENCES.has(venue) ? "inproceedings" : venue ? "article" : "misc";
    const f = [["title", `{${e.title}}`]];
    if (e.year) f.push(["year", e.year]);
    if (venue) f.push([pre ? "howpublished" : type === "inproceedings" ? "booktitle" : "journal", venue]);
    if (doi) f.push(["doi", doi]);
    const url = (e.links || {}).paper || (e.links || {}).preprint;
    if (url) f.push(["url", url]);
    const body = f.map(([k, v]) => `  ${k} = {${v}}`).join(",\n");
    return `@${type}{${e.id},\n${body}\n}`;
  }

  // ------------------------------------------------------------ detail view

  function renderDetail(kind, id) {
    const items = kind === "model" ? DATA.models : DATA.resources;
    const e = items.find((x) => x.id === id);
    if (!e) {
      app.innerHTML = `<div class="empty">No ${kind} with id “${esc(id)}”. <a href="#/${kind}s">Back to the list</a></div>`;
      return;
    }
    document.title = `${label(e)} · Single-Cell Foundation Models`;
    const links = e.links || {};
    const doi = entryDoi(e);
    const facts = [];
    const add = (k, v) => { if (v != null && v !== "" && !(Array.isArray(v) && !v.length)) facts.push([k, v]); };
    if (kind === "model") {
      add("Category", `<a href="#/models?cat=${esc(e.category)}">${esc(V.cat[e.category] || e.category)}</a>`);
    } else {
      add("Type", `<a href="#/resources?type=${esc(e.type)}">${esc(V.type[e.type] || e.type)}</a>`);
    }
    add("Tags", (e.tags || []).map((t) =>
      `<a href="#/${kind}s?tag=${esc(t)}">${esc(V.tag[t] || t)}</a>`).join(", "));
    add("Also known as", esc((e.aliases || []).join(", ")));
    add("Venue", esc([e.venue, e.venue_detail ? `(${e.venue_detail})` : ""].filter(Boolean).join(" ")));
    add("Year", esc(e.year ?? ""));
    add("Modality", esc(e.modality || ""));
    add("Architecture", esc(e.architecture || ""));
    add("Tasks", esc(e.task || ""));
    if (e.architecture_family) add("Architecture family", esc(lab("architecture_family", e.architecture_family)));
    add("Perturbation type", esc(asList(e.perturbation_type).map((v) => lab("perturbation_type", v)).join(", ")));
    add("Generalization", esc(asList(e.generalization).map((v) => lab("generalization", v)).join(", ")));
    if (!links.code && e.code_status) add("Code", esc(lab("code_status", e.code_status)));
    if (e.added) add("Added to catalogue", esc(e.added));
    if (e.review_basis) add("Checked against", esc(lab("review_basis", e.review_basis)) + (asList(e.sources).length
      ? ": " + asList(e.sources).map((u) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u.replace(/^https?:\/\/(doi\.org\/)?/, ""))}</a>`).join(", ") : ""));
    for (const [k, v] of Object.entries(e.model_card || {})) add(prettyField(k), esc(Array.isArray(v) ? v.join(", ") : v));
    if (doi) add("DOI", `<a href="https://doi.org/${esc(doi)}" target="_blank" rel="noopener">${esc(doi)}</a>`);

    const versions = links.paper && links.preprint ? `
      <div class="section"><h2>Versions</h2>
        <div class="row"><a class="btn" href="${esc(links.paper)}" target="_blank" rel="noopener">Published version</a>
        <a class="btn" href="${esc(links.preprint)}" target="_blank" rel="noopener">Preprint</a></div></div>` : "";

    const evaluatedBy = kind === "model"
      ? DATA.resources.filter((r) => (r.evaluates || []).includes(e.id)) : [];
    const evaluates = kind === "resource"
      ? (e.evaluates || []).map((mid) => DATA.models.find((m) => m.id === mid)).filter(Boolean) : [];
    const relList = (arr, k) => arr.map((x) =>
      `<li><a href="#/${k}/${encodeURIComponent(x.id)}">${esc(label(x))}</a>${x.year ? ` <span class="note">(${esc(x.year)})</span>` : ""}</li>`).join("");

    const q = encodeURIComponent(e.title);
    const explore = [
      doi ? `<a class="btn" href="https://www.connectedpapers.com/api/redirect/doi/${esc(doi)}" target="_blank" rel="noopener">Connected Papers</a>` : "",
      `<a class="btn" href="https://www.semanticscholar.org/search?q=${q}" target="_blank" rel="noopener">Semantic Scholar</a>`,
      `<a class="btn" href="https://scholar.google.com/scholar?q=${q}" target="_blank" rel="noopener">Google Scholar</a>`,
    ].join("");

    const folder = kind === "model" ? "models" : "resources";
    app.innerHTML = `
      <article class="detail">
        <a class="back" href="#/${kind}s">← All ${kind}s</a>
        <h1>${esc(label(e))}</h1>
        ${e.name ? `<p class="subtitle">${esc(e.title)}</p>` : ""}
        <div class="meta">${esc([e.venue, e.year].filter(Boolean).join(" "))} ${statusBadge(e)}</div>
        ${Object.keys(links).length ? `<div class="row" style="margin-top:12px">${Object.keys(LINK_LABELS).filter((k) => links[k])
          .map((k) => `<a class="btn" href="${esc(links[k])}" target="_blank" rel="noopener">${LINK_LABELS[k]}</a>`).join("")}</div>` : ""}
        ${e.key ? `<div class="section"><h2>Summary</h2><p style="margin:0">${esc(e.key)}</p></div>` : ""}
        ${ioDiagram(e)}
        <div class="section"><h2>Details</h2>
          <dl class="facts">${facts.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join("")}</dl></div>
        ${versions}
        ${evaluatedBy.length ? `<div class="section"><h2>Evaluated by</h2><ul>${relList(evaluatedBy, "resource")}</ul></div>` : ""}
        ${evaluates.length ? `<div class="section"><h2>Models evaluated</h2><ul>${relList(evaluates, "model")}</ul></div>` : ""}
        <div class="section"><h2>Explore related work</h2><div class="row">${explore}</div></div>
        ${e.citation ? `<div class="section"><h2>Citation</h2><p class="cite" id="cite">${esc(e.citation)}</p>
          <div class="row" style="margin-top:8px"><button type="button" class="btn small" id="copy-cite">Copy citation</button></div></div>` : ""}
        <p class="note" style="margin-top:14px">
          ${e.reviewed ? "Checked against the paper." : "Not yet reviewed against the full paper."}
          <a href="https://github.com/${esc(DATA.repo)}/blob/main/data/${folder}/${encodeURIComponent(e.id)}.yaml">Suggest a correction</a>
        </p>
      </article>`;
    const copy = document.getElementById("copy-cite");
    if (copy) copy.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(e.citation); copy.textContent = "Copied"; }
      catch (err) { copy.textContent = "Select the text to copy"; }
    });
    window.scrollTo(0, 0);
  }

  function ioDiagram(e) {
    const ins = asList(e.inputs), outs = asList(e.outputs);
    if (!ins.length && !outs.length) return "";
    const chips = (field, arr, param) => arr.length
      ? arr.map((v) => `<a class="io-chip" href="#/models?${param}=${esc(v)}">${esc(lab(field, v))}</a>`).join("")
      : `<span class="note">not recorded</span>`;
    return `
      <div class="section"><h2>What it takes and gives</h2>
        <div class="io-flow">
          <div class="io-col"><div class="io-head">Inputs</div>${chips("inputs", ins, "in")}</div>
          <div class="io-arrow-big" aria-hidden="true">→</div>
          <div class="io-model"><strong>${esc(label(e))}</strong>${e.architecture_family
            ? `<span>${esc(lab("architecture_family", e.architecture_family))}</span>` : ""}</div>
          <div class="io-arrow-big" aria-hidden="true">→</div>
          <div class="io-col"><div class="io-head">Outputs</div>${chips("outputs", outs, "out")}</div>
        </div></div>`;
  }

  // ------------------------------------------------------------ router

  function render() {
    if (!DATA) return;
    const { route, id, params } = parseHash();
    document.querySelectorAll("[data-nav]").forEach((a) => {
      const on = a.dataset.nav === route || a.dataset.nav === route + "s";
      on ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current");
    });
    if (route === "model" || route === "resource") {
      renderDetail(route, id);
      return;
    }
    const kind = route === "resources" ? "resources" : "models";
    document.title = `${kind === "models" ? "Models" : "Resources"} · Single-Cell Foundation Models`;
    if (document.activeElement !== qInput) qInput.value = params.q || "";
    renderList(kind, params);
  }

  let searchTimer;
  qInput.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      const { route, params } = parseHash();
      const kind = route === "resources" || route === "resource" ? "resources" : "models";
      const base = route === kind ? params : {};
      setParams(kind, { ...base, q: qInput.value.trim() }, false);
    }, 150);
  });
  window.addEventListener("hashchange", render);

  fetch("data.json")
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((d) => {
      DATA = d;
      for (const c of d.vocab.categories) V.cat[c.id] = c.label;
      for (const t of d.vocab.tags) V.tag[t.id] = t.label;
      for (const t of d.vocab.resource_types) V.type[t.id] = t.label;
      const VOCAB = { inputs: "inputs", outputs: "outputs", architecture_family: "architecture_families",
                      code_status: "code_status", review_basis: "review_basis",
                      perturbation_type: "perturbation_types", generalization: "generalization" };
      for (const [field, list_] of Object.entries(VOCAB)) for (const x of d.vocab[list_] || []) L[field][x.id] = x.label;
      // Model-card fields get filters/columns only once some model has data for them.
      V.card = Object.keys(d.vocab.model_card_fields || {}).filter((f) => d.models.some((m) => (m.model_card || {})[f] != null));
      document.getElementById("counts").textContent =
        `${d.counts.models} models · ${d.counts.resources} resources`;
      document.getElementById("generated").textContent = `Updated ${d.generated}`;
      if (d.repo) {
        document.getElementById("repo-link").href = `https://github.com/${d.repo}`;
        document.getElementById("contrib-link").href = `https://github.com/${d.repo}/blob/main/CONTRIBUTING.md`;
      }
      render();
    })
    .catch(() => {
      app.innerHTML = `<div class="empty">Could not load data.json. If you opened this file directly, serve the
        <code>docs/</code> folder over HTTP instead (for example <code>python -m http.server</code>).</div>`;
    });
})();
