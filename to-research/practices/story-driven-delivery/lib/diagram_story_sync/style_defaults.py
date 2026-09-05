"""Default visual styles per node role, shared across backends.

Backends translate these values into their native style language: DrawIO
encodes them as ``mxCell`` style strings (``fillColor=...;strokeColor=...``),
Miro maps them to item ``style`` fields (``fillColor``, ``borderColor``,
``textColor``, ``fontSize``). Keeping the dictionary common ensures that a
story map looks the same in either tool.
"""

STYLE_DEFAULTS = {
    'epic': {
        'fill': '#e1d5e7',
        'stroke': '#9673a6',
        'font_color': '#000000',
        'shape': 'rounded',
        'font_size': 11,
    },
    'sub_epic': {
        'fill': '#d5e8d4',
        'stroke': '#82b366',
        'font_color': '#000000',
        'shape': 'rounded',
        'font_size': 10,
    },
    'story_user': {
        'fill': '#fff2cc',
        'stroke': '#d6b656',
        'font_color': '#000000',
        'font_size': 8,
        'aspect': 'fixed',
    },
    'story_system': {
        'fill': '#1a237e',
        'stroke': '#0d47a1',
        'font_color': '#ffffff',
        'font_size': 8,
        'aspect': 'fixed',
    },
    'story_technical': {
        'fill': '#000000',
        'stroke': '#333333',
        'font_color': '#ffffff',
        'font_size': 8,
        'aspect': 'fixed',
    },
    'actor': {
        'fill': '#dae8fc',
        'stroke': '#6c8ebf',
        'font_color': '#000000',
        'font_size': 8,
        'aspect': 'fixed',
    },
    'acceptance_criteria': {
        'fill': '#fff2cc',
        'stroke': '#d6b656',
        'font_color': '#000000',
        'font_size': 8,
        'align': 'left',
    },
    'increment_lane': {
        'fill': '#f5f5f5',
        'stroke': '#666666',
        'font_color': '#000000',
        'font_size': 11,
        'font_style': 'bold',
    },
    'ac': {
        'fill': '#fff9c4',
        'stroke': '#f0c040',
        'font_color': '#333333',
        'font_size': 10,
        'align': 'left',
    },
}


STORY_TYPE_STYLE_KEYS = {
    'user': 'story_user',
    None: 'story_user',
    '': 'story_user',
    'system': 'story_system',
    'technical': 'story_technical',
}
"""Story ``story_type`` → ``STYLE_DEFAULTS`` key. Centralised so backends agree."""
