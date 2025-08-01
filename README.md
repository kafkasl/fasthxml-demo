# FastHTML + Hyperview Mobile Todo App

A mobile translation of the [FastHTML advanced todo app](https://github.com/AnswerDotAI/fasthtml/blob/main/examples/adv_app.py) (without authentication), built with **FastHTML** backend and **Hyperview** frontend running on Expo.

## Architecture

```
Mobile App (Expo/Hyperview) ←→ FastHTML Server (HXML responses) ←→ SQLite DB
```

## Key Implementation Details

### Hyperview Components
```python
def Doc(*c, **kwargs): return FT('doc', c, kwargs)
def Screen(*c, **kwargs): return FT('screen', c, kwargs)
def View(*c, **kwargs): return FT('view', c, kwargs)
```

### Self-Rendering Models
```python
@patch
def __ft__(self:Todo):
    """Todo objects render themselves as Hyperview XML"""
    return View(
        Text(f"{'✅ ' if self.done else ''}{self.title}"),
        # ... edit/delete buttons with behaviors
    )
```

### Response Helper
```python
def render_to_response(component):
    """Render component to Hyperview XML response"""
    content = to_xml(component)
    response = Response(content)
    response.headers['Content-Type'] = 'application/vnd.hyperview+xml'
    return response
```

## Key Patterns

- **Layout System**: Base template with styles, header, and main content areas
- **In-place Editing**: Mode switching (view ↔ edit) using `action="replace"`
- **Partial Updates**: Server-driven UI updates without full page reloads
- **Namespace Handling**: All XML fragments include `xmlns="https://hyperview.org/hyperview"`

## Running

```bash
# Backend
uv run python main.py

# Frontend
# Setup Expo: https://hyperview.org/docs/guide_installation
# Use Expo app to scan QR code pointing to /hyperview endpoint
```

## Why This Approach

- **One Backend**: FastHTML serves both web and mobile with same codebase
- **Hypermedia-Driven**: UI behavior controlled by server responses
- **Native Performance**: Hyperview renders to native mobile components
- **Simple Architecture**: No complex state management or API serialization

Built following patterns from [Hypermedia Systems](https://hypermedia.systems/).