# External Monitor Options

Snapshot date: 2026-03-19

Purpose: shortlist external monitoring services that could later watch `vps3` and/or a few critical public endpoints, while primary monitoring stays self-hosted on `vps3`.

## Current Direction

Planned approach:

- Self-host the main monitor on `vps3`
- Add one external monitor later to watch the blind spot:
  - `vps3` itself
  - critical public URLs
  - possibly a few heartbeat-style checks

Important note:

- Free monitoring tiers are common
- Free ongoing SMS is uncommon
- SMS usually means paid credits or a paid plan
- If SMS is not worth it, `ntfy` is a reasonable fallback alert channel to evaluate later

## Options

### 1. UptimeRobot

Best fit:

- Simple external checks for public URLs, ports, ping, DNS, and cron-style checks

Current notes:

- Main site advertises 50 free monitors
- Their help docs say SMS and voice are available on all plans, including Free
- SMS/voice still require purchased credits, so detection can be free while texting is not

Why it may fit later:

- Strong candidate if the main goal is "tell me if `vps3` or a public endpoint is down"
- Easy way to cover the self-hosted monitor's single biggest blind spot

Sources:

- https://uptimerobot.com/
- https://help.uptimerobot.com/en/articles/11361302-uptimerobot-sms-voice-call-credits-how-they-work

### 2. Better Stack

Best fit:

- External uptime plus a more full-featured incident/on-call platform if monitoring grows up later

Current notes:

- Pricing page shows a free tier for personal projects
- Free tier lists 10 monitors and heartbeats with Slack and e-mail alerts
- Pricing page shows unlimited SMS and phone alerts on paid responder plans, not the free tier

Why it may fit later:

- Good option if the monitor eventually grows beyond "is it up" into incidents, on-call, and status pages
- Probably more than needed for the first external layer

Sources:

- https://betterstack.com/pricing

### 3. Healthchecks.io

Best fit:

- Heartbeats for cron jobs, backups, replication checks, workers, and "I am alive" style reporting

Current notes:

- Strong fit for internal jobs that can report outward without exposing ports publicly
- Free Hobbyist plan lists 20 jobs
- Pricing page mentions 5 SMS and WhatsApp credits on that tier

Why it may fit later:

- Good match if the external piece should also watch backup jobs, worker liveness, or monitor heartbeats from inside the tailnet
- Less of a general website monitor than UptimeRobot or Better Stack

Sources:

- https://healthchecks.io/
- https://healthchecks.io/pricing/

### 4. HetrixTools

Best fit:

- Basic uptime and server monitoring with a straightforward free tier

Current notes:

- Pricing page shows a free-for-life tier
- Free tier lists 15 uptime monitors and 15 server monitors
- Free tier lists 1-minute check frequency
- SMS appears more aligned with paid usage than "fully free texting"

Why it may fit later:

- Worth keeping on the list if you want something simple and mostly uptime/server focused

Sources:

- https://hetrixtools.com/pricing/uptime-monitor/

### 5. Freshping

Best fit:

- Web endpoint monitoring

Current notes:

- Marketplace page states 50 URL monitors every minute for free
- Looks more web/URL oriented than host or heartbeat oriented
- Appears more tied to the Freshworks ecosystem than the other options

Why it may fit later:

- Useful if the only external need is public website checks
- Less compelling if the eventual goal includes infra or job-level monitoring

Sources:

- https://www.freshworks.com/apps/freshping_-_is_it_up_-_free_website_monitoring/

## Practical Take

If the goal is only to watch `vps3` and a few public domains later:

- Start with `UptimeRobot`
- Keep `Better Stack` as the "more serious later" option

If the goal later includes cron jobs, backups, or monitor-heartbeat checks:

- Add `Healthchecks.io` to the shortlist even if another service handles public uptime

## Re-check Before Choosing

These pricing details and alert limits can change. Re-check:

- free tier monitor counts
- heartbeat support
- SMS pricing or credits
- alert channels you actually want to use
