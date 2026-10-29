# YouTube Playlist Progress Tracker — Idea Notes

> A progress tracker for YouTube playlists: always know where you left off,
> what you've finished, and what's next.

## Chosen approach

Our own Android app (not a full YouTube clone) with our own UI for playlists and
progress, playing videos through **YouTube's official embedded player**.

- Because the player is ours, we know exact playback position, when a video
  ends, and the last video watched in each playlist.
- Must follow YouTube API terms: keep YouTube's ads/controls, no downloads,
  no background playback.
- Fallback / lite mode: "Open in YouTube" via deep link with timestamp
  (`?t=754`) plus manual mark watched.
- Possible later add-on: read Android media session (Notification Access) to
  detect videos watched in the real YouTube app (title-only, needs matching).
- Rejected as core: overlay + Accessibility Service (fragile, Play Store risk).

Constraint to remember: the YouTube Data API does **not** expose watch history
or per-video watch progress, so all tracking data lives in our app.

## Core features (v1)

- Import a playlist by link or from the user's YouTube account
- Per-playlist progress ("14 / 52 watched – 27%")
- **Continue where I left off**: one tap resumes the last video at the exact second
- Per-video status: Not started / In progress (12:30) / Watched
- Manual mark watched / unwatched, incl. bulk ("mark all above as watched")
- Auto-mark watched at ~90% played

## Nice later

- Home screen with "Continue watching" across all playlists
- Notes / bookmarks at timestamps (great for courses)
- Hide watched videos / show only unfinished
- Watch streaks, daily goals, estimated time left ("3h 20m remaining")
- Custom playlists mixing videos from different YouTube playlists
- Cross-device sync
- Home-screen widget showing the next video

## Data model (conceptual)

- **Playlist**: id, title, thumbnail, videos, lastOpenedVideo
- **Video**: id, title, duration, playlistId
- **Progress** (per video): status, lastPositionSeconds, lastWatchedAt, notes

## Existing apps (as of Oct 2026)

- Playlist Progress (Android, new, learning-focused):
  https://play.google.com/store/apps/details?id=com.ojasx.eduplay
- Web tools: SyncStudy, TrackMyCourse, PlayTrackr, playlist.tools
- Open source reference: https://github.com/ZackSatrday/PLAYCE

Differentiators to aim for: in-app player with automatic tracking,
cross-playlist "continue watching", widget, use beyond study
(podcasts, series, long video essays).

Next step: try Playlist Progress for a few days and note what's missing.
