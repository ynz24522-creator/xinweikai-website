# -*- coding: utf-8 -*-
"""Inline SVG line-art icons for categories plus a hero illustration.

All artwork is code-native: 48x48 viewBox, stroke uses currentColor so colour is
controlled by CSS, no external assets or fonts required.
"""

SVG_OPEN = ('<svg class="icon" viewBox="0 0 48 48" fill="none" stroke="currentColor" '
            'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">')

ICONS = {
    "resistors": '<rect x="11" y="18" width="26" height="12" rx="2.5"/><path d="M4 24h7M37 24h7"/>',
    "capacitors": '<path d="M15 11v26M33 11v26"/><path d="M4 24h11M33 24h11"/>',
    "inductors": ('<path d="M8 29a4 4 0 0 1 8 0"/><path d="M16 29a4 4 0 0 1 8 0"/>'
                  '<path d="M24 29a4 4 0 0 1 8 0"/><path d="M32 29a4 4 0 0 1 8 0"/>'
                  '<path d="M4 29h4M40 29h4"/>'),
    "diodes": '<path d="M13 14l16 10-16 10z"/><path d="M31 14v20"/><path d="M4 24h9M31 24h13"/>',
    "transistors": ('<circle cx="24" cy="24" r="14"/><path d="M17 17v14"/><path d="M17 24h9"/>'
                    '<path d="M26 15v7M26 26v7"/>'),
    "power": '<path d="M27 5L13 27h10l-2 16 14-22H25z"/>',
    "mcu": ('<rect x="13" y="13" width="22" height="22" rx="2.5"/>'
            '<path d="M19 7v6M29 7v6M19 35v6M29 35v6M7 19h6M7 29h6M35 19h6M35 29h6"/>'
            '<rect x="20" y="20" width="8" height="8" rx="1"/>'),
    "memory": ('<rect x="9" y="15" width="30" height="18" rx="2.5"/>'
               '<path d="M5 20h4M5 28h4M39 20h4M39 28h4M16 21h16M16 27h10"/>'),
    "amplifiers": '<path d="M12 9l26 15-26 15z"/><path d="M18 18h6M18 30h6"/>',
    "interface": ('<rect x="7" y="17" width="13" height="14" rx="2.5"/>'
                  '<rect x="28" y="17" width="13" height="14" rx="2.5"/><path d="M20 24h8"/>'),
    "logic": '<path d="M13 12h9a12 12 0 0 1 0 24h-9z"/><path d="M5 18h8M5 30h8M34 24h9"/>',
    "crystals": ('<rect x="17" y="10" width="14" height="28" rx="3"/>'
                 '<path d="M7 24h10M31 24h10"/><path d="M21 16h6M21 32h6"/>'),
    "sensors": ('<circle cx="24" cy="24" r="6"/>'
                '<path d="M15 13a15 15 0 0 0 0 22M33 13a15 15 0 0 1 0 22"/>'),
    "connectors": ('<rect x="7" y="16" width="34" height="17" rx="2.5"/>'
                   '<path d="M15 16V9M24 16V9M33 16V9"/>'),
    "switches": ('<rect x="7" y="19" width="34" height="13" rx="6.5"/><circle cx="18" cy="25.5" r="4"/>'),
    "opto": ('<path d="M22 13l12 18H10z"/><path d="M34 9l4-4M38 18h7M34 27l4 4"/>'),
    "rf": ('<path d="M24 40V19"/><path d="M15 20a13 13 0 0 1 18 0"/>'
           '<path d="M9 14a21 21 0 0 1 30 0"/><circle cx="24" cy="42" r="2.4"/>'),
    "protection": '<path d="M24 5l15 6v12c0 10-6 16-15 20-9-4-15-10-15-20V11z"/>',
    "battery-power": ('<rect x="7" y="15" width="28" height="18" rx="3"/>'
                      '<path d="M35 20v8"/><path d="M16 20v8M26 20v8"/>'),
    "tools": ('<path d="M31 8a9 9 0 0 0-9 11L9 32l7 7 13-13a9 9 0 0 0 11-9l-6 6-6-1-1-6z"/>'),
    "pcb-wire": ('<rect x="7" y="7" width="34" height="34" rx="3"/>'
                 '<circle cx="18" cy="18" r="3"/><circle cx="30" cy="30" r="3"/>'
                 '<path d="M18 18h9v12h3M18 21v10h9"/>'),
    "thermal": ('<rect x="7" y="14" width="34" height="8" rx="2.5"/>'
                '<path d="M14 22v16M20 22v16M26 22v16M32 22v16"/>'),
}

