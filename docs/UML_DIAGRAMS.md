# Living Documentation System — UML Diagrams

> **Project:** Living Documentation System  
> **Author:** Shantharam  
> **Date:** March 2026  
> **Tools:** Mermaid.js UML Notation

---

## Table of Contents

1. [Use Case Diagrams](#1-use-case-diagrams)
2. [Class Diagrams](#2-class-diagrams)
3. [Sequence Diagrams](#3-sequence-diagrams)

---

## 1. Use Case Diagrams

### 1.1 System-Level Use Case Diagram

```mermaid
graph TB
    subgraph Actors
        DEV["👤 Developer"]
        REVIEWER["👤 Reviewer"]
        GITHUB["🔗 GitHub Webhook"]
        ADMIN["👤 Admin"]
    end

    subgraph LDS["Living Documentation System"]
        UC1["Browse Repository Wiki"]
        UC2["Chat with Codebase"]
        UC3["Generate Wiki Pages"]
        UC4["Export Documentation"]
        UC5["Run Drift Report"]
        UC6["View Semantic Insights"]
        UC7["Analyze Dependencies"]
        UC8["Generate Architecture Diagrams"]
        UC9["Get NLP Summary"]
        UC10["Create Documentation PR"]
        UC11["Review Documentation PR"]
        UC12["Merge Documentation PR"]
        UC13["Trigger Auto-Update"]
        UC14["Configure LLM Providers"]
        UC15["Manage Wiki Cache"]
        UC16["Deep Research Analysis"]
        UC17["Authenticate"]
    end

    DEV --> UC1
    DEV --> UC2
    DEV --> UC3
    DEV --> UC4
    DEV --> UC5
    DEV --> UC6
    DEV --> UC7
    DEV --> UC8
    DEV --> UC9
    DEV --> UC10
    DEV --> UC16

    REVIEWER --> UC11
    REVIEWER --> UC12

    GITHUB --> UC13

    ADMIN --> UC14
    ADMIN --> UC15
    ADMIN --> UC17

    UC2 -.->|extends| UC16
    UC13 -.->|includes| UC10
    UC10 -.->|includes| UC5
```

### 1.2 Chat & RAG Use Cases

```mermaid
graph TB
    subgraph Actors
        USER["👤 User"]
    end

    subgraph ChatSystem["Chat Subsystem"]
        UC_CHAT["Chat with Repository"]
        UC_HTTP["HTTP Streaming Chat"]
        UC_WS["WebSocket Chat"]
        UC_RAG["RAG Context Retrieval"]
        UC_DEEP["Deep Research Mode"]
        UC_EMBED["Generate Embeddings"]
        UC_PROVIDER["Select LLM Provider"]
    end

    USER --> UC_CHAT

    UC_CHAT --> UC_HTTP
    UC_CHAT --> UC_WS

    UC_HTTP -.->|includes| UC_RAG
    UC_WS -.->|includes| UC_RAG
    UC_HTTP -.->|includes| UC_PROVIDER
    UC_HTTP -.->|extends| UC_DEEP

    UC_RAG -.->|includes| UC_EMBED
```

### 1.3 Documentation Intelligence Use Cases

```mermaid
graph TB
    subgraph Actors
        DEV["👤 Developer"]
        GH["🔗 GitHub"]
    end

    subgraph Intelligence["LDS Intelligence Engine"]
        UC_DRIFT["Generate Drift Report"]
        UC_SEMANTIC["Analyze Semantic Structure"]
        UC_DEPS["Analyze Dependencies"]
        UC_DIAG["Generate Diagrams"]
        UC_NLP["Generate NLP Summary"]
        UC_WEBHOOK["Receive Push Webhook"]
        UC_AUTO["Auto-Update Documentation"]
        UC_PR_CREATE["Create Documentation PR"]
        UC_PR_REVIEW["Review PR"]
        UC_PR_MERGE["Merge PR"]
        UC_PR_CLOSE["Close PR"]
        UC_FETCH["Fetch Repository Tree"]
    end

    DEV --> UC_DRIFT
    DEV --> UC_SEMANTIC
    DEV --> UC_DEPS
    DEV --> UC_DIAG
    DEV --> UC_NLP
    DEV --> UC_PR_CREATE
    DEV --> UC_PR_REVIEW
    DEV --> UC_PR_MERGE
    DEV --> UC_PR_CLOSE

    GH --> UC_WEBHOOK

    UC_WEBHOOK -.->|triggers| UC_AUTO
    UC_AUTO -.->|includes| UC_FETCH
    UC_AUTO -.->|includes| UC_PR_CREATE

    UC_DRIFT -.->|includes| UC_FETCH
    UC_SEMANTIC -.->|includes| UC_FETCH
    UC_DEPS -.->|includes| UC_FETCH
    UC_DIAG -.->|includes| UC_FETCH
    UC_NLP -.->|includes| UC_FETCH
```

---

## 2. Class Diagrams

### 2.1 Core Application & API Layer

```mermaid
classDiagram
    class FastAPIApp {
        -title: str
        -description: str
        +health() dict
        +root() dict
        +auth_status() dict
        +auth_validate(code) dict
        +get_models_config() dict
        +get_lang_config() dict
        +export_wiki(request) FileResponse
        +get_wiki_cache(owner, repo) WikiCacheData
        +save_wiki_cache(request) dict
        +delete_wiki_cache(owner, repo) dict
        +get_processed_projects() list
        +get_local_repo_structure(path) dict
        +start_polling() void
    }

    class WikiPage {
        +id: str
        +title: str
        +content: str
        +filePaths: list~str~
        +importance: str
        +relatedPages: list~str~
    }

    class WikiSection {
        +id: str
        +title: str
        +pages: list~str~
        +subsections: list~str~
    }

    class WikiStructureModel {
        +id: str
        +title: str
        +description: str
        +pages: list~WikiPage~
        +sections: list~WikiSection~
        +rootSections: list~str~
    }

    class RepoInfo {
        +owner: str
        +repo: str
        +type: str
        +token: str
        +localPath: str
        +repoUrl: str
    }

    class WikiCacheData {
        +wiki_structure: WikiStructureModel
        +generated_pages: dict
        +repo: RepoInfo
        +provider: str
        +model: str
    }

    class WikiCacheRequest {
        +repo: RepoInfo
        +language: str
        +wiki_structure: WikiStructureModel
        +generated_pages: dict
        +provider: str
        +model: str
    }

    class ExportRequest {
        +repo_url: str
        +pages: list~WikiPage~
        +format: str
    }

    class ModelConfig {
        +id: str
        +name: str
    }

    class ProviderConfig {
        +id: str
        +name: str
        +supportsCustomModel: bool
        +models: list~ModelConfig~
    }

    class ProcessedProjectEntry {
        +id: str
        +owner: str
        +repo: str
        +name: str
        +repo_type: str
        +submittedAt: int
        +language: str
    }

    FastAPIApp --> WikiCacheData : manages
    FastAPIApp --> ExportRequest : processes
    FastAPIApp --> ProcessedProjectEntry : lists
    WikiCacheData --> WikiStructureModel : contains
    WikiCacheData --> RepoInfo : references
    WikiStructureModel --> WikiPage : contains
    WikiStructureModel --> WikiSection : contains
    WikiCacheRequest --> RepoInfo : references
    WikiCacheRequest --> WikiStructureModel : references
    ProviderConfig --> ModelConfig : has many
```

### 2.2 RAG & Data Pipeline

```mermaid
classDiagram
    class RAG {
        -provider: str
        -model: str
        -embedder_type: str
        -is_ollama_embedder: bool
        -memory: Memory
        -embedder: Embedder
        -query_embedder: Callable
        -db_manager: DatabaseManager
        -transformed_docs: list~Document~
        -retriever: FAISSRetriever
        -generator: Generator
        +__init__(provider, model, use_s3)
        +initialize_db_manager() void
        +prepare_retriever(repo_url, type, token) void
        +call(query, language) tuple
        -_validate_and_filter_embeddings(documents) list
    }

    class Memory {
        -current_conversation: CustomConversation
        +call() dict
        +add_dialog_turn(user_query, response) bool
    }

    class CustomConversation {
        +dialog_turns: list~DialogTurn~
        +append_dialog_turn(dialog_turn) void
    }

    class DialogTurn {
        +id: str
        +user_query: UserQuery
        +assistant_response: AssistantResponse
    }

    class UserQuery {
        +query_str: str
    }

    class AssistantResponse {
        +response_str: str
    }

    class RAGAnswer {
        +rationale: str
        +answer: str
    }

    class DatabaseManager {
        -db: LocalDB
        -repo_url_or_path: str
        -repo_paths: str
        +prepare_database(repo_url, type, token) list~Document~
    }

    class FAISSRetriever {
        -embedder: Embedder
        -documents: list~Document~
        +__call__(query) RetrieverOutput
    }

    class Document {
        +text: str
        +meta_data: dict
        +vector: list~float~
    }

    class TextSplitter {
        +split_by: str
        +chunk_size: int
        +chunk_overlap: int
        +__call__(documents) list~Document~
    }

    class ToEmbeddings {
        -embedder: Embedder
        -batch_size: int
        +__call__(documents) list~Document~
    }

    RAG --> Memory : uses
    RAG --> DatabaseManager : uses
    RAG --> FAISSRetriever : queries
    RAG --> RAGAnswer : returns
    Memory --> CustomConversation : manages
    CustomConversation --> DialogTurn : contains
    DialogTurn --> UserQuery : has
    DialogTurn --> AssistantResponse : has
    DatabaseManager --> Document : processes
    FAISSRetriever --> Document : indexes
    TextSplitter --> Document : splits
    ToEmbeddings --> Document : embeds
```

### 2.3 LLM Provider Clients (Strategy Pattern)

```mermaid
classDiagram
    class ModelClient {
        <<abstract>>
        +convert_inputs_to_api_kwargs(input, kwargs, type)* dict
        +call(api_kwargs, model_type)* Any
        +acall(api_kwargs, model_type)* Any
        +parse_chat_completion(completion)* GeneratorOutput
        +parse_embedding_response(response)* EmbedderOutput
    }

    class OpenAIClient {
        -sync_client: OpenAI
        -async_client: AsyncOpenAI
        -base_url: str
        -chat_completion_parser: Callable
        +init_sync_client() OpenAI
        +init_async_client() AsyncOpenAI
        +call(api_kwargs, model_type) Any
        +acall(api_kwargs, model_type) Any
        +parse_chat_completion(completion) GeneratorOutput
        +parse_embedding_response(response) EmbedderOutput
        +track_completion_usage(completion) CompletionUsage
    }

    class OpenRouterClient {
        -api_key: str
        -base_url: str
        -session: aiohttp.ClientSession
        +call(api_kwargs, model_type) str
        +acall(api_kwargs, model_type) str
        +convert_inputs_to_api_kwargs(input, kwargs, type) dict
        -_process_xml_content(content) str
    }

    class BedrockClient {
        -aws_access_key_id: str
        -aws_secret_access_key: str
        -aws_region: str
        -aws_role_arn: str
        -sync_client: boto3.Client
        +init_sync_client() Client
        +call(api_kwargs, model_type) Any
        +acall(api_kwargs, model_type) Any
        -_get_model_provider(model_id) str
        -_format_prompt_for_provider(provider, prompt) dict
        -_extract_response_text(provider, response) str
    }

    class AzureAIClient {
        -api_type: str
        -sync_client: AzureOpenAI
        -async_client: AsyncAzureOpenAI
        +init_sync_client() AzureOpenAI
        +init_async_client() AsyncAzureOpenAI
        +call(api_kwargs, model_type) Any
        +acall(api_kwargs, model_type) Any
        +parse_chat_completion(completion) GeneratorOutput
    }

    class DashscopeClient {
        -sync_client: OpenAI
        -async_client: AsyncOpenAI
        -base_url: str
        +init_sync_client() OpenAI
        +init_async_client() AsyncOpenAI
        +call(api_kwargs, model_type) Any
        +acall(api_kwargs, model_type) Any
        +parse_chat_completion(completion) GeneratorOutput
        +parse_embedding_response(response) EmbedderOutput
    }

    class GoogleEmbedderClient {
        -_api_key: str
        +_initialize_client() void
        +call(api_kwargs, model_type) Any
        +acall(api_kwargs, model_type) Any
        +parse_embedding_response(response) EmbedderOutput
        +convert_inputs_to_api_kwargs(input, kwargs, type) dict
    }

    class OllamaDocumentProcessor {
        -embedder: Embedder
        +__call__(documents) list~Document~
    }

    class DashScopeEmbedder {
        -model_client: ModelClient
        -model_kwargs: dict
        +call(input) EmbedderOutput
        +acall(input) EmbedderOutput
    }

    class DashScopeBatchEmbedder {
        -embedder: DashScopeEmbedder
        -batch_size: int
        -cache_path: str
        +call(input) list~EmbedderOutput~
    }

    ModelClient <|-- OpenAIClient
    ModelClient <|-- OpenRouterClient
    ModelClient <|-- BedrockClient
    ModelClient <|-- AzureAIClient
    ModelClient <|-- DashscopeClient
    ModelClient <|-- GoogleEmbedderClient

    DashScopeEmbedder --> DashscopeClient : uses
    DashScopeBatchEmbedder --> DashScopeEmbedder : wraps
    OllamaDocumentProcessor --> Document : processes
```

### 2.4 LDS Intelligence Router

```mermaid
classDiagram
    class LDSRouter {
        -prefix: str = "/api/lds"
        -doc_prs: dict
        -repo_tree_cache: dict
        -last_known_commit: dict
        +drift_report(owner, repo, repo_type) dict
        +semantic_insights(owner, repo, repo_type) dict
        +dependency_analysis(owner, repo, repo_type) dict
        +diagrams(owner, repo, repo_type) dict
        +nlp_summary(owner, repo, repo_type) dict
        +create_pr(request: PRCreateRequest) dict
        +list_prs(repo_owner, repo_name) list
        +get_pr(pr_id) dict
        +review_pr(pr_id, request: PRReviewRequest) dict
        +merge_pr(pr_id, merged_by) dict
        +close_pr(pr_id) dict
        +github_webhook(request) dict
        +check_updates(owner, repo, repo_type) dict
    }

    class PRCreateRequest {
        +title: str
        +description: str
        +doc_content: str
        +author: str
        +repo_owner: str
        +repo_name: str
    }

    class PRReviewRequest {
        +reviewer: str
        +status: str
        +comment: str
    }

    class DocumentationPR {
        +id: str
        +title: str
        +description: str
        +doc_content: str
        +status: str
        +author: str
        +created_at: datetime
        +updated_at: datetime
        +reviews: list
        +github_pr: dict
    }

    class ChatCompletionRequest {
        +repo_url: str
        +messages: list~ChatMessage~
        +filePath: str
        +token: str
        +type: str
        +provider: str
        +model: str
        +language: str
        +excluded_dirs: str
        +excluded_files: str
        +included_dirs: str
        +included_files: str
    }

    class ChatMessage {
        +role: str
        +content: str
    }

    LDSRouter --> PRCreateRequest : receives
    LDSRouter --> PRReviewRequest : receives
    LDSRouter --> DocumentationPR : manages
    ChatCompletionRequest --> ChatMessage : contains
```

---

## 3. Sequence Diagrams

### 3.1 Chat Completion with RAG (HTTP Streaming)

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant Proxy as /api/chat/stream
    participant Backend as FastAPI Backend
    participant RAG as RAG Component
    participant DB as DatabaseManager
    participant FAISS as FAISSRetriever
    participant LLM as LLM Provider

    User->>Frontend: Send chat message
    Frontend->>Proxy: POST /api/chat/stream
    Proxy->>Backend: POST /chat/completions/stream

    Backend->>Backend: Parse ChatCompletionRequest
    Backend->>Backend: Check for Deep Research mode

    alt First request for this repo
        Backend->>RAG: prepare_retriever(repo_url)
        RAG->>DB: prepare_database(repo_url)
        DB->>DB: download_repo(repo_url)
        DB->>DB: read_all_documents(path)
        DB->>DB: transform_documents_and_save_to_db()
        DB-->>RAG: transformed_docs[]
        RAG->>RAG: _validate_and_filter_embeddings()
        RAG->>FAISS: Create FAISSRetriever(docs)
    end

    Backend->>Backend: Yield SSE heartbeat comments
    Backend->>FAISS: retriever(user_query)
    FAISS-->>Backend: retrieved_documents[]

    Backend->>Backend: Build system prompt + context
    Backend->>LLM: Stream completion request

    loop Token Streaming
        LLM-->>Backend: token chunk
        Backend-->>Proxy: SSE data chunk
        Proxy-->>Frontend: SSE data chunk
        Frontend-->>User: Render token
    end

    Backend->>RAG: memory.add_dialog_turn()
    Backend-->>Proxy: Stream complete
    Proxy-->>Frontend: Stream end
```

### 3.2 WebSocket Chat Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant WS as WebSocket /ws/chat
    participant RAG as RAG Component
    participant FAISS as FAISSRetriever
    participant LLM as LLM Provider

    User->>Frontend: Open chat
    Frontend->>WS: WebSocket CONNECT

    WS-->>Frontend: Connection Accepted

    User->>Frontend: Type message
    Frontend->>WS: Send JSON message

    WS->>WS: Parse request payload
    WS->>RAG: prepare_retriever(repo_url)
    RAG-->>WS: Retriever ready

    WS->>FAISS: retriever(query)
    FAISS-->>WS: relevant_documents[]

    WS->>WS: Construct prompt with context
    WS->>LLM: Request completion

    loop Token Streaming
        LLM-->>WS: token chunk
        WS-->>Frontend: Text frame (chunk)
        Frontend-->>User: Render incrementally
    end

    WS->>WS: Close connection
    WS-->>Frontend: WebSocket CLOSE
```

### 3.3 Documentation Drift Report Generation

```mermaid
sequenceDiagram
    actor Developer
    participant Frontend as Next.js Frontend
    participant API as FastAPI /api/lds
    participant GitHub as GitHub API
    participant Cache as File Tree Cache

    Developer->>Frontend: Click "Drift Report"
    Frontend->>API: GET /api/lds/drift-report?owner=X&repo=Y

    API->>Cache: Check repo_tree_cache
    alt Cache miss
        API->>GitHub: GET /repos/{owner}/{repo}/git/trees/HEAD?recursive=1
        GitHub-->>API: File tree JSON
        API->>Cache: Store tree with TTL
    else Cache hit
        Cache-->>API: Cached file tree
    end

    API->>API: Categorize files (code, docs, config)
    API->>API: Identify modules (top-level dirs)

    loop For each module
        API->>API: Check documentation coverage
        API->>API: Create finding if undocumented
    end

    API->>API: Check root README existence
    API->>API: Check docs/ directory existence
    API->>API: Compute severity levels

    API-->>Frontend: JSON response with findings
    Frontend-->>Developer: Render drift report card
```

### 3.4 Automatic Documentation Update via Webhook

```mermaid
sequenceDiagram
    actor Developer
    participant GitHub as GitHub
    participant Webhook as /api/lds/webhook/github
    participant LDS as LDS Engine
    participant LLM as LLM Provider
    participant GitAPI as GitHub API

    Developer->>GitHub: git push to main

    GitHub->>Webhook: POST (push event)
    Webhook->>Webhook: Verify X-Hub-Signature-256

    alt Invalid signature
        Webhook-->>GitHub: 403 Forbidden
    end

    Webhook->>Webhook: Check: default branch?
    Webhook->>Webhook: Check: not bot commit?

    Webhook->>LDS: _auto_update_docs(owner, repo, token)

    LDS->>GitAPI: Fetch repository file tree
    GitAPI-->>LDS: File tree

    LDS->>LDS: Find README.md content
    LDS->>LDS: Analyze: drift, NLP summary
    LDS->>LDS: Compose update prompt

    LDS->>LLM: Generate updated README
    LLM-->>LDS: Updated README content

    LDS->>GitAPI: Create branch docs/auto-update-{ts}
    GitAPI-->>LDS: Branch created

    LDS->>GitAPI: Update README.md on branch
    GitAPI-->>LDS: File updated

    LDS->>GitAPI: Create Pull Request
    GitAPI-->>LDS: PR #42 created

    LDS->>LDS: Store PR in doc_prs dict

    Webhook-->>GitHub: 200 OK (accepted)
```

### 3.5 Wiki Generation & Export

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant Backend as FastAPI Backend
    participant Cache as Wiki Cache (filesystem)
    participant GitHub as GitHub API
    participant LLM as LLM Provider

    User->>Frontend: Enter repo URL
    Frontend->>Backend: GET /api/wiki_cache?owner=X&repo=Y

    alt Cache exists
        Backend->>Cache: Read cache JSON
        Cache-->>Backend: WikiCacheData
        Backend-->>Frontend: Return cached wiki
    else No cache
        Frontend->>Backend: POST /chat/completions/stream
        Note right of Backend: Wiki generation via<br/>streaming chat

        Backend->>GitHub: Fetch repo structure
        GitHub-->>Backend: File tree

        Backend->>Backend: prepare_retriever()
        Backend->>Backend: Index all files

        loop For each wiki page
            Backend->>LLM: Generate page content
            LLM-->>Backend: Streamed page content
            Backend-->>Frontend: SSE chunks
        end

        Frontend->>Backend: POST /api/wiki_cache
        Backend->>Cache: Save wiki cache JSON
    end

    Frontend-->>User: Display wiki pages

    User->>Frontend: Click "Export"
    Frontend->>Backend: POST /export/wiki (format=markdown)
    Backend->>Backend: Compile pages to Markdown
    Backend-->>Frontend: File download
    Frontend-->>User: Download .md file
```

### 3.6 Pull Request Lifecycle

```mermaid
sequenceDiagram
    actor Author
    actor Reviewer
    participant API as /api/lds/pull-requests
    participant GitHub as GitHub API

    Author->>API: POST / (PRCreateRequest)
    API->>API: Create DocumentationPR (OPEN)

    alt GitHub token available
        API->>GitHub: Create branch
        API->>GitHub: Commit doc_content
        API->>GitHub: Create Pull Request
        GitHub-->>API: PR #N URL
    end

    API-->>Author: PR created (id, github_pr)

    Author->>API: GET /
    API-->>Author: List all PRs

    Reviewer->>API: POST /{id}/review (APPROVED)
    API->>API: Update PR status → APPROVED
    API-->>Reviewer: Review recorded

    Author->>API: POST /{id}/merge
    API->>API: Validate status = APPROVED

    alt GitHub PR linked
        API->>GitHub: Merge PR (squash)
        GitHub-->>API: Merged
    end

    API->>API: Update status → MERGED
    API-->>Author: PR merged

    Note over API: Alternative flow
    Author->>API: POST /{id}/close
    API->>API: Update status → CLOSED
    API-->>Author: PR closed
```

### 3.7 LLM Provider Selection (Strategy Pattern)

```mermaid
sequenceDiagram
    participant Handler as Chat Handler
    participant Config as config.py
    participant Factory as CLIENT_CLASSES map

    Handler->>Config: get_model_config(provider, model)
    Config->>Config: Load generator.json

    alt provider = "google"
        Config->>Factory: CLIENT_CLASSES["GoogleGenAIClient"]
        Factory-->>Config: GoogleGenAIClient class
    else provider = "openai"
        Config->>Factory: CLIENT_CLASSES["OpenAIClient"]
        Factory-->>Config: OpenAIClient class
    else provider = "openrouter"
        Config->>Factory: CLIENT_CLASSES["OpenRouterClient"]
        Factory-->>Config: OpenRouterClient class
    else provider = "ollama"
        Config->>Factory: CLIENT_CLASSES["OllamaClient"]
        Factory-->>Config: OllamaClient class
    else provider = "bedrock"
        Config->>Factory: CLIENT_CLASSES["BedrockClient"]
        Factory-->>Config: BedrockClient class
    else provider = "azure"
        Config->>Factory: CLIENT_CLASSES["AzureAIClient"]
        Factory-->>Config: AzureAIClient class
    else provider = "dashscope"
        Config->>Factory: CLIENT_CLASSES["DashscopeClient"]
        Factory-->>Config: DashscopeClient class
    end

    Config-->>Handler: {model_client: Class, model_kwargs: dict}

    Handler->>Handler: client = model_client()
    Handler->>Handler: generator = Generator(client, kwargs)
```

### 3.8 Data Pipeline — Document Embedding

```mermaid
sequenceDiagram
    participant RAG as RAG Component
    participant DBM as DatabaseManager
    participant Repo as Repository (Git)
    participant Reader as read_all_documents()
    participant Splitter as TextSplitter
    participant Embedder as Embedder (Provider)
    participant DB as LocalDB (FAISS)

    RAG->>DBM: prepare_database(repo_url)
    DBM->>Repo: download_repo() / git clone --depth=1
    Repo-->>DBM: Local file path

    DBM->>Reader: read_all_documents(path)

    loop For each file
        Reader->>Reader: Check inclusion/exclusion rules
        Reader->>Reader: count_tokens(content)
        alt tokens < MAX_EMBEDDING_TOKENS
            Reader->>Reader: Create Document(text, meta_data)
        else tokens too large
            Reader->>Reader: Skip file (log warning)
        end
    end

    Reader-->>DBM: List~Document~ (code + docs)

    DBM->>DBM: prepare_data_pipeline()
    DBM->>Splitter: Split documents by tokens
    Splitter-->>DBM: Chunked documents

    alt Ollama embedder
        DBM->>Embedder: Process one-by-one
        loop For each chunk
            Embedder-->>DBM: Single embedding vector
        end
    else Other providers
        DBM->>Embedder: Batch embed (batch_size=500)
        Embedder-->>DBM: Batch embedding vectors
    end

    DBM->>DB: Save to LocalDB
    DB-->>RAG: transformed_docs with vectors
```

---

> _UML Diagrams for the Living Documentation System — Generated March 2026_
