# [System Name] — System Design

## 1. Understanding the Problem

**What is it:** One or two sentences describing the product/system and the core user-facing behavior.

### Functional Requirements
1. Users should be able to ___
2. Users should be able to ___
3. Users should be able to ___

**Below the line (out of scope):**
- ___
- ___

### Non-Functional Requirements
1. The system should be [highly available / strongly consistent] — state the tradeoff explicitly.
2. [Action] should return in < ___ ms.
3. The system should support ___ users / ___ requests per second.
4. [Any other scale/consistency/durability constraint, with numbers.]

---

## 2. The Set Up

### Planning the Approach
One paragraph: what's the hardest part of this problem, and what order will you tackle the functional requirements in? (Usually: walk them in order, flag scaling problems as you go, solve them in deep dives.)

### Capacity Estimation (Back-of-the-Envelope)
> Keep this small — just enough numbers to justify later technology decisions (e.g. "this is why we need a cache" or "this is why one SQL instance won't cut it").

| Metric | Estimate | How derived |
|---|---|---|
| Total users (DAU/MAU) | ___ | given/assumed |
| Writes/sec (e.g. posts created) | ___ | DAU × avg posts/day ÷ 86,400 |
| Reads/sec (e.g. feed views) | ___ | DAU × avg views/day ÷ 86,400 |
| Read:Write ratio | ___:1 | reads ÷ writes |
| Storage/item | ___ KB | field sizes summed |
| Storage growth/day | ___ GB | writes/day × storage/item |
| Storage growth/year | ___ TB | ×365 |
| Bandwidth (peak) | ___ MB/s | peak QPS × avg payload size |

**Example:** `500M DAU × 2 posts/day ÷ 86,400s ≈ 11.5K writes/sec` → single relational instance won't handle this, so we need to shard or pick a horizontally-scalable store.

### Core Entities
1. **Entity A** — one-line description
2. **Entity B** — one-line description
3. **Entity C** — one-line description

**Example schema (illustrative — adjust per problem):**
```
Post
├── id            : string (partition key)
├── authorId       : string
├── content        : string
├── createdAt      : datetime (sort key / index)
└── mediaUrls      : string[]
```

### API / System Interface
One endpoint per functional requirement. For each, note *why* (idempotency, pagination cursor, auth assumption, etc.)

```
POST /___      -> creates ___
PUT  /___/:id  -> idempotent action, e.g. follow
GET  /___?cursor=___&limit=___ -> paginated read
```

---

## Technology Decision Format

> Use this bullet format **every time** you pick between two or more technologies (SQL vs NoSQL, cache vs no cache, queue vs direct call, etc.). Drop one of these blocks inline wherever a workflow or deep dive calls for "Component & data store choice."

**Decision: ___ (e.g. "Posts store: PostgreSQL vs. DynamoDB")**
- **Chosen:** ___
- **Why not [alternative]:** ___
- **Why [chosen]:**
  - ___ (e.g. access pattern fit — single-key lookups, no joins needed)
  - ___ (e.g. scale requirement — need horizontal write throughput)
  - ___ (e.g. consistency requirement — can tolerate eventual consistency)
- **Tradeoff accepted:** ___ (what you give up by choosing this)

**Cloud reference (Microsoft/Azure) — use the concrete service name, not the generic concept, when it helps your own understanding:**

| Generic concept | Azure option | Notes |
|---|---|---|
| Relational / SQL store | Azure SQL Database, Azure Database for PostgreSQL | Use when you need joins, transactions, strong schema |
| NoSQL key-value / document store | Azure Cosmos DB (SQL/Mongo/Cassandra API) | Use for horizontal scale, flexible schema, global distribution |
| Wide-column / high-throughput writes | Cosmos DB (Cassandra API), Azure Table Storage | Use for simple key-based access at massive scale |
| In-memory cache | Azure Cache for Redis | Use for hot-key reads, precomputed feeds, session data |
| Blob / media storage | Azure Blob Storage | Use for images, video, large objects (store URL, not blob, in DB) |
| Message queue (point-to-point) | Azure Service Bus (queues) | Use for reliable task processing, ordering, dead-lettering |
| Event streaming / fan-out | Azure Event Hubs, Event Grid | Use for high-throughput pub/sub, fan-out-on-write pipelines |
| API entry point | Azure API Management + Azure Front Door | Gateway, rate limiting, global routing |
| Compute (stateless services) | Azure App Service, Azure Kubernetes Service (AKS), Azure Functions | Functions for event-driven/bursty work, AKS for complex microservices |
| Search / ranking | Azure AI Search | Use for full-text / vector / hybrid search over feed or content |
| CDN | Azure CDN / Front Door | Use for static asset and media delivery close to users |

