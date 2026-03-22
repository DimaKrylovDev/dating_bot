# Dating App - Микросервисная Архитектура

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| Vector DB | Qdrant |
| Cache | Redis |
| Message Queue | Apache Kafka |
| Task Queue | Celery |
| Object Storage | MinIO (S3-compatible) |
| CDN | тоже не факт |
| AI/ML | OpenAI API / LangChain / DSPy / LangGraph (но не факт пока) |
| Monitoring | Prometheus + Grafana |
| Container | Docker + Docker Compose |

---

## 1. Архитектурная диаграмма (High-Level)

```mermaid
flowchart TB
    subgraph Clients["Клиенты"]
        Mobile["📱 Mobile App"]
        Web["🌐 Web App"]
    end

    subgraph Gateway["API Layer"]
        LB["Load Balancer<br/>Nginx"]
        APIGateway["API Gateway<br/>Nginx"]
    end

    subgraph MediaDelivery["Media Delivery"]
        CDN["🌍 CDN<br/>CloudFlare/CloudFront"]
    end

    subgraph Core["Core Services"]
        Auth["🔐 Auth Service<br/>:8001"]
        User["👤 User Service<br/>:8002"]
        Profile["📋 Profile Service<br/>:8003"]
    end

    subgraph Matching["Matching Domain"]
        Match["💕 Matching Service<br/>:8004"]
        Rating["⭐ Rating Service<br/>:8005"]
        Discovery["🔍 Discovery Service<br/>:8006"]
    end

    subgraph Communication["Communication"]
        Chat["💬 Chat Service<br/>:8007<br/>WebSocket"]
        Notify["🔔 Notification Service<br/>:8008"]
    end

    subgraph Intelligence["AI Services"]
        AI["🤖 AI Service<br/>:8010"]
    end

    subgraph Storage["Storage Layer"]
        MinIO["📦 MinIO<br/>S3 Storage"]
        ImageProc["🖼️ Image Processor<br/>Thumbnails, WebP"]
    end

    subgraph Infrastructure["Infrastructure"]
        Kafka["Apache Kafka"]
        Redis["Redis Cluster"]
        PG["PostgreSQL<br/>+ PostGIS"]
        Qdrant["🔮 Qdrant<br/>Vector DB"]
        Celery["Celery Workers"]
    end

    subgraph Monitoring["Monitoring"]
        Prometheus["Prometheus"]
        Grafana["Grafana"]
    end

    Mobile & Web --> LB
    Mobile & Web -.->|"GET photos"| CDN
    LB --> APIGateway

    APIGateway --> Auth
    APIGateway --> User
    APIGateway --> Profile
    APIGateway --> Match
    APIGateway --> Discovery
    APIGateway --> Chat
    APIGateway --> AI

    Auth & User & Profile --> PG
    Match & Rating & Discovery --> PG
    Chat --> PG
    AI --> PG
    AI --> Qdrant

    Profile -->|"Upload"| ImageProc
    ImageProc --> MinIO
    CDN -->|"Origin"| MinIO

    Auth --> Redis
    Rating --> Redis
    Discovery --> Redis
    Chat --> Redis

    Match --> Kafka
    Rating --> Kafka
    Chat --> Kafka
    AI --> Kafka

    Kafka --> Notify
    Kafka --> Rating
    Kafka --> AI

    Rating --> Celery
    AI --> Celery
    ImageProc --> Celery

    Core & Matching & Communication & Intelligence --> Prometheus
    Prometheus --> Grafana
```
---

## 4. Система рейтингов (3 уровня)

```mermaid
flowchart TB
    subgraph Level1["📊 Уровень 1: Первичный рейтинг"]
        L1_Input["Входные данные"]
        L1_Profile["Полнота профиля<br/>• Имя, возраст ✓<br/>• Bio ✓<br/>• Интересы ✓"]
        L1_Photos["Фотографии<br/>• Количество (1-6)<br/>• Верификация"]
        L1_Prefs["Предпочтения<br/>• Возраст<br/>• Пол<br/>• Город"]
        L1_Score["Primary Score<br/>0-100"]

        L1_Input --> L1_Profile
        L1_Input --> L1_Photos
        L1_Input --> L1_Prefs
        L1_Profile --> L1_Score
        L1_Photos --> L1_Score
        L1_Prefs --> L1_Score
    end

    subgraph Level2["📈 Уровень 2: Поведенческий рейтинг"]
        L2_Input["События"]
        L2_Likes["Лайки<br/>• Получено<br/>• Like ratio"]
        L2_Matches["Мэтчи<br/>• Количество<br/>• Match rate"]
        L2_Chats["Диалоги<br/>• Инициирование<br/>• Активность"]
        L2_Time["Время<br/>• Пиковая активность<br/>• Частота"]
        L2_Score["Behavioral Score<br/>0-100"]

        L2_Input --> L2_Likes
        L2_Input --> L2_Matches
        L2_Input --> L2_Chats
        L2_Input --> L2_Time
        L2_Likes --> L2_Score
        L2_Matches --> L2_Score
        L2_Chats --> L2_Score
        L2_Time --> L2_Score
    end

    subgraph Level3["🏆 Уровень 3: Комбинированный"]
        L3_Primary["Primary<br/>Weight: 30%"]
        L3_Behavioral["Behavioral<br/>Weight: 60%"]
        L3_Bonus["Бонусы<br/>Weight: 10%<br/>• Рефералы<br/>• Premium"]
        L3_Final["Final Rating<br/>0-100"]

        L3_Primary --> L3_Final
        L3_Behavioral --> L3_Final
        L3_Bonus --> L3_Final
    end

    L1_Score --> L3_Primary
    L2_Score --> L3_Behavioral
```
---

