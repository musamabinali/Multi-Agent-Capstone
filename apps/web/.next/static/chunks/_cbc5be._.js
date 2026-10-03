(globalThis.TURBOPACK = globalThis.TURBOPACK || []).push(["static/chunks/_cbc5be._.js", {

"[project]/lib/stores/ui.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "useUIStore": (()=>useUIStore)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zustand$40$5$2e$0$2e$15_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/zustand@5.0.15_@types+react@19.3.0_react@19.0.0/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
"use client";
;
const useUIStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zustand$40$5$2e$0$2e$15_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])()((set)=>({
        sidebarCollapsed: false,
        citationDrawerOpen: false,
        selectedCitation: null,
        toggleSidebar: ()=>set((s)=>({
                    sidebarCollapsed: !s.sidebarCollapsed
                })),
        openCitation: (selectedCitation)=>set({
                selectedCitation,
                citationDrawerOpen: true
            }),
        closeCitation: ()=>set({
                citationDrawerOpen: false,
                selectedCitation: null
            })
    }));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/CitationChips.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "CitationChips": (()=>CitationChips)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/stores/ui.ts [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
"use client";
;
function CitationChips({ citations }) {
    _s();
    const openCitation = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"])({
        "CitationChips.useUIStore[openCitation]": (s)=>s.openCitation
    }["CitationChips.useUIStore[openCitation]"]);
    if (citations.length === 0) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "mt-2 flex flex-wrap gap-1",
        "aria-label": "Citations",
        children: citations.map((c, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                onClick: ()=>openCitation(c),
                className: "rounded-[6px] border border-[var(--border)] bg-[var(--surface-elevated)] px-2 py-0.5 text-xs hover:border-[var(--primary)]",
                "aria-label": `Open source ${c.source} page ${c.page}`,
                children: [
                    "[",
                    c.source,
                    " · p.",
                    c.page,
                    "]"
                ]
            }, `${c.source}-${c.page}-${i}`, true, {
                fileName: "[project]/components/chat/CitationChips.tsx",
                lineNumber: 16,
                columnNumber: 5
            }, this))
    }, void 0, false, {
        fileName: "[project]/components/chat/CitationChips.tsx",
        lineNumber: 14,
        columnNumber: 3
    }, this);
}
_s(CitationChips, "HbEXVjdMB3y6cqPwNO2O4oYpAbY=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"]
    ];
});
_c = CitationChips;
var _c;
__turbopack_refresh__.register(_c, "CitationChips");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/StructuredResultTable.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "StructuredResultTable": (()=>StructuredResultTable)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
"use client";
;
function text(value) {
    if (typeof value === "string" && value.length > 0) return value;
    if (typeof value === "number") return String(value);
    return null;
}
function rowsFor(agent, structured) {
    const rows = [];
    const list = (value)=>Array.isArray(value) ? value.filter((v)=>typeof v === "string" || typeof v === "number").map(String) : [];
    if (agent === "rag_agent") {
        const count = structured.chunk_count;
        if (typeof count === "number") rows.push([
            "chunks",
            String(count)
        ]);
        return rows;
    }
    if (agent === "github_agent") {
        const prs = list(structured.pr_numbers);
        const issues = list(structured.issue_numbers);
        const shas = list(structured.commit_shas);
        if (prs.length > 0) rows.push([
            "pr_numbers",
            prs.join(", ")
        ]);
        if (issues.length > 0) rows.push([
            "issue_numbers",
            issues.join(", ")
        ]);
        if (shas.length > 0) rows.push([
            "commit_shas",
            shas.join(", ")
        ]);
        const repo = text(structured.repo);
        if (repo !== null) rows.push([
            "repo",
            repo
        ]);
        return rows;
    }
    const eventIds = list(structured.event_ids);
    const eventId = text(structured.event_id);
    const messageId = text(structured.message_id);
    const draftId = text(structured.draft_id);
    const status = text(structured.calendar_status);
    if (eventIds.length > 0) rows.push([
        "event_ids",
        eventIds.join(", ")
    ]);
    else if (eventId !== null) rows.push([
        "event_id",
        eventId
    ]);
    if (messageId !== null) rows.push([
        "message_id",
        messageId
    ]);
    if (draftId !== null) rows.push([
        "draft_id",
        draftId
    ]);
    if (status !== null) rows.push([
        "calendar_status",
        status
    ]);
    const availability = structured.availability;
    if (availability !== undefined && typeof availability === "object" && availability !== null) {
        const free = availability.free;
        const partial = availability.partial;
        if (typeof free === "boolean" || typeof partial === "boolean") {
            rows.push([
                "availability",
                `free=${String(free)} partial=${String(partial)}`
            ]);
        }
    }
    return rows;
}
function StructuredResultTable({ agent, structured }) {
    if (structured === undefined) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
            className: "mt-2 text-xs text-[var(--muted-foreground)]",
            children: "no structured result"
        }, void 0, false, {
            fileName: "[project]/components/chat/StructuredResultTable.tsx",
            lineNumber: 78,
            columnNumber: 4
        }, this);
    }
    const rows = rowsFor(agent, structured);
    if (rows.length === 0) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
            className: "mt-2 text-xs text-[var(--muted-foreground)]",
            children: "no structured result"
        }, void 0, false, {
            fileName: "[project]/components/chat/StructuredResultTable.tsx",
            lineNumber: 86,
            columnNumber: 4
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("table", {
        className: "mt-2 w-full text-xs",
        "aria-label": "Structured result",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tbody", {
            children: rows.map(([label, value])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                    className: "border-t border-[var(--border)]",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                            className: "py-1 pr-2 text-[var(--muted-foreground)]",
                            children: label
                        }, void 0, false, {
                            fileName: "[project]/components/chat/StructuredResultTable.tsx",
                            lineNumber: 96,
                            columnNumber: 7
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                            className: "py-1 font-mono tabular-nums",
                            children: value
                        }, void 0, false, {
                            fileName: "[project]/components/chat/StructuredResultTable.tsx",
                            lineNumber: 99,
                            columnNumber: 7
                        }, this)
                    ]
                }, label, true, {
                    fileName: "[project]/components/chat/StructuredResultTable.tsx",
                    lineNumber: 95,
                    columnNumber: 6
                }, this))
        }, void 0, false, {
            fileName: "[project]/components/chat/StructuredResultTable.tsx",
            lineNumber: 93,
            columnNumber: 4
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/chat/StructuredResultTable.tsx",
        lineNumber: 92,
        columnNumber: 3
    }, this);
}
_c = StructuredResultTable;
var _c;
__turbopack_refresh__.register(_c, "StructuredResultTable");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/ui/badge.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "Badge": (()=>Badge)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$clsx$40$2$2e$1$2e$1$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/clsx@2.1.1/node_modules/clsx/dist/clsx.mjs [app-client] (ecmascript)");
;
;
/* Solid pills use darkened (*-strong) backgrounds so white text passes
   WCAG AA; agent pills use surface backgrounds with accent text so the
   bright accents never carry text. Verified with the axe suite. */ const tones = {
    demo: "bg-zinc-700 text-white",
    free: "bg-[var(--info-strong)] text-white",
    live: "bg-[var(--success-strong)] text-white",
    ok: "bg-[var(--success-strong)] text-white",
    partial: "bg-[var(--warning)] text-black",
    error: "bg-[var(--error)] text-white",
    muted: "bg-[var(--surface-elevated)] text-[var(--muted-foreground)]",
    rag: "border border-[var(--accent-rag)] bg-[var(--surface-elevated)] text-[var(--accent-rag)]",
    github: "border border-[var(--accent-github)] bg-[var(--surface-elevated)] text-[var(--accent-github)]",
    calendar: "border border-[var(--accent-calendar)] bg-[var(--surface-elevated)] text-[var(--accent-calendar)]",
    gmail: "border border-[var(--accent-gmail)] bg-[var(--surface-elevated)] text-[var(--accent-gmail)]"
};
function Badge({ tone, children }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$clsx$40$2$2e$1$2e$1$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["clsx"])("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium", tones[tone]),
        children: children
    }, void 0, false, {
        fileName: "[project]/components/ui/badge.tsx",
        lineNumber: 41,
        columnNumber: 3
    }, this);
}
_c = Badge;
var _c;
__turbopack_refresh__.register(_c, "Badge");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/ui/card.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "Card": (()=>Card)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$clsx$40$2$2e$1$2e$1$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/clsx@2.1.1/node_modules/clsx/dist/clsx.mjs [app-client] (ecmascript)");
;
;
const borders = {
    rag: "border-l-4 border-l-[var(--accent-rag)]",
    github: "border-l-4 border-l-[var(--accent-github)]",
    calendar: "border-l-4 border-l-[var(--accent-calendar)]",
    gmail: "border-l-4 border-l-[var(--accent-gmail)]",
    none: ""
};
function Card({ accent = "none", children, className }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$clsx$40$2$2e$1$2e$1$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["clsx"])("rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-4", borders[accent], className),
        children: children
    }, void 0, false, {
        fileName: "[project]/components/ui/card.tsx",
        lineNumber: 19,
        columnNumber: 3
    }, this);
}
_c = Card;
var _c;
__turbopack_refresh__.register(_c, "Card");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/AgentMessageCard.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "AgentMessageCard": (()=>AgentMessageCard)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$CitationChips$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/CitationChips.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$StructuredResultTable$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/StructuredResultTable.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$badge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/ui/badge.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$card$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/ui/card.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$calendar$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Calendar$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/calendar.js [app-client] (ecmascript) <export default as Calendar>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mail$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mail$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/mail.js [app-client] (ecmascript) <export default as Mail>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$github$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Github$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/github.js [app-client] (ecmascript) <export default as Github>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$book$2d$open$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BookOpen$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/book-open.js [app-client] (ecmascript) <export default as BookOpen>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$framer$2d$motion$40$11$2e$18$2e$2_react_ad77ca5e76db208923200a5ee292bed7$2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/framer-motion@11.18.2_react_ad77ca5e76db208923200a5ee292bed7/node_modules/framer-motion/dist/es/render/components/motion/proxy.mjs [app-client] (ecmascript)");
"use client";
;
;
;
;
;
;
;
function accentFor(agent) {
    if (agent === "rag_agent") return "rag";
    if (agent === "github_agent") return "github";
    if (agent.includes("gmail")) return "gmail";
    return "calendar";
}
function iconFor(agent) {
    if (agent === "rag_agent") return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$book$2d$open$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BookOpen$3e$__["BookOpen"], {
        size: 16,
        "aria-hidden": true
    }, void 0, false, {
        fileName: "[project]/components/chat/AgentMessageCard.tsx",
        lineNumber: 25,
        columnNumber: 36
    }, this);
    if (agent === "github_agent") return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$github$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Github$3e$__["Github"], {
        size: 16,
        "aria-hidden": true
    }, void 0, false, {
        fileName: "[project]/components/chat/AgentMessageCard.tsx",
        lineNumber: 26,
        columnNumber: 39
    }, this);
    if (agent.includes("gmail")) return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mail$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mail$3e$__["Mail"], {
        size: 16,
        "aria-hidden": true
    }, void 0, false, {
        fileName: "[project]/components/chat/AgentMessageCard.tsx",
        lineNumber: 27,
        columnNumber: 38
    }, this);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$calendar$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Calendar$3e$__["Calendar"], {
        size: 16,
        "aria-hidden": true
    }, void 0, false, {
        fileName: "[project]/components/chat/AgentMessageCard.tsx",
        lineNumber: 28,
        columnNumber: 9
    }, this);
}
function labelFor(agent) {
    if (agent === "rag_agent") return "RAG agent";
    if (agent === "github_agent") return "GitHub agent";
    if (agent === "google_agent") return "Calendar / Gmail agent";
    return agent;
}
function AgentMessageCard({ output, streaming, durationMs }) {
    const accent = accentFor(output.agent);
    const status = streaming ? "streaming" : output.status;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$framer$2d$motion$40$11$2e$18$2e$2_react_ad77ca5e76db208923200a5ee292bed7$2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["motion"].div, {
        initial: {
            opacity: 0
        },
        animate: {
            opacity: 1
        },
        transition: {
            duration: 0.12
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$card$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Card"], {
            accent: accent,
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex items-center gap-2",
                    "aria-live": "polite",
                    children: [
                        iconFor(output.agent),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            className: "font-medium",
                            children: labelFor(output.agent)
                        }, void 0, false, {
                            fileName: "[project]/components/chat/AgentMessageCard.tsx",
                            lineNumber: 50,
                            columnNumber: 6
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$badge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Badge"], {
                            tone: status === "ok" ? "ok" : status === "error" ? "error" : status === "partial" ? "partial" : "muted",
                            children: [
                                status,
                                typeof durationMs === "number" ? ` · ${(durationMs / 1000).toFixed(1)}s` : ""
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/chat/AgentMessageCard.tsx",
                            lineNumber: 51,
                            columnNumber: 6
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/chat/AgentMessageCard.tsx",
                    lineNumber: 48,
                    columnNumber: 5
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: "mt-2 whitespace-pre-wrap text-sm",
                    children: output.answer
                }, void 0, false, {
                    fileName: "[project]/components/chat/AgentMessageCard.tsx",
                    lineNumber: 68,
                    columnNumber: 5
                }, this),
                output.tools !== undefined && output.tools.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: "mt-1 text-xs text-[var(--muted-foreground)]",
                    children: [
                        "Tools:",
                        " ",
                        output.tools.map((t)=>`${t.tool} (${t.status})`).join(", ")
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/chat/AgentMessageCard.tsx",
                    lineNumber: 70,
                    columnNumber: 6
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$CitationChips$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CitationChips"], {
                    citations: output.citations ?? []
                }, void 0, false, {
                    fileName: "[project]/components/chat/AgentMessageCard.tsx",
                    lineNumber: 75,
                    columnNumber: 5
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$StructuredResultTable$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["StructuredResultTable"], {
                    agent: output.agent,
                    structured: output.structured
                }, void 0, false, {
                    fileName: "[project]/components/chat/AgentMessageCard.tsx",
                    lineNumber: 76,
                    columnNumber: 5
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/chat/AgentMessageCard.tsx",
            lineNumber: 47,
            columnNumber: 4
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/chat/AgentMessageCard.tsx",
        lineNumber: 42,
        columnNumber: 3
    }, this);
}
_c = AgentMessageCard;
var _c;
__turbopack_refresh__.register(_c, "AgentMessageCard");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/Composer.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "Composer": (()=>Composer)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$send$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Send$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/send.js [app-client] (ecmascript) <export default as Send>");
;
var _s = __turbopack_refresh__.signature();
"use client";
;
;
function Composer({ mode, disabled, onSend }) {
    _s();
    const [value, setValue] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const submit = ()=>{
        const trimmed = value.trim();
        if (trimmed.length === 0 || disabled) return;
        setValue("");
        onSend(trimmed);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "border-t border-[var(--border)] bg-[var(--surface)] p-3",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-end gap-2",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                        value: value,
                        onChange: (e)=>setValue(e.target.value),
                        onKeyDown: (e)=>{
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                submit();
                            }
                        },
                        placeholder: "Type your message...",
                        "aria-label": "Type your message",
                        rows: 2,
                        disabled: disabled,
                        className: "min-h-11 flex-1 resize-none rounded-[10px] border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm"
                    }, void 0, false, {
                        fileName: "[project]/components/chat/Composer.tsx",
                        lineNumber: 23,
                        columnNumber: 5
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: submit,
                        disabled: disabled || value.trim().length === 0,
                        "aria-label": "Send message",
                        className: "rounded-[10px] bg-[var(--primary-solid)] p-2.5 text-white disabled:opacity-50",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$send$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Send$3e$__["Send"], {
                            size: 18,
                            "aria-hidden": true
                        }, void 0, false, {
                            fileName: "[project]/components/chat/Composer.tsx",
                            lineNumber: 45,
                            columnNumber: 6
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/chat/Composer.tsx",
                        lineNumber: 38,
                        columnNumber: 5
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/Composer.tsx",
                lineNumber: 22,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-1 text-xs text-[var(--muted-foreground)]",
                children: [
                    "Mode: ",
                    mode
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/Composer.tsx",
                lineNumber: 48,
                columnNumber: 4
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/chat/Composer.tsx",
        lineNumber: 21,
        columnNumber: 3
    }, this);
}
_s(Composer, "dBtK6I2q1m3rcfzPBa0nrbv/iCI=");
_c = Composer;
var _c;
__turbopack_refresh__.register(_c, "Composer");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/PartialAvailabilityNotice.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "PartialAvailabilityNotice": (()=>PartialAvailabilityNotice)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__TriangleAlert$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/triangle-alert.js [app-client] (ecmascript) <export default as TriangleAlert>");
"use client";
;
;
function PartialAvailabilityNotice({ answer, onVerify }) {
    const lowered = answer.toLowerCase();
    const isPartial = lowered.includes("partial") || lowered.includes("could not be verified") || lowered.includes("attendee");
    if (!isPartial) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        role: "alert",
        className: "rounded-[10px] border border-[var(--warning)] bg-[var(--surface-elevated)] p-3 text-sm",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-2 font-medium",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__TriangleAlert$3e$__["TriangleAlert"], {
                        size: 16,
                        "aria-hidden": true
                    }, void 0, false, {
                        fileName: "[project]/components/chat/PartialAvailabilityNotice.tsx",
                        lineNumber: 24,
                        columnNumber: 5
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        children: "Availability check is partial"
                    }, void 0, false, {
                        fileName: "[project]/components/chat/PartialAvailabilityNotice.tsx",
                        lineNumber: 25,
                        columnNumber: 5
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/PartialAvailabilityNotice.tsx",
                lineNumber: 23,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "mt-1 text-[var(--muted-foreground)]",
                children: "External attendee calendars could not be verified. Auto-create is refused."
            }, void 0, false, {
                fileName: "[project]/components/chat/PartialAvailabilityNotice.tsx",
                lineNumber: 27,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-2 flex gap-2",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    type: "button",
                    onClick: onVerify,
                    className: "rounded-[6px] border border-[var(--border)] px-3 py-1 text-sm hover:border-[var(--primary)]",
                    children: "Verify manually"
                }, void 0, false, {
                    fileName: "[project]/components/chat/PartialAvailabilityNotice.tsx",
                    lineNumber: 32,
                    columnNumber: 5
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/chat/PartialAvailabilityNotice.tsx",
                lineNumber: 31,
                columnNumber: 4
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/chat/PartialAvailabilityNotice.tsx",
        lineNumber: 19,
        columnNumber: 3
    }, this);
}
_c = PartialAvailabilityNotice;
var _c;
__turbopack_refresh__.register(_c, "PartialAvailabilityNotice");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/SupervisorRoutingCard.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "SupervisorRoutingCard": (()=>SupervisorRoutingCard)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$network$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Network$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/network.js [app-client] (ecmascript) <export default as Network>");
"use client";
;
;
function SupervisorRoutingCard({ agents, reasoning, showReasoning }) {
    if (agents.length === 0) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "rounded-[10px] border border-[var(--border)] bg-[var(--surface-elevated)] p-3 text-sm",
        "aria-live": "polite",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-2",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$network$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Network$3e$__["Network"], {
                        size: 16,
                        "aria-hidden": true
                    }, void 0, false, {
                        fileName: "[project]/components/chat/SupervisorRoutingCard.tsx",
                        lineNumber: 23,
                        columnNumber: 5
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        children: [
                            "Supervisor routed to ",
                            agents.length,
                            " agent",
                            agents.length === 1 ? "" : "s",
                            " in parallel:"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/chat/SupervisorRoutingCard.tsx",
                        lineNumber: 24,
                        columnNumber: 5
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        className: "font-medium",
                        children: agents.join(" · ")
                    }, void 0, false, {
                        fileName: "[project]/components/chat/SupervisorRoutingCard.tsx",
                        lineNumber: 28,
                        columnNumber: 5
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/SupervisorRoutingCard.tsx",
                lineNumber: 22,
                columnNumber: 4
            }, this),
            showReasoning && reasoning && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "mt-1 text-xs text-[var(--muted-foreground)]",
                children: reasoning
            }, void 0, false, {
                fileName: "[project]/components/chat/SupervisorRoutingCard.tsx",
                lineNumber: 31,
                columnNumber: 5
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/chat/SupervisorRoutingCard.tsx",
        lineNumber: 18,
        columnNumber: 3
    }, this);
}
_c = SupervisorRoutingCard;
var _c;
__turbopack_refresh__.register(_c, "SupervisorRoutingCard");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/lib/stores/settings.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "useSettingsStore": (()=>useSettingsStore)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zustand$40$5$2e$0$2e$15_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/zustand@5.0.15_@types+react@19.3.0_react@19.0.0/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zustand$40$5$2e$0$2e$15_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/zustand@5.0.15_@types+react@19.3.0_react@19.0.0/node_modules/zustand/esm/middleware.mjs [app-client] (ecmascript)");
"use client";
;
;
const useSettingsStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zustand$40$5$2e$0$2e$15_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])()((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zustand$40$5$2e$0$2e$15_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["persist"])((set)=>({
        compactMode: false,
        showReasoning: true,
        toggleCompact: ()=>set((s)=>({
                    compactMode: !s.compactMode
                })),
        toggleReasoning: ()=>set((s)=>({
                    showReasoning: !s.showReasoning
                }))
    }), {
    name: "makpa-settings"
}));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/lib/stores/thread.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "useThreadStore": (()=>useThreadStore)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zustand$40$5$2e$0$2e$15_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/zustand@5.0.15_@types+react@19.3.0_react@19.0.0/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
"use client";
;
const emptyView = ()=>({
        status: "streaming",
        answer: "",
        citations: [],
        tools: [],
        streaming: true
    });
const useThreadStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zustand$40$5$2e$0$2e$15_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])()((set)=>({
        threadId: null,
        messages: [],
        agents: [],
        agentViews: {},
        pendingInterrupt: null,
        overallStatus: "",
        reasoning: "",
        connected: false,
        setThread: (threadId)=>set({
                threadId,
                messages: [],
                agents: [],
                agentViews: {},
                pendingInterrupt: null,
                overallStatus: "",
                reasoning: ""
            }),
        reset: ()=>set({
                messages: [],
                agents: [],
                agentViews: {},
                pendingInterrupt: null,
                overallStatus: "",
                reasoning: ""
            }),
        pushUser: (content)=>set((s)=>({
                    messages: [
                        ...s.messages,
                        {
                            role: "user",
                            content
                        }
                    ]
                })),
        applyRouting: (agents, reasoning)=>set({
                agents,
                reasoning
            }),
        startAgents: (agents)=>set((s)=>{
                const views = {
                    ...s.agentViews
                };
                for (const a of agents)views[a] = emptyView();
                return {
                    agentViews: views
                };
            }),
        appendToken: (agent, delta)=>set((s)=>{
                const prev = s.agentViews[agent] ?? emptyView();
                return {
                    agentViews: {
                        ...s.agentViews,
                        [agent]: {
                            ...prev,
                            answer: prev.answer + delta
                        }
                    }
                };
            }),
        applyTool: (agent, tool, status)=>set((s)=>{
                const prev = s.agentViews[agent] ?? emptyView();
                const tools = [
                    ...prev.tools ?? [],
                    {
                        tool,
                        status
                    }
                ];
                return {
                    agentViews: {
                        ...s.agentViews,
                        [agent]: {
                            ...prev,
                            tools
                        }
                    }
                };
            }),
        endAgent: (agent, status)=>set((s)=>{
                const prev = s.agentViews[agent] ?? emptyView();
                return {
                    agentViews: {
                        ...s.agentViews,
                        [agent]: {
                            ...prev,
                            status,
                            streaming: false
                        }
                    }
                };
            }),
        applyOutputs: (outputs)=>set((s)=>{
                const views = {
                    ...s.agentViews
                };
                for (const [name, out] of Object.entries(outputs)){
                    views[name] = {
                        status: out.status,
                        answer: out.answer,
                        citations: out.citations ?? [],
                        tools: out.tools ?? [],
                        structured: out.structured,
                        streaming: false
                    };
                }
                const order = Object.keys(outputs);
                const messages = [
                    ...s.messages
                ];
                return {
                    agentViews: views,
                    agents: order.length > 0 ? order : s.agents,
                    messages
                };
            }),
        setInterrupt: (pendingInterrupt)=>set({
                pendingInterrupt
            }),
        setAggregate: (overallStatus)=>set({
                overallStatus
            }),
        setConnected: (connected)=>set({
                connected
            })
    }));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/ChatView.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "ChatView": (()=>ChatView)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$AgentMessageCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/AgentMessageCard.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$Composer$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/Composer.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$PartialAvailabilityNotice$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/PartialAvailabilityNotice.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$SupervisorRoutingCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/SupervisorRoutingCard.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/stores/settings.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/stores/thread.ts [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
"use client";
;
;
;
;
;
;
function ChatView({ mode, sending, onSend, onVerifyPartial }) {
    _s();
    const messages = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"])({
        "ChatView.useThreadStore[messages]": (s)=>s.messages
    }["ChatView.useThreadStore[messages]"]);
    const agents = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"])({
        "ChatView.useThreadStore[agents]": (s)=>s.agents
    }["ChatView.useThreadStore[agents]"]);
    const agentViews = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"])({
        "ChatView.useThreadStore[agentViews]": (s)=>s.agentViews
    }["ChatView.useThreadStore[agentViews]"]);
    const reasoning = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"])({
        "ChatView.useThreadStore[reasoning]": (s)=>s.reasoning
    }["ChatView.useThreadStore[reasoning]"]);
    const overallStatus = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"])({
        "ChatView.useThreadStore[overallStatus]": (s)=>s.overallStatus
    }["ChatView.useThreadStore[overallStatus]"]);
    const showReasoning = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSettingsStore"])({
        "ChatView.useSettingsStore[showReasoning]": (s)=>s.showReasoning
    }["ChatView.useSettingsStore[showReasoning]"]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex min-h-0 flex-1 flex-col",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "min-h-0 flex-1 space-y-3 overflow-y-auto p-4",
                "aria-live": "polite",
                children: [
                    messages.filter((m)=>m.role === "user").map((m)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "rounded-[10px] bg-[var(--surface-elevated)] p-3 text-sm",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: "font-medium",
                                    children: "You: "
                                }, void 0, false, {
                                    fileName: "[project]/components/chat/ChatView.tsx",
                                    lineNumber: 38,
                                    columnNumber: 8
                                }, this),
                                m.content
                            ]
                        }, `u-${m.role}-${m.content}`, true, {
                            fileName: "[project]/components/chat/ChatView.tsx",
                            lineNumber: 34,
                            columnNumber: 7
                        }, this)),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$SupervisorRoutingCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["SupervisorRoutingCard"], {
                        agents: agents,
                        reasoning: reasoning,
                        showReasoning: showReasoning
                    }, void 0, false, {
                        fileName: "[project]/components/chat/ChatView.tsx",
                        lineNumber: 42,
                        columnNumber: 5
                    }, this),
                    agents.map((agent)=>{
                        const view = agentViews[agent];
                        if (view === undefined) return null;
                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$AgentMessageCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AgentMessageCard"], {
                                    output: {
                                        agent,
                                        status: view.status,
                                        answer: view.answer,
                                        citations: view.citations ?? [],
                                        tools: view.tools ?? [],
                                        structured: view.structured
                                    },
                                    streaming: view.streaming
                                }, void 0, false, {
                                    fileName: "[project]/components/chat/ChatView.tsx",
                                    lineNumber: 52,
                                    columnNumber: 8
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$PartialAvailabilityNotice$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["PartialAvailabilityNotice"], {
                                    answer: view.answer,
                                    onVerify: onVerifyPartial
                                }, void 0, false, {
                                    fileName: "[project]/components/chat/ChatView.tsx",
                                    lineNumber: 63,
                                    columnNumber: 8
                                }, this)
                            ]
                        }, agent, true, {
                            fileName: "[project]/components/chat/ChatView.tsx",
                            lineNumber: 51,
                            columnNumber: 7
                        }, this);
                    }),
                    overallStatus && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-xs text-[var(--muted-foreground)]",
                        children: [
                            "Overall status: ",
                            overallStatus
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/chat/ChatView.tsx",
                        lineNumber: 71,
                        columnNumber: 6
                    }, this),
                    messages.length === 0 && agents.length === 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "py-16 text-center",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "text-2xl",
                                "aria-hidden": true,
                                children: "🎯"
                            }, void 0, false, {
                                fileName: "[project]/components/chat/ChatView.tsx",
                                lineNumber: 77,
                                columnNumber: 7
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                                className: "mt-2 text-lg font-medium",
                                children: "Start a conversation"
                            }, void 0, false, {
                                fileName: "[project]/components/chat/ChatView.tsx",
                                lineNumber: 80,
                                columnNumber: 7
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("ul", {
                                className: "mt-3 space-y-1 text-sm text-[var(--muted-foreground)]",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                        children: "“Summarize the sample PDF”"
                                    }, void 0, false, {
                                        fileName: "[project]/components/chat/ChatView.tsx",
                                        lineNumber: 82,
                                        columnNumber: 8
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                        children: "“List open PRs in octo-demo/hello-world”"
                                    }, void 0, false, {
                                        fileName: "[project]/components/chat/ChatView.tsx",
                                        lineNumber: 83,
                                        columnNumber: 8
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                        children: "“Schedule a meeting with a@x.com tomorrow”"
                                    }, void 0, false, {
                                        fileName: "[project]/components/chat/ChatView.tsx",
                                        lineNumber: 84,
                                        columnNumber: 8
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/chat/ChatView.tsx",
                                lineNumber: 81,
                                columnNumber: 7
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/chat/ChatView.tsx",
                        lineNumber: 76,
                        columnNumber: 6
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/ChatView.tsx",
                lineNumber: 27,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$Composer$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Composer"], {
                mode: mode,
                disabled: sending,
                onSend: onSend
            }, void 0, false, {
                fileName: "[project]/components/chat/ChatView.tsx",
                lineNumber: 89,
                columnNumber: 4
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/chat/ChatView.tsx",
        lineNumber: 26,
        columnNumber: 3
    }, this);
}
_s(ChatView, "cS9i3ThzjY02SjEjL1EU4P9EqM4=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$settings$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useSettingsStore"]
    ];
});
_c = ChatView;
var _c;
__turbopack_refresh__.register(_c, "ChatView");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/CitationDrawer.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "CitationDrawer": (()=>CitationDrawer)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/stores/ui.ts [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
"use client";
;
function CitationDrawer() {
    _s();
    const open = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"])({
        "CitationDrawer.useUIStore[open]": (s)=>s.citationDrawerOpen
    }["CitationDrawer.useUIStore[open]"]);
    const citation = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"])({
        "CitationDrawer.useUIStore[citation]": (s)=>s.selectedCitation
    }["CitationDrawer.useUIStore[citation]"]);
    const close = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"])({
        "CitationDrawer.useUIStore[close]": (s)=>s.closeCitation
    }["CitationDrawer.useUIStore[close]"]);
    if (!open || citation === null) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
        "aria-label": "Citation source preview",
        className: "fixed right-0 top-0 z-40 h-full w-80 border-l border-[var(--border)] bg-[var(--surface)] p-4",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center justify-between",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "font-medium",
                        children: "Source preview"
                    }, void 0, false, {
                        fileName: "[project]/components/chat/CitationDrawer.tsx",
                        lineNumber: 16,
                        columnNumber: 5
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: close,
                        "aria-label": "Close citation drawer",
                        className: "rounded p-1",
                        children: "✕"
                    }, void 0, false, {
                        fileName: "[project]/components/chat/CitationDrawer.tsx",
                        lineNumber: 17,
                        columnNumber: 5
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/CitationDrawer.tsx",
                lineNumber: 15,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dl", {
                className: "mt-3 space-y-1 text-sm",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dt", {
                                className: "text-[var(--muted-foreground)]",
                                children: "Source"
                            }, void 0, false, {
                                fileName: "[project]/components/chat/CitationDrawer.tsx",
                                lineNumber: 28,
                                columnNumber: 6
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dd", {
                                className: "font-mono",
                                children: citation.source
                            }, void 0, false, {
                                fileName: "[project]/components/chat/CitationDrawer.tsx",
                                lineNumber: 29,
                                columnNumber: 6
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/chat/CitationDrawer.tsx",
                        lineNumber: 27,
                        columnNumber: 5
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dt", {
                                className: "text-[var(--muted-foreground)]",
                                children: "Page"
                            }, void 0, false, {
                                fileName: "[project]/components/chat/CitationDrawer.tsx",
                                lineNumber: 32,
                                columnNumber: 6
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dd", {
                                className: "font-mono",
                                children: citation.page
                            }, void 0, false, {
                                fileName: "[project]/components/chat/CitationDrawer.tsx",
                                lineNumber: 33,
                                columnNumber: 6
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/chat/CitationDrawer.tsx",
                        lineNumber: 31,
                        columnNumber: 5
                    }, this),
                    citation.chunk_id !== undefined && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dt", {
                                className: "text-[var(--muted-foreground)]",
                                children: "Chunk"
                            }, void 0, false, {
                                fileName: "[project]/components/chat/CitationDrawer.tsx",
                                lineNumber: 37,
                                columnNumber: 7
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dd", {
                                className: "font-mono",
                                children: String(citation.chunk_id)
                            }, void 0, false, {
                                fileName: "[project]/components/chat/CitationDrawer.tsx",
                                lineNumber: 38,
                                columnNumber: 7
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/chat/CitationDrawer.tsx",
                        lineNumber: 36,
                        columnNumber: 6
                    }, this),
                    typeof citation.score === "number" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "flex gap-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dt", {
                                className: "text-[var(--muted-foreground)]",
                                children: "Score"
                            }, void 0, false, {
                                fileName: "[project]/components/chat/CitationDrawer.tsx",
                                lineNumber: 43,
                                columnNumber: 7
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dd", {
                                className: "font-mono tabular-nums",
                                children: citation.score.toFixed(3)
                            }, void 0, false, {
                                fileName: "[project]/components/chat/CitationDrawer.tsx",
                                lineNumber: 44,
                                columnNumber: 7
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/chat/CitationDrawer.tsx",
                        lineNumber: 42,
                        columnNumber: 6
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/CitationDrawer.tsx",
                lineNumber: 26,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "mt-3 text-xs text-[var(--muted-foreground)]",
                children: "Grounded answer — every citation is one click from its source."
            }, void 0, false, {
                fileName: "[project]/components/chat/CitationDrawer.tsx",
                lineNumber: 50,
                columnNumber: 4
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/chat/CitationDrawer.tsx",
        lineNumber: 11,
        columnNumber: 3
    }, this);
}
_s(CitationDrawer, "JXMgFesynjTYQC1AzLpArqoa9GU=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"]
    ];
});
_c = CitationDrawer;
var _c;
__turbopack_refresh__.register(_c, "CitationDrawer");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/ui/button.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "Button": (()=>Button)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$clsx$40$2$2e$1$2e$1$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/clsx@2.1.1/node_modules/clsx/dist/clsx.mjs [app-client] (ecmascript)");
;
;
function Button({ variant = "primary", className, ...rest }) {
    const styles = {
        primary: "bg-[var(--primary-solid)] text-[var(--primary-foreground)] hover:opacity-90",
        secondary: "bg-[var(--surface-elevated)] text-[var(--foreground)] hover:opacity-90",
        danger: "bg-[var(--error)] text-white hover:opacity-90",
        ghost: "bg-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$clsx$40$2$2e$1$2e$1$2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["clsx"])("rounded-[10px] px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50", styles[variant], className),
        ...rest
    }, void 0, false, {
        fileName: "[project]/components/ui/button.tsx",
        lineNumber: 19,
        columnNumber: 3
    }, this);
}
_c = Button;
var _c;
__turbopack_refresh__.register(_c, "Button");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/chat/ErrorCard.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "ErrorCard": (()=>ErrorCard)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/ui/button.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$circle$2d$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__CircleX$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/circle-x.js [app-client] (ecmascript) <export default as CircleX>");
"use client";
;
;
;
function ErrorCard({ message, retryable, onRetry, onContinue }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        role: "alert",
        className: "rounded-[10px] border border-[var(--error)] bg-[var(--surface)] p-4",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-2 font-medium",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$circle$2d$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__CircleX$3e$__["CircleX"], {
                        size: 16,
                        "aria-hidden": true
                    }, void 0, false, {
                        fileName: "[project]/components/chat/ErrorCard.tsx",
                        lineNumber: 20,
                        columnNumber: 5
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        children: "Supervisor error"
                    }, void 0, false, {
                        fileName: "[project]/components/chat/ErrorCard.tsx",
                        lineNumber: 21,
                        columnNumber: 5
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/ErrorCard.tsx",
                lineNumber: 19,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: "mt-1 text-sm text-[var(--muted-foreground)]",
                children: message
            }, void 0, false, {
                fileName: "[project]/components/chat/ErrorCard.tsx",
                lineNumber: 23,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-2 flex gap-2",
                children: [
                    retryable && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
                        onClick: onRetry,
                        children: "Retry"
                    }, void 0, false, {
                        fileName: "[project]/components/chat/ErrorCard.tsx",
                        lineNumber: 25,
                        columnNumber: 19
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
                        variant: "secondary",
                        onClick: onContinue,
                        children: "Continue without"
                    }, void 0, false, {
                        fileName: "[project]/components/chat/ErrorCard.tsx",
                        lineNumber: 26,
                        columnNumber: 5
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/chat/ErrorCard.tsx",
                lineNumber: 24,
                columnNumber: 4
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/chat/ErrorCard.tsx",
        lineNumber: 15,
        columnNumber: 3
    }, this);
}
_c = ErrorCard;
var _c;
__turbopack_refresh__.register(_c, "ErrorCard");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/modals/ConfirmationModal.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "ConfirmationModal": (()=>ConfirmationModal),
    "previewTools": (()=>previewTools)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/ui/button.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$react$2d$hook$2d$form$40$7$2e$89$2e$0_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$react$2d$hook$2d$form$2f$dist$2f$index$2e$esm$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/react-hook-form@7.89.0_@types+react@19.3.0_react@19.0.0/node_modules/react-hook-form/dist/index.esm.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zod$40$3$2e$25$2e$76$2f$node_modules$2f$zod$2f$v3$2f$external$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__$2a$__as__z$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/zod@3.25.76/node_modules/zod/v3/external.js [app-client] (ecmascript) <export * as z>");
