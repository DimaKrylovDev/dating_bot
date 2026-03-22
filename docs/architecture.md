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