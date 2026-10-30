# Chapter: YouTube Playlist Tracker

> Always know where you left off, what you've finished, and what's next in any YouTube playlist.

**Status:** idea and interactive design prototype. No app code yet.

- Design prototype: https://claude.ai/artifact/9jR9mhHjqkqmkESZr62DoW (private until shared)
- Design source files: [`design/`](design/README.md)

## Decisions

- **Name:** Chapter. Play Store listing "Chapter: Playlist Tracker". Backups: Pickup, Onward, Watchmark. Check Play Store availability first.
- **Platform:** Android first.
- **Business model:** paid, one-time purchase on the Play Store. No paywall screen, no subscription. Settings says "You own Chapter, and every future update is included."
- **Approach:** our own app and UI around YouTube's official embedded player. Not a YouTube clone, and no overlay or accessibility-service tricks.

## YouTube constraints that shape the product

- The YouTube Data API does not expose a user's watch history or watch progress, so all progress is tracked inside the app.
- The embedded player keeps YouTube's ads and branding. No downloads.
- No background playback or picture-in-picture outside the app (YouTube terms). The in-app mini player covers this.
- Apps cannot set video quality: the IFrame API quality functions have done nothing since October 2019. YouTube picks quality from player size and connection. The design shows an "Auto · 1080p" badge and a button that opens YouTube's own player menu. **To verify when building:** whether that menu offers quality inside an Android WebView embed.
- Playlists are imported with the YouTube Data API v3. Each playlist item's upload date (`contentDetails.videoPublishedAt`) lets the app detect newest-first playlists.

## Features (all designed in the prototype)

### Core tracking
- Add a playlist by link, or import from the user's YouTube account, with a live preview.
- Home: "Continue watching" card that resumes at the exact second, playlists with progress, weekly goal.
- Playlist screen: progress ring, Continue/Start button, filters (All / Up next / Watched).
- Each video shows not started / in progress / watched. Tap the circle to toggle watched.
- Video menu: mark watched or unwatched, mark all above as watched, reset progress, open in YouTube at the saved time.
- Auto-mark as watched at 80%, 90% (default), 95% or the end.
- Undo on every bulk or destructive action.
- Reverse order per playlist, plus a "looks newest first" suggestion. The chosen order drives episode numbers, Continue, Up next, autoplay, "mark all above" and mixes.

### Player
- Opens as a sheet over the app. Swipe down to minimise into a mini player.
- Tap to show or hide controls (they auto-hide after about 3 seconds). Double-tap left or right to skip ±10s, with a ripple; more taps add 10s each.
- Drag the timeline to scrub, with a bubble showing time and chapter.
- Chapters: segmented timeline, current-chapter row, Chapters tab (done / now / upcoming).
- Notes and one-tap bookmarks pinned to timestamps, shown as dots on the timeline.
- Speed 0.75× to 2× (shows the time saved), sleep timer (end of video, 15, 30, 60 min), captions toggle, "Ends at" clock.
- Full screen: the video rotates into landscape. Lock controls, side panels for speed and quality, "Up next" countdown card.
- Quality: Auto badge and "Choose in YouTube's menu" button.
- Ambient glow behind the video, slow zoom while playing.

### Library, stats and more
- Library grid with Completed and Mix badges.
- Mixes: combine unwatched videos from any playlists. Progress is shared with the original videos.
- Stats: streak, week of day dots, weekly bar chart, goal ring, totals.
- Settings: watched threshold, autoplay next, rewind 5s on resume, weekly goal, daily reminder, sync across devices, export to CSV, theme (System / Dark / Light), accent colour, replay the welcome tour.
- Onboarding: 3 animated steps, no sign-up, ends on "Add your first playlist".
- Home-screen widgets: 4×2 continue, 2×2 progress ring, 2×2 streak, 4×3 continue with up next, 4×2 light theme.

## Design system

- **Look:** dark first, with a full light theme. Near-black background, one warm accent.
- **Dark colours:** background #0A0A0D, surface #15151A, raised surface #22222A, text #F3F3F5, muted text #A3A3AE.
- **Light colours:** background #F3F3F6, surface #FFFFFF, raised surface #E8E8EE, text #111116, muted text #5B5B67.
- **Accent:** Ember #FF7A45 by default. Alternatives: Iris #8B7CFF, Mint #3DDC97, Sky #4DA3FF. Accent text and rings are darkened or lightened automatically to keep contrast at 4.5:1 for text and 3:1 for graphics.
- **Fonts (Google Fonts):** Bricolage Grotesque for headings, Geist for UI text, Geist Mono for times and numbers.
- **Motion:** screens and sheets use ease-out `cubic-bezier(.22,1,.36,1)` over about 500–600 ms. Small pops (checks, toggles, badges) use a springy `cubic-bezier(.34,1.56,.64,1)`. Lists cascade in at about 35 ms per row.
- **Accessibility:** touch targets at least 44 px, labels on icon-only buttons.

## Data model

- **Playlist:** id, title, channel, art, videos, addedAt, reversed, newestFirst (detected), orderOk (suggestion dismissed).
- **Mix:** id, title, refs (video ids), art, addedAt, reversed. Progress lives on the original videos.
- **Video:** id, n (position), title, duration, pos (seconds), watched, lastAt.
- **Note:** id, videoId, t (seconds), text ("Bookmark" for quick bookmarks).
- **Chapters:** parsed from timestamps in the video description.
- **Settings:** threshold, autoNext, rewind5, goalHours, reminder, sync, theme, accent.

## Suggested stack (decide in the new repo)

- Kotlin and Jetpack Compose. Room for local data, WorkManager for reminders, Glance for widgets.
- YouTube IFrame player in a WebView (for example the open-source android-youtube-player library). YouTube Data API v3 for import: an API key, plus OAuth for "Import from my account".
- Sync: Google sign-in with the Drive app-data folder, or Firebase. Choose later.

## Open questions and next steps

- Confirm the name is free on the Play Store.
- Check that the embedded player's own menu offers quality on Android.
- Read the YouTube API Services Terms and branding guidelines before building.
- Price: [YOUR PRICE].
- Try the closest competitor for a few days and note what's missing: Playlist Progress (Android), https://play.google.com/store/apps/details?id=com.ojasx.eduplay

## Existing apps (as of Oct 2026)

- Playlist Progress (Android, new, learning-focused): https://play.google.com/store/apps/details?id=com.ojasx.eduplay
- Web tools: SyncStudy, TrackMyCourse, PlayTrackr, playlist.tools
- Open-source reference: https://github.com/ZackSatrday/PLAYCE

Where Chapter stands out: in-app player with automatic tracking, "continue watching" across playlists, widgets, mixes, and use beyond studying (podcasts, series, long video essays).
