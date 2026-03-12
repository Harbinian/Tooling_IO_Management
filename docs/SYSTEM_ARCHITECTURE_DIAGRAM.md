# System Architecture Diagram

## 1. Overall Architecture

```mermaid
flowchart LR
    U[User]
    FE[Frontend App\nVue + Tailwind + shadcn + Mist]
    API[Backend API Layer\nFlask / Route Modules]
    AUTH[Authentication & RBAC]
    WF[Workflow Engine\nOrder / Keeper / Transport / Final Confirm]
    NOTI[Notification Service]
    FS[Feishu Adapter]
    AUDIT[Audit Log Service]
    LOC[Tool Location Service]
    DASH[Dashboard Metrics Service]
    DB[(SQL Server)]

    U --> FE
    FE --> API

    API --> AUTH
    API --> WF
    API --> NOTI
    API --> AUDIT
    API --> LOC
    API --> DASH

    NOTI --> FS

    AUTH --> DB
    WF --> DB
    NOTI --> DB
    AUDIT --> DB
    LOC --> DB
    DASH --> DB