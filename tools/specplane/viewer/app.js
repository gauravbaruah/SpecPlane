(function () {
  const DATA = window.SPECPLANE_VIEW || { records: {}, changes: [], gaps: {}, impacts: {} };
  const PERSPECTIVES = [
    ["system", "System"],
    ["product", "Product"],
    ["quality", "Quality"],
    ["governance", "Governance"],
    ["ownership", "Ownership"],
  ];
  const LABELS = {
    map: "Map",
    blast: "Blast",
    layers: "Layers",
    journey: "Journey",
    diagrams: "Diagrams",
    data: "Data",
  };
  let diagramSeq = 0;
  if (window.mermaid && window.mermaid.initialize) {
    window.mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
  }
  const REL = {
    realized_by: "Realized by",
    implements: "Implements",
    uses: "Uses",
    depends_on: "Depends on",
    depended_on_by: "Depended on by",
  };
  const GAPS = [
    ["phase1_no_join", "Promises with no known realization", "Phase 1 capabilities. Normal for planned work: nothing realizes them yet."],
    ["open_changes", "Open changes", "Work in flight. Listed so nothing in specs/changes/ goes unseen."],
    ["replaced", "Replaced", "Leftovers. They stay visible and are not the default."],
    ["missing_success_sensor", "Open changes without a success sensor", "The change says what moves but not how anyone would know it worked."],
    ["inferred_unpromoted", "Inferred, not promoted", "Recovered from code. Useful to explore, not part of the live model until someone promotes the id."],
  ];
  let findText = "";
  let expanded = {};
  const THEME_KEY = "specplane-view-theme";

  function systemTheme() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function savedTheme() {
    try {
      const value = localStorage.getItem(THEME_KEY);
      return value === "light" || value === "dark" ? value : "";
    } catch (err) {
      return "";
    }
  }

  function applyTheme(name) {
    if (name === "light" || name === "dark") document.documentElement.setAttribute("data-theme", name);
    else document.documentElement.removeAttribute("data-theme");
  }

  function setTheme(name) {
    applyTheme(name);
    try { localStorage.setItem(THEME_KEY, name); } catch (err) { /* the page still switches */ }
  }

  applyTheme(savedTheme());

  function h(tag, props, children) {
    const node = document.createElement(tag);
    const p = props || {};
    if (p.class) node.className = p.class;
    if (p.id) node.id = p.id;
    if (p.href != null) node.setAttribute("href", p.href);
    if (p.type) node.type = p.type;
    if (p.placeholder) node.placeholder = p.placeholder;
    if (p.value != null && tag === "INPUT") node.value = p.value;
    if (p.open) node.open = true;
    if (p.on) {
      Object.keys(p.on).forEach(function (ev) { node.addEventListener(ev, p.on[ev]); });
    }
    (children || []).forEach(function (kid) {
      if (kid == null || kid === false) return;
      node.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
    });
    return node;
  }

  function parse() {
    const raw = (location.hash || "#live").slice(1);
    const parts = raw.split("?");
    const path = parts[0] || "live";
    const query = new URLSearchParams(parts[1] || "");
    const bits = path.split("/");
    return { kind: bits[0] || "live", arg: decodeURIComponent(bits.slice(1).join("/")), query: query };
  }

  function href(path, query) {
    const q = new URLSearchParams(query || {});
    const s = q.toString();
    return "#" + path + (s ? "?" + s : "");
  }

  function go(path, query) {
    location.hash = href(path, query).slice(1);
  }

  function record(id) { return DATA.records[id]; }

  function levelOf(id) {
    const rec = record(id);
    if (rec && rec.level) return rec.level;
    const cut = id.indexOf(".");
    return cut > 0 ? id.slice(0, cut) : "";
  }

  function bitMark(bit) {
    return h("span", { class: "mark " + (bit || "live") });
  }

  function breakable(text) {
    const frag = document.createDocumentFragment();
    String(text).split(/([._/])/).forEach(function (part) {
      if (!part) return;
      frag.append(document.createTextNode(part));
      if (part === "." || part === "_" || part === "/") frag.append(document.createElement("wbr"));
    });
    return frag;
  }

  function idLink(id) {
    if (!id) return document.createTextNode("");
    if (String(id).indexOf("change.") === 0 || (DATA.changes || []).some(function (c) { return c.id === id; })) {
      const slug = String(id).replace(/^change:/, "").replace(/^change\./, "");
      return h("a", { class: "mono inflight", href: href("change/" + slug) }, [breakable(slug)]);
    }
    const rec = record(id);
    const cls = "mono" + (rec && rec.bit === "inferred" ? " bit inferred" : "");
    return h("a", { class: cls, href: href("id/" + encodeURIComponent(id)) }, [breakable(id)]);
  }

  function shell(route, body) {
    const lenses = [
      ["live", "Live"],
      ["changes", "Changes"],
      ["gaps", "Gaps"],
    ];
    const nav = h("nav", { class: "nav" }, lenses.map(function (pair) {
      return h("a", { href: href(pair[0]), class: route.kind === pair[0] || (pair[0] === "live" && route.kind === "id") || (pair[0] === "changes" && route.kind === "change") ? "on" : "" }, [pair[1]]);
    }));
    const chosen = document.documentElement.getAttribute("data-theme") || systemTheme();
    const theme = h("div", { class: "theme" }, ["light", "dark"].map(function (name) {
      return h("button", {
        type: "button",
        class: chosen === name ? "on" : "",
        on: { click: function () { setTheme(name); rerender(false); } },
      }, [name[0].toUpperCase() + name.slice(1)]);
    }));
    const top = h("header", { class: "top" }, [
      h("div", { class: "brand" }, ["SpecPlane"]),
      nav,
      h("div", { class: "top-end" }, [theme, h("div", { class: "quiet" }, ["read-only"])]),
    ]);
    return h("div", {}, [top, honesty(route), h("main", { class: "page" }, [body, footer()])]);
  }

  function honesty(route) {
    if (route.kind === "id") {
      const rec = record(route.arg);
      if (!rec) return null;
      return h("div", { class: "bar" }, [
        h("div", {}, [h("a", { href: href("live") }, ["Live"]), "  ›  ", idLink(rec.id)]),
        h("div", { class: "row" }, [bitMark(rec.bit), h("span", { class: "bit " + rec.bit }, [rec.bit === "inferred" ? "inferred · not live" : rec.bit]), rec.review_state ? " · " + rec.review_state : ""]),
      ]);
    }
    if (route.kind === "change") {
      return h("div", { class: "bar" }, [
        h("div", {}, [h("a", { href: href("changes") }, ["Changes"]), "  ›  ", route.arg]),
        h("div", { class: "inflight" }, ["change · " + route.arg + " · in-flight"]),
      ]);
    }
    return null;
  }

  function footer() {
    return h("p", { class: "foot" }, ["Review still happens on the pull request."]);
  }

  function liveIndex(route) {
    const bit = route.query.get("bit") || "live";
    const q = findText.trim().toLowerCase();
    const rows = Object.keys(DATA.records).filter(function (id) {
      return levelOf(id) === "capability";
    }).map(function (id) { return DATA.records[id]; }).filter(function (rec) {
      if ((rec.bit || "live") !== bit) return false;
      if (!q) return true;
      return rec.id.toLowerCase().indexOf(q) >= 0 || (rec.purpose || "").toLowerCase().indexOf(q) >= 0;
    });
    const counts = { live: 0, inferred: 0, replaced: 0 };
    Object.keys(DATA.records).forEach(function (id) {
      if (levelOf(id) !== "capability") return;
      const b = DATA.records[id].bit || "live";
      if (counts[b] != null) counts[b] += 1;
    });
    const filters = h("div", { class: "filters" }, ["live", "inferred", "replaced"].map(function (name) {
      return h("button", {
        class: bit === name ? "on" : "",
        on: { click: function () { go("live", { bit: name }); } },
      }, [name[0].toUpperCase() + name.slice(1) + " " + counts[name]]);
    }));
    const find = h("input", {
      id: "find",
      class: "find",
      type: "search",
      placeholder: "Find by id or words in purpose",
      value: findText,
      on: { input: function (ev) { findText = ev.target.value; rerender(true); } },
    });
    const table = h("table", { class: "index" }, [
      h("thead", {}, [h("tr", {}, [h("th", {}, ["id"]), h("th", {}, ["purpose"]), h("th", {}, ["bit"]), h("th", {}, [""])])]),
      h("tbody", {}, rows.map(function (rec) {
        const n = (rec.in_flight || []).length;
        return h("tr", {}, [
          h("td", {}, [bitMark(rec.bit), " ", idLink(rec.id)]),
          h("td", {}, [rec.purpose || ""]),
          h("td", { class: "quiet" }, [(rec.bit || "live") + (rec.review_state ? " · " + rec.review_state : "")]),
          h("td", {}, [n ? h("a", { class: "inflight", href: href("change/" + rec.in_flight[0].id) }, [n === 1 ? "1 open change" : n + " open changes"]) : ""]),
        ]);
      })),
    ]);
    return h("section", {}, [
      h("h1", {}, ["Live"]),
      h("p", { class: "note" }, ["Capabilities in the spec root. Components, containers, and foundations are reached from an id."]),
      h("div", { class: "tools" }, [filters, find]),
      table,
      h("p", { class: "quiet" }, ["In flight is not a filter. An id is in flight when an open change names it."]),
    ]);
  }

  function changesIndex() {
    const q = findText.trim().toLowerCase();
    const rows = (DATA.changes || []).filter(function (c) {
      return !q || c.id.toLowerCase().indexOf(q) >= 0 || (c.why || "").toLowerCase().indexOf(q) >= 0;
    });
    return h("section", {}, [
      h("h1", {}, ["Changes"]),
      h("p", { class: "note" }, ["Open change folders. Nothing here is live until it is promoted."]),
      h("div", { class: "tools" }, [h("input", {
        id: "find", class: "find", type: "search", placeholder: "Find by slug or why", value: findText,
        on: { input: function (ev) { findText = ev.target.value; rerender(true); } },
      })]),
      h("table", { class: "index" }, [
        h("tbody", {}, rows.map(function (c) {
          const sensor = c.check_sync && c.check_sync.sensors === "declared"
            ? (c.check_sync.sensor_rows || []).length + " sensors declared · not run"
            : "No success sensor declared";
          return h("tr", {}, [
            h("td", {}, [h("a", { class: "mono inflight", href: href("change/" + c.id) }, [breakable(c.id)])]),
            h("td", { class: "quiet" }, [c.kind || ""]),
            h("td", {}, [(c.promise_ids || []).map(function (id, i) { return h("span", {}, [i ? ", " : "", idLink(id)]); })]),
            h("td", { class: "quiet" }, [sensor]),
          ]);
        })),
      ]),
    ]);
  }

  function gapsIndex() {
    const gaps = DATA.gaps || {};
    return h("section", {}, [
      h("h1", {}, ["Gaps"]),
      h("p", { class: "note" }, ["Where SpecPlane knows its model is incomplete. Advisory: nothing here is an error, and nothing here has been filled in for you."]),
      ...GAPS.map(function (bucket) {
        const ids = gaps[bucket[0]] || [];
        return h("div", { class: "bucket" }, [
          h("h2", {}, [bucket[1], " ", h("span", { class: "mono quiet" }, [bucket[0]])]),
          h("p", { class: "note" }, [bucket[2]]),
          ids.length ? h("div", {}, ids.map(function (id) { return h("div", { class: "item" }, [idLink(id)]); })) : h("div", { class: "quiet" }, ["(none)"]),
        ]);
      }),
    ]);
  }

  function recordPage(route) {
    const rec = record(route.arg);
    if (!rec) return h("p", {}, ["Not in this spec root: ", route.arg]);
    const graph = (DATA.impacts || {})[rec.id];
    const projections = rec.projections || ["map"];
    const proj = projections.indexOf(route.query.get("proj")) >= 0 ? route.query.get("proj") : projections[0];
    const node = route.query.get("node") || "";
    const persp = route.query.get("persp") || "system";
    return h("div", { class: "split" }, [
      h("div", { class: "copy" }, [
        h("div", { class: "kicker" }, [rec.level || "record"]),
        h("div", { class: "row" }, [bitMark(rec.bit), h("span", { class: "mono" }, [breakable(rec.id)])]),
        h("div", { class: "quiet" }, [
          rec.bit === "inferred" ? "inferred · not live" : rec.bit,
          rec.review_state ? " · " + rec.review_state : "",
          rec.status ? " · status " + rec.status : "",
        ]),
        rec.path ? h("div", { class: "quiet mono" }, [breakable(rec.path)]) : null,
        h("div", { class: "kicker" }, ["Promise"]),
        h("p", { class: "purpose" }, [rec.purpose || (rec.bit === "inferred" ? "retrieve returns no live slice for an inferred id." : "")]),
        flight(rec),
        definition(rec, graph),
        realization(rec, graph),
        questions(rec, graph),
      ]),
      h("div", {}, [
        switcher(projections, proj, function (name) { go("id/" + encodeURIComponent(rec.id), { proj: name }); }),
        proj === "blast" ? perspectiveRow(persp, function (name) {
          go("id/" + encodeURIComponent(rec.id), { proj: "blast", persp: name, node: node });
        }) : null,
        drawProjection(rec, graph, proj, node, persp, function (id) {
          go("id/" + encodeURIComponent(rec.id), { proj: proj, persp: persp, node: id });
        }),
      ]),
    ]);
  }

  function flight(rec) {
    if (!rec.in_flight || !rec.in_flight.length) return null;
    return h("div", {}, rec.in_flight.map(function (c) {
      return h("p", {}, [h("span", { class: "inflight" }, ["In flight "]), idLink(c.id), c.kind ? " · " + c.kind : ""]);
    }));
  }

  function productItems(graph, id) {
    if (!graph) return [];
    const items = ((graph.perspectives || {}).product || {}).items || [];
    return items.filter(function (item) { return item.subject === id; });
  }

  function definition(rec, graph) {
    const duties = rec.responsibilities || [];
    const items = productItems(graph, rec.id).filter(function (item) {
      if (item.kind === "flow" || item.kind === "open_question") return false;
      if (item.kind === "responsibility" && duties.length) return false;
      return true;
    });
    if (!duties.length && !items.length) return null;
    return h("details", {}, [
      h("summary", {}, ["Definition ", h("span", {}, ["what is promised"])]),
      ...duties.map(function (line) { return h("div", { class: "item" }, [line, h("div", { class: "src" }, ["responsibilities"])]); }),
      ...items.map(itemRow),
    ]);
  }

  function realization(rec, graph) {
    const realized = (rec.links || []).filter(function (link) { return link.rel === "realized_by"; }).map(function (link) { return link.id; });
    const quality = graph ? (graph.perspectives || {}).quality || {} : {};
    const rows = [];
    ["criteria", "verification", "contracts", "sensors", "rollout"].forEach(function (key) {
      (quality[key] || []).forEach(function (item) {
        if (item.kind === "data_models") return;
        if (realized.indexOf(item.subject) >= 0) rows.push(item);
      });
    });
    if (!realized.length && !rows.length) {
      if (rec.level === "capability" && rec.bit !== "inferred") {
        return h("p", { class: "note" }, ["Nothing realizes this yet. realized_by is added by engineering when work is planned; that is normal for a planned capability."]);
      }
      return null;
    }
    return h("details", {}, [
      h("summary", {}, ["Realization ", h("span", {}, ["how it is built and checked"])]),
      ...realized.map(function (id) {
        return h("div", { class: "item" }, [idLink(id), h("div", { class: "src" }, [rec.id + " · realized_by"])]);
      }),
      ...rows.map(function (item) {
        return h("div", { class: "item" }, [
          item.detail || item.kind || "",
          h("div", { class: "src" }, [(item.subject || "") + " · " + (item.source || "")]),
        ]);
      }),
    ]);
  }

  function questions(rec, graph) {
    const items = productItems(graph, rec.id).filter(function (item) { return item.kind === "open_question"; });
    if (!items.length) return null;
    return h("details", {}, [
      h("summary", {}, ["Open questions ", h("span", {}, ["declared unknowns"])]),
      ...items.map(itemRow),
    ]);
  }

  function itemRow(item) {
    return h("div", { class: "item" }, [
      item.detail || item.goal || item.kind || "",
      h("div", { class: "src" }, [(item.subject ? item.subject + " · " : "") + (item.source || "")]),
    ]);
  }

  function switcher(names, current, onclick) {
    return h("div", { class: "tabs" }, names.map(function (name) {
      return h("button", { class: name === current ? "on" : "", on: { click: function () { onclick(name); } } }, [LABELS[name] || name]);
    }));
  }

  function perspectiveRow(current, onclick) {
    return h("div", { class: "persp" }, [
      h("span", { class: "quiet" }, ["Read this blast for"]),
      ...PERSPECTIVES.map(function (pair) {
        return h("button", { class: pair[0] === current ? "on" : "", on: { click: function () { onclick(pair[0]); } } }, [pair[1]]);
      }),
    ]);
  }

  function drawProjection(rec, graph, proj, selected, persp, onselect) {
    if (proj === "map") return graphBlock(mapColumns(rec), selected, onselect, null, "derived · from declared links");
    if (proj === "layers") return graphBlock(layerColumns(rec), selected, onselect, null, "derived · 5C placement");
    if (proj === "journey") return journeyBlock(rec, graph);
    if (proj === "diagrams") return diagramBlock(rec);
    if (proj === "data") return dataBlock(rec, graph);
    if (proj === "blast") return blastBlock(graph, rec.id, selected, persp, onselect);
    return null;
  }

  function mapColumns(rec) {
    const cols = [{ head: "Selected", nodes: [nodeModel(rec.id, { selected: true })] }];
    const grouped = {};
    (rec.links || []).forEach(function (link) {
      grouped[link.rel] = grouped[link.rel] || [];
      grouped[link.rel].push(nodeModel(link.id, { via: link.rel }));
    });
    Object.keys(REL).forEach(function (rel) {
      if (grouped[rel] && grouped[rel].length) cols.push({ head: REL[rel], nodes: grouped[rel] });
    });
    return cols;
  }

  function layerColumns(rec) {
    const ids = [rec.id].concat((rec.links || []).map(function (link) { return link.id; }));
    const grouped = {};
    ids.forEach(function (id) {
      const level = levelOf(id) || "other";
      grouped[level] = grouped[level] || [];
      grouped[level].push(nodeModel(id, { via: level, selected: id === rec.id }));
    });
    return Object.keys(grouped).map(function (level) { return { head: level, nodes: grouped[level] }; });
  }

  function nodeModel(id, extra) {
    const rec = record(id);
    return {
      id: id,
      bit: rec ? rec.bit : "",
      epistemic: rec && rec.bit === "inferred" ? "inferred" : "declared",
      sub: (extra && extra.via) || "",
      change: false,
      selectedId: extra && extra.selected,
    };
  }

  let placeCanvas = null;
  window.addEventListener("resize", function () { if (placeCanvas) placeCanvas(); });

  function viewportCanvas(content) {
    const layer = h("div", { class: "canvas-layer" });
    layer.append(content);
    const view = h("div", { class: "canvas" });
    view.append(layer);
    let x = 0;
    let y = 0;
    let scale = 1;
    let drag = null;
    let moved = false;
    function paint() {
      layer.style.transform = "translate(" + x + "px," + y + "px) scale(" + scale + ")";
    }
    function place() {
      const parent = view.parentElement;
      if (!parent) return;
      const left = parent.getBoundingClientRect().left;
      const width = document.documentElement.clientWidth;
      const stacked = window.matchMedia("(max-width: 1100px)").matches;
      if (stacked) {
        view.style.marginLeft = (-left) + "px";
        view.style.width = width + "px";
      } else {
        view.style.marginLeft = "0px";
        view.style.width = Math.max(0, width - left) + "px";
      }
    }
    placeCanvas = place;
    view.addEventListener("wheel", function (ev) {
      ev.preventDefault();
      const next = Math.min(2.5, Math.max(0.35, scale * (ev.deltaY < 0 ? 1.08 : 0.92)));
      const rect = view.getBoundingClientRect();
      const ox = ev.clientX - rect.left;
      const oy = ev.clientY - rect.top;
      x = ox - (ox - x) * (next / scale);
      y = oy - (oy - y) * (next / scale);
      scale = next;
      paint();
    }, { passive: false });
    view.addEventListener("pointerdown", function (ev) {
      if (ev.button !== 0) return;
      drag = { x: ev.clientX, y: ev.clientY, ox: x, oy: y };
      moved = false;
    });
    view.addEventListener("pointermove", function (ev) {
      if (!drag) return;
      const dx = ev.clientX - drag.x;
      const dy = ev.clientY - drag.y;
      if (!moved && Math.hypot(dx, dy) < 4) return;
      moved = true;
      x = drag.ox + dx;
      y = drag.oy + dy;
      paint();
    });
    function endDrag() { drag = null; }
    view.addEventListener("pointerup", endDrag);
    view.addEventListener("pointercancel", endDrag);
    view.addEventListener("click", function (ev) {
      if (!moved) return;
      ev.preventDefault();
      ev.stopPropagation();
      moved = false;
    }, true);
    requestAnimationFrame(place);
    return view;
  }

  function graphBlock(cols, selected, onselect, extra, prov) {
    const graph = h("div", { class: "graph" }, cols.map(function (col) {
      return h("div", { class: "col" }, [
        h("div", { class: "colhead" }, [col.head]),
        ...visibleNodes(col, selected, onselect),
      ]);
    }));
    return h("div", {}, [
      h("div", { class: "quiet" }, [prov || ""]),
      viewportCanvas(graph),
      extra || null,
    ]);
  }

  function visibleNodes(col, selected, onselect) {
    const key = col.head;
    const nodes = col.nodes || [];
    const open = expanded[key];
    const shown = open || nodes.length <= 7 ? nodes : nodes.slice(0, 6);
    const out = shown.map(function (node) { return nodeButton(node, selected, onselect); });
    if (!open && nodes.length > 7) {
      out.push(h("button", { class: "more", on: { click: function () { expanded[key] = true; rerender(false); } } }, ["+" + (nodes.length - 6) + " more"]));
    }
    return out;
  }

  function nodeButton(node, selected, onselect) {
    const on = node.id === selected || node.selectedId && !selected;
    const cls = ["node", node.epistemic || "declared", node.bit || "", node.change ? "change" : "", node.dim ? "dim" : "", on ? "is-selected" : ""].filter(Boolean).join(" ");
    return h("button", { class: cls, on: { click: function () { onselect(node.id); } } }, [
      h("div", { class: "id" }, [breakable(node.id)]),
      h("div", { class: "sub" }, [node.sub || " "]),
    ]);
  }

  function blastBlock(graph, selfId, selected, persp, onselect) {
    if (!graph) return h("p", { class: "note" }, ["impact returned nothing for this id."]);
    const known = perspectiveSubjects(graph, persp);
    const byDist = {};
    (graph.affected || []).forEach(function (node) {
      const d = node.distance || 0;
      byDist[d] = byDist[d] || [];
      const inSet = !known || known.has(node.id);
      byDist[d].push({
        id: node.id,
        bit: (record(node.id) || {}).bit || "",
        epistemic: node.epistemic_state || "declared",
        sub: annotation(graph, node, persp, inSet),
        change: node.level === "change" || String(node.id).indexOf("change.") === 0,
        dim: known && !inSet,
      });
    });
    const cols = Object.keys(byDist).sort(function (a, b) { return Number(a) - Number(b); }).map(function (dist) {
      return { head: dist === "0" ? "Selected" : dist === "1" ? "1 hop" : dist + " hops", nodes: byDist[dist] };
    });
    const chosen = (graph.affected || []).filter(function (node) { return node.id === selected; })[0];
    const panel = chosen ? whyPanel(chosen, graph, persp) : h("p", { class: "quiet" }, ["Select an id to see why it is in this blast."]);
    const absence = absenceLine(graph, persp);
    return graphBlock(cols, selected, onselect, h("div", {}, [absence, panel]), "derived · kernel impact");
  }

  function perspectiveSubjects(graph, persp) {
    const p = graph.perspectives || {};
    if (persp === "system") return null;
    if (persp === "product") return new Set(((p.product || {}).items || []).map(function (item) { return item.subject; }).filter(Boolean));
    if (persp === "quality") {
      const q = p.quality || {};
      const ids = [];
      ["criteria", "verification", "journeys", "sensors", "contracts", "rollout"].forEach(function (key) {
        (q[key] || []).forEach(function (item) { if (item.subject) ids.push(item.subject); });
      });
      return new Set(ids);
    }
    if (persp === "governance") return new Set(((p.governance || {}).concerns || []).map(function (item) { return item.subject; }));
    if (persp === "ownership") return new Set(((p.ownership || {}).associations || []).map(function (item) { return item.subject; }));
    return null;
  }

  function annotation(graph, node, persp, inSet) {
    if (persp === "system" || inSet === false && persp === "system") {
      return (node.epistemic_state || "declared") + (node.relationship ? " · " + node.relationship : "");
    }
    if (!inSet) {
      if (persp === "governance") return "No governance relationship identified in the current model.";
      if (persp === "ownership") return "No ownership information represented.";
      if (persp === "quality") return "Quality evidence not represented.";
      return "not represented";
    }
    const p = graph.perspectives || {};
    if (persp === "ownership") {
      const hit = ((p.ownership || {}).associations || []).filter(function (item) { return item.subject === node.id; })[0];
      return hit ? "owner " + hit.owner + " · " + hit.epistemic_state : "No ownership information represented.";
    }
    if (persp === "governance") {
      const hit = ((p.governance || {}).concerns || []).filter(function (item) { return item.subject === node.id; })[0];
      return hit ? hit.concern + " · " + (hit.source || "declared") : "No governance relationship identified in the current model.";
    }
    if (persp === "product") {
      const hit = ((p.product || {}).items || []).filter(function (item) { return item.subject === node.id; })[0];
      return hit ? (hit.kind || "product") : "not represented";
    }
    if (persp === "quality") {
      const q = p.quality || {};
      const hit = ["criteria", "verification", "journeys", "sensors", "contracts", "rollout"].reduce(function (found, key) {
        return found || (q[key] || []).filter(function (item) { return item.subject === node.id; })[0];
      }, null);
      return hit ? (hit.kind || "quality") + " · " + (hit.source || "") : "Quality evidence not represented.";
    }
    return (node.epistemic_state || "declared") + (node.relationship ? " · " + node.relationship : "");
  }

  function absenceLine(graph, persp) {
    const p = graph.perspectives || {};
    if (persp === "governance" && !((p.governance || {}).concerns || []).length) {
      const line = (((p.governance || {}).gaps || [])[0] || {}).statement || "No governance relationship identified in the current model.";
      return h("p", { class: "note" }, [line, " That is not a finding of no impact."]);
    }
    if (persp === "ownership") {
      const missing = ((p.ownership || {}).gaps || []).length;
      const found = ((p.ownership || {}).associations || []).length;
      if (!found) return h("p", { class: "note" }, ["No ownership information represented."]);
      if (missing) return h("p", { class: "note" }, [found + " declare an owner. The rest are not represented."]);
    }
    return null;
  }

  function whyPanel(node, graph, persp) {
    const steps = node.path || [];
    const chain = steps.length
      ? steps.map(function (step) { return step.from + " —" + step.relationship + "→ " + step.to; }).join("  ·  ")
      : "This is the selected id.";
    return h("div", { class: "why" }, [
      h("div", {}, [chain]),
      node.note ? h("div", { class: "note" }, [node.note]) : null,
      h("div", { class: "src" }, [node.epistemic_state || "declared", node.relationship ? " · " + node.relationship : "", " · impact.affected.path"]),
      h("div", {}, [idLink(node.id)]),
      perspectiveDetail(graph, node.id, persp),
    ]);
  }

  function perspectiveDetail(graph, id, persp) {
    const p = graph.perspectives || {};
    if (persp === "product") {
      return h("div", {}, productItems(graph, id).slice(0, 6).map(itemRow));
    }
    if (persp === "governance") {
      const hits = ((p.governance || {}).concerns || []).filter(function (item) { return item.subject === id; });
      if (!hits.length) return h("p", { class: "note" }, ["No governance relationship identified in the current model."]);
      return h("div", {}, hits.map(function (item) {
        return h("div", { class: "item" }, [(item.statements || []).join("; "), h("div", { class: "src" }, [item.subject + " · " + item.source])]);
      }));
    }
    if (persp === "ownership") {
      const hits = ((p.ownership || {}).associations || []).filter(function (item) { return item.subject === id; });
      if (!hits.length) return h("p", { class: "note" }, ["No ownership information represented."]);
      return h("div", {}, hits.map(function (item) {
        return h("div", { class: "item" }, [item.owner, h("div", { class: "src" }, [item.source + " · " + item.epistemic_state])]);
      }));
    }
    return null;
  }

  function outcomeLines(outcomes) {
    if (!outcomes || typeof outcomes !== "object") return [];
    return Object.keys(outcomes).map(function (key) {
      const value = outcomes[key];
      const text = Array.isArray(value) ? value.join(", ") : String(value);
      return key + ": " + text;
    });
  }

  function diagramBlock(rec) {
    const diagrams = rec.diagrams || [];
    if (!diagrams.length) return h("p", { class: "note" }, ["No diagram declared on this id."]);
    return h("div", {}, [
      h("div", { class: "quiet" }, ["declared · diagrams on this id"]),
      viewportCanvas(h("div", { class: "diagrams" }, diagrams.map(function (diagram) { return diagramCard(diagram); }))),
    ]);
  }

  function diagramCard(diagram) {
    const host = h("div", { class: "diagram" });
    const title = diagram.title || diagram.type || "diagram";
    const source = diagram.mermaid || "";
    if (source && window.mermaid && window.mermaid.render) {
      const id = "spdiag" + (++diagramSeq);
      window.mermaid.render(id, source).then(function (result) {
        const holder = document.createElement("div");
        holder.innerHTML = result.svg;
        host.replaceChildren();
        while (holder.firstChild) host.append(holder.firstChild);
      }).catch(function () {
        host.replaceChildren(h("pre", {}, [source]));
      });
    } else if (source) {
      host.append(h("pre", {}, [source]));
    }
    return h("div", { class: "item" }, [
      title,
      diagram.type ? h("div", { class: "src" }, [diagram.type + " · diagrams"]) : null,
      diagram.description ? h("div", {}, [diagram.description]) : null,
      host,
    ]);
  }

  function dataBlock(rec, graph) {
    const contracts = ((((graph || {}).perspectives || {}).quality || {}).contracts) || [];
    const mine = contracts.filter(function (item) {
      return item.subject === rec.id && item.kind === "data_models" && item.models;
    });
    if (!mine.length) return h("p", { class: "note" }, ["No data model declared on this id."]);
    return h("div", {}, [
      h("div", { class: "quiet" }, ["declared · implementation.contracts.data_models"]),
      ...mine.map(function (item) {
        return h("div", {}, Object.keys(item.models).map(function (name) {
          return h("div", { class: "item" }, [
            modelLine(name, item.models[name]),
            h("div", { class: "src" }, [item.subject + " · " + (item.source || "contracts.data_models")]),
          ]);
        }));
      }),
    ]);
  }

  function modelLine(name, value) {
    let extra = "";
    if (Array.isArray(value)) extra = value.join(", ");
    else if (value && typeof value === "object") {
      const fields = value.fields;
      extra = Array.isArray(fields) ? fields.join(", ") : Object.keys(value).join(", ");
    } else if (value != null && value !== "") extra = String(value);
    return extra ? name + " — " + extra : name;
  }

  function journeyBlock(rec, graph) {
    const flows = productItems(graph, rec.id).filter(function (item) { return item.kind === "flow"; });
    const journeys = (((graph || {}).perspectives || {}).quality || {}).journeys || [];
    const mine = journeys.filter(function (item) { return item.subject === rec.id; });
    return h("div", {}, [
      h("div", { class: "quiet" }, ["declared · flows on this id"]),
      ...flows.map(function (item) {
        const stages = (item.stages || []).length ? item.stages.join(" → ") : "";
        const endings = outcomeLines(item.outcomes);
        return h("div", { class: "item" }, [
          item.detail || item.flow_id || item.goal || "flow",
          item.goal ? h("div", {}, [item.goal]) : null,
          stages ? h("div", {}, [stages]) : null,
          ...endings.map(function (line) { return h("div", {}, [line]); }),
          h("div", { class: "src" }, [(item.subject || rec.id) + " · " + (item.source || "flows")]),
        ]);
      }),
      ...mine.map(function (item) {
        const bits = [];
        if ((item.exceptions || []).length) bits.push("exceptions: " + item.exceptions.join(", "));
        if ((item.recovery || []).length) bits.push("recovery: " + item.recovery.join(", "));
        return h("div", { class: "item" }, [
          item.flow_id || "journey",
          bits.length ? h("div", {}, [bits.join(" · ")]) : null,
          h("div", { class: "src" }, [item.subject + " · " + (item.source || "flows")]),
        ]);
      }),
    ]);
  }

  function changePage(route) {
    const change = (DATA.changes || []).filter(function (item) { return item.id === route.arg; })[0];
    if (!change) return h("p", {}, ["No open change named ", route.arg]);
    const graph = (DATA.impacts || {})["change:" + change.id];
    const node = route.query.get("node") || "";
    const persp = route.query.get("persp") || "system";
    const sync = change.check_sync || {};
    return h("div", { class: "split" }, [
      h("div", { class: "copy" }, [
        h("div", { class: "kicker" }, ["Change"]),
        h("div", { class: "row" }, [h("span", { class: "mono inflight" }, [breakable(change.id)])]),
        h("div", { class: "quiet" }, ["in-flight", change.kind ? " · kind " + change.kind : ""]),
        h("div", { class: "kicker" }, ["Why"]),
        h("p", { class: "purpose" }, [change.why || ""]),
        h("h2", { class: "kicker" }, ["Promise ids"]),
        h("div", {}, (change.promise_ids || []).map(function (id) { return h("div", { class: "item" }, [idLink(id)]); })),
        deltaBlock(change.delta),
        sensorBlock(sync),
        h("h2", { class: "kicker" }, ["What SpecPlane checked"]),
        h("p", { class: "note" }, ["SpecPlane checked declared coverage. It did not verify behavior."]),
        h("p", { class: "quiet" }, ["coverage " + (sync.coverage || ""), " · sensors " + (sync.sensors || ""), " · behavior unverified"]),
        h("p", { class: "note" }, ["SpecPlane did not certify that an implementation satisfies the spec."]),
      ]),
      h("div", {}, [
        switcher(change.projections || ["blast"], "blast", function () {}),
        perspectiveRow(persp, function (name) { go("change/" + change.id, { persp: name, node: node }); }),
        blastBlock(graph, "change." + change.id, node, persp, function (id) {
          go("change/" + change.id, { persp: persp, node: id });
        }),
      ]),
    ]);
  }

  function deltaBlock(delta) {
    const keys = delta ? Object.keys(delta) : [];
    if (!keys.length) return null;
    return h("div", {}, [
      h("h2", { class: "kicker" }, ["Delta"]),
      ...keys.map(function (key) {
        return h("div", {}, [h("div", { class: "quiet" }, [key]), ...(delta[key] || []).map(function (line) {
          return h("div", { class: "item" }, [line]);
        })]);
      }),
    ]);
  }

  function sensorBlock(sync) {
    const rows = (sync && sync.sensor_rows) || [];
    if (!rows.length) return h("p", { class: "note" }, ["No success sensor declared."]);
    return h("div", {}, [
      h("h2", { class: "kicker" }, ["Success sensors"]),
      ...rows.map(function (row) {
        return h("div", { class: "item" }, [
          h("div", { class: "sensor" }, [row.must || ""]),
          h("div", { class: "src" }, [(row.change || "") + " · success.yaml · not run"]),
        ]);
      }),
    ]);
  }

  function rerender(keepFind) {
    const input = document.getElementById("find");
    const pos = keepFind && input ? input.selectionStart : null;
    render();
    if (keepFind) {
      const next = document.getElementById("find");
      if (next) {
        next.focus();
        next.selectionStart = next.selectionEnd = pos;
      }
    }
  }

  function render() {
    const route = parse();
    let body;
    if (route.kind === "changes") body = changesIndex();
    else if (route.kind === "gaps") body = gapsIndex();
    else if (route.kind === "id") body = recordPage(route);
    else if (route.kind === "change") body = changePage(route);
    else body = liveIndex(route);
    document.getElementById("app").replaceChildren(shell(route, body));
  }

  window.addEventListener("hashchange", function () { render(); });
  render();
})();