## 6. Диаграмма сервисов и их взаимодействия

```mermaid
flowchart TB
    subgraph Services["Микросервисы"]
        Auth["🔐 Auth Service<br/>JWT, OAuth, Sessions"]
        User["👤 User Service<br/>Пользователи, Рефералы"]
        Profile["📋 Profile Service<br/>Анкеты, Фото, Гео"]
        Match["💕 Matching Service<br/>Лайки, Мэтчи"]
        Rating["⭐ Rating Service<br/>Рейтинги 3 уровней"]
        Discovery["🔍 Discovery Service<br/>Лента, Фильтры"]
        Chat["💬 Chat Service<br/>WebSocket, История"]
        Notify["🔔 Notification<br/>Push, Email, SMS"]
        AI["🤖 AI Service<br/>Рекомендации"]
        Analytics["📊 Analytics<br/>Метрики, Отчёты"]
    end

    subgraph Kafka_Topics["Kafka Topics"]
        T_User["user.events"]
        T_Match["match.events"]
        T_Chat["chat.events"]
        T_Rating["rating.events"]
        T_Notify["notification.events"]
    end

    Auth -.->|"user.registered"| T_User
    Profile -.->|"profile.updated"| T_User
    User -.->|"referral.created"| T_User

    Match -.->|"swipe.created"| T_Match
    Match -.->|"match.created"| T_Match

    Chat -.->|"message.sent"| T_Chat
    Chat -.->|"chat.initiated"| T_Chat

    Rating -.->|"rating.updated"| T_Rating

    T_User -.-> Rating
    T_User -.-> Discovery
    T_Match -.-> Rating
    T_Match -.-> Notify
    T_Match -.-> Chat
    T_Chat -.-> Rating
    T_Chat -.-> Notify
    T_Rating -.-> Discovery

    Match & Chat & Rating -.->|"notification.send"| T_Notify
    T_Notify -.-> Notify

    Profile --> AI
    Rating --> AI
```

---

## 7. Диаграмма базы данных (ERD)

```mermaid
erDiagram
    ACCOUNTS ||--|| USERS : has
    USERS ||--|| PROFILES : has
    USERS ||--|| USER_RATINGS : has
    USERS ||--o{ REFERRAL_BONUSES : earns
    PROFILES ||--o{ PHOTOS : contains
    PROFILES ||--o{ PROFILE_INTERESTS : has
    INTERESTS ||--o{ PROFILE_INTERESTS : used_in
    PROFILES ||--|| SEARCH_PREFERENCES : configures
    USERS ||--o{ SWIPES : makes
    USERS ||--o{ SWIPES : receives
    SWIPES }o--|| MATCHES : creates
    MATCHES ||--|| CHAT_ROOMS : has
    CHAT_ROOMS ||--o{ MESSAGES : contains
    USER_RATINGS ||--o{ RATING_HISTORY : tracks

    ACCOUNTS {
        uuid id PK
        string email UK
        string phone UK
        string password_hash
        boolean is_verified
        timestamp created_at
    }

    USERS {
        uuid id PK,FK
        string username UK
        string referral_code UK
        uuid referred_by FK
        int referral_count
        jsonb settings
    }

    PROFILES {
        uuid id PK
        uuid user_id FK,UK
        string name
        date birthdate
        string gender
        text bio
        geography location
        string city
        int completion_score
        boolean is_verified
    }

    PHOTOS {
        uuid id PK
        uuid profile_id FK
        string url
        string thumbnail_url
        int position
        boolean is_primary
        boolean is_verified
    }

    INTERESTS {
        int id PK
        string name UK
        string category
    }

    PROFILE_INTERESTS {
        uuid profile_id PK,FK
        int interest_id PK,FK
    }

    SEARCH_PREFERENCES {
        uuid id PK
        uuid profile_id FK,UK
        int min_age
        int max_age
        string[] gender_preference
        int max_distance
    }

    SWIPES {
        uuid id PK
        uuid swiper_id FK
        uuid swiped_id FK
        string action
        timestamp created_at
    }

    MATCHES {
        uuid id PK
        uuid user1_id FK
        uuid user2_id FK
        timestamp matched_at
        boolean chat_initiated
        uuid chat_initiated_by FK
    }

    USER_RATINGS {
        uuid id PK
        uuid user_id FK,UK
        decimal primary_rating
        decimal behavioral_rating
        decimal combined_rating
        int likes_received
        int matches_count
        decimal like_ratio
        decimal match_rate
        jsonb activity_pattern
        timestamp last_calculated_at
    }

    RATING_HISTORY {
        uuid id PK
        uuid user_id FK
        string rating_type
        decimal old_value
        decimal new_value
        string change_reason
        timestamp created_at
    }

    CHAT_ROOMS {
        uuid id PK
        uuid match_id FK,UK
        uuid user1_id FK
        uuid user2_id FK
        timestamp last_message_at
    }

    MESSAGES {
        uuid id PK
        uuid room_id FK
        uuid sender_id FK
        text content
        string message_type
        boolean is_read
        timestamp created_at
    }

    REFERRAL_BONUSES {
        uuid id PK
        uuid user_id FK
        uuid referred_user_id FK
        string bonus_type
        int bonus_value
        timestamp created_at
    }
```

