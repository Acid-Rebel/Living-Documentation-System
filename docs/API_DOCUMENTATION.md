# Living Documentation System — API Documentation

> **Version:** 1.0.0  
> **Base URL:** `http://localhost:8001` (configurable via `SERVER_BASE_URL`)  
> **Framework:** FastAPI (Python 3.13) + Next.js Frontend Proxy  
> **Transport:** REST (HTTP/1.1) + WebSocket  
> **Date:** March 2026

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Authentication](#2-authentication)
3. [Data Models](#3-data-models)
4. [Core API Endpoints](#4-core-api-endpoints)
   - [Health & Root](#41-health--root)
   - [Authentication](#42-authentication)
   - [Model Configuration](#43-model-configuration)
   - [Language Configuration](#44-language-configuration)
   - [Wiki Cache Management](#45-wiki-cache-management)
   - [Processed Projects](#46-processed-projects)
   - [Wiki Export](#47-wiki-export)
   - [Local Repository](#48-local-repository)
   - [Chat Completions (Streaming)](#49-chat-completions-streaming)
   - [WebSocket Chat](#410-websocket-chat)
5. [Living Docs Engine (LDS) Endpoints](#5-living-docs-engine-lds-endpoints)
   - [Drift Report](#51-drift-report)
   - [Semantic Insights](#52-semantic-insights)
   - [Dependency Analysis](#53-dependency-analysis)
   - [AI-Enhanced Diagrams](#54-ai-enhanced-diagrams)
   - [NLP Summary](#55-nlp-summary)
   - [Pull Request Management](#56-pull-request-management)
   - [GitHub Webhook](#57-github-webhook)
   - [Manual Update Check](#58-manual-update-check)
6. [Frontend Proxy Routes (Next.js)](#6-frontend-proxy-routes-nextjs)
7. [Environment Variables](#7-environment-variables)
8. [Error Handling](#8-error-handling)
9. [Sequence Diagrams](#9-sequence-diagrams)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Port 3000)              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ /api/auth │ │/api/chat │ │/api/wiki │ │/api/models    │  │
│  │  /status  │ │ /stream  │ │/projects │ │   /config     │  │
│  └─────┬─────┘ └─────┬────┘ └─────┬────┘ └──────┬────────┘  │
│        │             │            │              │           │
└────────┼─────────────┼────────────┼──────────────┼───────────┘
         │ HTTP Proxy  │            │              │
         ▼             ▼            ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Port 8001)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    core/api.py                        │   │
│  │  /health  /auth/*  /models/config  /export/wiki      │   │
│  │  /api/wiki_cache  /api/processed_projects            │   │
│  │  /chat/completions/stream  /ws/chat                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            core/lds_router.py (/api/lds/*)            │   │
│  │  /drift-report  /semantic-insights                    │   │
│  │  /dependency-analysis  /diagrams  /nlp-summary       │   │
│  │  /pull-requests  /webhook/github  /check-updates     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │  RAG Pipeline │  │ LLM Providers  │  │ GitHub API     │  │
│  │  (AdalFlow)   │  │ Google/OpenAI  │  │ Integration    │  │
│  │              │  │ OpenRouter/    │  │                │  │
│  │              │  │ Ollama/Bedrock │  │                │  │
│  └──────────────┘  └────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication

The system employs an **optional** authorization-code mechanism configured via environment variables.

| Variable | Description |
|---|---|
| `DEEPWIKI_AUTH_MODE` | Set to `true` to enable authentication gating |
| `DEEPWIKI_AUTH_CODE` | Secret code required when auth mode is active |

When enabled, mutation endpoints (e.g., cache deletion) require the authorization code.

---

## 3. Data Models

All request/response bodies are validated with **Pydantic v2** models.

### 3.1 `RepoInfo`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `owner` | `string` | ✅ | Repository owner/organization |
| `repo` | `string` | ✅ | Repository name |
| `type` | `string` | ✅ | Platform: `github`, `gitlab`, `bitbucket` |
| `token` | `string` | ❌ | Personal access token for private repos |
| `localPath` | `string` | ❌ | Path to a local repository |
| `repoUrl` | `string` | ❌ | Full URL of the repository |

### 3.2 `WikiPage`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique page identifier |
| `title` | `string` | Page title |
| `content` | `string` | Markdown content |
| `filePaths` | `string[]` | Associated source-file paths |
| `importance` | `string` | `"high"` \| `"medium"` \| `"low"` |
| `relatedPages` | `string[]` | IDs of related pages |

### 3.3 `WikiStructureModel`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Structure identifier |
| `title` | `string` | Wiki title |
| `description` | `string` | Wiki description |
| `pages` | `WikiPage[]` | All wiki pages |
| `sections` | `WikiSection[]` | _(optional)_ Section groupings |
| `rootSections` | `string[]` | _(optional)_ Top-level section IDs |

### 3.4 `ChatCompletionRequest`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `repo_url` | `string` | _(required)_ | Repository URL to query |
| `messages` | `ChatMessage[]` | _(required)_ | Conversation history |
| `filePath` | `string` | `null` | Focus on a specific file |
| `token` | `string` | `null` | Access token for private repos |
| `type` | `string` | `"github"` | Repository platform type |
| `provider` | `string` | `"google"` | LLM provider (see §7) |
| `model` | `string` | `null` | Specific model override |
| `language` | `string` | `"en"` | Response language code |
| `excluded_dirs` | `string` | `null` | Newline-separated dirs to exclude |
| `excluded_files` | `string` | `null` | Newline-separated files to exclude |
| `included_dirs` | `string` | `null` | Newline-separated dirs to include |
| `included_files` | `string` | `null` | Newline-separated files to include |

### 3.5 `ChatMessage`

| Field | Type | Description |
|-------|------|-------------|
| `role` | `string` | `"user"` or `"assistant"` |
| `content` | `string` | Message body text |

### 3.6 `PRCreateRequest`

| Field | Type | Description |
|-------|------|-------------|
| `title` | `string` | Pull request title |
| `description` | `string` | PR description body |
| `doc_content` | `string` | Updated documentation content |
| `author` | `string` | Author name |
| `repo_owner` | `string` | Repository owner |
| `repo_name` | `string` | Repository name |

### 3.7 `PRReviewRequest`

| Field | Type | Description |
|-------|------|-------------|
| `reviewer` | `string` | Reviewer name |
| `status` | `string` | `"APPROVED"` or `"CHANGES_REQUESTED"` |
| `comment` | `string` | _(optional)_ Review comment |

---

## 4. Core API Endpoints

### 4.1 Health & Root

#### `GET /health`

Health check endpoint for monitoring and Docker orchestration.

**Response `200 OK`:**

```json
{
  "status": "healthy",
  "timestamp": "2026-03-11T10:00:00.000000",
  "service": "deepwiki-api"
}
```

#### `GET /`

Root endpoint that dynamically lists all registered API routes.

**Response `200 OK`:**

```json
{
  "message": "Welcome to Streaming API",
  "version": "1.0.0",
  "endpoints": {
    "Health": ["GET /health"],
    "Auth": ["GET /auth/status", "POST /auth/validate"],
    "Api": ["GET /api/wiki_cache", "POST /api/wiki_cache", "DELETE /api/wiki_cache", "GET /api/processed_projects"]
  }
}
```

---

### 4.2 Authentication

#### `GET /auth/status`

Check if authentication is required for the application.

**Response `200 OK`:**

```json
{ "auth_required": false }
```

#### `POST /auth/validate`

Validate an authorization code.

**Request Body:**

```json
{ "code": "your-secret-code" }
```

**Response `200 OK`:**

```json
{ "success": true }
```

---

### 4.3 Model Configuration

#### `GET /models/config`

Returns all available LLM providers and their models.

**Response `200 OK`:**

```json
{
  "providers": [
    {
      "id": "google",
      "name": "Google",
      "supportsCustomModel": true,
      "models": [
        { "id": "gemini-2.5-flash", "name": "gemini-2.5-flash" }
      ]
    },
    {
      "id": "openai",
      "name": "Openai",
      "supportsCustomModel": false,
      "models": [
        { "id": "gpt-4o", "name": "gpt-4o" }
      ]
    }
  ],
  "defaultProvider": "google"
}
```

---

### 4.4 Language Configuration

#### `GET /lang/config`

Returns the list of supported languages for wiki generation.

**Response `200 OK`:**

```json
{
  "supported_languages": {
    "en": "English",
    "ja": "Japanese (日本語)",
    "zh": "Mandarin Chinese (中文)",
    "es": "Spanish (Español)",
    "kr": "Korean (한국어)",
    "vi": "Vietnamese (Tiếng Việt)",
    "fr": "Français (French)",
    "ru": "Русский (Russian)"
  },
  "default": "en"
}
```

---

### 4.5 Wiki Cache Management

#### `GET /api/wiki_cache`

Retrieve cached wiki data for a repository.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | `string` | ✅ | Repository owner |
| `repo` | `string` | ✅ | Repository name |
| `repo_type` | `string` | ✅ | `github`, `gitlab`, etc. |
| `language` | `string` | ✅ | Language code (e.g., `en`) |

**Response `200 OK`:** Returns `WikiCacheData` object or `null` if not found.

```json
{
  "wiki_structure": { "id": "...", "title": "...", "description": "...", "pages": [...] },
  "generated_pages": { "page-1": { "id": "page-1", "title": "...", "content": "..." } },
  "repo": { "owner": "user", "repo": "project", "type": "github" },
  "provider": "google",
  "model": "gemini-2.5-flash"
}
```

#### `POST /api/wiki_cache`

Store generated wiki data in the server-side cache.

**Request Body:** `WikiCacheRequest`

```json
{
  "repo": { "owner": "user", "repo": "project", "type": "github" },
  "language": "en",
  "wiki_structure": { "id": "...", "title": "...", "description": "...", "pages": [] },
  "generated_pages": {},
  "provider": "google",
  "model": "gemini-2.5-flash"
}
```

**Response `200 OK`:**

```json
{ "message": "Wiki cache saved successfully" }
```

#### `DELETE /api/wiki_cache`

Delete a specific wiki cache entry.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | `string` | ✅ | Repository owner |
| `repo` | `string` | ✅ | Repository name |
| `repo_type` | `string` | ✅ | Repository type |
| `language` | `string` | ✅ | Language code |
| `authorization_code` | `string` | ❌ | Required if auth mode is enabled |

**Response `200 OK`:**

```json
{ "message": "Wiki cache for user/project (en) deleted successfully" }
```

**Error Responses:**

| Code | Description |
|------|-------------|
| `400` | Unsupported language |
| `401` | Invalid authorization code (when auth mode is on) |
| `404` | Cache not found |
| `500` | Internal server error |

---

### 4.6 Processed Projects

#### `GET /api/processed_projects`

List all previously processed projects from the wiki cache directory.

**Response `200 OK`:**

```json
[
  {
    "id": "deepwiki_cache_github_user_project_en.json",
    "owner": "user",
    "repo": "project",
    "name": "user/project",
    "repo_type": "github",
    "submittedAt": 1741680000000,
    "language": "en"
  }
]
```

> **Note:** Results are sorted by `submittedAt` (most recent first).

---

### 4.7 Wiki Export

#### `POST /export/wiki`

Export wiki content as a downloadable Markdown or JSON file.

**Request Body:**

```json
{
  "repo_url": "https://github.com/user/project",
  "pages": [
    {
      "id": "page-1",
      "title": "Getting Started",
      "content": "## Introduction\n...",
      "filePaths": ["src/main.py"],
      "importance": "high",
      "relatedPages": ["page-2"]
    }
  ],
  "format": "markdown"
}
```

**Response:** File download with `Content-Disposition: attachment` header.

| Format | Content-Type | Filename Pattern |
|--------|-------------|-----------------|
| `markdown` | `text/markdown` | `{repo}_wiki_{timestamp}.md` |
| `json` | `application/json` | `{repo}_wiki_{timestamp}.json` |

---

### 4.8 Local Repository

#### `GET /local_repo/structure`

Return the file tree and README content for a local repository.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | `string` | ✅ | Absolute path to the local repo |

**Response `200 OK`:**

```json
{
  "file_tree": "src/main.py\nsrc/utils.py\nREADME.md",
  "readme": "# Project Name\nProject description..."
}
```

**Error Responses:**

| Code | Description |
|------|-------------|
| `400` | No path provided |
| `404` | Directory not found |
| `500` | Error processing repository |

---

### 4.9 Chat Completions (Streaming)

#### `POST /chat/completions/stream`

Stream a RAG-powered chat completion response. Supports Deep Research mode (multi-turn iterative analysis).

**Request Body:** `ChatCompletionRequest` (see §3.4)

**Response:** `text/event-stream` (Server-Sent Events)

The response streams text chunks directly. SSE heartbeats (`: heartbeat\n\n`) are sent during retriever initialization to prevent HTTP timeout.

**Supported LLM Providers:**

| Provider ID | Service | Environment Variable |
|-------------|---------|---------------------|
| `google` | Google Gemini | `GOOGLE_API_KEY` |
| `openai` | OpenAI | `OPENAI_API_KEY` |
| `openrouter` | OpenRouter | `OPENROUTER_API_KEY` |
| `ollama` | Ollama (local) | _(none — runs locally)_ |
| `bedrock` | AWS Bedrock | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| `azure` | Azure OpenAI | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| `dashscope` | Alibaba DashScope | `DASHSCOPE_API_KEY` |

**Deep Research Mode:**

Prefix the user message with `[DEEP RESEARCH]` to enable multi-turn research. The system will:
1. **Iteration 1:** Create a research plan and initial findings
2. **Iterations 2–4:** Progressive deep-dive into specific aspects
3. **Iteration 5+:** Synthesize all findings into a final conclusion

**Example Request:**

```bash
curl -X POST http://localhost:8001/chat/completions/stream \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/project",
    "messages": [{"role": "user", "content": "Explain the authentication flow"}],
    "provider": "google",
    "language": "en"
  }'
```

---

### 4.10 WebSocket Chat

#### `WS /ws/chat`

WebSocket endpoint providing real-time, bidirectional chat with the same RAG pipeline as the HTTP streaming endpoint.

**Connection:** `ws://localhost:8001/ws/chat`

**Client → Server (JSON):**

```json
{
  "repo_url": "https://github.com/user/project",
  "messages": [{ "role": "user", "content": "What does this repo do?" }],
  "provider": "google",
  "language": "en"
}
```

**Server → Client:** Sequential text frames containing streamed response chunks.

**Connection Lifecycle:**
1. Client opens WebSocket connection
2. Client sends a single JSON message with the `ChatCompletionRequest` payload
3. Server streams response as multiple text frames
4. Server closes the connection upon completion

---

## 5. Living Docs Engine (LDS) Endpoints

All LDS endpoints are prefixed with `/api/lds` and tagged as `Living Docs Engine`.

### 5.1 Drift Report

#### `GET /api/lds/drift-report`

Analyze documentation drift by comparing code modules against documentation coverage.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `owner` | `string` | _(required)_ | Repository owner |
| `repo` | `string` | _(required)_ | Repository name |
| `repo_type` | `string` | `"github"` | Repository platform |

**Response `200 OK`:**

```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_findings": 3,
      "high_severity": 1,
      "medium_severity": 1,
      "low_severity": 1,
      "files_analyzed": 45,
      "code_files": 30,
      "doc_files": 5
    },
    "findings": [
      {
        "id": "drift-1",
        "type": "MissingDocumentation",
        "severity": "high",
        "description": "Repository has no root-level README file.",
        "file": "/"
      },
      {
        "id": "drift-2",
        "type": "MissingDocumentation",
        "severity": "medium",
        "description": "Module 'core/' contains source code but has no documentation files.",
        "file": "core/"
      }
    ]
  }
}
```

**Finding Types:**

| Type | Severity | Trigger |
|------|----------|---------|
| `MissingDocumentation` | `high` | No root README |
| `MissingDocumentation` | `medium` | Code module without docs |
| `ConfigUndocumented` | `low` | Config files without a `docs/` directory |

---

### 5.2 Semantic Insights

#### `GET /api/lds/semantic-insights`

Derive structural semantics from the repository file tree — module complexity, cross-module relationships, and primary language.

**Query Parameters:** Same as [§5.1](#51-drift-report).

**Response `200 OK`:**

```json
{
  "status": "success",
  "data": {
    "symbols": [
      {
        "name": "core",
        "type": "module",
        "complexity": "high",
        "file_count": 18,
        "language": "Python"
      }
    ],
    "relations": [
      { "source": "core", "target": "frontend", "type": "imports" }
    ],
    "primary_language": "Python",
    "total_code_files": 42
  }
}
```

---

### 5.3 Dependency Analysis

#### `GET /api/lds/dependency-analysis`

Analyze internal module dependencies and detect external package managers.

**Query Parameters:** Same as [§5.1](#51-drift-report).

**Response `200 OK`:**

```json
{
  "status": "success",
  "data": {
    "modules": [
      { "name": "core", "dependencies": ["frontend"] },
      { "name": "frontend", "dependencies": [] }
    ],
    "external_packages": [
      "npm packages (see package.json)",
      "pip packages (see requirements.txt)"
    ],
    "total_files": 120,
    "primary_language": "Python"
  }
}
```

---

### 5.4 AI-Enhanced Diagrams

#### `GET /api/lds/diagrams`

Generate Mermaid.js diagrams from deep file-structure analysis.

**Query Parameters:** Same as [§5.1](#51-drift-report).

**Response `200 OK`:**

```json
{
  "status": "success",
  "data": {
    "class_diagram": "graph LR\n    subgraph core_grp[\"core (Module)\"]\n        core_models[\"fa:fa-database Models\"]\n    end",
    "dependency_diagram": "graph TD\n    Client([\"fa:fa-user Client / Browser\"])\n    ...",
    "call_diagram": "sequenceDiagram\n    actor User\n    ...",
    "diagram_types": ["class", "dependency", "call"]
  }
}
```

**Diagram Types:**

| Key | Description | Mermaid Type |
|-----|-------------|-------------|
| `class_diagram` | Internal module structure & components | `graph LR` |
| `dependency_diagram` | High-level architecture / dependency graph | `graph TD` |
| `call_diagram` | Request flow / sequence diagram | `sequenceDiagram` |

**Framework-Aware:** The system auto-detects frameworks (Django, FastAPI, Flask, Next.js, Express, React, Spring, Rails) and generates context-specific diagrams.

---

### 5.5 NLP Summary

#### `GET /api/lds/nlp-summary`

Generate a natural-language summary of the repository structure.

**Query Parameters:** Same as [§5.1](#51-drift-report).

**Response `200 OK`:**

```json
{
  "status": "success",
  "data": {
    "overview": "This repository contains 120 total files: 80 source code, 10 documentation...",
    "primary_language": "Python",
    "total_files": 120,
    "code_files": 80,
    "doc_files": 10,
    "config_files": 8,
    "frontend_files": 22,
    "module_count": 5,
    "module_summaries": [
      {
        "name": "core",
        "file_count": 18,
        "extensions": ".py",
        "complexity": "high",
        "description": "Module 'core' contains 18 source file(s) (.py). Complexity: high."
      }
    ],
    "key_findings": [
      "Large codebase with significant engineering investment.",
      "Documentation is present with 10 doc file(s)."
    ]
  }
}
```

---

### 5.6 Pull Request Management

Documentation pull requests can be created manually or auto-generated by the system on new commits.

#### `POST /api/lds/pull-requests`

Create a new documentation PR (optionally pushes to GitHub).

**Request Body:** `PRCreateRequest` (see §3.6)

**Response `200 OK`:**

```json
{
  "status": "success",
  "data": {
    "id": "pr-1",
    "title": "docs: update README",
    "status": "OPEN",
    "author": "developer",
    "created_at": "2026-03-11T10:00:00+00:00",
    "github_pr": {
      "number": 42,
      "html_url": "https://github.com/user/project/pull/42",
      "branch": "docs/auto-update-1741680000",
      "state": "open"
    }
  }
}
```

#### `GET /api/lds/pull-requests`

List all documentation pull requests.

**Query Parameters (optional):**

| Parameter | Type | Description |
|-----------|------|-------------|
| `repo_owner` | `string` | Filter by repo owner |
| `repo_name` | `string` | Filter by repo name |

#### `GET /api/lds/pull-requests/{pr_id}`

Get details of a specific pull request.

#### `POST /api/lds/pull-requests/{pr_id}/review`

Add a review to a pull request.

**Request Body:** `PRReviewRequest` (see §3.7)

**Status Transitions:**
- `APPROVED` → PR status becomes `APPROVED`
- `CHANGES_REQUESTED` → PR status becomes `REJECTED`

#### `POST /api/lds/pull-requests/{pr_id}/merge`

Merge a pull request. If linked to a GitHub PR, merges on GitHub via squash merge.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `merged_by` | `string` | `"user"` | Who performed the merge |

**PR Status Lifecycle:**

```
OPEN → APPROVED → MERGED
OPEN → REJECTED
OPEN → CLOSED
```

#### `POST /api/lds/pull-requests/{pr_id}/close`

Close a pull request without merging.

---

### 5.7 GitHub Webhook

#### `POST /api/lds/webhook/github`

Receive GitHub push webhooks and trigger automatic documentation updates.

**Setup:**
1. Go to GitHub repo → Settings → Webhooks
2. **Payload URL:** `https://<your-host>/api/lds/webhook/github`
3. **Content type:** `application/json`
4. **Secret:** Set `LDS_WEBHOOK_SECRET` env var (optional)
5. **Events:** Select "Just the push event"

**Headers Used:**

| Header | Purpose |
|--------|---------|
| `X-Hub-Signature-256` | HMAC signature verification |
| `X-GitHub-Event` | Event type (`push`, `ping`) |

**Response Codes:**

| Status | Body | Condition |
|--------|------|-----------|
| `200` | `{"status": "pong"}` | Ping event |
| `200` | `{"status": "accepted", ...}` | Push to default branch |
| `200` | `{"status": "ignored", ...}` | Non-default branch or bot commit |
| `403` | Error | Invalid webhook signature |

---

### 5.8 Manual Update Check

#### `POST /api/lds/check-updates`

Manually trigger a check for new commits and auto-generate doc update.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `owner` | `string` | _(required)_ | Repository owner |
| `repo` | `string` | _(required)_ | Repository name |
| `repo_type` | `string` | `"github"` | Repository platform |

**Response States:**

| Status Value | Description |
|-------------|-------------|
| `initialized` | First check — tracking started |
| `no_change` | No new commits since last check |
| `update_triggered` | New commit detected, doc update scheduled |
| `error` | Could not fetch latest commit |

---

## 6. Frontend Proxy Routes (Next.js)

The Next.js frontend proxies requests to the FastAPI backend. These routes handle CORS and forward requests transparently.

| Frontend Route | Method | Backend Target |
|---------------|--------|---------------|
| `/api/auth/status` | `GET` | `/auth/status` |
| `/api/auth/validate` | `POST` | `/auth/validate` |
| `/api/models/config` | `GET` | `/models/config` |
| `/api/chat/stream` | `POST` | `/chat/completions/stream` |
| `/api/wiki/projects` | `GET` | `/api/processed_projects` |
| `/api/wiki/projects` | `DELETE` | `/api/wiki_cache` (DELETE) |

---

## 7. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ | Google Gemini API key (default provider) |
| `OPENAI_API_KEY` | ❌ | OpenAI API key |
| `OPENROUTER_API_KEY` | ❌ | OpenRouter API key |
| `AWS_ACCESS_KEY_ID` | ❌ | AWS credentials for Bedrock |
| `AWS_SECRET_ACCESS_KEY` | ❌ | AWS credentials for Bedrock |
| `AWS_REGION` | ❌ | AWS region for Bedrock |
| `AZURE_OPENAI_API_KEY` | ❌ | Azure OpenAI key |
| `AZURE_OPENAI_ENDPOINT` | ❌ | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_VERSION` | ❌ | Azure OpenAI API version |
| `DASHSCOPE_API_KEY` | ❌ | Alibaba DashScope key |
| `GITHUB_TOKEN` | ❌ | GitHub PAT for API calls & PR creation |
| `LDS_WEBHOOK_SECRET` | ❌ | Secret for webhook signature verification |
| `DEEPWIKI_AUTH_MODE` | ❌ | Enable auth gating (`true`/`false`) |
| `DEEPWIKI_AUTH_CODE` | ❌ | Authorization code when auth is enabled |
| `DEEPWIKI_EMBEDDER_TYPE` | ❌ | Embedder backend: `openai`, `google`, `ollama`, `bedrock` |
| `DEEPWIKI_CONFIG_DIR` | ❌ | Custom config directory path |
| `SERVER_BASE_URL` | ❌ | Backend URL for Next.js proxy (default: `http://localhost:8001`) |
| `REPO_OWNER` | ❌ | Auto-poll target repo owner |
| `REPO_NAME` | ❌ | Auto-poll target repo name |

---

## 8. Error Handling

All API errors follow a consistent pattern:

### HTTP Error Responses

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|------------|---------|
| `400` | Bad Request — invalid parameters or unsupported values |
| `401` | Unauthorized — invalid authorization code |
| `403` | Forbidden — invalid webhook signature |
| `404` | Not Found — resource does not exist |
| `500` | Internal Server Error — unexpected failure |
| `503` | Service Unavailable — backend unreachable (from proxy) |

### Streaming Error Responses

In streaming endpoints, errors are sent as SSE data events:

```
data: {"error": "No valid document embeddings found."}
```

---

## 9. Sequence Diagrams

### Wiki Generation Flow

```
Client              Frontend (Next.js)         Backend (FastAPI)          GitHub API         LLM Provider
  │                       │                         │                       │                    │
  │──GET /api/wiki/───────▶│                         │                       │                    │
  │  projects              │──GET /api/──────────────▶│                       │                    │
  │                        │  processed_projects     │                       │                    │
  │                        │◀─────────JSON───────────│                       │                    │
  │◀──────JSON─────────────│                         │                       │                    │
  │                        │                         │                       │                    │
  │──POST /api/chat/──────▶│                         │                       │                    │
  │  stream                │──POST /chat/────────────▶│                       │                    │
  │                        │  completions/stream     │──Fetch repo tree──────▶│                    │
  │                        │                         │◀─────file list────────│                    │
  │                        │                         │──RAG retrieval────────────────────────────▶│
  │                        │                         │◀───embeddings─────────────────────────────│
  │                        │                         │──Stream LLM──────────────────────────────▶│
  │◀──SSE stream───────────│◀──SSE stream────────────│◀──token stream────────────────────────────│
  │                        │                         │                       │                    │
```

### Automated Documentation Update Flow

```
GitHub                    Backend (FastAPI)                    GitHub API
  │                            │                                  │
  │──POST /api/lds/────────────▶│                                  │
  │  webhook/github            │                                  │
  │                            │──Fetch repo tree─────────────────▶│
  │                            │◀──file list──────────────────────│
  │                            │                                  │
  │                            │  [Analyze: drift, diagrams,      │
  │                            │   NLP summary, dependencies]     │
  │                            │                                  │
  │                            │──Generate updated README──────────│
  │                            │──Create branch───────────────────▶│
  │                            │──Update README on branch─────────▶│
  │                            │──Create Pull Request─────────────▶│
  │                            │◀──PR #{number}───────────────────│
  │◀───200 accepted────────────│                                  │
```

---

> _Auto-generated for the Living Documentation System by Shantharam — March 2026_
