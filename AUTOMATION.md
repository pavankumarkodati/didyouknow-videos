# Daily automation: Did You Know (@socmed311)

Runs every day at 6:20 PM US Central, about 20 minutes after the 6:00 PM Instagram post.

## One template only
Every post is a **"Mind Blown" video: 5 facts, 31 s, one category** (`style: "five"` in `scripts/make_video.py`). The single-fact (13 s) template was retired on Nov 28, 2026. Never make or schedule any other format.

## Accounts
- Buffer organization "My organization" (id `6b074d4c40dc56d56c21bfd8`), Instagram channel `socmed311` (id `6b074dc18541f09ecba3c597`). Free plan: 10 scheduled posts per channel at most.
- Videos are served to Buffer from this public repo:
  `https://raw.githubusercontent.com/pavankumarkodati/didyouknow-videos/main/videos/<file>.mp4`
  Push the video to `main` and check that link returns HTTP 200 before giving it to Buffer.

## Calendar rule (one video per day at 6:00 PM America/Chicago)
For a post date T: `d = (T - 2026-11-26).days`
- category: `["food", "animals", "history", "space", "human_body"][d % 5]`
- style: always `five`

## Each run
1. **Check today's post.** Use Buffer `list_posts` for the Instagram channel to find today's 6:00 PM post. Record its status and its `externalLink` (the Reel URL). If it errored, say so in the summary.
2. **Find the slot to fill.** Find the earliest date from tomorrow to today+10 with no scheduled post (normally today+10). If all 10 days are already filled, or Buffer already has 10 scheduled posts, skip steps 3 to 5.
3. **Write 5 new facts** for that date's category. Never reuse a fact in `data/used_facts.json`, even reworded. Each fact must be well established and checked with a web search. Avoid myths and "studies suggest" claims. Headline ≤ 8 words with the keyword in `*asterisks*`, explanation ≤ 2 short lines. Put the most surprising fact last. Pick an emoji illustration for each fact that actually shows the thing (e.g. 🗼 is Tokyo Tower, not the Eiffel Tower).
4. **Render** the video: write a spec JSON (see the docstring in `scripts/make_video.py`) and run `python3 scripts/make_video.py spec.json`. Name it `videos/<category>-5-facts-<n>.mp4` with the next unused number. Open the `_preview.jpg` it writes and check that the text fits and nothing overlaps. Delete the preview, add the facts to `data/used_facts.json`, then commit and push.
5. **Queue the video in Buffer** with `create_post`: `customScheduled`, `dueAt` = T at 18:00:00-06:00 (-05:00 during daylight time), `schedulingType` automatic, `metadata.instagram` = `{type: "reel", shouldShareToFeed: true}`, and `thumbnailOffset` 2500.
   Caption format:
   `5 <category> facts that sound fake… but are true <emoji> <teaser for fact 5>\n\nWhich one shocked you most? Comment 1–5 👇\n\nFollow @socmed311 for a new fact every day 💡\n\n<8 hashtags>`
   - Hashtags start with `#didyouknow #funfacts`. Never write "#5" or "#1" in the text, because Instagram turns it into a hashtag.
5b. **Update the project facts log.** Read the claude.ai Project doc `claude/facts_used_log.md` with the Projects tool (`project_read`), then write it back to the same path (`project_write`). Keep its template and existing text exactly as they are. Only add:
   - a row to "Instagram Reels schedule" (`| <Mon D> | <file>.mp4 | <category> | Scheduled |`), and change the line under that table to "Content runs out after <last date>; the daily run adds one new video each day." Mark rows for days that have passed as `Posted`.
   - a row to the "Mind Blown videos" table (`| <file>.mp4 | <category> | <the 5 facts in order joined with →> |`)
   - each new fact as the next numbered item under its category in "Facts per category".
   If the Projects tool isn't available, say so in the summary.
6. **Summary** (sent to the owner's phone as a notification). Keep it short:
   - ✅ Posted today: <title> — <Reel link> (or ❌ with the error)
   - 🗓️ Freed slot filled: <date> 6 PM
   - 🎬 New video: <title> (<category>), with its 5 facts in one line each
   - 📦 Buffer queue: <n>/10 scheduled