**Example decision using this table:**
> "Precomputed Feed store: Azure Cosmos DB vs. Azure SQL Database — **chosen: Cosmos DB** because (1) access pattern is a single partition-key lookup by userId, (2) we need to sustain >10K writes/sec during fan-out, which a single SQL instance can't do without heavy sharding, (3) we can tolerate eventual consistency per our non-functional requirements. **Tradeoff:** no joins/ad-hoc queries — fine since this table is write-optimized and queried one way only."

---

## 3. High-Level Design

> Organize by **workflow** (one workflow = one functional requirement's end-to-end path, e.g. "Create Post", "Follow User", "View Feed", "Page Feed"). For each workflow: diagram the request path, name the components/DB choice and why (using the Technology Decision format above), and explicitly flag (but don't yet solve) any scaling problems you notice.

### Workflow 1: ___
- **Flow diagram:** `diagrams/workflow-1-___.excalidraw` (+ exported `.png`)
- Request path (step by step, matching the diagram's numbered arrows)
- **Technology Decision(s):** _(use format above — e.g. SQL vs NoSQL for this workflow's primary store)_
- ⚠️ Known issue to revisit in Deep Dives: ___

### Workflow 2: ___
- **Flow diagram:** `diagrams/workflow-2-___.excalidraw` (+ exported `.png`)
- Request path
- **Technology Decision(s):** _(use format above)_
- ⚠️ Known issue to revisit in Deep Dives: ___

### Workflow 3: ___
- **Flow diagram:** `diagrams/workflow-3-___.excalidraw` (+ exported `.png`)
- Request path
- **Technology Decision(s):** _(use format above)_
- ⚠️ Known issue to revisit in Deep Dives: ___

### Workflow 4: ___
- **Flow diagram:** `diagrams/workflow-4-___.excalidraw` (+ exported `.png`)
- Request path
- **Technology Decision(s):** _(use format above)_

---

## 4. Potential Deep Dives

> One deep dive **per workflow** (not a generic bottleneck list) — take the ⚠️ issue flagged under that workflow in section 3 and resolve it. Each deep dive gets its own updated flow diagram showing the fix layered onto the original workflow diagram, and uses the Technology Decision format whenever choosing between solutions.

### Deep Dive — Workflow 1: ___
- **Problem:** ___
- **Updated flow diagram:** `diagrams/deepdive-1-___.excalidraw` (+ exported `.png`) — shows the new/changed components vs. the Workflow 1 diagram
- **Technology Decision:** _(use format above — e.g. "Option A: queue vs. Option B: direct fan-out write", with bullet reasons for the chosen one)_
- **Back-of-envelope math** (storage size, cost/user, QPS, latency impact)

### Deep Dive — Workflow 2: ___
- **Problem:** ___
- **Updated flow diagram:** `diagrams/deepdive-2-___.excalidraw` (+ exported `.png`)
- **Technology Decision:** _(use format above)_
- **Back-of-envelope math**

### Deep Dive — Workflow 3: ___
- **Problem:** ___
- **Updated flow diagram:** `diagrams/deepdive-3-___.excalidraw` (+ exported `.png`)
- **Technology Decision:** _(use format above)_
- **Back-of-envelope math**

### Deep Dive — Workflow 4: ___
- **Problem:** ___
- **Updated flow diagram:** `diagrams/deepdive-4-___.excalidraw` (+ exported `.png`)
- **Technology Decision:** _(use format above)_
- **Back-of-envelope math**

### Final Design
- One consolidated Excalidraw diagram merging every workflow + its deep-dive fix: `diagrams/final-design.excalidraw` (+ exported `.png`)

---

## 5. What's Expected at Each Level

### Mid-level
- Breadth over depth (~80/20). Functional, complete high-level design. Surface-level familiarity with components is fine.

### Senior
- ~60/40 breadth/depth. Should speed through high-level design to spend real time on 2+ deep dives, articulating tradeoffs and proactively surfacing fan-out/bottleneck issues.

### Staff+
- ~40/60 breadth/depth. Deep, experience-backed reasoning on technology choices; should breeze through the basics and spend most time on nuanced tradeoffs across multiple deep dives.