HERO_BOARD = """
<svg class="hero-art" viewBox="0 0 520 380" fill="none" aria-hidden="true">
  <defs>
    <linearGradient id="boardGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1b4f8a"/><stop offset="100%" stop-color="#0d2b52"/>
    </linearGradient>
    <linearGradient id="traceGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#4fc3f7" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#4fc3f7" stop-opacity="0.75"/>
    </linearGradient>
  </defs>
  <rect x="24" y="26" width="472" height="328" rx="22" fill="url(#boardGrad)" stroke="#2e6fae" stroke-width="2"/>
  <g stroke="url(#traceGrad)" stroke-width="2.4" stroke-linecap="round" fill="none">
    <path d="M60 300h96v-56h74"/><path d="M60 96h70v48h60"/>
    <path d="M420 84h-58v54h-64"/><path d="M420 296h-72v-52h-52"/>
    <path d="M150 340v-30h58"/><path d="M372 44v34h-52"/>
  </g>
  <g fill="#0a2244" stroke="#4fc3f7" stroke-width="2">
    <circle cx="60" cy="300" r="7"/><circle cx="60" cy="96" r="7"/>
    <circle cx="420" cy="84" r="7"/><circle cx="420" cy="296" r="7"/>
    <circle cx="150" cy="340" r="7"/><circle cx="372" cy="44" r="7"/>
    <circle cx="230" cy="244" r="7"/><circle cx="240" cy="144" r="7"/>
  </g>
  <g>
    <rect x="196" y="150" width="132" height="96" rx="10" fill="#0e2b4e" stroke="#7dd3fc" stroke-width="2"/>
    <g stroke="#7dd3fc" stroke-width="3" stroke-linecap="round">
      <path d="M214 150v-16M238 150v-16M262 150v-16M286 150v-16M310 150v-16"/>
      <path d="M214 246v16M238 246v16M262 246v16M286 246v16M310 246v16"/>
      <path d="M196 172h-16M196 196h-16M196 220h-16"/>
      <path d="M328 172h16M328 196h16M328 220h16"/>
    </g>
    <text x="262" y="208" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, monospace"
      font-size="26" fill="#a5e4ff">XWK</text>
  </g>
  <g stroke="#f9a825" stroke-width="2" fill="#3a2a06">
    <rect x="86" y="150" width="46" height="22" rx="4"/>
    <rect x="86" y="192" width="46" height="22" rx="4"/>
    <rect x="386" y="150" width="46" height="22" rx="4"/>
    <rect x="386" y="192" width="46" height="22" rx="4"/>
  </g>
  <g fill="#2b5c93" stroke="#93c5fd" stroke-width="1.6">
    <rect x="360" y="252" width="70" height="34" rx="6"/>
    <rect x="286" y="76" width="60" height="30" rx="6"/>
  </g>
  <g fill="#4fc3f7">
    <circle cx="150" cy="106" r="4"/><circle cx="176" cy="106" r="4"/>
    <circle cx="360" cy="272" r="4"/><circle cx="392" cy="272" r="4"/>
  </g>
</svg>
"""

SHELF_ART = """
<svg class="shelf-art" viewBox="0 0 520 300" fill="none" aria-hidden="true">
  <rect x="16" y="18" width="488" height="264" rx="18" fill="#f1f5fb" stroke="#d7e0ee" stroke-width="2"/>
  <g stroke="#c3d2e6" stroke-width="4" stroke-linecap="round">
    <path d="M40 108h440M40 196h440"/>
  </g>
  <g fill="#ffffff" stroke="#93b4d8" stroke-width="2">
    <rect x="52" y="40" width="96" height="60" rx="8"/>
    <rect x="168" y="40" width="96" height="60" rx="8"/>
    <rect x="284" y="40" width="96" height="60" rx="8"/>
    <rect x="400" y="40" width="88" height="60" rx="8"/>
    <rect x="52" y="124" width="120" height="64" rx="8"/>
    <rect x="192" y="124" width="104" height="64" rx="8"/>
    <rect x="316" y="124" width="172" height="64" rx="8"/>
  </g>
  <g stroke="#2f6fae" stroke-width="2.6" stroke-linecap="round" fill="none">
    <path d="M66 74h20M96 74h20M128 74h8"/>
    <circle cx="200" cy="70" r="14"/><circle cx="230" cy="70" r="14"/>
    <path d="M300 62h64M300 78h48"/>
    <path d="M416 62h56M416 78h40"/>
    <path d="M68 160h88M68 176h60"/>
    <path d="M208 146h72M208 162h72M208 178h40"/>
    <path d="M332 142h140M332 158h140M332 174h96"/>
  </g>
  <g fill="#f9a825"><circle cx="66" cy="62" r="4"/><circle cx="340" cy="62" r="4"/><circle cx="66" cy="142" r="4"/></g>
</svg>
"""


def cat_icon(cat_id):
    return SVG_OPEN + ICONS.get(cat_id, ICONS["pcb-wire"]) + "</svg>"


def service_icon(name):
    paths = {
        "search": '<circle cx="21" cy="21" r="12"/><path d="M30 30l12 12"/>',
        "bom": ('<rect x="10" y="8" width="28" height="34" rx="3"/>'
                '<path d="M17 17h14M17 24h14M17 31h8"/>'),
        "stock": ('<path d="M8 20l16-10 16 10-16 10z"/><path d="M8 28l16 10 16-10"/>'
                  '<path d="M24 30v10"/>'),
        "sample": '<path d="M24 8l4.6 9.8 10.4 1.4-7.6 7.4 1.9 10.4L24 31.9 14.7 37l1.9-10.4L9 19.2l10.4-1.4z"/>',
        "invoice": ('<rect x="12" y="7" width="24" height="34" rx="3"/>'
                    '<path d="M18 16h12M18 23h12M18 30h7"/>'),
        "support": ('<path d="M10 26v-4a14 14 0 0 1 28 0v4"/>'
                    '<rect x="6" y="24" width="8" height="12" rx="3"/>'
                    '<rect x="34" y="24" width="8" height="12" rx="3"/>'
                    '<path d="M38 36v2a4 4 0 0 1-4 4h-6"/>'),
    }
    return SVG_OPEN + paths.get(name, paths["search"]) + "</svg>"


LOGO = """
<svg class="logo-mark" viewBox="0 0 48 48" fill="none" aria-hidden="true">
  <rect x="3" y="3" width="42" height="42" rx="11" fill="#0f3d75"/>
  <path d="M12 32l7-16 5 11 5-11 7 16" stroke="#7dd3fc" stroke-width="3.2"
        stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="19" cy="16" r="2.6" fill="#f9a825"/>
</svg>
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
<rect width="48" height="48" rx="11" fill="#0f3d75"/>
<path d="M12 32l7-16 5 11 5-11 7 16" fill="none" stroke="#7dd3fc" stroke-width="3.4"
 stroke-linecap="round" stroke-linejoin="round"/></svg>
"""
