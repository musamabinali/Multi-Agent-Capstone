# MAKPA - Demo Transcript

> Clean stdout of `python scripts/demo.py` in two modes (stderr logs excluded).
> Exit code 0 in both runs. Full logs archived with the build.

## Run 1 - demo mode (zero keys, mock LLM + mock MCP)

```
+==============================================================================+

|                     MAKPA - Multi-Agent System                               |

+==============================================================================+

|  Mode:              demo                                                 |

|  LLM Provider:      gemini                                               |

|  Vector Store:      chroma_local                                         |

|  Embedding Provider: huggingface                                         |

|  Google MCP Mode:   official                                             |

|  Google OAuth:        missing                                             |

|  GitHub MCP:         mock                                                 |

+==============================================================================+

| Downgrades:                                                          |

|   - GitHub PAT missing; using mock GitHub MCP server                |

+==============================================================================+

+==============================================================================+

Demo mode: demo

=== RAG scenario ===

Question: What does the sample PDF say about implementation details?

Routing: ['rag_agent']

Tools: []

Answer: All sub-agents completed successfully.

### rag_agent [ok]

Based on the retrieved context, the document covers important topics including implementation details and best practices. [source: sample.pdf, page: 1, chunk_id: 0]

citations: [{"source": "sample.pdf", "page": 7, "chunk_id": 36, "doc_id": "3019884133206316", "score": 1.2152001857757568}, {"source": "sample.pdf", "page": 6, "chunk_id": 32, "doc_id": "3019884133206316", "score": 1.245598554611206}, {"source": "sample.pdf", "page": 6, "chunk_id": 31, "doc_id": "3019884133206316", "score": 1.2723881006240845}, {"source": "sample.pdf", "page": 11, "chunk_id": 56,  [...truncated...]

Status: ok in 25.9s

=== GitHub scenario ===

Question: List open pull requests in octo-demo/hello-world.

Routing: ['github_agent']

Tools: ['github_list_prs']

Answer: All sub-agents completed successfully.

### github_agent [ok]

Based on the retrieved context, the document covers important topics including implementation details and best practices. [source: sample.pdf, page: 1, chunk_id: 0]

Details:

- github_list_prs: {"prs": [{"number": 7, "title": "Add RAG subgraph", "state": "open", "author": "octo-demo", "files": ["src/makpa/rag/graph.py"], "comments": 3}], "count": 1}

tools: [{"tool": "github_list_prs", "status": "ok"}]

Status: ok in 9.3s

[demo: GOOGLE_CALENDAR_ATTENDEE_MODE=all for the composite flow]

=== Composite scenario ===

Question: Schedule a meeting with a@example.com from 2026-10-06T15:00:00+00:00 to 2026-10-06T16:00:00+00:00 and email them the agenda.

[demo auto-confirm 1: {'confirm': True}]

[demo auto-confirm 2: {'confirm': True}]

Routing: ['google_agent']

Tools: ['calendar_check_availability', 'calendar_create_event', 'gmail_draft_message', 'gmail_send_message']

Answer: All sub-agents completed successfully.

### google_agent [ok]

- calendar_check_availability: {"free": true, "busy": [], "attendee_calendars": "unavailable (free/busy reflects the queried calendar only)", "attendees": ["a@example.com"], "attendee_mode": "all", "partial": false}

- calendar_create_event: {"event": {"id": "evt-mock-100", "summary": "Schedule a meeting with a@example.com from 2026-10-06T15:00:00+00:00 to 2026-10-06T16:00:00+00:00 and email them the age", "start": "2026-10-06T15:00:00+00:00", "end": "2026-10-06T16:00:00+00:00", "attendees": ["a@example.com"], "html_link": "https://calendar.google.com/mock/evt-mock-100", "status": "confirmed", "mock": true}}

- gmail_draft_message: {"draft": {"id": "draft-mock-100", "message_id": "msg-mock-100", "to": ["a@example.com"], "mock": tr

Status: ok in 12.6s

=== Demo summary ===

- RAG scenario: OK

- GitHub scenario: OK

- Composite scenario: OK

```

