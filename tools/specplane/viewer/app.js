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
  let openSections = {};
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
    if (p.src) node.setAttribute("src", p.src);
    if (p.alt != null) node.setAttribute("alt", p.alt);
    if (p.label) node.setAttribute("aria-label", p.label);
    if (p.type) node.type = p.type;
    if (p.placeholder) node.placeholder = p.placeholder;
    if (p.value != null && String(tag).toLowerCase() === "input") node.value = p.value;
    if (p.open) node.open = true;
    if (p.on) {
      Object.keys(p.on).forEach(function (ev) { node.addEventListener(ev, p.on[ev]); });
    }
    function place(kid) {
      if (kid == null || kid === false) return;
      if (Array.isArray(kid)) { kid.forEach(place); return; }
      node.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
    }
    (children || []).forEach(place);
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

  function glyph(name) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    if (name === "sun") {
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", "currentColor");
      path.setAttribute("stroke-width", "1.75");
      path.setAttribute("stroke-linecap", "round");
      path.setAttribute("stroke-linejoin", "round");
      path.setAttribute("d", "M12 3v2.25M18.364 5.636l-1.591 1.591M21 12h-2.25M18.364 18.364l-1.591-1.591M12 18.75V21M7.227 16.773l-1.591 1.591M5.25 12H3M7.227 7.227 5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0z");
    } else {
      path.setAttribute("fill", "currentColor");
      path.setAttribute("d", "M21.75 15A9.75 9.75 0 0 1 9 2.25 7.5 7.5 0 1 0 21.75 15z");
    }
    svg.append(path);
    return svg;
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
    const next = chosen === "dark" ? "light" : "dark";
    const theme = h("button", {
      type: "button",
      class: "theme-btn",
      label: next === "dark" ? "Dark" : "Light",
      on: { click: function () { setTheme(next); rerender(false); } },
    }, [glyph(next === "dark" ? "moon" : "sun")]);
    const ctx = DATA.context || {};
    const rootName = ctx.spec_root || "specs";
    const branch = ctx.branch || "";
    const where = rootName + "/" + (branch ? " @ " + branch : "") + " · read-only";
    const systems = Object.keys(DATA.records || {}).filter(function (id) {
      return (DATA.records[id] || {}).level === "system";
    }).sort();
    const top = h("header", { class: "top" }, [
      h("div", { class: "brand" }, [
        h("img", { src: "logo.png", alt: "" }),
        "SpecPlane",
        ...systems.map(function (id) {
          return h("a", { class: "sys", href: href("id/" + encodeURIComponent(id)) }, [breakable(id)]);
        }),
      ]),
      nav,
      h("div", { class: "top-end" }, [
        h("div", { class: "where" }, [where]),
        theme,
      ]),
    ]);
    return h("div", {}, [top, honesty(route), h("main", { class: "page" }, [body])]);
  }

  let trail = [];

  function noteVisit(id) {
    const at = trail.lastIndexOf(id);
    if (at === trail.length - 1) return;
    if (at >= 0) trail = trail.slice(0, at + 1);
    else trail.push(id);
  }

  function crumb(id) {
    return h("span", { class: "crumb" }, [
      h("span", { class: "sep" }, ["›"]),
      h("a", { class: "mono", href: href("id/" + encodeURIComponent(id)) }, [breakable(id)]),
    ]);
  }

  function honesty(route) {
    if (route.kind === "id") {
      const rec = record(route.arg);
      if (!rec) return null;
      noteVisit(rec.id);
      const back = trail.length > 1 ? trail[trail.length - 2] : "";
      return h("div", { class: "bar" }, [
        h("div", { class: "trail" }, [
          h("a", { href: back ? href("id/" + encodeURIComponent(back)) : href("live") }, [back ? "← Back" : "← Live"]),
          ...trail.slice(0, -1).map(crumb),
          crumb(rec.id),
        ]),
        h("div", { class: "quiet mono" }, [rec.bit === "inferred" ? "inferred · not live" : (rec.bit || "live")]),
      ]);
    }
    if (route.kind === "change") {
      return h("div", { class: "bar" }, [
        h("div", { class: "trail" }, [
          h("a", { href: href("changes") }, ["← Changes"]),
          h("span", { class: "crumb" }, [h("span", { class: "sep" }, ["›"]), h("span", { class: "mono inflight" }, [breakable(route.arg)])]),
        ]),
        h("div", { class: "inflight" }, ["in-flight"]),
      ]);
    }
    if (route.kind === "live" || route.kind === "changes" || route.kind === "gaps") trail = [];
    return null;
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
    const filters = h("div", { class: "seg" }, ["live", "inferred", "replaced"].map(function (name) {
      return h("button", {
        class: bit === name ? "on" : "",
        on: { click: function () { go("live", { bit: name }); } },
      }, [name[0].toUpperCase() + name.slice(1) + " ", h("span", { class: "count" }, [String(counts[name])])]);
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
        return h("tr", { on: { click: function () { go("id/" + encodeURIComponent(rec.id)); } } }, [
          h("td", {}, [bitMark(rec.bit), " ", idLink(rec.id)]),
          h("td", {}, [rec.purpose || ""]),
          h("td", { class: "quiet" }, [(rec.bit || "live") + (rec.review_state ? " · " + rec.review_state : "")]),
          h("td", {}, [n ? h("a", {
            class: "inflight",
            href: href("change/" + rec.in_flight[0].id),
            on: { click: function (ev) { ev.stopPropagation(); } },
          }, [n === 1 ? "1 open change" : n + " open changes"]) : ""]),
        ]);
      })),
    ]);
    const feet = {
      live: "In flight is not a filter: an id is in flight when an open change names it.",
      inferred: "Inferred ids were recovered from code. They are explorable and stay marked until promoted.",
      replaced: "Replaced ids stay so history resolves. They are not part of the live model.",
    };
    return h("section", {}, [
      h("h1", {}, ["Live"]),
      h("p", { class: "note" }, ["Capabilities in the spec root. Components, containers, and foundations are reached from an id."]),
      h("div", { class: "tools" }, [filters, find]),
      table,
      h("p", { class: "quiet" }, [feet[bit] || feet.live]),
    ]);
  }

  function changesIndex() {
    const q = findText.trim().toLowerCase();
    const rows = (DATA.changes || []).filter(function (c) {
      return !q || c.id.toLowerCase().indexOf(q) >= 0 || (c.why || "").toLowerCase().indexOf(q) >= 0;
    });
    return h("section", { class: "changes-index" }, [
      h("h1", {}, ["Changes"]),
      h("p", { class: "note" }, ["Open change folders. Nothing here is live until it is promoted."]),
      h("div", { class: "tools" }, [h("input", {
        id: "find", class: "find", type: "search", placeholder: "Find by slug or why", value: findText,
        on: { input: function (ev) { findText = ev.target.value; rerender(true); } },
      })]),
      h("table", { class: "index changes" }, [
        h("tbody", {}, rows.map(function (c) {
          const sensor = c.check_sync && c.check_sync.sensors === "declared"
            ? (c.check_sync.sensor_rows || []).length + " sensors declared · not run"
            : "No success sensor declared";
          return h("tr", { on: { click: function () { go("change/" + c.id); } } }, [
            h("td", {}, [h("a", { class: "mono inflight", href: href("change/" + c.id) }, [breakable(c.id)])]),
            h("td", { class: "quiet mono kind" }, [c.kind || ""]),
            h("td", { class: "promises" }, (c.promise_ids || []).map(function (id) { return idLink(id); })),
            h("td", { class: "quiet" }, [sensor]),
            h("td", { class: "opened" }, [c.opened ? "Opened " + c.opened : ""]),
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
          const query = { proj: proj, persp: persp, node: id };
          const dg = route.query.get("dg");
          if (dg) query.dg = dg;
          go("id/" + encodeURIComponent(rec.id), query);
        }),
      ]),
    ]);
  }

  function flight(rec) {
    if (!rec.in_flight || !rec.in_flight.length) return null;
    return h("div", {}, rec.in_flight.map(function (c) {
      return h("div", { class: "strip" }, [
        h("div", {}, [h("span", { class: "acc-sub" }, ["In flight"]), " ", idLink(c.id), c.kind ? h("span", { class: "quiet" }, [" " + c.kind]) : ""]),
        c.why ? h("div", {}, [c.why]) : null,
        h("a", { href: href("change/" + c.id) }, ["Open change →"]),
      ]);
    }));
  }

  function plural(n, one, many) {
    return n + " " + (n === 1 ? one : (many || one + "s"));
  }

  function section(key, title, sub, summary, body) {
    const open = !!openSections[key];
    return h("div", { class: "acc" }, [
      h("button", { class: "acc-head", type: "button", on: { click: function () { openSections[key] = !open; rerender(false); } } }, [
        h("span", { class: "acc-text" }, [
          h("span", {}, [h("span", { class: "acc-title" }, [title + " "]), h("span", { class: "acc-sub" }, [sub])]),
          summary ? h("span", { class: "acc-sum" }, [summary]) : null,
        ]),
        h("span", { class: "acc-chev" }, [open ? "Close ↑" : "Open ↓"]),
      ]),
      open ? h("div", { class: "acc-body" }, body) : null,
    ]);
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
    const summary = [duties.length ? plural(duties.length, "responsibility", "responsibilities") : "", items.length ? plural(items.length, "declared line") : ""].filter(Boolean).join(" · ");
    return section("def:" + rec.id, "Definition", "what is promised", summary, [
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
    return section("real:" + rec.id, "Realization", "how it is built and checked", [realized.length ? plural(realized.length, "realizing id") : "", rows.length ? plural(rows.length, "check") : ""].filter(Boolean).join(" · "), [
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
    return section("ask:" + rec.id, "Open questions", "declared unknowns", plural(items.length, "question"), items.map(itemRow));
  }

  function itemRow(item) {
    return h("div", { class: "item" }, [
      item.detail || item.goal || item.kind || "",
      h("div", { class: "src" }, [(item.subject ? item.subject + " · " : "") + (item.source || "")]),
    ]);
  }

  function switcher(names, current, onclick) {
    return h("div", { class: "tabs seg" }, names.map(function (name) {
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
    if (proj === "map") return graphBlock(mapColumns(rec), selected, onselect, mapWhy(rec, selected), "derived · from declared links");
    if (proj === "layers") return graphBlock(layerColumns(rec), selected, onselect, null, "derived · 5C placement");
    if (proj === "journey") return journeyBlock(rec, graph);
    if (proj === "diagrams") return diagramBlock(rec, selected, onselect);
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

  function graphBlock(cols, selected, onselect, extra, prov, kind) {
    const graph = h("div", { class: "graph" + (kind ? " " + kind : "") }, cols.map(function (col) {
      return h("div", { class: "col" }, [
        h("div", { class: "colhead" }, [col.head]),
        ...visibleNodes(col, selected, onselect),
      ]);
    }));
    return h("div", {}, [
      h("div", { class: "quiet" }, [prov || ""]),
      graph,
      legend(),
      extra || null,
    ]);
  }

  function legend() {
    return h("div", { class: "legend" }, [
      ["declared", "declared link"],
      ["derived", "derived reach"],
      ["inferred", "inferred link"],
      ["unknown", "not represented"],
    ].map(function (pair) {
      return h("span", {}, [h("span", { class: "swatch " + pair[0] }), pair[1]]);
    }));
  }

  function visibleNodes(col, selected, onselect) {
    if (col.further) {
      return [h("button", {
        class: "more further-box",
        on: { click: function () { expanded.furtherHops = true; rerender(false); } },
      }, ["+" + col.count + " more ids at " + col.minDist + "+ hops — select to expand"])];
    }
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
    const on = selected ? node.id === selected : node.distance === 0 || (node.selectedId && !selected);
    const cls = ["node", node.epistemic || "declared", node.bit || "", node.change ? "change" : "", node.dim ? "dim" : "", on ? "is-selected" : ""].filter(Boolean).join(" ");
    const lines = node.lines && node.lines.length ? node.lines : ["", ""];
    return h("button", { class: cls, on: { click: function () { onselect(node.id); } } }, [
      h("div", { class: "pre" }, [node.epistemic || "declared"]),
      h("div", { class: "id" }, [breakable(node.id)]),
      h("div", { class: "sub" }, [node.sub || " "]),
      h("div", { class: "line", title: lines[0] || "" }, [lines[0] || " "]),
      h("div", { class: "line", title: lines[1] || "" }, [lines[1] || " "]),
    ]);
  }

  function shortRel(rel) {
    return String(rel || "").replace(/\..*$/, "") || "linked";
  }

  function shortId(id) {
    const s = String(id || "");
    const i = s.lastIndexOf(".");
    return i >= 0 ? s.slice(i + 1) : s;
  }

  function hopRel(node) {
    if (!node.distance) return "selected";
    const steps = node.path || [];
    const via = steps.length ? steps[steps.length - 1].from : "";
    const rel = node.relationship || "";
    return via ? rel + " · " + via : rel;
  }

  function isTerminal(node) {
    return node.level === "foundation" || shortRel(node.relationship) === "uses";
  }

  function hopLines(node, persp, inSet, graph) {
    const hop = !node.distance
      ? "selected"
      : isTerminal(node)
        ? "terminal · not expanding"
        : (node.direct && node.distance === 1 ? "direct" : node.distance + " hops");
    if (persp === "system") return [hop, node.epistemic_state || "declared"];
    const extra = perspectiveLines(graph, node, persp, inSet);
    return [hop, extra[0] || node.epistemic_state || "declared"];
  }

  function blastCards(graph, persp, nodes) {
    const known = perspectiveSubjects(graph, persp);
    return nodes.map(function (node) {
      const inSet = !known || known.has(node.id);
      return {
        id: node.id,
        distance: node.distance || 0,
        bit: (record(node.id) || {}).bit || "",
        epistemic: node.epistemic_state || "declared",
        sub: hopRel(node),
        lines: hopLines(node, persp, inSet, graph),
        change: node.level === "change" || String(node.id).indexOf("change.") === 0,
        dim: known && !inSet,
      };
    });
  }

  function blastBlock(graph, selfId, selected, persp, onselect) {
    if (!graph) return h("p", { class: "note" }, ["impact returned nothing for this id."]);
    const byDist = {};
    (graph.affected || []).forEach(function (node) {
      const d = node.distance || 0;
      byDist[d] = byDist[d] || [];
      byDist[d].push(node);
    });
    if (expanded.furtherFor !== selfId) {
      expanded.furtherHops = false;
      expanded.furtherFor = selfId;
    }
    const dists = Object.keys(byDist).map(Number).sort(function (a, b) { return a - b; });
    const cols = [];
    dists.forEach(function (dist) {
      if (dist >= 3 && !expanded.furtherHops) return;
      const head = dist === 0 ? "Selected" : dist === 1 ? "1 hop · direct" : dist + " hops";
      cols.push({ head: head, nodes: blastCards(graph, persp, byDist[dist]) });
    });
    const far = dists.filter(function (dist) { return dist >= 3; }).reduce(function (n, dist) { return n + byDist[dist].length; }, 0);
    if (far && !expanded.furtherHops) {
      cols.push({ head: "Further", further: true, count: far, minDist: 3 });
    }
    const chosen = (graph.affected || []).filter(function (node) { return node.id === selected; })[0]
      || (graph.affected || []).filter(function (node) { return !node.distance; })[0];
    const panel = chosen ? whyPanel(chosen, graph, persp) : h("p", { class: "quiet" }, ["Select an id to see why it is in this blast."]);
    const absence = absenceLine(graph, persp);
    return graphBlock(cols, selected, onselect, h("div", {}, [absence, panel]), "derived · kernel impact", "blast");
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

  function perspectiveLines(graph, node, persp, inSet) {
    if (persp === "system") return [node.epistemic_state || "declared", ""];
    if (!inSet) {
      if (persp === "governance") return ["not represented", "No governance relationship identified in the current model."];
      if (persp === "ownership") return ["not represented", "No ownership information represented."];
      if (persp === "quality") return ["not represented", "Quality evidence not represented."];
      return ["not represented", ""];
    }
    const text = annotation(graph, node, persp, inSet);
    const cut = text.indexOf(" · ");
    if (cut < 0) return [text, ""];
    return [text.slice(0, cut), text.slice(cut + 3)];
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

  function whyBox(id, text, prov, extra) {
    return h("div", { class: "why" }, [
      h("div", { class: "acc-sub" }, ["Why this is here"]),
      h("div", { class: "mono" }, [breakable(id)]),
      h("div", {}, [text]),
      h("div", { class: "src" }, [prov]),
      (record(id) || String(id).indexOf("change.") === 0) ? h("a", { href: href(String(id).indexOf("change.") === 0 ? "change/" + String(id).replace(/^change\./, "") : "id/" + encodeURIComponent(id)) }, ["Open " + id + " →"]) : null,
      extra || null,
    ]);
  }

  function mapWhy(rec, selected) {
    if (!selected) return h("p", { class: "quiet" }, ["Select an id to see why it is on this map."]);
    if (selected === rec.id) return whyBox(selected, "The selected id.", "declared · this record");
    const link = (rec.links || []).filter(function (item) { return item.id === selected; })[0];
    const rel = link ? (REL[link.rel] || link.rel) : "Linked";
    return whyBox(selected, rel + " from " + rec.id + ".", (link ? rec.id + " · " + link.rel : "declared link"));
  }

  function whyPanel(node, graph, persp) {
    const steps = node.path || [];
    const chain = steps.length
      ? steps.map(function (step) { return step.from + " —" + step.relationship + "→ " + step.to; }).join("  ·  ")
      : "The selected id.";
    return whyBox(
      node.id,
      chain,
      (node.epistemic_state || "declared") + (node.relationship ? " · " + node.relationship : "") + " · impact.affected.path",
      h("div", {}, [node.note ? h("div", { class: "note" }, [node.note]) : null, perspectiveDetail(graph, node.id, persp)])
    );
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

  function parseFlow(src) {
    const nodes = [];
    const by = {};
    const edges = [];
    function tok(t) {
      const m = String(t).trim().match(/^([A-Za-z0-9_]+)\s*(?:\(\[(.+?)\]\)|\{(.+?)\}|\[(.+?)\]|\((.+?)\))?$/);
      if (!m) return null;
      const id = m[1];
      if (!by[id]) {
        by[id] = { id: id, text: "", shape: "box" };
        nodes.push(by[id]);
      }
      const n = by[id];
      if (m[2]) { n.text = m[2]; n.shape = "end"; }
      else if (m[3]) { n.text = m[3]; n.shape = "decision"; }
      else if (m[4] || m[5]) n.text = m[4] || m[5];
      return id;
    }
    String(src || "").split("\n").slice(1).forEach(function (line) {
      const p = line.trim().split(/\s*-->\s*(?:\|([^|]*)\|\s*)?/);
      if (p.length < 3) {
        if (line.trim() && line.trim().indexOf("flowchart") !== 0) tok(line);
        return;
      }
      for (let i = 0; i + 2 < p.length; i += 2) {
        const a = tok(p[i]);
        const b = tok(p[i + 2]);
        if (a && b) edges.push({ from: a, to: b, label: p[i + 1] || "" });
      }
    });
    return { nodes: nodes, edges: edges };
  }

  function flowPlace(nodes, edges) {
    const ids = nodes.map(function (n) { return n.id; });
    const inc = {};
    edges.forEach(function (e) { inc[e.to] = true; });
    const start = ids.filter(function (id) { return !inc[id]; })[0] || ids[0];
    const rank = {};
    const row = {};
    const occ = {};
    function place(id, r) {
      let w = r;
      while (occ[rank[id] + "," + w]) w += 1;
      row[id] = w;
      occ[rank[id] + "," + w] = true;
    }
    const q = [];
    function run() {
      while (q.length) {
        const u = q.shift();
        edges.filter(function (e) { return e.from === u; }).forEach(function (e) {
          if (rank[e.to] === undefined) {
            rank[e.to] = rank[u] + 1;
            place(e.to, row[u]);
            q.push(e.to);
          }
        });
      }
    }
    if (start) {
      rank[start] = 0;
      place(start, 0);
      q.push(start);
      run();
    }
    ids.forEach(function (id) {
      if (rank[id] === undefined) {
        rank[id] = 0;
        place(id, 0);
        q.push(id);
        run();
      }
    });
    return { rank: rank, row: row };
  }

  function edgePath(a, b) {
    const acx = a.x + a.w / 2;
    const bcx = b.x + b.w / 2;
    if (b.r > a.r) {
      const y1 = a.y + a.h;
      const y2 = b.y;
      const mid = (y1 + y2) / 2;
      if (a.l === b.l) return "M" + acx + " " + y1 + " L" + bcx + " " + y2;
      return "M" + acx + " " + y1 + " C" + acx + " " + mid + " " + bcx + " " + mid + " " + bcx + " " + y2;
    }
    if (b.r === a.r) {
      const y = a.y + 18;
      const x1 = b.l > a.l ? a.x + a.w : a.x;
      const x2 = b.l > a.l ? b.x : b.x + b.w;
      return "M" + x1 + " " + y + " L" + x2 + " " + y;
    }
    const x1 = a.x + a.w;
    const y1 = a.y + 22;
    const y2 = b.y + 22;
    const bend = x1 + 36;
    return "M" + x1 + " " + y1 + " C" + bend + " " + y1 + " " + bend + " " + y2 + " " + (b.x + b.w) + " " + y2;
  }

  function layoutFlow(src) {
    const parsed = parseFlow(src);
    if (!parsed.nodes.length) return null;
    const place = flowPlace(parsed.nodes, parsed.edges);
    const nw = 168;
    const nh = 72;
    const gx = 64;
    const gy = 56;
    const pad = 16;
    const pos = {};
    let maxR = 0;
    let maxL = 0;
    parsed.nodes.forEach(function (n) {
      const r = place.rank[n.id] || 0;
      const l = place.row[n.id] || 0;
      maxR = Math.max(maxR, r);
      maxL = Math.max(maxL, l);
      pos[n.id] = { x: pad + l * (nw + gx), y: pad + r * (nh + gy), w: nw, h: nh, r: r, l: l };
    });
    const edges = parsed.edges.map(function (e, i) {
      const a = pos[e.from];
      const b = pos[e.to];
      const midX = ((a.x + a.w / 2) + (b.x + b.w / 2)) / 2;
      const midY = b.r > a.r ? a.y + a.h + gy / 2 : (a.y + b.y) / 2;
      return { key: i, d: edgePath(a, b), label: e.label, x: midX, y: midY, back: b.r < a.r };
    });
    return {
      kind: "flow",
      nodes: parsed.nodes,
      pos: pos,
      edges: edges,
      width: pad * 2 + (maxL + 1) * nw + maxL * gx,
      height: pad * 2 + (maxR + 1) * nh + maxR * gy,
    };
  }

  function parseSequence(src) {
    const alias = {};
    const parts = [];
    const msgs = [];
    function part(name, label) {
      const key = name;
      if (alias[key] != null) return alias[key];
      alias[key] = parts.length;
      const shown = (label || key).trim();
      parts.push({ name: shown, ref: record(shown) ? shown : "" });
      return alias[key];
    }
    String(src || "").split("\n").forEach(function (raw) {
      const line = raw.trim();
      if (!line || /^sequenceDiagram\b/i.test(line)) return;
      const declared = line.match(/^participant\s+(\S+)(?:\s+as\s+(.+))?$/i);
      if (declared) {
        part(declared[1], declared[2] || declared[1]);
        return;
      }
      const msg = line.match(/^(.+?)\s*(-->>|->>|-->|->)\s*(.+?)\s*:\s*(.*)$/);
      if (!msg) return;
      msgs.push({
        from: part(msg[1].trim(), msg[1].trim()),
        to: part(msg[3].trim(), msg[3].trim()),
        label: msg[4],
        ret: msg[2].indexOf("--") === 0,
      });
    });
    return { parts: parts, msgs: msgs };
  }

  function layoutSequence(src) {
    const parsed = parseSequence(src);
    if (!parsed.parts.length) return null;
    const n = parsed.parts.length;
    const bw = 140;
    const gap = 36;
    const pad = 16;
    const width = pad * 2 + n * bw + (n - 1) * gap;
    const cw = bw + gap;
    const heads = parsed.parts.map(function (p, i) {
      return { name: p.name, ref: p.ref, x: pad + i * cw, y: pad, w: bw, h: 64 };
    });
    const top = pad + 64 + 28;
    const step = 42;
    const height = top + Math.max(parsed.msgs.length, 1) * step + 16;
    const msgs = parsed.msgs.map(function (m, i) {
      const x1 = heads[m.from].x + bw / 2;
      const x2 = heads[m.to].x + bw / 2;
      const y = top + i * step;
      return {
        left: Math.min(x1, x2),
        width: Math.max(Math.abs(x2 - x1), 28),
        top: y,
        label: m.label,
        ret: m.ret,
        self: m.from === m.to,
        fwd: x2 >= x1,
        ax: x2,
      };
    });
    const lifelines = heads.map(function (head) {
      return { x: head.x + bw / 2, top: head.y + head.h, h: height - (head.y + head.h) - 8 };
    });
    return { kind: "sequence", heads: heads, msgs: msgs, lifelines: lifelines, width: width, height: height };
  }

  function svgWires(edges, width, height) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "wires");
    svg.setAttribute("width", String(width));
    svg.setAttribute("height", String(height));
    const marker = "spArrow" + (++diagramSeq);
    svg.innerHTML = "<defs><marker id=\"" + marker + "\" viewBox=\"0 0 8 8\" refX=\"7\" refY=\"4\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto\"><path d=\"M0 0 L8 4 L0 8 z\" fill=\"currentColor\"></path></marker></defs>";
    edges.forEach(function (edge) {
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", edge.d);
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", "currentColor");
      path.setAttribute("stroke-width", "1.5");
      if (edge.back) path.setAttribute("stroke-dasharray", "4 4");
      path.setAttribute("marker-end", "url(#" + marker + ")");
      svg.appendChild(path);
    });
    return svg;
  }

  function diagramPicker(list, index, onpick) {
    return h("div", { class: "picker" }, [
      h("div", { class: "picker-head" }, [
        h("span", {}, [plural(list.length, "diagram") + " declared here"]),
        h("div", { class: "pager" }, [
          h("button", { type: "button", on: { click: function () { onpick((index - 1 + list.length) % list.length); } } }, ["‹"]),
          h("span", { class: "mono" }, [(index + 1) + " of " + list.length]),
          h("button", { type: "button", on: { click: function () { onpick((index + 1) % list.length); } } }, ["›"]),
        ]),
      ]),
      h("div", {}, list.map(function (diagram, i) {
        return h("button", {
          type: "button",
          class: "pick" + (i === index ? " on" : ""),
          on: { click: function () { onpick(i); } },
        }, [
          h("span", { class: "mono" }, [String(i + 1)]),
          h("span", {}, [diagram.title || diagram.type || "diagram"]),
          h("span", { class: "quiet" }, [diagram.type || "diagram"]),
        ]);
      })),
    ]);
  }

  function flowStage(layout, selected, onselect) {
    const stage = h("div", { class: "stage" });
    stage.style.width = layout.width + "px";
    stage.style.height = layout.height + "px";
    stage.appendChild(svgWires(layout.edges, layout.width, layout.height));
    layout.edges.forEach(function (edge) {
      if (!edge.label) return;
      const label = h("div", { class: "edge-label" }, [edge.label]);
      label.style.left = edge.x + "px";
      label.style.top = edge.y + "px";
      stage.appendChild(label);
    });
    layout.nodes.forEach(function (n) {
      const box = layout.pos[n.id];
      const on = n.id === selected;
      const btn = h("button", {
        type: "button",
        class: "node declared" + (on ? " is-selected" : ""),
        on: { click: function () { onselect(n.id); } },
      }, [
        h("div", { class: "pre" }, [n.shape === "end" ? "outcome" : n.shape === "decision" ? "decision" : "step"]),
        h("div", { class: "id" }, [breakable(n.text || n.id)]),
      ]);
      btn.style.left = box.x + "px";
      btn.style.top = box.y + "px";
      btn.style.width = box.w + "px";
      stage.appendChild(btn);
    });
    return stage;
  }

  function sequenceStage(layout, selected, onselect) {
    const stage = h("div", { class: "stage" });
    stage.style.width = layout.width + "px";
    stage.style.height = layout.height + "px";
    layout.lifelines.forEach(function (line) {
      const el = h("div", { class: "lifeline" });
      el.style.left = line.x + "px";
      el.style.top = line.top + "px";
      el.style.height = line.h + "px";
      stage.appendChild(el);
    });
    layout.msgs.forEach(function (msg) {
      const line = h("div", { class: "msg" + (msg.ret ? " ret" : "") });
      line.style.left = msg.left + "px";
      line.style.top = msg.top + "px";
      line.style.width = msg.width + "px";
      const label = h("div", { class: "msg-label" }, [msg.label]);
      label.style.left = (msg.left + msg.width / 2) + "px";
      label.style.top = (msg.top - 16) + "px";
      const arrow = h("div", { class: "msg-arrow" }, [msg.self ? "▼" : msg.fwd ? "▶" : "◀"]);
      arrow.style.left = (msg.self ? msg.left + msg.width - 8 : msg.fwd ? msg.left + msg.width - 10 : msg.left - 2) + "px";
      arrow.style.top = (msg.top - 7) + "px";
      stage.appendChild(line);
      stage.appendChild(label);
      stage.appendChild(arrow);
    });
    layout.heads.forEach(function (head) {
      const on = head.name === selected || head.ref === selected;
      const btn = h("button", {
        type: "button",
        class: "node " + (head.ref ? "declared" : "unknown") + (on ? " is-selected" : ""),
        on: { click: function () { onselect(head.ref || head.name); } },
      }, [
        h("div", { class: "pre" }, [head.ref ? "participant" : "external"]),
        h("div", { class: "id" }, [breakable(head.name)]),
      ]);
      btn.style.left = head.x + "px";
      btn.style.top = head.y + "px";
      btn.style.width = head.w + "px";
      stage.appendChild(btn);
    });
    return stage;
  }

  function diagramBlock(rec, selected, onselect) {
    const list = rec.diagrams || [];
    if (!list.length) return h("p", { class: "note" }, ["No diagram declared on this id."]);
    let index = parseInt(parse().query.get("dg") || "0", 10);
    if (!(index >= 0 && index < list.length)) index = 0;
    const diagram = list[index];
    const source = diagram.mermaid || "";
    const kind = (diagram.type || "").toLowerCase();
    const flow = kind === "flowchart" || /^\s*flowchart\b/i.test(source) ? layoutFlow(source) : null;
    const sequence = !flow && (kind === "sequence" || /^\s*sequenceDiagram\b/i.test(source)) ? layoutSequence(source) : null;
    function pick(i) {
      go("id/" + encodeURIComponent(rec.id), { proj: "diagrams", dg: String(i) });
    }
    let picture = null;
    if (flow) picture = diagramFrame(flowStage(flow, selected, onselect));
    else if (sequence) picture = diagramFrame(sequenceStage(sequence, selected, onselect));
    else picture = diagramCard(diagram);
    const why = selected
      ? whyBox(selected, "Declared in “" + (diagram.title || diagram.type || "diagram") + "”.", "declared · diagrams")
      : h("p", { class: "quiet" }, ["Select a node to see why it is in this diagram."]);
    return h("div", {}, [
      h("div", { class: "quiet" }, ["declared · diagrams on this id"]),
      diagramPicker(list, index, pick),
      diagram.description ? h("p", { class: "note" }, [diagram.description]) : null,
      picture,
      flow || sequence ? why : null,
    ]);
  }

  function diagramFrame(picture) {
    return h("div", { class: "diagram-frame" }, [picture]);
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
      diagramFrame(host),
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
