# Chapter: design prototype files

Source files of the interactive design canvas:
https://claude.ai/artifact/9jR9mhHjqkqmkESZr62DoW
(private until it is shared from the canvas's Share menu)

| File | What it is |
|---|---|
| `canvas.json` | Canvas layout: which frames exist, where they sit, row titles |
| `Main.dc.html` | The whole interactive app: every screen, sample data, logic and animations |
| `Playlist`, `Player`, `Stats`, `Import`, `Reverse`, `Onboarding`, `Mix`, `Settings`, `Chapters`, `Speed` | Frames that open `Main` on a different start screen |
| `Light.dc.html` | `Main` in the light theme |
| `Fullscreen.dc.html` | `Main` in the landscape full-screen player |
| `Widgets.dc.html` | Static home-screen widget designs |

These are Design Component files (`.dc.html`). They run inside the Claude design
canvas, which supplies their `support.js` runtime, so opening them directly in a
browser will not work. Use them as the reference for the real Android build:
layout, colours, copy, animation timings and behaviour. `Main.dc.html` holds the
colour tokens (`palette`), sample data (`seedPlaylists`), and all the interaction
logic in its script block.
