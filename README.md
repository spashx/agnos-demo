# Roombook, an AGNOS demonstration

> **This history is simulated.** The people, their commits, the dates, the public holidays, the
> Verification outputs written in the plans and the friction metrics are made up to show how the AGNOS
> process looks when a team has used it for two months, with AI agents (Claude Code and GitHub Copilot) as co-authors
> of part of the commits or committing alone. Nothing here was really done by these people or these agents.

This repository holds the development of a small product, **Roombook**, following the process. AGNOS itself
is not stored here: `agnos-init` added it, so `CLAUDE.md` and `AGENTS.md` hold only a block naming the process skill of the
AGNOS plugin. Read this repository to see what the process produces, run the AGNOS skills against it to test them, or start
an agent session in it with the plugin installed.

## The product

A meeting-room booking service in Python (`service/`) with a TypeScript HTTP client and command-line tool
(`client/`), and a small server-rendered web interface (`client/src/ui/`). As the product now has a user
interface, it has a design system: every colour, size and spacing comes from the tokens of
`client/design/tokens.json`, and the stylesheet is generated from them.

| Session | Feature | What it delivers |
|---|---|---|
| BKG | FTR-BKG-001, FTR-BKG-002 | Rooms, reservations, overlap/capacity/closed-room rules, cancellation, durable storage |
| NTF | FTR-NTF-001 | Creation event, reminders before the meeting, retries on failure |
| CLI | FTR-CLI-001 | HTTP/JSON API, typed client, command-line tool |
| DSN | FTR-DSN-001 | Design system: three-tier tokens, contrast and literal checks, stylesheet generated from the tokens |
| WEB | FTR-WEB-001 | Web interface: rooms, booking, cancellation, worded refusals, unavailable service |

The process artifacts are in `agnos-process/` (requirements, ADRs, plans, session state, generated index). The code
cites them in comments, and the AGNOS Performance Center shows the links: see [this demo's Performance Center][perf-center].

## AGNOS

- [This demo's Performance Center][perf-center]: its traceability matrix, quality score, call graph and history.
- [The AGNOS marketplace][marketplace]: the plugin `agnos` to install in Claude Code or GitHub Copilot.
- [The AGNOS process repository][process]: where AGNOS is developed.

## The team

Four people of Acme, a fictitious company. The role is the suffix of the identity, so the history can be filtered by
role. Each one works mostly with an AI agent, named as a co-author of the commit.

| Role | Suffix | Identities | Authors of | Usual agent |
|---|---|---|---|---|
| Product manager | `-pm` | linda-pm | features and requirements | Claude Code (Opus) |
| Technical | `-tech` | andy-tech, sachin-tech | ADRs, plans, production code, unit tests written before the code they check, session closing | Claude Code (andy), GitHub Copilot (sachin) |
| UX designer | `-ux` | john-ux | the design system (tokens, component catalogue), the screens, design fixes | Claude Code (Sonnet) |

## Timeline

Monday 2026-08-24 to Friday 2026-10-23, Europe/Paris, working days only, 09:00 to 18:00. Two fictitious public
holidays are declared in [docs/WORKING_CALENDAR.md](docs/WORKING_CALENDAR.md). Each session is developed on a
`feature/<TRI>` branch merged into `main`: BKG 08-24 to 09-18, NTF 09-21 to 10-02, CLI 10-05 to 10-23. The UX
work runs in parallel with the CLI session: DSN (the design system) starts from `main` after the NTF merge, 10-05
to 10-15, and WEB (the interface) starts from the typed client of the CLI session, merges DSN first, and is merged
into `main` on 10-23.

## Explore

```
git log --author=-tech --format="%h %ad %an %s" --date=short   # everything done by the technical people
git log --author=-pm --format="%h %ad %an %s" --date=short     # everything done by the product manager
git log --author=-ux --format="%h %ad %an %s" --date=short     # everything done by the UX designer
git log --grep=TASK-BKG-007 --format="%h %an %s"               # the commits of one task
git log --graph --oneline --all                                 # the sessions and their merges
```

## Run the tools

```
cd service && python -m unittest discover -s tests -t .         # Python tests (standard library only)
cd client && node --test "tests/*.test.ts"                      # TypeScript tests (Node 22.18 or later)
cd service && python -m roombook                                # the service on http://127.0.0.1:8080, rooms from service/rooms.json
cd client && npm run ui                                       # web interface on http://127.0.0.1:3000 (ROOMBOOK_URL names the service)
cd client && node src/cli.ts rooms                             # command-line tool: rooms, book, cancel
```

The AGNOS skills `agnos-index` and `agnos-perf-center` run from an AGNOS installation, on this folder as the project.

[perf-center]: https://spashx.github.io/agnos-website/demo/PERF-CENTER.html
[marketplace]: https://github.com/spashx/agnos-marketplace
[process]: https://github.com/spashx/agnos
