# Frontend migration — vanilla CSS → shadcn/ui, identity preserved

**Tasks:** [TASKS.md](../TASKS.md) Phase 5 (T027–T035) · **Lane:** `lane:web`
**Owner:** Claude by default ([AGENTS.md](../AGENTS.md) §1 — the `frontend-design` skill only loads
for Claude, and this is precisely a job where the look degrades if several hands re-decide the palette).

Other AIs: you may wire these components to endpoints. Do not restyle them, do not introduce a
colour, and do not hand-roll markup that bypasses the component layer.

---

## The brief in one line

**The look does not change. The implementation does.** Success is a side-by-side screenshot where a
reviewer cannot reliably tell which build is which. This is a re-platforming, not a redesign.

## Why this is a real migration and not a copy-paste

The current `frontend/style.css` is 10 KB of minified, single-line CSS. It declares **7 custom
properties** — and then hardcodes **76 distinct hex values**, nearly all of them used exactly once.
Values like `#8fa190`, `#90a091`, `#90a393`, `#91a392` are four different greys that are visually the
same grey. That is not a token system; it is a pile of one-off decisions that happens to look
coherent because one person made them all in one sitting.

Porting those 76 values forward into Tailwind would carry the mess into a codebase that has to grow
auth screens, settings and repo views. **T029 exists to resolve them into a real scale first** — and
it must happen *before* any component is installed, because once components exist they start
depending on whatever tokens they find.

The shadcn stock zinc/slate theme is the "looks AI-generated" default the `frontend-design` skill
exists to avoid. Treat installed components as **unstyled structure**; the identity below goes on top.

---

## The identity to preserve

### Palette — extracted from the current build

These are the load-bearing values. Everything else in the 76 is a near-duplicate that should collapse
into the nearest step of a proper scale.

| Role | Value | Where it lives today |
| --- | --- | --- |
| Canvas | `#07100d` | `body` background — near-black, green-shifted, *not* neutral |
| Panel | `rgba(12,27,21,.82)` | `--panel`, translucent over the orbs |
| Surface (solid) | `#102018` / `#111e18` / `#0d1912` | buttons, insets — collapse to 2 steps |
| Hairline | `rgba(198,230,203,.13)` | `--line` — every border in the app |
| Text primary | `#e6f1e7` | `--ink` |
| Text muted | `#93a396` | `--muted` |
| **Accent — lime** | `#befb5b` | `--lime`, the signature colour |
| Accent — violet | `#b6a5ff` | `--violet` |
| Accent — orange | `#ffc37c` | `--orange` |
| Orb (lime) | `#a3ff31` | ambient, `blur(90px)`, `opacity:.1` |
| Orb (violet) | `#6956e7` | ambient, second orb |

The greens are the identity: the canvas is not black, it is a very dark green, and the "greys" are
all green-shifted. A port that reaches for Tailwind's neutral scale will look subtly wrong in a way
that is hard to name and impossible to unsee. **Build the greys from the canvas hue.**

Map these to shadcn's semantic slots rather than overriding component-by-component:
`--background`, `--card`, `--popover`, `--border`, `--input`, `--foreground`, `--muted-foreground`,
`--primary` (lime), `--ring` (lime at low alpha). Get the slots right and most components inherit the
identity for free.

### Typography — three faces, three jobs

| Face | Role | Current usage |
| --- | --- | --- |
| **Space Grotesk** | Display — brand, `h1`, `h2` | `600 21px` brand, `500 30px` headings |
| **Manrope** | Body — 400/500/600/700/800 | `body` default |
| **DM Mono** | Utility — eyebrows, labels, metrics, counts | `9px`–`12px`, letterspaced `.08em` |

The mono-for-data-and-labels rule is doing a lot of the work in this design. Keep it strict: if it is
a number, a file name, a token count or a section label, it is DM Mono. Self-host the three faces
rather than keeping the `fonts.googleapis.com` link — two preconnects and a render-blocking
stylesheet is the current cost, and shadcn projects have no reason to pay it.

### Radii — tighter than shadcn's default

Current values: `2, 3, 5, 6, 7, 8, 9px` and `50%`. shadcn ships `0.5rem` (8px) as `--radius` and
derives the rest. **Set `--radius` to `7px`** and define the small steps explicitly — the sharpness
at 3px on badges and bars is part of the look, and letting shadcn derive `sm` from an 8px base
rounds it off.

### Signature elements — do not lose these in the port

1. **The ambient orbs.** Two fixed, 420px, `blur(90px)`, `opacity:.1` — lime top-right, violet
   bottom-left. They sit behind translucent panels, which is why `--panel` has alpha. If panels go
   opaque, the whole atmosphere dies.
2. **The noise overlay.** A fixed inline-SVG `feTurbulence` at `opacity:.04`. Keep it as a data URI;
   do not replace it with an image asset.
3. **The numbered eyebrows** (`01 THE AGENT CONFIG COMPILER`, `02 SOURCES`…). These encode a real
   left-to-right pipeline order, so they earn their place — keep them, and keep them mono.
4. **The `.brand-mark`** — a 27px lime-outlined `L` at 7px radius.
5. **The live dot** — 7px lime circle with a `0 0 12px` lime glow. Signals "workspace intelligence"
   in the nav.

---

## Component mapping

| Today | shadcn | Notes |
| --- | --- | --- |
| `.panel` | `Card` | Must stay translucent — override `bg` with `--panel`, keep the hairline border |
| `.source` (checkbox label) | `Checkbox` + `Label` in a custom row | Selected state is a border/bg shift, not a checkmark |
| `.conflict` | `Card` + `RadioGroup` | Resolution is a radio choice; today it is hand-rolled |
| `.task-tabs` / `.file-tabs` | `Tabs` | Two separate tab groups, same visual treatment |
| `.copy-button` / `.add-button` | `Button` variants | Add `ghost-lime` and `icon-sm` variants via CVA |
| `.dropzone` | Custom + `react-dropzone` | No shadcn primitive; keep the dashed hairline + `⌁` |
| `.status` / `.saved` badges | `Badge` | New variants: `lime`, `violet`, `orange` |
| `<pre id="manifest">` | Custom + syntax highlighting | Currently uses `<mark>` for highlights — preserve that lime-tint treatment |
| `.bar` (compaction meter) | `Progress` | Restyle heavily; the stock look is wrong |
| Auth screens (new) | `Form` + `Input` + `Button` | No existing design — extend the language, don't invent a second one |

---

## Order of work

1. **T027 — closed.** Bundler is **Vite** (decided 2026-07-26, PLAN.md).
2. **T029 first, then T028's components.** Tokens before components, always. Installing shadcn
   components against the stock theme and restyling after is how projects end up with two systems.
3. Port shell → panels → routing (T030–T032). Each is independently reviewable.
4. **T033 auth screens.** The only genuinely new design work. Everything else is a port.
5. **T034 quality floor** — visible focus, `prefers-reduced-motion`, mobile. The current build has
   none of these; the port is where they get added.
6. **T035** — delete `frontend/` only at parity, and fix README's run instructions in the same PR.

## What "done" means

- Screenshot diff against the current build shows no unintended change.
- Zero stock zinc/slate anywhere.
- Zero hardcoded hex outside the token definition file.
- Keyboard-navigable end to end with visible focus.
- Usable at mobile width.
- The orbs, the noise, the mono labels and the lime are all still there.