;
var _s = __turbopack_refresh__.signature();
"use client";
;
;
;
;
const schema = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zod$40$3$2e$25$2e$76$2f$node_modules$2f$zod$2f$v3$2f$external$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__$2a$__as__z$3e$__["z"].object({
    acknowledged: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$zod$40$3$2e$25$2e$76$2f$node_modules$2f$zod$2f$v3$2f$external$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__$2a$__as__z$3e$__["z"].literal(true)
});
function previewTools(interrupt) {
    const raw = interrupt.payload.payload_preview;
    if (!Array.isArray(raw)) return [];
    const tools = [];
    for (const item of raw){
        if (item !== null && typeof item === "object" && "tool" in item) {
            const tool = item.tool;
            if (typeof tool === "string") tools.push(tool);
        }
    }
    return tools;
}
function isEmailGate(interrupt) {
    const blob = previewTools(interrupt).join(" ");
    return interrupt.kind.includes("email") || interrupt.kind.includes("send") || interrupt.agent.includes("gmail") || blob.includes("gmail_send_message");
}
function isCalendarGate(interrupt) {
    const blob = previewTools(interrupt).join(" ");
    return interrupt.kind.includes("calendar") || interrupt.kind.includes("event") || blob.includes("calendar_");
}
function isGitHubGate(interrupt) {
    const blob = previewTools(interrupt).join(" ");
    return interrupt.kind.includes("github") || blob.includes("github_");
}
function ConfirmationModal({ interrupt, busy, onConfirm, onCancel, onRollback }) {
    _s();
    const { register, watch } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$react$2d$hook$2d$form$40$7$2e$89$2e$0_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$react$2d$hook$2d$form$2f$dist$2f$index$2e$esm$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useForm"])({
        defaultValues: {
            acknowledged: false
        }
    });
    const acknowledged = watch("acknowledged");
    const acknowledgedParsed = schema.safeParse({
        acknowledged
    }).success;
    const dialogRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const [entries] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        "ConfirmationModal.useState": ()=>Object.entries(interrupt.payload)
    }["ConfirmationModal.useState"]);
    const showRollback = isEmailGate(interrupt) || interrupt.kind === "2" || interrupt.kind.includes("gate");
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ConfirmationModal.useEffect": ()=>{
            const first = dialogRef.current?.querySelector("button, input");
            first?.focus();
            const onKey = {
                "ConfirmationModal.useEffect.onKey": (e)=>{
                    if (e.key === "Escape") onCancel();
                }
            }["ConfirmationModal.useEffect.onKey"];
            window.addEventListener("keydown", onKey);
            return ({
                "ConfirmationModal.useEffect": ()=>window.removeEventListener("keydown", onKey)
            })["ConfirmationModal.useEffect"];
        }
    }["ConfirmationModal.useEffect"], [
        onCancel
    ]);
    const title = isCalendarGate(interrupt) ? "Confirm calendar event" : isEmailGate(interrupt) ? "Confirm email send" : isGitHubGate(interrupt) ? "Confirm GitHub write" : "Confirm action";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "fixed inset-0 z-50 flex items-center justify-center bg-black/60",
        role: "presentation",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            ref: dialogRef,
            role: "alertdialog",
            "aria-modal": "true",
            "aria-label": title,
            className: "w-full max-w-lg rounded-[14px] border border-[var(--border)] bg-[var(--surface)] p-5",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex items-center justify-between",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                            className: "text-base font-medium",
                            children: title
                        }, void 0, false, {
                            fileName: "[project]/components/modals/ConfirmationModal.tsx",
                            lineNumber: 110,
                            columnNumber: 6
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: onCancel,
                            "aria-label": "Close confirmation",
                            className: "rounded p-1 text-[var(--muted-foreground)]",
                            children: "✕"
                        }, void 0, false, {
                            fileName: "[project]/components/modals/ConfirmationModal.tsx",
                            lineNumber: 111,
                            columnNumber: 6
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/modals/ConfirmationModal.tsx",
                    lineNumber: 109,
                    columnNumber: 5
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dl", {
                    className: "mt-3 space-y-1 text-sm",
                    children: entries.map(([key, value])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex gap-2",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dt", {
                                    className: "w-28 shrink-0 text-[var(--muted-foreground)]",
                                    children: key
                                }, void 0, false, {
                                    fileName: "[project]/components/modals/ConfirmationModal.tsx",
                                    lineNumber: 123,
                                    columnNumber: 8
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("dd", {
                                    className: "min-w-0 flex-1 break-words font-mono text-xs",
                                    children: typeof value === "string" ? value : JSON.stringify(value)
                                }, void 0, false, {
                                    fileName: "[project]/components/modals/ConfirmationModal.tsx",
                                    lineNumber: 126,
                                    columnNumber: 8
                                }, this)
                            ]
                        }, key, true, {
                            fileName: "[project]/components/modals/ConfirmationModal.tsx",
                            lineNumber: 122,
                            columnNumber: 7
                        }, this))
                }, void 0, false, {
                    fileName: "[project]/components/modals/ConfirmationModal.tsx",
                    lineNumber: 120,
                    columnNumber: 5
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                    className: "mt-3 flex items-center gap-2 text-sm",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                            type: "checkbox",
                            ...register("acknowledged")
                        }, void 0, false, {
                            fileName: "[project]/components/modals/ConfirmationModal.tsx",
                            lineNumber: 133,
                            columnNumber: 6
                        }, this),
                        "I reviewed the payload above"
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/modals/ConfirmationModal.tsx",
                    lineNumber: 132,
                    columnNumber: 5
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "mt-4 flex justify-end gap-2",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
                            variant: "secondary",
                            onClick: onCancel,
                            disabled: busy,
                            children: "Cancel"
                        }, void 0, false, {
                            fileName: "[project]/components/modals/ConfirmationModal.tsx",
                            lineNumber: 137,
                            columnNumber: 6
                        }, this),
                        showRollback && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
                            variant: "danger",
                            onClick: onRollback,
                            disabled: busy || !acknowledgedParsed,
                            children: "Rollback event"
                        }, void 0, false, {
                            fileName: "[project]/components/modals/ConfirmationModal.tsx",
                            lineNumber: 141,
                            columnNumber: 7
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
                            onClick: onConfirm,
                            disabled: busy || !acknowledgedParsed,
                            children: busy ? "Working…" : title.includes("email") ? "Confirm & send" : "Confirm & create"
                        }, void 0, false, {
                            fileName: "[project]/components/modals/ConfirmationModal.tsx",
                            lineNumber: 149,
                            columnNumber: 6
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/modals/ConfirmationModal.tsx",
                    lineNumber: 136,
                    columnNumber: 5
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/modals/ConfirmationModal.tsx",
            lineNumber: 102,
            columnNumber: 4
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/modals/ConfirmationModal.tsx",
        lineNumber: 98,
        columnNumber: 3
    }, this);
}
_s(ConfirmationModal, "vyZsS7nj/4ksk+Q4p3euP4pXWhw=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$react$2d$hook$2d$form$40$7$2e$89$2e$0_$40$types$2b$react$40$19$2e$3$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$react$2d$hook$2d$form$2f$dist$2f$index$2e$esm$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useForm"]
    ];
});
_c = ConfirmationModal;
var _c;
__turbopack_refresh__.register(_c, "ConfirmationModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/shell/ModePill.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "ModePill": (()=>ModePill)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$badge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/ui/badge.tsx [app-client] (ecmascript)");
"use client";
;
;
function ModePill({ mode }) {
    const tone = mode === "live" ? "live" : mode === "free" ? "free" : "demo";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
        "aria-label": `Mode: ${mode}`,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$badge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Badge"], {
            tone: tone,
            children: [
                "Mode: ",
                mode
            ]
        }, void 0, true, {
            fileName: "[project]/components/shell/ModePill.tsx",
            lineNumber: 13,
            columnNumber: 4
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/shell/ModePill.tsx",
        lineNumber: 12,
        columnNumber: 3
    }, this);
}
_c = ModePill;
var _c;
__turbopack_refresh__.register(_c, "ModePill");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/shell/Sidebar.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "Sidebar": (()=>Sidebar)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$shell$2f$ModePill$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/shell/ModePill.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/ui/button.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/stores/ui.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$panel$2d$left$2d$close$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PanelLeftClose$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/panel-left-close.js [app-client] (ecmascript) <export default as PanelLeftClose>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$panel$2d$left$2d$open$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PanelLeftOpen$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/panel-left-open.js [app-client] (ecmascript) <export default as PanelLeftOpen>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$message$2d$square$2d$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MessageSquarePlus$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/message-square-plus.js [app-client] (ecmascript) <export default as MessageSquarePlus>");
;
var _s = __turbopack_refresh__.signature();
"use client";
;
;
;
;
;
;
function groupLabel(createdAt) {
    if (createdAt === undefined) return "Older";
    const created = new Date(createdAt).getTime();
    const now = Date.now();
    const day = 86_400_000;
    if (now - created < day) return "Today";
    if (now - created < 2 * day) return "Yesterday";
    if (now - created < 7 * day) return "This week";
    return "Older";
}
function Sidebar({ mode, threads, activeThreadId, onNewChat }) {
    _s();
    const { sidebarCollapsed, toggleSidebar } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"])();
    const [filter, setFilter] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const visible = threads.filter((t)=>t.thread_id.toLowerCase().includes(filter.toLowerCase()));
    const groups = new Map();
    for (const t of visible){
        const label = groupLabel(t.created_at);
        const list = groups.get(label) ?? [];
        list.push(t);
        groups.set(label, list);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
        className: sidebarCollapsed ? "w-14" : "w-64",
        "aria-label": "Threads sidebar",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex h-full flex-col gap-2 border-r border-[var(--border)] bg-[var(--surface)] p-2",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex items-center justify-between gap-2",
                    children: [
                        !sidebarCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$shell$2f$ModePill$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ModePill"], {
                            mode: mode
                        }, void 0, false, {
                            fileName: "[project]/components/shell/Sidebar.tsx",
                            lineNumber: 54,
                            columnNumber: 28
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: toggleSidebar,
                            "aria-label": sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar",
                            className: "rounded p-1 text-[var(--muted-foreground)] hover:text-[var(--foreground)]",
                            children: sidebarCollapsed ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$panel$2d$left$2d$open$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PanelLeftOpen$3e$__["PanelLeftOpen"], {
                                size: 18
                            }, void 0, false, {
                                fileName: "[project]/components/shell/Sidebar.tsx",
                                lineNumber: 64,
                                columnNumber: 8
                            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$panel$2d$left$2d$close$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PanelLeftClose$3e$__["PanelLeftClose"], {
                                size: 18
                            }, void 0, false, {
                                fileName: "[project]/components/shell/Sidebar.tsx",
                                lineNumber: 66,
                                columnNumber: 8
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/components/shell/Sidebar.tsx",
                            lineNumber: 55,
                            columnNumber: 6
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/shell/Sidebar.tsx",
                    lineNumber: 53,
                    columnNumber: 5
                }, this),
                !sidebarCollapsed && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Button"], {
                            onClick: onNewChat,
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "inline-flex items-center gap-2",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$message$2d$square$2d$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MessageSquarePlus$3e$__["MessageSquarePlus"], {
                                        size: 16,
                                        "aria-hidden": true
                                    }, void 0, false, {
                                        fileName: "[project]/components/shell/Sidebar.tsx",
                                        lineNumber: 74,
                                        columnNumber: 9
                                    }, this),
                                    " New chat"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/shell/Sidebar.tsx",
                                lineNumber: 73,
                                columnNumber: 8
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/components/shell/Sidebar.tsx",
                            lineNumber: 72,
                            columnNumber: 7
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                            value: filter,
                            onChange: (e)=>setFilter(e.target.value),
                            placeholder: "Search threads",
                            "aria-label": "Search threads",
                            className: "rounded-[6px] border border-[var(--border)] bg-[var(--background)] px-2 py-1 text-sm"
                        }, void 0, false, {
                            fileName: "[project]/components/shell/Sidebar.tsx",
                            lineNumber: 77,
                            columnNumber: 7
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                            className: "flex-1 overflow-y-auto",
                            "aria-label": "Thread list",
                            children: [
                                [
                                    ...groups.entries()
                                ].map(([label, items])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        className: "mt-2",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "px-2 text-xs uppercase text-[var(--muted-foreground)]",
                                                children: label
                                            }, void 0, false, {
                                                fileName: "[project]/components/shell/Sidebar.tsx",
                                                lineNumber: 87,
                                                columnNumber: 10
                                            }, this),
                                            items.map((t)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                                    href: `/chat/${encodeURIComponent(t.thread_id)}`,
                                                    "aria-current": t.thread_id === activeThreadId ? "page" : undefined,
                                                    className: t.thread_id === activeThreadId ? "block rounded px-2 py-1 text-sm bg-[var(--surface-elevated)]" : "block rounded px-2 py-1 text-sm hover:bg-[var(--surface-elevated)]",
                                                    children: t.thread_id
                                                }, t.thread_id, false, {
                                                    fileName: "[project]/components/shell/Sidebar.tsx",
                                                    lineNumber: 91,
                                                    columnNumber: 11
                                                }, this))
                                        ]
                                    }, label, true, {
                                        fileName: "[project]/components/shell/Sidebar.tsx",
                                        lineNumber: 86,
                                        columnNumber: 9
                                    }, this)),
                                visible.length === 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "px-2 text-sm text-[var(--muted-foreground)]",
                                    children: "No threads yet."
                                }, void 0, false, {
                                    fileName: "[project]/components/shell/Sidebar.tsx",
                                    lineNumber: 109,
                                    columnNumber: 9
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/shell/Sidebar.tsx",
                            lineNumber: 84,
                            columnNumber: 7
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "border-t border-[var(--border)] pt-2 text-xs text-[var(--muted-foreground)]",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                    href: "/settings",
                                    className: "underline",
                                    children: "Settings"
                                }, void 0, false, {
                                    fileName: "[project]/components/shell/Sidebar.tsx",
                                    lineNumber: 115,
                                    columnNumber: 8
                                }, this),
                                " · ",
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                                    href: "/health",
                                    className: "underline",
                                    children: "Health"
                                }, void 0, false, {
                                    fileName: "[project]/components/shell/Sidebar.tsx",
                                    lineNumber: 119,
                                    columnNumber: 8
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/shell/Sidebar.tsx",
                            lineNumber: 114,
                            columnNumber: 7
                        }, this)
                    ]
                }, void 0, true)
            ]
        }, void 0, true, {
            fileName: "[project]/components/shell/Sidebar.tsx",
            lineNumber: 52,
            columnNumber: 4
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/shell/Sidebar.tsx",
        lineNumber: 48,
        columnNumber: 3
    }, this);
}
_s(Sidebar, "kkS211YMZOA9qRrBHSNZDIRiq/0=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$ui$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useUIStore"]
    ];
});
_c = Sidebar;
var _c;
__turbopack_refresh__.register(_c, "Sidebar");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/shell/AppShell.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "AppShell": (()=>AppShell)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$shell$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/shell/Sidebar.tsx [app-client] (ecmascript)");
"use client";
;
;
function AppShell({ mode, threads, activeThreadId, onNewChat, children }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex h-screen",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$shell$2f$Sidebar$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Sidebar"], {
                mode: mode,
                threads: threads,
                activeThreadId: activeThreadId,
                onNewChat: onNewChat
            }, void 0, false, {
                fileName: "[project]/components/shell/AppShell.tsx",
                lineNumber: 22,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                className: "flex min-w-0 flex-1 flex-col",
                children: children
            }, void 0, false, {
                fileName: "[project]/components/shell/AppShell.tsx",
                lineNumber: 28,
                columnNumber: 4
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/shell/AppShell.tsx",
        lineNumber: 21,
        columnNumber: 3
    }, this);
}
_c = AppShell;
var _c;
__turbopack_refresh__.register(_c, "AppShell");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/components/shell/DowngradeBanner.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "DowngradeBanner": (()=>DowngradeBanner)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/client/app-dir/link.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__TriangleAlert$3e$__ = __turbopack_import__("[project]/node_modules/.pnpm/lucide-react@0.454.0_react@19.0.0/node_modules/lucide-react/dist/esm/icons/triangle-alert.js [app-client] (ecmascript) <export default as TriangleAlert>");
"use client";
;
;
;
function DowngradeBanner({ mode, downgrades }) {
    if (downgrades.length === 0) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("output", {
        "aria-live": "polite",
        className: "block rounded-[10px] border border-[var(--warning)] bg-[var(--surface-elevated)] p-3 text-sm",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center gap-2 font-medium",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$lucide$2d$react$40$0$2e$454$2e$0_react$40$19$2e$0$2e$0$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$triangle$2d$alert$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__TriangleAlert$3e$__["TriangleAlert"], {
                        size: 16,
                        "aria-hidden": true
                    }, void 0, false, {
                        fileName: "[project]/components/shell/DowngradeBanner.tsx",
                        lineNumber: 20,
                        columnNumber: 5
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        children: [
                            "Running in ",
                            mode.toUpperCase(),
                            " mode"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/shell/DowngradeBanner.tsx",
                        lineNumber: 21,
                        columnNumber: 5
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/shell/DowngradeBanner.tsx",
                lineNumber: 19,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("ul", {
                className: "mt-1 list-disc pl-6 text-[var(--muted-foreground)]",
                children: downgrades.map((reason)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                        children: reason
                    }, reason, false, {
                        fileName: "[project]/components/shell/DowngradeBanner.tsx",
                        lineNumber: 25,
                        columnNumber: 6
                    }, this))
            }, void 0, false, {
                fileName: "[project]/components/shell/DowngradeBanner.tsx",
                lineNumber: 23,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                href: "/settings",
                className: "mt-1 inline-block text-[var(--primary)] underline",
                children: "Configure credentials"
            }, void 0, false, {
                fileName: "[project]/components/shell/DowngradeBanner.tsx",
                lineNumber: 28,
                columnNumber: 4
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/shell/DowngradeBanner.tsx",
        lineNumber: 15,
        columnNumber: 3
    }, this);
}
_c = DowngradeBanner;
var _c;
__turbopack_refresh__.register(_c, "DowngradeBanner");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/lib/api/client.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "createThread": (()=>createThread),
    "fetchHealth": (()=>fetchHealth),
    "invokeThread": (()=>invokeThread),
    "listThreads": (()=>listThreads),
    "loadThread": (()=>loadThread),
    "resumeThread": (()=>resumeThread),
    "triggerIngest": (()=>triggerIngest)
});
async function request(path, init) {
    const res = await fetch(path, {
        ...init,
        headers: {
            "Content-Type": "application/json",
            ...init?.headers ?? {}
        }
    });
    if (!res.ok) {
        const body = await res.text().catch(()=>"");
        throw new Error(`${init?.method ?? "GET"} ${path} → ${res.status}: ${body}`);
    }
    return await res.json();
}
function fetchHealth() {
    return request("/api/health");
}
function createThread() {
    return request("/api/threads", {
        method: "POST"
    });
}
function listThreads() {
    return request("/api/threads");
}
function loadThread(threadId) {
    return request(`/api/threads/${encodeURIComponent(threadId)}`);
}
function invokeThread(threadId, message) {
    return request(`/api/threads/${encodeURIComponent(threadId)}/invoke`, {
        method: "POST",
        body: JSON.stringify({
            message
        })
    });
}
function resumeThread(threadId, body) {
    return request(`/api/threads/${encodeURIComponent(threadId)}/resume`, {
        method: "POST",
        body: JSON.stringify(body)
    });
}
function triggerIngest(path) {
    return request("/api/ingest", {
        method: "POST",
        body: JSON.stringify(path ? {
            path
        } : {})
    });
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/lib/sse/parser.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "KNOWN_SSE_EVENTS": (()=>KNOWN_SSE_EVENTS),
    "isKnownSSEEvent": (()=>isKnownSSEEvent),
    "parseSSEBlock": (()=>parseSSEBlock),
    "splitSSEBuffer": (()=>splitSSEBuffer)
});
function parseSSEBlock(block) {
    let event = null;
    const dataLines = [];
    for (const line of block.split("\n")){
        if (line.startsWith("event:")) {
            event = line.slice("event:".length).trim();
        } else if (line.startsWith("data:")) {
            dataLines.push(line.slice("data:".length).trimStart());
        }
    }
    if (event === null) return null;
    const raw = dataLines.join("\n");
    let data = {};
    if (raw.length > 0) {
        try {
            const parsed = JSON.parse(raw);
            if (parsed !== null && typeof parsed === "object" && !Array.isArray(parsed)) {
                data = parsed;
            }
        } catch  {
            data = {};
        }
    }
    return {
        kind: event,
        data
    };
}
function splitSSEBuffer(buffer) {
    const parts = buffer.split("\n\n");
    const remainder = parts.pop() ?? "";
    const events = [];
    for (const part of parts){
        const trimmed = part.trim();
        if (trimmed.length === 0) continue;
        const evt = parseSSEBlock(trimmed);
        if (evt !== null) events.push(evt);
    }
    return [
        events,
        remainder
    ];
}
const KNOWN_SSE_EVENTS = new Set([
    "routing",
    "agent_start",
    "agent_token",
    "agent_tool",
    "agent_end",
    "interrupt",
    "aggregate",
    "error",
    "done"
]);
function isKnownSSEEvent(kind) {
    return KNOWN_SSE_EVENTS.has(kind);
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/lib/hooks/useChatStream.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "useChatStream": (()=>useChatStream)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$sse$2f$parser$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/sse/parser.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/stores/thread.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var _s = __turbopack_refresh__.signature();
"use client";
;
;
;
function asString(value) {
    return typeof value === "string" ? value : "";
}
function asStringArray(value) {
    return Array.isArray(value) ? value.filter((v)=>typeof v === "string") : [];
}
function asStructured(value) {
    if (value === null || typeof value !== "object" || Array.isArray(value)) return undefined;
    return value;
}
function asCitations(value) {
    if (!Array.isArray(value)) return undefined;
    const out = [];
    for (const item of value){
        if (item !== null && typeof item === "object" && "source" in item && "page" in item) {
            const rec = item;
            const source = rec.source;
            const page = rec.page;
            if (typeof source === "string" && typeof page === "number") out.push(item);
        }
    }
    return out;
}
function useChatStream() {
    _s();
    const abortRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const stop = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useChatStream.useCallback[stop]": ()=>{
            abortRef.current?.abort();
            abortRef.current = null;
            __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState().setConnected(false);
        }
    }["useChatStream.useCallback[stop]"], []);
    const send = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useChatStream.useCallback[send]": async (threadId, message, cb)=>{
            stop();
            const store = __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState();
            store.pushUser(message);
            store.setAggregate("");
            store.setInterrupt(null);
            const controller = new AbortController();
            abortRef.current = controller;
            store.setConnected(true);
            let reconnects = 0;
            const url = `/api/threads/${encodeURIComponent(threadId)}/stream`;
            while(reconnects <= 3){
                try {
                    const res = await fetch(url, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            message
                        }),
                        signal: controller.signal
                    });
                    if (!res.ok || res.body === null) throw new Error(`stream ${res.status}`);
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = "";
                    for(;;){
                        const { done, value } = await reader.read();
                        if (done) break;
                        buffer += decoder.decode(value, {
                            stream: true
                        });
                        const [events, remainder] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$sse$2f$parser$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["splitSSEBuffer"])(buffer);
                        buffer = remainder;
                        const live = __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState();
                        for (const evt of events){
                            if (!(0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$sse$2f$parser$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["isKnownSSEEvent"])(evt.kind)) continue; // log-and-ignore unknown
                            switch(evt.kind){
                                case "routing":
                                    {
                                        const agents = asStringArray(evt.data.agents);
                                        live.applyRouting(agents, asString(evt.data.reasoning));
                                        live.startAgents(agents);
                                        break;
                                    }
                                case "agent_start":
                                    {
                                        const agent = asString(evt.data.agent);
                                        if (agent) live.startAgents([
                                            agent
                                        ]);
                                        break;
                                    }
                                case "agent_token":
                                    {
                                        const agent = asString(evt.data.agent);
                                        const delta = asString(evt.data.delta);
                                        if (agent) live.appendToken(agent, delta);
                                        break;
                                    }
                                case "agent_tool":
                                    {
                                        const agent = asString(evt.data.agent);
                                        const tool = asString(evt.data.tool);
                                        const status = asString(evt.data.status) || "ok";
                                        if (agent && tool) live.applyTool(agent, tool, status);
                                        break;
                                    }
                                case "agent_end":
                                    {
                                        const agent = asString(evt.data.agent);
                                        const status = asString(evt.data.status) || "ok";
                                        if (agent) {
                                            const citations = asCitations(evt.data.citations);
                                            const structured = asStructured(evt.data.structured);
                                            if (citations !== undefined || structured !== undefined) {
                                                const outputs = {
                                                    [agent]: {
                                                        agent,
                                                        status,
                                                        answer: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState().agentViews[agent]?.answer ?? "",
                                                        citations,
                                                        structured
                                                    }
                                                };
                                                live.applyOutputs(outputs);
                                            }
                                            live.endAgent(agent, status);
                                        }
                                        break;
                                    }
                                case "interrupt":
                                    {
                                        const agent = asString(evt.data.agent) || "google_agent";
                                        const kind = asString(evt.data.kind) || "confirm";
                                        const payload = evt.data.payload !== null && typeof evt.data.payload === "object" && !Array.isArray(evt.data.payload) ? evt.data.payload : evt.data;
                                        live.setInterrupt({
                                            agent,
                                            kind,
                                            payload
                                        });
                                        live.setAggregate("confirmation_required");
                                        cb?.onInterrupt?.();
                                        break;
                                    }
                                case "aggregate":
                                    {
                                        live.setAggregate(asString(evt.data.status) || "ok");
                                        break;
                                    }
                                case "error":
                                    {
                                        live.setAggregate("error");
                                        break;
                                    }
                                case "done":
                                    {
                                        break;
                                    }
                            }
                        }
                    }
                    // Reconcile with authoritative non-streaming state (citations/ids preserved).
                    try {
                        const full = await (await fetch(`/api/threads/${encodeURIComponent(threadId)}`)).json();
                        const outputs = full.agent_outputs;
                        if (outputs !== undefined) __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState().applyOutputs(outputs);
                        const pending = full.pending_interrupt;
                        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState().setInterrupt(pending ?? null);
                        const status = full.status;
                        if (typeof status === "string" && status) __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState().setAggregate(status);
                    } catch  {
                    // Keep streamed partials; reconnect chip stays honest via `connected`.
                    }
                    cb?.onDone?.();
                    return;
                } catch (err) {
                    if (controller.signal.aborted) return;
                    reconnects += 1;
                    if (reconnects > 3) {
                        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState().setAggregate("error");
                        return;
                    }
                    await new Promise({
                        "useChatStream.useCallback[send]": (r)=>setTimeout(r, 500 * reconnects)
                    }["useChatStream.useCallback[send]"]);
                }
            }
        }
    }["useChatStream.useCallback[send]"], [
        stop
    ]);
    return {
        send,
        stop
    };
}
_s(useChatStream, "U0vc+uvQhSjb+jpXG8OSSOv8/nw=");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/lib/hooks/useHealth.ts [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "useHealth": (()=>useHealth)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/api/client.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f40$tanstack$2b$react$2d$query$40$5$2e$104$2e$1_react$40$19$2e$0$2e$0$2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/@tanstack+react-query@5.104.1_react@19.0.0/node_modules/@tanstack/react-query/build/modern/useQuery.js [app-client] (ecmascript)");
var _s = __turbopack_refresh__.signature();
"use client";
;
;
function useHealth(refetchInterval = 15_000) {
    _s();
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f40$tanstack$2b$react$2d$query$40$5$2e$104$2e$1_react$40$19$2e$0$2e$0$2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            "health"
        ],
        queryFn: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["fetchHealth"],
        refetchInterval
    });
}
_s(useHealth, "4ZpngI1uv+Uo3WQHEZmTQ5FNM+k=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f40$tanstack$2b$react$2d$query$40$5$2e$104$2e$1_react$40$19$2e$0$2e$0$2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQuery"]
    ];
});
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/app/chat/[threadId]/page.tsx [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, k: __turbopack_refresh__, m: module, z: __turbopack_require_stub__ } = __turbopack_context__;
{
__turbopack_esm__({
    "default": (()=>ThreadPage)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$ChatView$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/ChatView.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$CitationDrawer$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/CitationDrawer.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$ErrorCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/chat/ErrorCard.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$modals$2f$ConfirmationModal$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/modals/ConfirmationModal.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$shell$2f$AppShell$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/shell/AppShell.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$shell$2f$DowngradeBanner$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/components/shell/DowngradeBanner.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/api/client.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$hooks$2f$useChatStream$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/hooks/useChatStream.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$hooks$2f$useHealth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/hooks/useHealth.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/lib/stores/thread.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/next@15.1.6_@babel+core@7.2_cfb1502737cfe2ba051be860d32ee190/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f40$tanstack$2b$react$2d$query$40$5$2e$104$2e$1_react$40$19$2e$0$2e$0$2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_import__("[project]/node_modules/.pnpm/@tanstack+react-query@5.104.1_react@19.0.0/node_modules/@tanstack/react-query/build/modern/useQuery.js [app-client] (ecmascript)");
;
var _s = __turbopack_refresh__.signature();
"use client";
;
;
;
;
;
;
;
;
;
;
;
;
;
function ThreadPage() {
    _s();
    const params = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useParams"])();
    const threadId = decodeURIComponent(params.threadId);
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const health = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$hooks$2f$useHealth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useHealth"])();
    const threads = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f40$tanstack$2b$react$2d$query$40$5$2e$104$2e$1_react$40$19$2e$0$2e$0$2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            "threads"
        ],
        queryFn: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["listThreads"]
    });
    const { send, stop } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$hooks$2f$useChatStream$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useChatStream"])();
    const [sending, setSending] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [resuming, setResuming] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const pendingInterrupt = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"])({
        "ThreadPage.useThreadStore[pendingInterrupt]": (s)=>s.pendingInterrupt
    }["ThreadPage.useThreadStore[pendingInterrupt]"]);
    const overallStatus = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"])({
        "ThreadPage.useThreadStore[overallStatus]": (s)=>s.overallStatus
    }["ThreadPage.useThreadStore[overallStatus]"]);
    const storeMessages = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"])({
        "ThreadPage.useThreadStore[storeMessages]": (s)=>s.messages
    }["ThreadPage.useThreadStore[storeMessages]"]);
    const mode = typeof health.data?.mode === "string" ? health.data.mode : "demo";
    const lastUserMessage = [
        ...storeMessages
    ].reverse().find((m)=>m.role === "user")?.content;
    // Mount-time hydration must never clobber a live stream: the backend
    // answers fresh threads with an empty "ok" snapshot, which can resolve
    // after stream events and wipe cards. Apply only while still pristine.
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ThreadPage.useEffect": ()=>{
            let cancelled = false;
            const store = __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState();
            if (store.threadId !== threadId) store.setThread(threadId);
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["loadThread"])(threadId).then({
                "ThreadPage.useEffect": (full)=>{
                    if (cancelled) return;
                    const live = __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState();
                    if (live.threadId !== threadId) return;
                    if (live.messages.length > 0) return;
                    live.applyRouting(full.agents, "");
                    live.applyOutputs(full.agent_outputs);
                    live.setInterrupt(full.pending_interrupt);
                    live.setAggregate(full.status);
                }
            }["ThreadPage.useEffect"]).catch({
                "ThreadPage.useEffect": ()=>undefined
            }["ThreadPage.useEffect"]);
            return ({
                "ThreadPage.useEffect": ()=>{
                    cancelled = true;
                    stop();
                }
            })["ThreadPage.useEffect"];
        }
    }["ThreadPage.useEffect"], [
        threadId,
        stop
    ]);
    const onSend = async (message)=>{
        setSending(true);
        try {
            await send(threadId, message);
        } finally{
            setSending(false);
        }
    };
    const doResume = async (body)=>{
        setResuming(true);
        try {
            const full = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["resumeThread"])(threadId, body);
            const store = __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState();
            store.applyOutputs(full.agent_outputs);
            store.setInterrupt(full.pending_interrupt);
            store.setAggregate(full.status);
        } finally{
            setResuming(false);
        }
    };
    const onNewChat = async ()=>{
        const created = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createThread"])();
        router.push(`/chat/${encodeURIComponent(created.thread_id)}`);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$shell$2f$AppShell$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["AppShell"], {
        mode: mode,
        threads: threads.data?.threads ?? [],
        activeThreadId: threadId,
        onNewChat: onNewChat,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex items-center justify-between border-b border-[var(--border)] p-3",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                    className: "font-mono text-sm",
                    children: threadId
                }, void 0, false, {
                    fileName: "[project]/app/chat/[threadId]/page.tsx",
                    lineNumber: 101,
                    columnNumber: 5
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/chat/[threadId]/page.tsx",
                lineNumber: 100,
                columnNumber: 4
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "p-3",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$shell$2f$DowngradeBanner$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DowngradeBanner"], {
                    mode: mode,
                    downgrades: health.data?.downgrades ?? []
                }, void 0, false, {
                    fileName: "[project]/app/chat/[threadId]/page.tsx",
                    lineNumber: 104,
                    columnNumber: 5
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/chat/[threadId]/page.tsx",
                lineNumber: 103,
                columnNumber: 4
            }, this),
            overallStatus === "error" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "px-3",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$ErrorCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ErrorCard"], {
                    message: "The supervisor hit an error. Completed agents are preserved above.",
                    retryable: true,
                    onRetry: ()=>{
                        if (lastUserMessage !== undefined) onSend(lastUserMessage);
                    },
                    onContinue: ()=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"].getState().setAggregate("partial")
                }, void 0, false, {
                    fileName: "[project]/app/chat/[threadId]/page.tsx",
                    lineNumber: 111,
                    columnNumber: 6
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/chat/[threadId]/page.tsx",
                lineNumber: 110,
                columnNumber: 5
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$ChatView$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ChatView"], {
                mode: mode,
                sending: sending || resuming,
                onSend: onSend,
                onVerifyPartial: ()=>undefined
            }, void 0, false, {
                fileName: "[project]/app/chat/[threadId]/page.tsx",
                lineNumber: 121,
                columnNumber: 4
            }, this),
            pendingInterrupt !== null && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$modals$2f$ConfirmationModal$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ConfirmationModal"], {
                interrupt: pendingInterrupt,
                busy: resuming,
                onConfirm: ()=>doResume({
                        confirm: true
                    }),
                onCancel: ()=>doResume({
                        confirm: false
                    }),
                onRollback: ()=>doResume({
                        rollback: true
                    })
            }, void 0, false, {
                fileName: "[project]/app/chat/[threadId]/page.tsx",
                lineNumber: 128,
                columnNumber: 5
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$chat$2f$CitationDrawer$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["CitationDrawer"], {}, void 0, false, {
                fileName: "[project]/app/chat/[threadId]/page.tsx",
                lineNumber: 136,
                columnNumber: 4
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/chat/[threadId]/page.tsx",
        lineNumber: 94,
        columnNumber: 3
    }, this);
}
_s(ThreadPage, "gH+/ZQ9h2hTyRq2/K15Mk9Qqxts=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useParams"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$15$2e$1$2e$6_$40$babel$2b$core$40$7$2e$2_cfb1502737cfe2ba051be860d32ee190$2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$hooks$2f$useHealth$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useHealth"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f40$tanstack$2b$react$2d$query$40$5$2e$104$2e$1_react$40$19$2e$0$2e$0$2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQuery"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$hooks$2f$useChatStream$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useChatStream"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$stores$2f$thread$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useThreadStore"]
    ];
});
_c = ThreadPage;
var _c;
__turbopack_refresh__.register(_c, "ThreadPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_refresh__.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/app/chat/[threadId]/page.tsx [app-rsc] (ecmascript, Next.js server component, client modules)": ((__turbopack_context__) => {

var { r: __turbopack_require__, f: __turbopack_module_context__, i: __turbopack_import__, s: __turbopack_esm__, v: __turbopack_export_value__, n: __turbopack_export_namespace__, c: __turbopack_cache__, M: __turbopack_modules__, l: __turbopack_load__, j: __turbopack_dynamic__, P: __turbopack_resolve_absolute_path__, U: __turbopack_relative_url__, R: __turbopack_resolve_module_id_path__, b: __turbopack_worker_blob_url__, g: global, __dirname, t: __turbopack_require_real__ } = __turbopack_context__;
{
}}),
}]);

//# sourceMappingURL=_cbc5be._.js.map