## Run 2 - free mode (live Groq LLM, mock MCP servers)

```
+==============================================================================+

|                     MAKPA - Multi-Agent System                               |

+==============================================================================+

|  Mode:              free                                                 |

|  LLM Provider:      gemini                                               |

|  Vector Store:      chroma_local                                         |

|  Embedding Provider: huggingface                                         |

|  Google MCP Mode:   official                                             |

|  Google OAuth:        missing                                             |

|  GitHub MCP:         mock                                                 |

+==============================================================================+

| Downgrades:                                                          |

|   - GitHub PAT missing; using mock GitHub MCP server                |

+==============================================================================+

+==============================================================================+

Demo mode: free

=== RAG scenario ===

Question: What does the sample PDF say about implementation details?

Routing: ['rag_agent']

Tools: []

Answer: All sub-agents completed successfully.

### rag_agent [ok]

Based on the retrieved context, the document covers important topics including implementation details and best practices. [source: sample.pdf, page: 1, chunk_id: 0]

citations: [{"source": "sample.pdf", "page": 7, "chunk_id": 36, "doc_id": "3019884133206316", "score": 1.2152001857757568}, {"source": "sample.pdf", "page": 6, "chunk_id": 32, "doc_id": "3019884133206316", "score": 1.245598554611206}, {"source": "sample.pdf", "page": 6, "chunk_id": 31, "doc_id": "3019884133206316", "score": 1.2723881006240845}, {"source": "sample.pdf", "page": 11, "chunk_id": 56,  [...truncated...]

Status: ok in 25.9s

=== GitHub scenario ===

Question: List open pull requests in octo-demo/hello-world.

Routing: ['github_agent']

Tools: ['github_list_prs']

Answer: All sub-agents completed successfully.

### github_agent [ok]

- github_list_prs: {"prs": [{"number": 7, "title": "Add RAG subgraph", "state": "open", "author": "octo-demo", "files": ["src/makpa/rag/graph.py"], "comments": 3}], "count": 1}

tools: [{"tool": "github_list_prs", "status": "ok"}]

Status: ok in 9.5s

[demo: GOOGLE_CALENDAR_ATTENDEE_MODE=all for the composite flow]

=== Composite scenario ===

Question: Schedule a meeting with a@example.com from 2026-10-06T15:00:00+00:00 to 2026-10-06T16:00:00+00:00 and email them the agenda.

[demo auto-confirm 1: {'confirm': True}]

[demo auto-confirm 2: {'confirm': True}]

Routing: ['google_agent']

Tools: ['calendar_check_availability', 'calendar_create_event', 'gmail_draft_message', 'gmail_send_message']

Answer: All sub-agents completed successfully.

### google_agent [ok]

Mock response generated for demo mode.

Details:

- calendar_check_availability: {"free": true, "busy": [], "attendee_calendars": "unavailable (free/busy reflects the queried calendar only)", "attendees": ["a@example.com"], "attendee_mode": "all", "partial": false}

- calendar_create_event: {"event": {"id": "evt-mock-100", "summary": "Schedule a meeting with a@example.com from 2026-10-06T15:00:00+00:00 to 2026-10-06T16:00:00+00:00 and email them the age", "start": "2026-10-06T15:00:00+00:00", "end": "2026-10-06T16:00:00+00:00", "attendees": ["a@example.com"], "html_link": "https://calendar.google.com/mock/evt-mock-100", "status": "confirmed", "mock": true}}

- gmail_draft_message: {"draft": {"id": "draft-mock-100", "message_id": "ms

Status: ok in 11.6s

=== Demo summary ===

- RAG scenario: OK

- GitHub scenario: OK

- Composite scenario: OK

```
