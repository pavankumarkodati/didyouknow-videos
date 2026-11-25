# Daily automation: Did You Know (@socmed311)

Runs every day at 6:20 PM US Central, about 20 minutes after the 6:00 PM Instagram post.

## Accounts
- Buffer organization "My organization" (id `6b074d4c40dc56d56c21bfd8`), Instagram channel `socmed311` (id `6b074dc18541f09ecba3c597`). Free plan: 10 scheduled posts per channel at most.
- Videos are served to Buffer from this public repo:
  `https://raw.githubusercontent.com/pavankumarkodati/didyouknow-videos/main/videos/<file>.mp4`
  Push the video to `main` and check that link returns HTTP 200 before giving it to Buffer.

## Calendar rule (one video per day at 6:00 PM America/Chicago)
For a post date T: `d = (T - 2026-11-26).days`
- style: `five` (5-fact "Mind Blown", 31 s) if d is even, `single` (13 s) if d is odd
- category: `["food", "animals", "history", "space", "human_body"][d % 5]`

## Each run
1. **Check today's post.** Use Buffer `list_posts` for the Instagram channel to find today's 6:00 PM post. Record its status and its `externalLink` (the Reel URL). If it errored, say so in the summary.
2. **Find the slot to fill.** Find the earliest date from tomorrow to today+10 with no scheduled post (normally today+10). If all 10 days are already filled, skip steps 3 to 5.
3. **Write new facts** for that date's category and style: 1 for single, 5 for five. Never reuse a fact in `data/used_facts.json`, even reworded. Each fact must be well established and checked with a web search. Avoid myths and "studies suggest" claims. Headline ≤ 8 words with the keyword in `*asterisks*`, explanation ≤ 2 short lines. For five, put the most surprising fact last. Pick an emoji illustration for each fact.
4. **Render** the video: write a spec JSON (see the docstring in `scripts/make_video.py`) and run `python3 scripts/make_video.py spec.json`. Name it `videos/<category>-<short-slug>.mp4` and use a new, unique name. Open the `_preview.jpg` it writes and check that the text fits and nothing overlaps. Delete the preview, add the facts to `data/used_facts.json`, then commit and push.
5. **Queue the video in Buffer** with `create_post`: `customScheduled`, `dueAt` = T at 18:00:00-06:00 (-05:00 during daylight time), `schedulingType` automatic, `metadata.instagram` = `{type: "reel", shouldShareToFeed: true}`, and `thumbnailOffset` 2000 (single) or 2500 (five).
   Caption format:
   - single: `<fact hook> <emoji>\n\nDid you know that? Comment YES or NO 👇\n\nFollow @socmed311 for a new fact every day 💡\n\n<8 hashtags>`
   - five: `5 <category> facts that sound fake… but are true <emoji> <teaser for fact 5>\n\nWhich one shocked you most? Comment 1–5 👇\n\nFollow @socmed311 for a new fact every day 💡\n\n<8 hashtags>`
   - Hashtags start with `#didyouknow #funfacts`. Never write "#5" or "#1" in the text, because Instagram turns it into a hashtag.
6. **Summary** (sent to the owner's phone as a notification). Keep it short:
   - ✅ Posted today: <title> — <Reel link> (or ❌ with the error)
   - 🗓️ Freed slot filled: <date> 6 PM
   - 🎬 New video: <title> (<style>, <category>), with its fact(s) in one line each
   - 📦 Buffer queue: <n>/10 scheduled
