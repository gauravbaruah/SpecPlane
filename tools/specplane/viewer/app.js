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
    if (p.role) node.setAttribute("role", p.role);
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

  function recordStatus(rec) {
    const bit = rec.bit || "live";
    const bitText = bit === "inferred" ? "inferred · not live" : bit === "replaced" ? "replaced" + (rec.replaced_by ? " → " + rec.replaced_by : "") : "live";
    const reviewed = !!(rec.review_state && rec.review_state !== "unreviewed");
    return h("div", { class: "statusline" }, [
      h("span", { class: "bit " + bit }, [bitText]),
      rec.review_state ? h("span", { class: reviewed ? "rev on" : "rev" }, [(reviewed ? "●" : "○") + " " + rec.review_state]) : null,
      rec.status ? h("span", { class: "st" }, ["status " + rec.status]) : null,
    ]);
  }

  function changeState(change) {
    return change && change.state === "archived" ? "archived" : "in-flight";
  }

  function changeStatus(change) {
    const state = changeState(change);
    return h("div", { class: "statusline" }, [
      h("span", { class: "bit " + (state === "archived" ? "archived" : "inflight") }, [state]),
      change.kind ? h("span", { class: "st" }, ["kind " + change.kind]) : null,
      change.opened ? h("span", { class: "st" }, ["opened " + change.opened]) : null,
    ]);
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
      ["activity", "Activity"],
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
    return h("div", { class: "shell" }, [top, honesty(route), h("main", { class: "page" }, [body])]);
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
        h("div", { class: "pin" }, [[rec.id, rec.bit || "live", rec.review_state].filter(Boolean).join(" · ")]),
      ]);
    }
    if (route.kind === "change") {
      return h("div", { class: "bar" }, [
        h("div", { class: "trail" }, [
          h("a", { href: href("changes") }, ["← Changes"]),
          h("span", { class: "crumb" }, [h("span", { class: "sep" }, ["›"]), h("span", { class: "mono inflight" }, [breakable(route.arg)])]),
        ]),
        h("div", { class: "pin" }, ["change · " + route.arg + " · " + changeState(changeById(route.arg))]),
      ]);
    }
    if (route.kind === "live" || route.kind === "changes" || route.kind === "gaps" || route.kind === "activity") trail = [];
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
      h("div", { class: "lede" }, [
        h("h1", {}, ["Live"]),
        h("p", { class: "note" }, ["Capabilities in the spec root. Components, containers, and foundations are reached from an id."]),
      ]),
      h("div", { class: "tools" }, [filters, find]),
      table,
      h("p", { class: "quiet" }, [feet[bit] || feet.live]),
    ]);
  }

  function changesIndex(route) {
    const state = route.query.get("state") === "archived" ? "archived" : "in-flight";
    const q = findText.trim().toLowerCase();
    const counts = { "in-flight": 0, archived: 0 };
    (DATA.changes || []).forEach(function (c) { counts[changeState(c)] += 1; });
    const rows = (DATA.changes || []).filter(function (c) {
      if (changeState(c) !== state) return false;
      return !q || c.id.toLowerCase().indexOf(q) >= 0 || (c.why || "").toLowerCase().indexOf(q) >= 0;
    });
    const filters = h("div", { class: "seg" }, ["in-flight", "archived"].map(function (name) {
      const label = name === "in-flight" ? "In-flight" : "Archived";
      return h("button", {
        class: state === name ? "on" : "",
        on: { click: function () { go("changes", { state: name }); } },
      }, [label + " ", h("span", { class: "count" }, [String(counts[name])])]);
    }));
    const feet = {
      "in-flight": "Open change folders. Nothing here is live until it is promoted.",
      archived: "Archived folders stay so the decision can be read. They are not open work.",
    };
    return h("section", { class: "changes-index" }, [
      h("div", { class: "lede" }, [
        h("h1", {}, ["Changes"]),
        h("p", { class: "note" }, ["Change folders. In-flight is open work. Archived is a folder under specs/changes/_archive."]),
      ]),
      h("div", { class: "tools" }, [filters, h("input", {
        id: "find", class: "find", type: "search", placeholder: "Find by slug or why", value: findText,
        on: { input: function (ev) { findText = ev.target.value; rerender(true); } },
      })]),
      h("table", { class: "index changes" }, [
        h("tbody", {}, rows.map(function (c) {
          const sensor = c.check_sync && c.check_sync.sensors === "declared"
            ? (c.check_sync.sensor_rows || []).length + " sensors declared · not run"
            : "No success sensor declared";
          return h("tr", { on: { click: function () { go("change/" + c.id); } } }, [
            h("td", {}, [h("a", { class: "mono" + (changeState(c) === "archived" ? "" : " inflight"), href: href("change/" + c.id) }, [breakable(c.id)])]),
            h("td", { class: "quiet mono kind" }, [c.kind || ""]),
            h("td", { class: "promises" }, (c.promise_ids || []).map(function (id) { return idLink(id); })),
            h("td", { class: "quiet" }, [sensor]),
            h("td", { class: "opened" }, [c.opened ? "Opened " + c.opened : ""]),
          ]);
        })),
      ]),
      h("p", { class: "quiet" }, [feet[state]]),
    ]);
  }

  function changeById(id) {
    return (DATA.changes || []).find(function (c) { return c.id === id; }) || null;
  }

  function copySummary(text) {
    function mark() {
      const note = document.getElementById("copied");
      if (note) note.textContent = "Copied.";
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(mark);
    }
  }

  var LATER = "This command exited nonzero, and a later run of the same command exited 0. That is the order of the exits.";
  var COMMANDS = {
    validate: {
      about: "Checks that spec names, links, and the changelog are structurally honest. That keeps later commands from trusting broken YAML.",
      ok: "Exit 0. No structural errors were found.",
      bad: "Exit was not 0. At least one structural error was found, such as a broken link, a bad name, or a missing changelog entry."
    },
    retrieve: {
      about: "Returns the live promise for one id, and keeps any open change apart from that promise. That is how you see what is live before you change it.",
      ok: "Exit 0. The id was found and the live graph was printed.",
      bad: "Exit was not 0. The id was unknown, so nothing was invented."
    },
    context: {
      about: "Prints the specification, the open change, the declared implementation, and the evidence for one id or one declared file. That keeps those four sources apart when someone asks how something works.",
      ok: "Exit 0. The four sources were printed, or the file was reported as unmapped.",
      bad: "Exit was not 0. The id was unknown."
    },
    blast: {
      about: "Computes which specs a change can affect, from the declared links. That shows the likely impact before you edit.",
      ok: "Exit 0. The affected set was printed.",
      bad: "Exit was not 0. The starting id was unknown, or the affected set could not be built."
    },
    impact: {
      about: "Explains the same affected set as system, product, quality, governance, and ownership. That gives five readings of one blast.",
      ok: "Exit 0. Those readings were printed.",
      bad: "Exit was not 0. The starting id was unknown, or the readings could not be built."
    },
    check_sync: {
      about: "Checks that changed specs are named by an open change. That keeps a merge from treating uncovered work as if the spec already covered it. It does not run the bound checks.",
      ok: "Exit 0. Every changed id was covered, or the only notes were Phase 1 warnings.",
      bad: "Exit was not 0. A changed id had no open change covering it, or an empty impact list failed the check."
    },
    reconcile: {
      about: "Compares files a component declares with the files that changed. That shows a missing declared path, or a changed file no component declares. The result is advisory.",
      ok: "Exit 0. The comparison was printed.",
      bad: "Exit was not 0. The comparison could not be printed."
    },
    list_gaps: {
      about: "Lists advisory gaps, such as a missing sensor or a Phase 1 spec with no relationships. That is a queue to look at. It does not fail the command.",
      ok: "Exit 0. The queue was printed.",
      bad: "Exit was not 0. The queue could not be printed."
    },
    run: {
      about: "Runs checks already bound on one change and records the exits. That tells you whether those checks passed. A pass does not mean the whole spec is satisfied.",
      ok: "Exit 0. Every bound check that ran exited 0, or nothing was bound to run.",
      bad: "Exit was not 0. A bound check failed, or the change could not be run."
    },
    promote: {
      about: "Drops the inferred mark on named ids and appends a changelog row. That is how those ids become live. It does not accept an open change folder, and it does not promote a whole inventory.",
      ok: "Exit 0. The named ids were promoted.",
      bad: "Exit was not 0. A named id could not be promoted."
    },
    init: {
      about: "Copies the kit into a product repo and creates empty specs folders. That is how a project starts SpecPlane without copying this product's specs.",
      ok: "Exit 0. The kit was copied.",
      bad: "Exit was not 0. The copy did not finish."
    },
    view: {
      about: "Generates the local readout and serves it on 127.0.0.1. That is the page a person reads. The count is recorded when that process exits.",
      ok: "Exit 0. The server process ended with exit code 0.",
      bad: "Exit was not 0. The server process ended some other way, including being stopped."
    },
    mcp: {
      about: "Starts the stdio server for retrieve, blast, impact, check_sync, list_gaps, and run. That is how an agent host calls those commands. The count is recorded when that process exits.",
      ok: "Exit 0. The server process ended with exit code 0.",
      bad: "Exit was not 0. The server process ended some other way."
    },
    telemetry_status: {
      about: "Says whether the local command log is on. Nothing is uploaded.",
      ok: "Exit 0. The on or off state was printed.",
      bad: "Exit was not 0. The state could not be printed."
    },
    telemetry_show: {
      about: "Prints the local event file. Nothing is uploaded.",
      ok: "Exit 0. The local file was printed.",
      bad: "Exit was not 0. The local file could not be printed."
    },
    telemetry_enable: {
      about: "Turns the local command log on. Nothing is uploaded.",
      ok: "Exit 0. Recording was turned on.",
      bad: "Exit was not 0. Recording could not be turned on."
    },
    telemetry_disable: {
      about: "Turns the local command log off. Nothing is uploaded.",
      ok: "Exit 0. Recording was turned off.",
      bad: "Exit was not 0. Recording could not be turned off."
    },
    usage: {
      about: "Recorded when the CLI is started without a recognized command. That is the help path.",
      ok: "Exit 0. Help was printed.",
      bad: "Exit was not 0. The CLI was started with arguments it did not recognize."
    }
  };

  function helpButton(label, tip) {
    return h("button", { type: "button", class: "help", label: label }, [
      "?",
      h("span", { class: "tip", role: "tooltip" }, [tip]),
    ]);
  }

  function activityTable(lines) {
    var byName = {};
    var order = [];
    var caller = "";
    lines.forEach(function (line) {
      var later = line.match(/^(\S+) nonzero, then later ok · (\d+)$/);
      if (later) {
        if (!byName[later[1]]) {
          byName[later[1]] = { name: later[1], ok: "0", bad: "0", later: "0" };
          order.push(later[1]);
        }
        byName[later[1]].later = later[2];
        return;
      }
      if (line.indexOf("caller · ") === 0) {
        caller = line.slice("caller · ".length);
        return;
      }
      var row = line.match(/^(\S+) (\d+) · (\d+) ok(?: · (\d+) nonzero)?$/);
      if (!row) return;
      byName[row[1]] = {
        name: row[1],
        ok: row[3],
        bad: row[4] || "0",
        later: (byName[row[1]] && byName[row[1]].later) || "0",
      };
      if (order.indexOf(row[1]) < 0) order.push(row[1]);
    });
    var body = order.map(function (name) {
      var row = byName[name];
      var info = COMMANDS[name] || {
        about: "A local command count.",
        ok: "Exit 0.",
        bad: "Exit was not 0.",
      };
      return h("tr", {}, [
        h("td", { class: "mono" }, [name]),
        h("td", { class: "about" }, [info.about]),
        h("td", { class: "count" }, [
          row.ok,
          helpButton("What ok means", info.ok),
        ]),
        row.bad === "0"
          ? h("td", { class: "count quiet" }, ["—"])
          : h("td", { class: "count" }, [
            row.bad,
            helpButton("What a nonzero exit means", info.bad),
          ]),
        row.later === "0"
          ? h("td", { class: "count quiet" }, ["—"])
          : h("td", { class: "count" }, [
            row.later,
            helpButton("What this sequence means", LATER),
          ]),
      ]);
    });
    var table = h("table", { class: "index activity" }, [
      h("thead", {}, [
        h("tr", {}, [
          h("th", {}, ["Command"]),
          h("th", {}, ["What it does"]),
          h("th", {}, ["OK"]),
          h("th", {}, ["Nonzero"]),
          h("th", {}, ["Later ok"]),
        ]),
      ]),
      h("tbody", {}, body),
    ]);
    if (!caller) return table;
    return h("div", { class: "activity-block" }, [
      table,
      h("p", { class: "callers" }, [
        "Started as  ",
        caller,
        helpButton(
          "What these names mean",
          "cursor_skill means a skill set SPECPLANE_CALLER when it ran the CLI. unattributed means that variable was not set. That is normal. It is not a failed check."
        ),
      ]),
    ]);
  }

  function activityIndex() {
    const activity = DATA.activity || {};
    const lines = activity.lines || [];
    const text = activity.text || lines.join("\n");
    const notice = lines.length === 1 ? lines[0] : "";
    const showTable = notice !== "No local events in the last 30 days." && notice !== "Local command events are off.";
    return h("section", { class: "activity-index" }, [
      h("div", { class: "lede" }, [
        h("h1", {}, ["Activity"]),
        h("p", { class: "note" }, ["This machine, last 30 days. Nothing here is uploaded."]),
      ]),
      h("div", { class: "tools" }, [
        h("button", {
          type: "button",
          class: "copy-btn",
          on: { click: function () { copySummary(text); } },
        }, ["Copy summary"]),
        h("span", { id: "copied", class: "quiet" }, [""]),
      ]),
      showTable ? activityTable(lines) : h("p", { class: "note" }, [notice]),
    ]);
  }

  function gapsIndex() {
    const gaps = DATA.gaps || {};
    return h("section", { class: "gaps-index" }, [
      h("div", { class: "lede" }, [
        h("h1", {}, ["Gaps"]),
        h("p", { class: "note" }, ["Where SpecPlane knows its model is incomplete. Advisory: nothing here is an error, and nothing here has been filled in for you."]),
      ]),
      ...GAPS.map(function (bucket) {
        const ids = gaps[bucket[0]] || [];
        return h("div", { class: "bucket" }, [
          h("div", { class: "bucket-head" }, [
            h("h2", {}, [bucket[1]]),
            h("span", { class: "bucket-key" }, [bucket[0] + " · " + ids.length]),
          ]),
          h("p", { class: "meaning" }, [bucket[2]]),
          ids.length ? h("table", { class: "index gaps" }, [
            h("tbody", {}, ids.map(function (id) {
              const change = changeById(id);
              const rec = change ? null : record(id);
              const purpose = change ? (change.why || "") : (rec && rec.purpose) || "";
              const bit = change
                ? "in-flight" + (change.kind ? " · " + change.kind : "")
                : rec && rec.bit === "inferred" ? "inferred · not live" : (rec && rec.bit) || "";
              return h("tr", {
                on: { click: function () { go(change ? "change/" + id : "id/" + encodeURIComponent(id)); } },
              }, [
                h("td", {}, [h("span", { class: "idcell" }, [bitMark(change ? "inflight" : rec && rec.bit), idLink(id)])]),
                h("td", {}, [purpose]),
                h("td", { class: "gap-bit" + (change ? " inflight" : rec && rec.bit === "inferred" ? " bit inferred" : rec && rec.bit === "replaced" ? " replaced" : "") }, [bit]),
              ]);
            })),
          ]) : h("div", { class: "gap-empty" }, ["(none)"]),
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
        h("div", { class: "identity" }, [
          h("div", { class: "eyebrow" }, [rec.level || "record"]),
          h("div", { class: "row" }, [bitMark(rec.bit), h("span", { class: rec.bit === "replaced" ? "id-title replaced" : "id-title" }, [breakable(rec.id)])]),
          recordStatus(rec),
          rec.path ? h("div", { class: "quiet mono" }, [breakable(rec.path)]) : null,
        ]),
        h("div", { class: "promise" }, [
          h("div", { class: "kicker" }, ["Promise"]),
          h("p", { class: "purpose" }, [rec.purpose || (rec.bit === "inferred" ? "retrieve returns no live slice for an inferred id." : "")]),
        ]),
        flight(rec),
        definition(rec, graph),
        promiseTrace(rec),
        realization(rec, graph),
        questions(rec, graph),
        sourceHistory(rec),
      ]),
      h("div", { class: "stage" }, [
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
    return h("div", { class: "strips" }, rec.in_flight.map(function (c) {
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

  function section(key, title, sub, summary, body, startOpen) {
    if (openSections[key] == null) openSections[key] = !!startOpen;
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

  function block(label, src, rows) {
    const body = (rows || []).filter(Boolean);
    if (!body.length) return null;
    return h("div", { class: "blk" }, [
      h("div", { class: "blk-head" }, [
        h("span", { class: "blk-label" }, [label]),
        src ? h("span", { class: "blk-src" }, [src]) : null,
      ]),
      ...body,
    ]);
  }

  function textRow(text) {
    if (!text) return null;
    return h("div", { class: "item" }, [String(text)]);
  }

  function kvLines(pairs) {
    return (pairs || []).filter(function (pair) { return pair && pair[1]; }).map(function (pair) {
      return h("div", { class: "kv-line" }, [
        h("span", { class: "kv-k" }, [pair[0]]),
        h("span", { class: "kv-v" }, [pair[1] instanceof Node ? pair[1] : String(pair[1])]),
      ]);
    });
  }

  function kvRow(pairs) {
    const lines = kvLines(pairs);
    if (!lines.length) return null;
    return h("div", { class: "item" }, lines);
  }

  function idListRow(label, ids) {
    if (!ids.length) return null;
    return h("div", { class: "item" }, [
      h("div", { class: "kv-k" }, [label]),
      h("div", { class: "ids" }, ids.map(idLink)),
    ]);
  }

  function sourceKey(item) {
    const source = item.source || "";
    const cut = source.lastIndexOf(".");
    return cut >= 0 ? source.slice(cut + 1) : source;
  }

  function fieldValue(item) {
    const detail = String(item.detail || "");
    const prefix = sourceKey(item) + ": ";
    return detail.indexOf(prefix) === 0 ? detail.slice(prefix.length) : detail;
  }

  function splitOnce(text) {
    const raw = String(text || "");
    const cut = raw.indexOf(": ");
    if (cut < 0) return ["", raw];
    return [raw.slice(0, cut), raw.slice(cut + 2)];
  }

  function ofKind(items, kinds) {
    return items.filter(function (item) { return kinds.indexOf(item.kind) >= 0; });
  }

  function flowRow(item) {
    const pairs = [];
    if (item.kinds && item.kinds.length) pairs.push(["kinds", item.kinds.join(", ")]);
    if (item.stages && item.stages.length) pairs.push(["stages", item.stages.join(" → ")]);
    const outcomes = item.outcomes || {};
    Object.keys(outcomes).forEach(function (key) {
      const texts = outcomes[key];
      if (texts && texts.length) pairs.push([key, texts.join("; ")]);
    });
    return h("div", { class: "item" }, [
      item.flow_id ? h("div", { class: "row-id" }, [item.flow_id]) : null,
      item.goal ? h("div", {}, [item.goal]) : (!item.flow_id ? String(item.detail || "") : null),
      ...kvLines(pairs),
    ]);
  }

  function definitionSummary(duties, flows, constraints, success, road) {
    const parts = [];
    if (duties.length) parts.push(plural(duties.length, "responsibility", "responsibilities"));
    if (flows.length) parts.push(plural(flows.length, "flow"));
    if (constraints.length) {
      const klass = constraints.filter(function (item) { return sourceKey(item) === "data_classification"; })[0];
      parts.push(klass ? "constraints (" + fieldValue(klass) + ")" : "constraints");
    }
    const primary = success.filter(function (item) { return item.kind === "success_metric"; })[0];
    if (primary && primary.detail) parts.push("target: " + primary.detail);
    const roadItem = road.filter(function (item) { return item.kind === "roadmap"; })[0];
    if (roadItem) {
      const detail = String(roadItem.detail || "");
      const phase = ((detail.match(/phase=(.*?)(?: priority=|$)/) || [])[1] || "").trim();
      const priority = ((detail.match(/priority=(.*)$/) || [])[1] || "").trim();
      const bit = [phase, priority].filter(Boolean).join(" ");
      if (bit) parts.push(bit);
    }
    return parts.join(" · ");
  }

  function definition(rec, graph) {
    const items = productItems(graph, rec.id);
    const duties = (rec.responsibilities && rec.responsibilities.length)
      ? rec.responsibilities.slice()
      : ofKind(items, ["responsibility"]).map(function (item) { return item.detail; });
    const flows = ofKind(items, ["flow"]);
    const business = ofKind(items, ["business_value"]);
    const constraints = ofKind(items, ["constraint"]);
    const success = ofKind(items, ["success_metric", "success_target", "success_metric_source"]);
    const events = ofKind(items, ["analytics_event"]);
    const road = ofKind(items, ["roadmap", "roadmap_dependency", "roadmap_enables"]);
    const refs = ofKind(items, ["flow_ref"]);
    const blocks = [
      duties.length ? block("Responsibilities", "responsibilities", duties.map(textRow)) : null,
      flows.length ? block("Flows", "flows", flows.map(flowRow)) : null,
      business.length ? block("Business value", "business_value", [kvRow(business.map(function (item) {
        const key = sourceKey(item);
        const labels = { user_outcome: "user_outcome", objective: "objective", revenue_dependency: "revenue", strategic_priority: "priority" };
        return [labels[key] || key, fieldValue(item)];
      }))]) : null,
      constraints.length ? block("Constraints", "constraints", [kvRow(constraints.map(function (item) {
        const key = sourceKey(item);
        return [key === "data_classification" ? "classification" : key, fieldValue(item)];
      }))]) : null,
      success.length ? block("Success", "success_metrics", [kvRow(success.map(function (item) {
        if (item.kind === "success_metric") return ["primary", item.detail || ""];
        const parts = splitOnce(item.detail);
        const name = parts[0] || (item.kind === "success_metric_source" ? "derived_from" : "target");
        return [item.kind === "success_metric_source" ? name + " from" : name, parts[1] || item.detail || ""];
      }))]) : null,
      events.length ? block("Analytics events", "analytics_events", events.map(function (item) { return textRow(item.detail); })) : null,
      road.length ? block("Roadmap", "roadmap", roadmapRows(road)) : null,
      refs.length ? block("Flow slice", "planning.user_flows", refs.map(function (item) {
        return kvRow([["flow_ref", item.detail || ""]]);
      })) : null,
    ].filter(Boolean);
    if (!blocks.length) return null;
    return section("def:" + rec.id, "Definition", "what is promised", definitionSummary(duties, flows, constraints, success, road), blocks);
  }

  function roadmapRows(items) {
    const rows = [];
    ofKind(items, ["roadmap"]).forEach(function (item) {
      const detail = String(item.detail || "");
      const phase = ((detail.match(/phase=(.*?)(?: priority=|$)/) || [])[1] || "").trim();
      const priority = ((detail.match(/priority=(.*)$/) || [])[1] || "").trim();
      rows.push(kvRow([["phase", phase], ["priority", priority]]));
    });
    [["depends_on", "roadmap_dependency"], ["enables", "roadmap_enables"]].forEach(function (pair) {
      const ids = ofKind(items, [pair[1]]).map(function (item) { return item.related_id || item.detail; }).filter(Boolean);
      if (ids.length) rows.push(idListRow(pair[0], ids));
    });
    return rows;
  }

  function checkGroup(item) {
    if (item.kind === "acceptance_criterion") return ["Acceptance criteria", "validation.acceptance_criteria"];
    if (item.kind === "edge_case" || item.kind === "readiness") return ["Edge cases & readiness", "validation"];
    if (item.kind === "test_strategy") return ["Test strategy", "validation.test_strategy"];
    if (item.kind === "apis" || item.kind === "events" || item.kind === "states") return ["Contracts", "contracts"];
    if (item.strategy || item.rollback_trigger || item.source === "rollout") return ["Rollout", "rollout"];
    return ["Observability", "observability"];
  }

  function checkRow(item) {
    if (item.strategy || item.rollback_trigger) return kvRow([["strategy", item.strategy || ""], ["rollback", item.rollback_trigger || ""]]);
    if (item.kind === "test_strategy" && item.name) return kvRow([[item.name, item.detail || ""]]);
    if (item.kind === "apis" || item.kind === "events" || item.kind === "states") return kvRow([[item.kind, item.detail || ""]]);
    return textRow(item.detail || item.kind || "");
  }

  function realization(rec, graph) {
    const realized = (rec.links || []).filter(function (link) { return link.rel === "realized_by"; }).map(function (link) { return link.id; });
    const quality = graph ? (graph.perspectives || {}).quality || {} : {};
    const own = rec.level !== "capability";
    const rows = [];
    ["criteria", "verification", "contracts", "sensors", "rollout"].forEach(function (key) {
      (quality[key] || []).forEach(function (item) {
        if (item.kind === "data_models") return;
        const subject = item.subject || "";
        if (own ? subject === rec.id : realized.indexOf(subject) >= 0) rows.push(item);
      });
    });
    if (!realized.length && !rows.length) {
      if (rec.level === "capability" && rec.bit !== "inferred") {
        return h("p", { class: "note" }, ["Nothing realizes this yet. realized_by is added by engineering when work is planned; that is normal for a planned capability."]);
      }
      return null;
    }
    const containers = realized.filter(function (id) { return levelOf(id) === "container"; });
    const components = realized.filter(function (id) { return levelOf(id) !== "container"; });
    const blocks = [
      block("Realized by", "realized_by", [
        idListRow("containers", containers),
        idListRow("components", components),
      ]),
    ];
    const order = ["Contracts", "Acceptance criteria", "Edge cases & readiness", "Test strategy", "Observability", "Rollout"];
    const buckets = {};
    rows.forEach(function (item) {
      const grouped = checkGroup(item);
      const subject = item.subject || rec.id;
      buckets[subject] = buckets[subject] || {};
      const slot = buckets[subject][grouped[0]] || { src: grouped[1], rows: [] };
      slot.rows.push(checkRow(item));
      buckets[subject][grouped[0]] = slot;
    });
    const subjects = realized.filter(function (id) { return buckets[id]; });
    Object.keys(buckets).forEach(function (id) {
      if (subjects.indexOf(id) < 0) subjects.push(id);
    });
    subjects.forEach(function (subject) {
      order.forEach(function (label) {
        const slot = buckets[subject][label];
        if (!slot) return;
        blocks.push(block(label, subject + " · " + slot.src, slot.rows));
      });
    });
    const present = blocks.filter(Boolean);
    const acceptance = rows.filter(function (item) { return item.kind === "acceptance_criterion"; }).length;
    const slos = rows.filter(function (item) { return item.kind === "slos"; }).length;
    const strategy = (rows.filter(function (item) { return item.strategy; })[0] || {}).strategy;
    const summary = [
      containers.length ? plural(containers.length, "container") : "",
      components.length ? plural(components.length, "component") : "",
      acceptance ? plural(acceptance, "acceptance criterion", "acceptance criteria") : "",
      slos ? plural(slos, "SLO") : "",
      strategy ? strategy + " rollout" : "",
    ].filter(Boolean).join(" · ");
    return section("real:" + rec.id, "Realization", "how it is built and checked", summary, present);
  }

  function questions(rec, graph) {
    const items = productItems(graph, rec.id).filter(function (item) { return item.kind === "open_question"; });
    if (!items.length) return null;
    return section("ask:" + rec.id, "Open questions", "declared unknowns", plural(items.length, "question"), items.map(itemRow));
  }

  function traceStep(label, src, gap, items) {
    return h("div", { class: "trace-step" }, [
      h("div", { class: "trace-label" }, [label]),
      h("div", { class: gap ? "trace-box gap" : "trace-box" }, [
        h("div", { class: "trace-src" }, [src]),
        h("div", { class: "trace-items" }, items),
      ]),
    ]);
  }

  function checkText(measured) {
    const checks = measured.checks || {};
    if (checks.missing) return measured.emitted_by + " is not in this spec root.";
    if (!checks.declared) return measured.emitted_by + ": no validation declared";
    const parts = [];
    if (checks.acceptance) parts.push(plural(checks.acceptance, "acceptance criterion", "acceptance criteria"));
    if (checks.strategies && checks.strategies.length) parts.push(checks.strategies.join(", ") + " tests declared");
    return measured.emitted_by + ": " + parts.join("; ");
  }

  function promiseTrace(rec) {
    const trace = rec.trace || {};
    const targets = trace.targets || [];
    const sensors = trace.sensors || [];
    if (!targets.length && !sensors.length) return null;
    let missing = 0;
    const traced = targets.some(function (target) { return (target.measured_by || []).length; });
    const rows = targets.map(function (target) {
      const measured = target.measured_by || [];
      const steps = [traceStep("Target", "success_metrics.targets", false, [
        h("span", { class: "row-id" }, [target.name]),
        h("span", {}, [" " + target.value]),
      ])];
      if (!measured.length) return h("div", { class: "trace" }, steps);
      const orphans = measured.filter(function (item) { return !item.emitted_by; });
      missing += orphans.length;
      steps.push(traceStep("Measured by", "success_metrics.derived_from", false, measured.map(function (item) {
        return h("span", { class: "row-id" }, [item.name]);
      })));
      steps.push(traceStep("Emitted by", "analytics_events.emitted_by", orphans.length > 0, measured.map(function (item) {
        return item.emitted_by
          ? idLink(item.emitted_by)
          : h("span", { class: "note" }, [item.name + " has no emitted_by. Nothing in the model produces it."]);
      })));
      const linked = measured.filter(function (item) { return item.emitted_by; });
      steps.push(traceStep("Checked by", "component validation", !linked.length, linked.length
        ? linked.map(function (item) { return h("span", {}, [checkText(item)]); })
        : [h("span", { class: "note" }, ["Not connected in the model."])]));
      return h("div", { class: "trace" }, steps);
    });
    if (targets.length && !traced) {
      rows.push(h("p", { class: "note" }, ["derived_from is not represented, so these targets are not traced to an event."]));
    }
    sensors.forEach(function (sensor) {
      rows.push(h("div", { class: "trace-sensor" }, [
        h("div", { class: "trace-src" }, ["open change sensor on this promise · " + sensor.change + " · success.yaml"]),
        h("div", {}, [sensor.must]),
        h("div", { class: "trace-src" }, ["declared · not executed"]),
      ]));
    });
    const summary = [
      targets.length ? plural(targets.length, "target") + (traced ? " traced through events to components" : "") : "",
      missing ? plural(missing, "event") + " with no emitter" : "",
      sensors.length ? plural(sensors.length, "open-change sensor") + ", not run" : "",
    ].filter(Boolean).join(" · ");
    return section("trace:" + rec.id, "Promise → realization", "how success is judged and checked", summary, rows);
  }

  function sourceHistory(rec) {
    const history = rec.history || {};
    const changelog = history.changelog || [];
    const refs = history.refs || [];
    const paths = history.realization_paths || [];
    const meta = [
      ["version", history.version],
      ["introduced_in", history.introduced_in],
      ["last_updated", history.last_updated],
      ["owner", history.owner],
    ];
    if (!rec.path && !meta.some(function (pair) { return pair[1]; }) && !changelog.length && !refs.length && !paths.length) return null;
    const fileRows = [];
    if (rec.path) fileRows.push(h("div", { class: "item" }, [breakable(rec.path)]));
    if (meta.some(function (pair) { return pair[1]; })) fileRows.push(kvRow(meta));
    if (paths.length) fileRows.push(kvRow([["realization.paths", paths.join(", ")]]));
    const blocks = [
      fileRows.length ? block("File", "the repository is the source", fileRows) : null,
      changelog.length ? block("Changelog", "changelog", changelog.map(function (entry) {
        const text = (entry.summary || "") + (entry.breaking ? " · breaking" : "");
        return kvRow([[entry.date || "undated", text]]);
      })) : null,
      refs.length ? block("Refs", "refs", refs.map(function (ref) {
        const label = [ref.title, ref.type ? "(" + ref.type + ")" : ""].filter(Boolean).join(" ");
        return kvRow([[ref.id || ref.path || ref.url || "ref", label || ref.path || ref.url || ""]]);
      })) : null,
    ].filter(Boolean);
    const summary = [rec.path, history.version ? "v" + history.version : ""].filter(Boolean).join(" · ");
    return section("src:" + rec.id, "Source & history", "why SpecPlane says this", summary, blocks);
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
    if (proj === "map") return graphBlock(mapColumns(rec, graph), selected, onselect, mapWhy(rec, selected, graph), "derived · from declared links", "", "Where this sits: the declared links one hop out from the selected id.");
    if (proj === "layers") return graphBlock(layerColumns(rec), selected, onselect, layerWhy(rec, selected), "derived · 5C placement", "", "The same declared links placed on the 5C axis around the selected id.");
    if (proj === "journey") return journeyBlock(rec, graph, selected, onselect);
    if (proj === "diagrams") return diagramBlock(rec, selected, onselect);
    if (proj === "data") return dataBlock(rec, graph);
    if (proj === "blast") return blastBlock(graph, rec.id, selected, persp, onselect);
    return null;
  }

  function linksOf(id, rel) {
    const rec = record(id);
    return ((rec && rec.links) || []).filter(function (link) { return link.rel === rel; });
  }

  function listedBy(id, field) {
    const out = [];
    Object.keys(DATA.records).forEach(function (other) {
      const list = DATA.records[other][field] || [];
      if (list.indexOf(id) >= 0) out.push(other);
    });
    return out;
  }

  function pushNode(nodes, id, via) {
    if (!id || nodes.some(function (node) { return node.id === id && node.sub === via; })) return;
    nodes.push(nodeModel(id, { via: via }));
  }

  function nodeKey(id, via) {
    return String(id) + "\t" + String(via || "");
  }

  function edgeKind(a, b) {
    const left = record(a);
    const right = record(b);
    if ((left && left.bit === "inferred") || (right && right.bit === "inferred")) return "inferred";
    return "declared";
  }

  function mapColumns(rec, graph) {
    const level = rec.level || "";
    const context = [];
    const middle = [];
    const uses = [];
    const edges = [];
    const selected = [nodeModel(rec.id, { selected: true })];
    function tie(fromId, fromVia, toId, toVia) {
      const from = nodeKey(fromId, fromVia);
      const to = nodeKey(toId, toVia);
      if (edges.some(function (edge) { return edge.from === from && edge.to === to; })) return;
      edges.push({ from: from, to: to, kind: edgeKind(fromId, toId) });
    }
    function laid(pairs) {
      const cols = mapCols(pairs);
      cols.edges = edges;
      return cols;
    }
    if (level === "capability") {
      listedBy(rec.id, "system_context").forEach(function (id) {
        pushNode(context, id, "system_context");
        tie(id, "system_context", rec.id, "");
      });
      productItems(graph, rec.id).forEach(function (item) {
        const id = item.related_id || item.detail;
        if (item.kind === "roadmap_dependency") {
          pushNode(context, id, "roadmap.depends_on");
          tie(id, "roadmap.depends_on", rec.id, "");
        }
        if (item.kind === "roadmap_enables") {
          pushNode(context, id, "roadmap.enables");
          tie(rec.id, "", id, "roadmap.enables");
        }
      });
      (rec.links || []).forEach(function (link) {
        if (link.rel === "realized_by") {
          pushNode(middle, link.id, "realized_by");
          tie(rec.id, "", link.id, "realized_by");
        }
      });
      middle.forEach(function (node) {
        linksOf(node.id, "uses").forEach(function (link) {
          const via = "uses · " + shortId(node.id);
          pushNode(uses, link.id, via);
          tie(node.id, "realized_by", link.id, via);
        });
      });
      return laid([
        ["Context", context],
        ["Selected", selected],
        ["Realized by", middle],
        ["Uses", uses],
      ]);
    }
    if (level === "component") {
      linksOf(rec.id, "implements").forEach(function (link) {
        pushNode(context, link.id, "implements");
        tie(rec.id, "", link.id, "implements");
      });
      listedBy(rec.id, "contains").forEach(function (id) {
        pushNode(context, id, "contains");
        tie(id, "contains", rec.id, "");
      });
      linksOf(rec.id, "depended_on_by").forEach(function (link) {
        pushNode(context, link.id, "depended_on_by");
        tie(link.id, "depended_on_by", rec.id, "");
      });
      linksOf(rec.id, "depends_on").forEach(function (link) {
        pushNode(middle, link.id, "depends_on");
        tie(rec.id, "", link.id, "depends_on");
      });
      linksOf(rec.id, "uses").forEach(function (link) {
        pushNode(uses, link.id, "uses");
        tie(rec.id, "", link.id, "uses");
      });
      return laid([
        ["Serves & contained in", context],
        ["Selected", selected],
        ["Depends on", middle],
        ["Uses", uses],
      ]);
    }
    if (level === "container") {
      listedBy(rec.id, "contains").forEach(function (id) {
        pushNode(context, id, "contains");
        tie(id, "contains", rec.id, "");
      });
      linksOf(rec.id, "implements").forEach(function (link) {
        pushNode(context, link.id, "implements");
        tie(rec.id, "", link.id, "implements");
      });
      (rec.contains || []).forEach(function (id) {
        pushNode(middle, id, "contains");
        tie(rec.id, "", id, "contains");
      });
      linksOf(rec.id, "uses").forEach(function (link) {
        pushNode(uses, link.id, "uses");
        tie(rec.id, "", link.id, "uses");
      });
      return laid([
        ["Context", context],
        ["Selected", selected],
        ["Contains", middle],
        ["Uses", uses],
      ]);
    }
    if (level === "foundation") {
      Object.keys(DATA.records).forEach(function (other) {
        if (linksOf(other, "uses").some(function (link) { return link.id === rec.id; })) {
          pushNode(context, other, "used_by");
          tie(other, "used_by", rec.id, "");
        }
      });
      return laid([
        ["Used by", context],
        ["Selected", selected],
      ]);
    }
    return laid([["Selected", selected]]);
  }

  function mapCols(pairs) {
    return pairs.filter(function (pair) { return pair[0] === "Selected" || pair[1].length; }).map(function (pair) {
      return { head: pair[0], nodes: pair[1] };
    });
  }

  function layerColumns(rec) {
    const buckets = { capability: [], system: [], container: [], component: [], foundation: [] };
    const edges = [];
    function place(level, id, via, selected) {
      const bucket = buckets[level];
      if (!bucket || !id) return null;
      const found = bucket.filter(function (node) { return node.id === id; })[0];
      if (found) {
        if (selected) found.selectedId = true;
        return found;
      }
      const node = nodeModel(id, { via: via, selected: !!selected });
      bucket.push(node);
      return node;
    }
    function tie(from, to) {
      if (!from || !to || from.key === to.key) return;
      if (edges.some(function (edge) { return edge.from === from.key && edge.to === to.key; })) return;
      edges.push({ from: from.key, to: to.key, kind: edgeKind(from.id, to.id) });
    }
    function foundationsOf(comp) {
      linksOf(comp.id, "uses").forEach(function (link) {
        if (levelOf(link.id) !== "foundation") return;
        tie(comp, place("foundation", link.id, "uses · " + shortId(comp.id)));
      });
    }
    function systemsFor(cap) {
      listedBy(cap.id, "system_context").forEach(function (id) {
        if (levelOf(id) !== "system") return;
        tie(place("system", id, "system_context"), cap);
      });
    }
    const level = rec.level || levelOf(rec.id);
    if (level === "capability") {
      const self = place("capability", rec.id, "", true);
      systemsFor(self);
      (rec.links || []).forEach(function (link) {
        if (link.rel !== "realized_by") return;
        const lv = levelOf(link.id);
        if (lv === "container" || lv === "component") place(lv, link.id, "realized_by");
      });
      buckets.system.forEach(function (sys) {
        const holds = ((record(sys.id) || {}).contains) || [];
        buckets.container.forEach(function (box) {
          if (holds.indexOf(box.id) >= 0) tie(sys, box);
        });
      });
      buckets.container.forEach(function (box) {
        const holds = ((record(box.id) || {}).contains) || [];
        buckets.component.forEach(function (comp) {
          if (holds.indexOf(comp.id) >= 0) tie(box, comp);
        });
      });
      buckets.component.forEach(foundationsOf);
    } else if (level === "system") {
      const self = place("system", rec.id, "", true);
      (rec.system_context || []).forEach(function (id) { tie(self, place("capability", id, "system_context")); });
      (rec.contains || []).forEach(function (id) {
        const lv = levelOf(id);
        if (lv === "container") {
          const box = place("container", id, "contains");
          tie(self, box);
          ((record(id) || {}).contains || []).forEach(function (child) {
            if (levelOf(child) !== "component") return;
            const comp = place("component", child, "contains");
            tie(box, comp);
            foundationsOf(comp);
          });
        } else if (lv === "component") {
          const comp = place("component", id, "contains");
          tie(self, comp);
          foundationsOf(comp);
        }
      });
    } else if (level === "container") {
      const self = place("container", rec.id, "", true);
      listedBy(rec.id, "contains").forEach(function (id) {
        if (levelOf(id) !== "system") return;
        tie(place("system", id, "contains"), self);
      });
      linksOf(rec.id, "implements").forEach(function (link) { systemsFor(place("capability", link.id, "implements")); });
      (rec.contains || []).forEach(function (id) {
        if (levelOf(id) !== "component") return;
        const comp = place("component", id, "contains");
        tie(self, comp);
        foundationsOf(comp);
      });
    } else if (level === "component") {
      const self = place("component", rec.id, "", true);
      linksOf(rec.id, "implements").forEach(function (link) { systemsFor(place("capability", link.id, "implements")); });
      listedBy(rec.id, "contains").forEach(function (id) {
        if (levelOf(id) !== "container") return;
        const box = place("container", id, "contains");
        tie(box, self);
        listedBy(id, "contains").forEach(function (sys) {
          if (levelOf(sys) === "system") tie(place("system", sys, "contains"), box);
        });
      });
      foundationsOf(self);
    } else if (level === "foundation") {
      const self = place("foundation", rec.id, "", true);
      Object.keys(DATA.records).forEach(function (other) {
        if (levelOf(other) !== "component") return;
        if (!linksOf(other, "uses").some(function (link) { return link.id === rec.id; })) return;
        const comp = place("component", other, "uses");
        tie(comp, self);
        listedBy(other, "contains").forEach(function (id) {
          if (levelOf(id) === "container") tie(place("container", id, "contains"), comp);
        });
      });
    } else {
      place(buckets[level] ? level : "capability", rec.id, "", true);
    }
    const cols = ["capability", "system", "container", "component", "foundation"].filter(function (name) {
      return buckets[name].length;
    }).map(function (name) {
      return { head: name.charAt(0).toUpperCase() + name.slice(1), nodes: buckets[name] };
    });
    cols.edges = edges;
    return cols;
  }

  function nodeModel(id, extra) {
    const rec = record(id);
    const via = (extra && extra.via) || "";
    return {
      id: id,
      key: nodeKey(id, via),
      bit: rec ? rec.bit : "",
      epistemic: rec && rec.bit === "inferred" ? "inferred" : "declared",
      sub: via,
      change: false,
      selectedId: extra && extra.selected,
    };
  }

  function graphBlock(cols, selected, onselect, extra, prov, kind, caption) {
    const edges = cols.edges || [];
    const graph = h("div", { class: "graph" + (kind ? " " + kind : "") + (edges.length ? " linked" : "") }, cols.map(function (col) {
      return h("div", { class: "col" }, [
        h("div", { class: "colhead" }, [col.head]),
        ...visibleNodes(col, selected, onselect),
      ]);
    }));
    if (edges.length) graph.setAttribute("data-edges", JSON.stringify(edges));
    return h("div", {}, [
      caption || prov ? h("div", { class: "proj-note" }, [
        caption ? h("div", {}, [caption]) : null,
        prov ? h("div", { class: "mono" }, [prov]) : null,
      ]) : null,
      expandable("graph-frame", graph),
      legend(edges),
      extra || null,
    ]);
  }

  function legend(edges) {
    const items = [
      ["declared", "declared link"],
      ["derived", "derived reach"],
      ["inferred", "inferred link"],
      ["unknown", "not represented"],
    ];
    if ((edges || []).some(function (edge) { return edge.kind === "promised"; })) {
      items.unshift(["promised", "declared promise"]);
    }
    return h("div", { class: "legend" }, items.map(function (pair) {
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

  function idParts(id) {
    const text = String(id || "");
    const cut = text.indexOf(".");
    if (cut < 0) return { pre: "", name: text };
    return { pre: text.slice(0, cut + 1), name: text.slice(cut + 1) };
  }

  function nodeButton(node, selected, onselect) {
    const current = node.distance === 0 || !!node.selectedId;
    const focus = !!(selected && node.id === selected);
    const cls = ["node", node.epistemic || "declared", node.bit || "", node.change ? "change" : "", node.dim ? "dim" : "", current ? "is-current" : "", focus ? "is-focus" : ""].filter(Boolean).join(" ");
    const parts = idParts(node.id);
    const flight = ((record(node.id) || {}).in_flight || []).map(function (change) { return change.id; }).filter(Boolean);
    const lines = (node.lines || []).filter(Boolean);
    const button = h("button", { class: cls, on: { click: function () { onselect(node.id); } } }, [
      parts.pre ? h("div", { class: "pre" }, [parts.pre]) : null,
      h("div", { class: "id" }, [breakable(parts.name || node.id)]),
      node.sub ? h("div", { class: "sub" }, [node.sub]) : null,
      !current && flight.length ? h("div", { class: "tag" }, ["↳ " + flight.join(", ")]) : null,
      ...lines.map(function (line) { return h("div", { class: "line", title: line }, [line]); }),
    ]);
    if (node.key) button.setAttribute("data-key", node.key);
    return button;
  }

  function mapCurve(a, b) {
    function n(value) { return Math.round(value * 10) / 10; }
    if (Math.abs(a.x - b.x) < 1) {
      const x0 = n(a.x + a.w / 2);
      return a.y < b.y
        ? "M" + x0 + " " + n(a.y + a.h) + " L" + x0 + " " + n(b.y)
        : "M" + x0 + " " + n(a.y) + " L" + x0 + " " + n(b.y + b.h);
    }
    const fwd = b.x > a.x;
    const x1 = n(fwd ? a.x + a.w : a.x);
    const x2 = n(fwd ? b.x : b.x + b.w);
    const y1 = n(a.y + a.h / 2);
    const y2 = n(b.y + b.h / 2);
    const mx = n((x1 + x2) / 2);
    return "M" + x1 + " " + y1 + " C" + mx + " " + y1 + " " + mx + " " + y2 + " " + x2 + " " + y2;
  }

  function drawEdges(graph) {
    const raw = graph.getAttribute("data-edges");
    if (!raw) return;
    let edges;
    try { edges = JSON.parse(raw); } catch (err) { return; }
    const box = graph.getBoundingClientRect();
    const pos = {};
    graph.querySelectorAll("[data-key]").forEach(function (el) {
      const rect = el.getBoundingClientRect();
      pos[el.getAttribute("data-key")] = {
        x: rect.left - box.left,
        y: rect.top - box.top,
        w: rect.width,
        h: rect.height,
      };
    });
    const parts = [];
    edges.forEach(function (edge) {
      const from = pos[edge.from];
      const to = pos[edge.to];
      if (!from || !to) return;
      parts.push(edge.kind + " " + mapCurve(from, to));
    });
    const sig = parts.join("|");
    if (graph._edgeSig === sig) return;
    graph._edgeSig = sig;
    const previous = graph.querySelector(".edges");
    if (previous) previous.remove();
    if (!parts.length) return;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "edges");
    svg.setAttribute("aria-hidden", "true");
    parts.forEach(function (part) {
      const cut = part.indexOf(" ");
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("class", part.slice(0, cut));
      path.setAttribute("d", part.slice(cut + 1));
      svg.appendChild(path);
    });
    graph.insertBefore(svg, graph.firstChild);
  }

  function paintMapEdges() {
    document.querySelectorAll(".graph.linked").forEach(function (graph) {
      drawEdges(graph);
      if (graph._edgeObs || typeof ResizeObserver === "undefined") return;
      graph._edgeObs = new ResizeObserver(function () { drawEdges(graph); });
      graph._edgeObs.observe(graph);
    });
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
        key: node.id,
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

  function blastEdges(graph, visible) {
    const edges = [];
    const seen = {};
    (graph.affected || []).forEach(function (node) {
      if (!visible[node.id]) return;
      const steps = node.path || [];
      const last = steps[steps.length - 1];
      if (!last || !last.from || last.from === node.id || !visible[last.from]) return;
      const pair = last.from + "\t" + node.id;
      if (seen[pair]) return;
      seen[pair] = true;
      const rel = last.relationship || "";
      let kind = "derived";
      if (rel === "promises" || rel === "promise_ids") kind = "promised";
      else if (edgeKind(last.from, node.id) === "inferred") kind = "inferred";
      edges.push({ from: last.from, to: node.id, kind: kind });
    });
    return edges;
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
    const visible = {};
    cols.forEach(function (col) {
      (col.nodes || []).forEach(function (node) { visible[node.id] = true; });
    });
    cols.edges = blastEdges(graph, visible);
    const chosen = selected
      ? (graph.affected || []).filter(function (node) { return node.id === selected; })[0]
      : null;
    const changeBlast = String(selfId).indexOf("change.") === 0;
    const panel = chosen
      ? whyPanel(chosen, graph, persp)
      : aboutBox(
        changeBlast
          ? [
            "What this change says it touches, and what the kernel reaches from there. Only the promised ids are a claim.",
            "A solid accent curve is a promise this change declares. A dotted curve is reach the kernel derives.",
            "Select a node to see the hop chain. Foundations are listed and not expanded.",
          ]
          : [
            "If this changes, what else should someone care about. Grouped by hop distance; nearer means more directly affected.",
            "A dotted curve is the hop the kernel recorded. It is not a second walk.",
            "Select a node to see the hop chain. Foundations are listed and not expanded.",
          ],
        changeBlast ? "declared promise · derived reach" : "derived · kernel impact"
      );
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

  function aboutBox(lines, prov) {
    return h("div", { class: "why" }, [
      h("div", { class: "why-head" }, ["About this projection"]),
      ...lines.map(function (line) { return h("div", {}, [line]); }),
      prov ? h("div", { class: "src" }, [prov]) : null,
    ]);
  }

  function whyBox(id, text, prov, extra) {
    return h("div", { class: "why" }, [
      h("div", { class: "why-head" }, ["Why this is here"]),
      h("div", { class: "mono" }, [breakable(id)]),
      h("div", {}, [text]),
      h("div", { class: "src" }, [prov]),
      (record(id) || String(id).indexOf("change.") === 0) ? h("a", { href: href(String(id).indexOf("change.") === 0 ? "change/" + String(id).replace(/^change\./, "") : "id/" + encodeURIComponent(id)) }, ["Open " + id + " →"]) : null,
      extra || null,
    ]);
  }

  function mapWhy(rec, selected, graph) {
    if (!selected) return aboutBox([
      "Each node is here because one declared field names it. Select a node to see which field.",
      "Nodes are ids. Open one to move the selection; the page recomposes around it.",
    ], "derived · from declared links");
    if (selected === rec.id) return whyBox(selected, "The selected id.", "declared · this record");
    let via = "";
    mapColumns(rec, graph).forEach(function (col) {
      (col.nodes || []).forEach(function (node) {
        if (node.id === selected && node.sub) via = node.sub;
      });
    });
    if (!via) return whyBox(selected, "A declared link names this id.", "declared");
    return whyBox(selected, via + " names this id from " + rec.id + ".", "declared · " + via);
  }

  function layerWhy(rec, selected) {
    if (!selected) return aboutBox([
      "Capability is the value axis; system, container, and component are the structural axis. Foundations are shared rules.",
    ], "derived · 5C placement");
    if (selected === rec.id) return whyBox(selected, "The selected id.", "declared · this record");
    let via = "";
    layerColumns(rec).forEach(function (col) {
      (col.nodes || []).forEach(function (node) {
        if (node.id === selected && node.sub) via = node.sub;
      });
    });
    if (!via) return whyBox(selected, "A declared link places this id on the 5C axis.", "declared");
    return whyBox(selected, via + " places this id on the 5C axis from " + rec.id + ".", "declared · " + via);
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


  function applyMermaidTheme() {
    if (!window.mermaid || !window.mermaid.initialize) return;
    const style = getComputedStyle(document.documentElement);
    function token(name) {
      return style.getPropertyValue(name).trim();
    }
    const dark = (document.documentElement.getAttribute("data-theme") || systemTheme()) === "dark";
    window.mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: "base",
      themeVariables: {
        darkMode: dark,
        background: token("--bg-sunken"),
        fontFamily: "Schibsted Grotesk, sans-serif",
        fontSize: "14px",
        primaryColor: token("--bg-surface"),
        primaryTextColor: token("--ink-1"),
        primaryBorderColor: token("--ink-4"),
        secondaryColor: token("--bg-raised"),
        secondaryTextColor: token("--ink-1"),
        secondaryBorderColor: token("--ink-4"),
        tertiaryColor: token("--bg-sunken"),
        tertiaryTextColor: token("--ink-1"),
        tertiaryBorderColor: token("--ink-4"),
        lineColor: token("--ink-4"),
        textColor: token("--ink-1"),
        mainBkg: token("--bg-surface"),
        nodeBorder: token("--ink-4"),
        clusterBkg: token("--bg-sunken"),
        clusterBorder: token("--ink-4"),
        titleColor: token("--ink-1"),
        edgeLabelBackground: token("--bg-sunken"),
        actorBkg: token("--bg-surface"),
        actorBorder: token("--ink-4"),
        actorTextColor: token("--ink-1"),
        actorLineColor: token("--ink-4"),
        signalColor: token("--ink-3"),
        signalTextColor: token("--ink-2"),
        labelBoxBkgColor: token("--bg-surface"),
        labelBoxBorderColor: token("--ink-4"),
        labelTextColor: token("--ink-1"),
        loopTextColor: token("--ink-2"),
        noteBkgColor: token("--bg-raised"),
        noteTextColor: token("--ink-1"),
        noteBorderColor: token("--ink-4"),
        activationBkgColor: token("--bg-raised"),
        activationBorderColor: token("--ink-4"),
        sequenceNumberColor: token("--ink-1"),
      },
    });
  }

  function releaseWheel(frame) {
    frame.addEventListener("wheel", function (ev) {
      ev.stopPropagation();
    }, { capture: true, passive: true });
  }

  function sizeDiagram(svg) {
    const box = (svg.getAttribute("viewBox") || "").trim().split(/[\s,]+/);
    const width = Number(box[2]);
    const height = Number(box[3]);
    if (!(width > 0) || !(height > 0)) return;
    svg.setAttribute("width", String(width));
    svg.setAttribute("height", String(height));
    svg.style.maxWidth = "none";
    svg.style.width = width + "px";
    svg.style.height = height + "px";
  }

  function plainLabel(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function wireDiagram(svg, selected, onselect) {
    const hosts = [];
    svg.querySelectorAll("g.node").forEach(function (node) { hosts.push(node); });
    svg.querySelectorAll("text.actor").forEach(function (text) {
      if (text.parentElement && hosts.indexOf(text.parentElement) < 0) hosts.push(text.parentElement);
    });
    hosts.forEach(function (host) {
      let label = "";
      const named = host.querySelector(".nodeLabel");
      if (named && named.closest("g.node") === host) label = plainLabel(named.textContent);
      if (!label) {
        const actor = host.querySelector(":scope > text.actor");
        if (actor) label = plainLabel(actor.textContent);
      }
      if (!label || !record(label)) return;
      host.classList.add("spec-id");
      if (selected && label === selected) host.classList.add("is-focus");
      host.addEventListener("click", function (ev) {
        ev.stopPropagation();
        onselect(label);
      });
    });
  }

  let expandedFrame = null;

  function syncExpandButtons() {
    document.querySelectorAll(".expand-btn").forEach(function (btn) {
      const frame = btn.closest(".graph-frame, .diagram-frame");
      btn.textContent = frame && frame === expandedFrame ? "Close" : "Expand";
    });
  }

  function closeExpand() {
    if (expandedFrame) expandedFrame.classList.remove("is-expanded");
    expandedFrame = null;
    document.body.classList.remove("is-expanded");
    const backdrop = document.querySelector(".expand-backdrop");
    if (backdrop) backdrop.hidden = true;
    syncExpandButtons();
  }

  function toggleExpand(frame) {
    if (expandedFrame === frame) {
      closeExpand();
      return;
    }
    if (expandedFrame) expandedFrame.classList.remove("is-expanded");
    expandedFrame = frame;
    frame.classList.add("is-expanded");
    document.body.classList.add("is-expanded");
    const backdrop = document.querySelector(".expand-backdrop");
    if (backdrop) backdrop.hidden = false;
    syncExpandButtons();
    paintMapEdges();
  }

  function expandable(className, picture) {
    const frame = h("div", { class: className });
    frame.append(
      h("div", { class: "diagram-bar" }, [
        h("button", {
          type: "button",
          class: "expand-btn",
          on: { click: function (ev) {
            ev.stopPropagation();
            toggleExpand(frame);
          } },
        }, ["Expand"]),
      ]),
      h("div", { class: "expand-stage" }, [picture])
    );
    return frame;
  }

  function diagramFrame(picture) {
    const frame = expandable("diagram-frame", picture);
    releaseWheel(frame);
    return frame;
  }

  function diagramPicture(diagram, selected, onselect) {
    const host = h("div", { class: "diagram" });
    const frame = diagramFrame(host);
    const source = diagram.mermaid || "";
    if (source && window.mermaid && window.mermaid.render) {
      applyMermaidTheme();
      const id = "spdiag" + (++diagramSeq);
      window.mermaid.render(id, source).then(function (result) {
        const holder = document.createElement("div");
        holder.innerHTML = result.svg;
        const svg = holder.querySelector("svg");
        host.replaceChildren();
        if (!svg) {
          host.append(h("pre", {}, [source]));
          return;
        }
        sizeDiagram(svg);
        wireDiagram(svg, selected, onselect);
        host.append(svg);
      }).catch(function () {
        host.replaceChildren(h("pre", {}, [source]));
      });
    } else if (source) {
      host.append(h("pre", {}, [source]));
    }
    return frame;
  }

  function mermaidSource(rec, index, source) {
    if (!source) return null;
    const key = "src:" + rec.id + ":" + index;
    const open = !!expanded[key];
    return h("div", { class: "mermaid-source" }, [
      h("button", {
        type: "button",
        class: "more",
        on: { click: function () { expanded[key] = !open; rerender(false); } },
      }, [open ? "Hide Mermaid source ↑" : "View Mermaid source ↓"]),
      open ? h("pre", {}, [source]) : null,
    ]);
  }

  function diagramBlock(rec, selected, onselect) {
    const list = rec.diagrams || [];
    if (!list.length) return h("p", { class: "note" }, ["No diagram declared on this id."]);
    let index = parseInt(parse().query.get("dg") || "0", 10);
    if (!(index >= 0 && index < list.length)) index = 0;
    const diagram = list[index];
    const source = diagram.mermaid || "";
    function pick(i) {
      go("id/" + encodeURIComponent(rec.id), { proj: "diagrams", dg: String(i) });
    }
    const why = selected
      ? whyBox(selected, "Declared in “" + (diagram.title || diagram.type || "diagram") + "”.", "declared · diagrams")
      : aboutBox([
        "This diagram is declared Mermaid. A label that is an id can be followed.",
      ], "declared · diagrams");
    return h("div", {}, [
      h("div", { class: "quiet" }, ["declared · diagrams on this id"]),
      diagramPicker(list, index, pick),
      diagram.description ? h("p", { class: "note" }, [diagram.description]) : null,
      diagramPicture(diagram, selected, onselect),
      mermaidSource(rec, index, source),
      why,
    ]);
  }


  function dataBlock(rec, graph) {
    const contracts = ((((graph || {}).perspectives || {}).quality || {}).contracts) || [];
    const mine = contracts.filter(function (item) {
      return item.subject === rec.id && item.kind === "data_models" && item.models;
    });
    if (!mine.length) return h("p", { class: "note" }, ["No data model declared on this id."]);
    const cards = [];
    mine.forEach(function (item) {
      Object.keys(item.models).forEach(function (name) {
        cards.push(h("div", { class: "col" }, [
          h("div", { class: "colhead" }, [name]),
          h("div", { class: "node" }, [modelFields(item.models[name]) || name]),
          h("div", { class: "src" }, [item.subject + " · " + (item.source || "contracts.data_models")]),
        ]));
      });
    });
    return h("div", {}, [
      h("div", { class: "quiet" }, ["declared · implementation.contracts.data_models"]),
      aboutBox([
        "Entities are declared on this id. A reference the model does not declare is left as written, not filled in.",
      ], "declared · data models"),
      expandable("graph-frame", h("div", { class: "graph" }, cards)),
    ]);
  }

  function modelFields(value) {
    if (Array.isArray(value)) return value.join(", ");
    if (value && typeof value === "object") {
      const fields = value.fields;
      return Array.isArray(fields) ? fields.join(", ") : Object.keys(value).join(", ");
    }
    if (value != null && value !== "") return String(value);
    return "";
  }

  function journeyWhy(selected, staged) {
    if (!selected) return aboutBox([
      "Stages run left to right in the order the flow declares them.",
      "A stage is not matched to a handler.",
    ], "declared · flows");
    if (staged) return whyBox(selected, "Declared as a stage on this flow. No handler is inferred.", "declared · flows.stages");
    return whyBox(selected, "Declared as a flow on this id. It has no stage list.", "declared · flows");
  }

  function stageColumns(item) {
    const stages = item.stages || [];
    const flow = item.flow_id || "flow";
    const edges = [];
    const cols = stages.map(function (stage, index) {
      const node = {
        id: stage,
        key: nodeKey(flow, stage),
        bit: "",
        epistemic: "declared",
        sub: "stage",
      };
      if (index) edges.push({ from: nodeKey(flow, stages[index - 1]), to: node.key, kind: "declared" });
      return { head: (index + 1) + " " + stage, nodes: [node] };
    });
    cols.edges = edges;
    return cols;
  }

  function flowCards(items) {
    const nodes = items.map(function (item, index) {
      const name = item.flow_id || item.detail || ("flow " + (index + 1));
      const lines = [];
      if (item.goal && item.goal !== name) lines.push(item.goal);
      outcomeLines(item.outcomes).forEach(function (line) { lines.push(line); });
      return {
        id: name,
        key: nodeKey("flow", String(index) + " " + name),
        bit: "",
        epistemic: "declared",
        sub: "flow",
        lines: lines.slice(0, 3),
      };
    });
    return [{ head: "Flows", nodes: nodes }];
  }

  function journeyBlock(rec, graph, selected, onselect) {
    const flows = productItems(graph, rec.id).filter(function (item) { return item.kind === "flow"; });
    const journeys = (((graph || {}).perspectives || {}).quality || {}).journeys || [];
    const mine = journeys.filter(function (item) { return item.subject === rec.id; });
    const staged = flows.filter(function (item) { return (item.stages || []).length; });
    const prose = flows.filter(function (item) { return !(item.stages || []).length; });
    const hit = staged.some(function (item) { return (item.stages || []).indexOf(selected) >= 0; });
    return h("div", {}, [
      h("div", { class: "quiet" }, ["declared · flows on this id"]),
      journeyWhy(selected, hit),
      ...staged.map(function (item) {
        const endings = outcomeLines(item.outcomes);
        return h("div", { class: "blk" }, [
          item.flow_id || item.goal ? h("div", { class: "blk-label" }, [item.flow_id || item.goal]) : null,
          item.goal && item.flow_id ? h("div", { class: "quiet" }, [item.goal]) : null,
          graphBlock(stageColumns(item), selected, onselect, null, "", "", ""),
          endings.length ? h("div", { class: "quiet" }, [endings.join(" · ")]) : null,
        ]);
      }),
      prose.length ? graphBlock(flowCards(prose), selected, onselect, null, "", "", "") : null,
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
    if (!change) return h("p", {}, ["No change named ", route.arg]);
    const graph = (DATA.impacts || {})["change:" + change.id];
    const node = route.query.get("node") || "";
    const persp = route.query.get("persp") || "system";
    const sync = change.check_sync || {};
    return h("div", { class: "split" }, [
      h("div", { class: "copy" }, [
        h("div", { class: "identity" }, [
          h("div", { class: "eyebrow" }, ["Change"]),
          h("div", { class: "row" }, [
            bitMark(changeState(change) === "archived" ? "archived" : "inflight"),
            h("span", { class: "id-title" + (changeState(change) === "archived" ? "" : " inflight") }, [breakable(change.id)]),
          ]),
          changeStatus(change),
        ]),
        h("div", { class: "promise" }, [
          h("div", { class: "kicker" }, ["Why"]),
          h("p", { class: "purpose" }, [change.why || ""]),
        ]),
        section("decl:" + change.id, "What the change declares", "proposal.yaml · delta.yaml · success.yaml", "", [
          promiseBlock(change),
          deltaBlock(change.delta),
          sensorBlock(sync),
        ], true),
        section("chk:" + change.id, "What SpecPlane checked", "check_sync · run", "", [
          block("Coverage", "check_sync", [
            h("div", { class: "item" }, [changeState(change) === "archived"
              ? "This folder is archived. It is not an open change."
              : "SpecPlane checked declared coverage. It did not verify behavior."]),
            kvRow([
              ["coverage", sync.coverage || ""],
              ["sensors", sync.sensors || ""],
              ["behavior", sync.behavior || "unverified"],
            ]),
          ]),
          block("Run", "run", [
            h("div", { class: "item" }, ["SpecPlane did not certify that an implementation satisfies the spec."]),
          ]),
        ], true),
        section("inf:" + change.id, "What SpecPlane infers", "blast", "", [
          block("Reach", "", [
            h("div", { class: "item" }, ["Ids past the ones this change names are reached by the kernel from declared links. The change does not claim them."]),
          ]),
        ], true),
        section("src:" + change.id, "Source", "the repository is the source", change.folder || ("specs/changes/" + change.id + "/"), [
          block("Files", "", changeFiles(change, sync).map(function (path) {
            return h("div", { class: "item quiet" }, [path]);
          })),
        ]),
      ]),
      h("div", { class: "stage" }, [
        switcher(change.projections || ["blast"], "blast", function () {}),
        perspectiveRow(persp, function (name) { go("change/" + change.id, { persp: name, node: node }); }),
        blastBlock(graph, "change." + change.id, node, persp, function (id) {
          go("change/" + change.id, { persp: persp, node: id });
        }),
      ]),
    ]);
  }

  function promiseBlock(change) {
    const ids = change.promise_ids || [];
    if (!ids.length) return null;
    return block("Promise ids", "proposal.yaml promise_ids", [
      h("div", { class: "item" }, [h("div", { class: "ids" }, ids.map(idLink))]),
    ]);
  }

  function deltaClaim(key) {
    if (key === "ADDED") return "not on the live spec yet";
    if (key === "MODIFIED") return "the live promise changes";
    if (key === "REMOVED") return "leaves the live spec";
    if (key === "RENAMED") return "the name changes";
    return "";
  }

  function deltaBlock(delta) {
    const keys = delta ? Object.keys(delta) : [];
    if (!keys.length) return null;
    const rows = [];
    keys.forEach(function (key) {
      (delta[key] || []).forEach(function (line) {
        if (typeof line === "string") line = { text: line };
        rows.push(h("div", { class: "item" }, [
          line.text ? h("div", {}, [line.text]) : null,
          h("div", {}, kvLines([
            ["claim", deltaClaim(key)],
            ["id", line.id ? idLink(line.id) : ""],
            ["group", line.group || ""],
          ])),
        ]));
      });
    });
    if (!rows.length) return null;
    return block("Delta", "delta.yaml", rows);
  }

  function sensorBlock(sync) {
    const rows = (sync && sync.sensor_rows) || [];
    if (!rows.length) return block("Success sensors", "success.yaml sensors", [
      h("div", { class: "item" }, ["No success sensor declared."]),
    ]);
    return block("Success sensors", "success.yaml sensors", rows.map(function (row) {
      return h("div", { class: "item" }, [
        row.must ? h("div", { class: "sensor" }, [row.must]) : null,
        h("div", {}, kvLines([
          ["id", row.id || ""],
          ["promise", row.promise ? idLink(row.promise) : ""],
          ["bound check", row.bound_check || "none · not_run"],
        ])),
      ]);
    }));
  }

  function changeFiles(change, sync) {
    const folder = change.folder || ("specs/changes/" + change.id + "/");
    const names = ["proposal.yaml"];
    if (change.delta && Object.keys(change.delta).length) names.push("delta.yaml");
    if (((sync && sync.sensor_rows) || []).length) names.push("success.yaml");
    return names.map(function (name) { return folder + name; });
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
    closeExpand();
    const route = parse();
    let body;
    if (route.kind === "changes") body = changesIndex(route);
    else if (route.kind === "gaps") body = gapsIndex();
    else if (route.kind === "activity") body = activityIndex();
    else if (route.kind === "id") body = recordPage(route);
    else if (route.kind === "change") body = changePage(route);
    else body = liveIndex(route);
    document.getElementById("app").replaceChildren(shell(route, body));
    paintMapEdges();
  }

  const expandBackdrop = h("div", { class: "expand-backdrop", on: { click: closeExpand } });
  expandBackdrop.hidden = true;
  document.body.appendChild(expandBackdrop);
  window.addEventListener("hashchange", function () { render(); });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") closeExpand();
  });
  render();
})();
