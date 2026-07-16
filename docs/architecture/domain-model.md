# Domain Model

## Bounded Contexts

| Domain | Responsibility | Events Emitted |
|--------|---------------|----------------|
| **Identity** | User registration, authentication, roles | `UserRegistered`, `UserLoggedIn`, `RoleAssigned` |
| **Customer** | Customer profiles, demographics | `CustomerCreated`, `CustomerUpdated` |
| **Complaint** | Complaint intake, classification, status | `ComplaintFiled`, `ComplaintClassified`, `ComplaintResolved` |
| **Interaction** | Communication history (calls, emails, chats) | `InteractionLogged` |
| **Workflow** | Complaint routing, SLA tracking, escalations | `TaskAssigned`, `SLAWarning`, `Escalated` |
| **Notification** | Email, SMS, in-app notifications | `NotificationSent` |
| **Analytics** | Aggregated reports, dashboards, KPI snapshots | `ReportGenerated` |
| **Search** | Full-text and vector search indexing | `IndexUpdated` |
| **Audit** | Immutable audit log for compliance | `ActionLogged` |
| **Knowledge** | FAQ, policy documents, knowledge base articles | `ArticlePublished` |
| **Configuration** | System settings, feature flags, business rules | `SettingChanged` |

## Core Entities

### Complaint
```
Complaint
├── id: UUID (PK)
├── customer_id: UUID (FK → Customer)
├── category: ComplaintCategory
├── sub_category: str
├── issue_type: str
├── description: str
├── status: ComplaintStatus (filed, in_review, escalated, resolved)
├── severity: SeverityLevel (low, medium, high, critical)
├── sentiment: SentimentResult
├── assigned_to: UUID (FK → User, nullable)
├── filed_at: datetime
├── resolved_at: datetime (nullable)
└── metadata: JSONB
```

### Customer
```
Customer
├── id: UUID (PK)
├── external_id: str (nullable)
├── name: str
├── email: str
├── phone: str (nullable)
├── date_of_birth: date (nullable)
├── policy_numbers: str[]
├── is_active: bool
├── created_at: datetime
└── updated_at: datetime
```

### User
```
User
├── id: UUID (PK)
├── email: str (unique)
├── password_hash: str
├── display_name: str
├── roles: Role[] (super_admin, admin, analyst, agent, auditor, readonly)
├── is_active: bool
├── last_login_at: datetime (nullable)
└── created_at: datetime
```

## Aggregate Boundaries

- **Complaint** is the primary aggregate root. All complaint-related operations go through the `ComplaintService`.
- **Customer** is a separate aggregate. Complaints reference customers by ID only.
- **User** (Identity) is a separate aggregate used for authorisation.
