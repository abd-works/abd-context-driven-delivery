"""The abd.works engineering look canvases wear: dark surfaces, thin borders, mono uppercase labels, one orange accent."""

MONO = "'JetBrains Mono', ui-monospace, monospace"
SANS = "'Inter', system-ui, sans-serif"
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
         '&amp;family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap">')

BACKGROUND = "#0B0B0B"
ACCENT = "#E5531A"

LOOK = {
    "epic": {"fill": "#111113", "stroke": "#2A2A2A", "color": ACCENT, "size": 16, "weight": 600, "font": MONO,
             "extra": "text-transform: uppercase; letter-spacing: 0.1em; justify-content: flex-start; padding-left: 16px; "},
    "sub_epic": {"fill": ACCENT, "stroke": ACCENT, "color": BACKGROUND, "size": 13, "weight": 700, "font": MONO,
                 "extra": "text-transform: uppercase; letter-spacing: 0.06em; justify-content: flex-start; padding-left: 16px; "},
    "actor": {"fill": "#111113", "stroke": "#2A2A2A", "color": "#9B9BA8", "size": 11, "weight": 500, "font": SANS, "extra": ""},
    "story": {"fill": "#111113", "stroke": "#2A2A2A", "color": "#E8E8ED", "size": 12, "weight": 600, "font": SANS,
              "extra": f"box-shadow: inset 3px 0 0 {ACCENT}; "},
}