---

## 8. Sequence диаграммы

### 7.1 Процесс мэтча

```mermaid
sequenceDiagram
    autonumber
    participant U as User A
    participant API as API Gateway
    participant M as Matching Service
    participant K as Kafka
    participant R as Rating Service
    participant N as Notification
    participant C as Chat Service

    U->>API: POST /swipe {target: userB, action: "like"}
    API->>M: Forward request
    M->>M: Check if User B liked User A

    alt Mutual Like (Match!)
        M->>M: Create Match record
        M->>K: Publish match.created
        M-->>API: {match: true, match_id: "..."}
        API-->>U: Match notification

        par Async Processing
            K->>R: Update ratings
            R->>R: +behavioral_score for both
            and
            K->>C: Create chat room
            C->>C: Initialize room
            and
            K->>N: Send notifications
            N->>N: Push to both users
        end
    else No Match Yet
        M->>K: Publish swipe.created
        M-->>API: {match: false}
        API-->>U: Continue swiping
        K->>R: Update target's rating
    end
```

### 7.2 Генерация ленты анкет

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant API as API Gateway
    participant D as Discovery Service
    participant Redis as Redis Cache
    participant R as Rating Service
    participant PG as PostgreSQL

    U->>API: GET /discovery/feed
    API->>D: Get next profile

    D->>Redis: Get cached feed

    alt Cache Hit
        Redis-->>D: Return profile_ids[cursor]
        D->>D: Increment cursor
    else Cache Miss
        D->>R: Get user preferences
        R-->>D: {age: 25-35, distance: 50km, ...}

        D->>PG: Query profiles with PostGIS
        Note over D,PG: WHERE ST_DWithin(location, user_location, 50000)<br/>AND age BETWEEN 25 AND 35<br/>ORDER BY combined_rating DESC<br/>LIMIT 10

        PG-->>D: Profile IDs (sorted by rating)
        D->>Redis: Cache feed (TTL: 1h)
    end

    D->>PG: Get full profile data
    PG-->>D: Profile details

    alt Last profile in batch (cursor = 9)
        D->>D: Trigger async preload
        Note over D: Celery task: generate next batch
    end

    D-->>API: Profile data
    API-->>U: Display profile
```

### 7.3 AI рекомендации

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant API as API Gateway
    participant AI as AI Service
    participant Profile as Profile Service
    participant Rating as Rating Service
    participant LLM as OpenAI API

    U->>API: GET /ai/analyze-profile
    API->>AI: Request analysis

    par Gather Data
        AI->>Profile: Get profile data
        Profile-->>AI: {bio, photos, interests, ...}
        and
        AI->>Rating: Get rating history
        Rating-->>AI: {current: 65, trend: "declining", ...}
    end

    AI->>AI: Prepare prompt with context
    AI->>LLM: Analyze profile
    Note over AI,LLM: "Analyze this dating profile and<br/>suggest improvements..."

    LLM-->>AI: Analysis results

    AI->>AI: Parse & prioritize recommendations
    AI-->>API: Structured recommendations
    API-->>U: Display tips
```
---
