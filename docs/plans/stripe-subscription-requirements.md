# Stripe Subscription - Finalne Ustalenia

**Data:** 2025-12-18
**Status:** Requirements Approved

## Podsumowanie

Implementacja 3-poziomowego systemu subskrypcji (Free/Pro/Pro Plus) z wykorzystaniem Stripe Checkout i Billing Portal.

## Struktura Planów i Ceny

### Free Tier (Darmowy)
- **Cena:** $0
- **AI Limit:** $1/miesiąc
  - ⚠️ **Wymaga własnego OpenRouter token** (BYOK - Bring Your Own Key)
  - Użytkownik podaje swój API key w ustawieniach
  - Aplikacja nie ponosi kosztów AI dla free users
- **Storage Limit:** 100 MB (104,857,600 bytes)
- **Funkcje:**
  - Podstawowe zarządzanie gear
  - AI Chat tylko z własnym tokenem
  - Image processing - standard quality
  - Wybór wszystkich dostępnych modeli AI

### Pro Tier
- **Cena:**
  - **Monthly:** $5.00/miesiąc
  - **Annual:** $50/rok (17% zniżki = 2 miesiące gratis)
- **AI Limit:** $10/miesiąc (bez potrzeby własnego tokenu)
- **Storage Limit:** 5 GB (5,368,709,120 bytes)
- **Funkcje:**
  - Wszystkie funkcje Free
  - AI Chat bez własnego tokenu (aplikacja płaci)
  - Image processing - high quality
  - Image search (zaawansowane wyszukiwanie po obrazach)
  - Wybór wszystkich dostępnych modeli AI
  - Limity wystarczające dla użytkowników indywidualnych

### Pro Plus Tier
- **Cena:**
  - **Monthly:** $15.00/miesiąc
  - **Annual:** $150/rok (17% zniżki = 2 miesiące gratis)
- **AI Limit:** $50/miesiąc (bez potrzeby własnego tokenu)
- **Storage Limit:** 50 GB (53,687,091,200 bytes)
- **Funkcje:**
  - Wszystkie funkcje Pro
  - Znacznie wyższe limity AI i storage
  - Wybór wszystkich dostępnych modeli AI
  - **Brak ekskluzywnych funkcji** - tylko wyższe limity

**Uwaga:** Pro Plus tier NIE ma ekskluzywnych funkcji typu API access, batch operations czy priority support. To wyłącznie tier z wyższymi limitami dla power users.

## Stripe Configuration

### Products w Stripe Dashboard

**Product 1: Pro Plan**
- Name: "Gear Stack Pro"
- Description: "Enhanced features with higher AI and storage limits"
- Statement descriptor: "GEARSTACK PRO"

**Product 2: Pro Plus Plan**
- Name: "Gear Stack Pro Plus"
- Description: "Maximum AI and storage limits for power users"
- Statement descriptor: "GEARSTACK PRO+"

### Prices w Stripe Dashboard

| Plan | Interval | Amount | Price ID (do skopiowania) |
|------|----------|--------|---------------------------|
| Pro | Monthly | $5.00 USD | `STRIPE_PRO_MONTHLY_PRICE_ID` |
| Pro | Annual | $50.00 USD | `STRIPE_PRO_ANNUAL_PRICE_ID` |
| Pro Plus | Monthly | $15.00 USD | `STRIPE_PRO_PLUS_MONTHLY_PRICE_ID` |
| Pro Plus | Annual | $150.00 USD | `STRIPE_PRO_PLUS_ANNUAL_PRICE_ID` |

**Annual discount:** 17% (równowartość 2 miesięcy gratis)

### Webhook Events (do skonfigurowania)

Wymagane eventy w Stripe webhook endpoint:
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

## Premium Features Mapping

### AI Chat
- **Free:** Tylko z własnym OpenRouter API tokenem
  - User podaje token w Settings → AI Settings
  - Aplikacja używa tokenu usera do requestów
  - Limit $1/miesiąc (tracking po stronie usera)
- **Pro/Pro Plus:** Bez własnego tokenu
  - Aplikacja używa własnego API key
  - Tracking usage w bazie danych
  - Limity: Pro $10/mo, Pro Plus $50/mo

### Image Processing Quality
- **Free:** Standard quality
- **Pro/Pro Plus:** High quality mode

### Image Search
- **Free:** ❌ Niedostępne
- **Pro/Pro Plus:** ✅ Dostępne

### AI Models
- **Wszystkie tiery:** Pełny wybór dostępnych modeli
  - Brak ograniczeń na modele (GPT-4, Claude Opus, etc.)
  - Różnica tylko w limitach budżetowych ($1/$10/$50)

## Grandfathered Accounts (Migracja)

### Obecni Premium Users

**Status:** Automatyczna migracja do Pro tier z lifetime access

**Implementacja:**
1. Wszyscy users z `is_premium = true` przed wdrożeniem:
   - Tworzony rekord w tabeli `subscriptions`
   - `plan_tier = 'pro'`
   - `status = 'active'`
   - `is_grandfathered = true` (nowe pole boolean)
   - `stripe_customer_id = NULL` (brak płatności)
   - `stripe_subscription_id = NULL`

2. Grandfathered accounts:
   - ✅ Pełny dostęp do Pro tier features
   - ✅ Limity Pro tier (AI: $10, Storage: 5GB)
   - ✅ **Lifetime access** (na zawsze bezpłatny Pro)
   - ✅ Widoczne w admin panel jako "Grandfathered Pro"
   - ❌ Nie mogą upgrade do Pro Plus (tylko przez nową subskrypcję paid)
   - ❌ Nie pojawiają się w Stripe Dashboard (tylko w aplikacji)

3. Migration script:
```sql
-- W migracji 047_add_billing_tables.py
INSERT INTO subscriptions (user_id, plan_tier, status, is_grandfathered, created_at, updated_at)
SELECT
    id,
    'pro',
    'active',
    TRUE,  -- is_grandfathered
    created_at,
    NOW()
FROM users
WHERE is_premium = TRUE;
```

### Wyświetlanie w UI

**Settings → Subscription Status Card:**
```
Current Plan: Pro (Lifetime Access)
[Badge: Grandfathered]

✨ You have lifetime Pro access as an early supporter!
- AI Limit: $10/month
- Storage: 5 GB
- High quality image processing
- Image search enabled
```

**Admin Panel:**
```
User: john@example.com
Subscription: Pro (Grandfathered)
Stripe Customer: N/A
Status: Active
Billing: Lifetime (no charges)
```

## Feature Limits Configuration

### Database: `feature_limits` table

| Role | AI Limit (USD) | Storage Limit (bytes) | Description |
|------|----------------|----------------------|-------------|
| `user` | 1.00 | 104,857,600 | Free tier: 100MB, $1 AI (BYOK) |
| `premium` | 10.00 | 5,368,709,120 | Pro tier: 5GB, $10 AI |
| `business` | 50.00 | 53,687,091,200 | Pro Plus tier: 50GB, $50 AI |
| `admin` | NULL | NULL | Admin: unlimited |
| `owner` | NULL | NULL | Owner: unlimited |

**Mapping:**
- Free tier → `user` role limits
- Pro tier → `premium` role limits
- Pro Plus tier → `business` role limits
- Grandfathered → `premium` role limits (same as Pro)

## OpenRouter Token Management (Free Tier)

### Nowe wymagania dla Free tier

**Backend:**
1. Dodać pole do `users` table:
   ```python
   openrouter_api_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
   ```

2. Endpoint do zapisywania tokenu:
   ```python
   @router.patch("/users/me/openrouter-token")
   async def update_openrouter_token(request: UpdateOpenRouterTokenRequest):
       # Walidacja tokenu (opcjonalnie: test call do OpenRouter)
       # Zapisz encrypted w bazie
       # Zwróć success
   ```

3. Logika AI Chat:
   ```python
   if user.subscription.plan_tier == 'free':
       if not user.openrouter_api_token:
           raise HTTPException(400, "OpenRouter token required for free tier")
       api_key = decrypt(user.openrouter_api_token)
   else:
       api_key = settings.openrouter.api_key  # App's key
   ```

**Frontend:**
1. Settings → AI Settings:
   - Input field: "OpenRouter API Token" (tylko dla Free users)
   - Link: "Get your token at openrouter.ai"
   - Validation: sprawdź czy token jest poprawny (test call)
   - Zapisz encrypted

2. AI Chat:
   - Free user bez tokenu → banner: "Add your OpenRouter token to use AI Chat"
   - Free user z tokenem → działa normalnie
   - Pro/Business → działa od razu bez tokenu

## Scope Implementacji

### MVP (Minimum Viable Product)
✅ **Pełny zakres** - wszystkie 3 plany + Billing Portal + webhooks

**Co wchodzi:**
- ✅ 3 plany subskrypcji (Free/Pro/Business)
- ✅ Stripe Checkout (hosted)
- ✅ Stripe Billing Portal (subscription management)
- ✅ Webhook processing (subscription events)
- ✅ Pricing page (public)
- ✅ Billing management page (authenticated)
- ✅ Admin panel integration
- ✅ Migration grandfathered accounts
- ✅ OpenRouter token management for Free tier

**Co NIE wchodzi (future enhancements):**
- ❌ Usage-based billing (pay-as-you-go)
- ❌ Team/organization plans
- ❌ Promo codes (Stripe supports, ale implementacja później)
- ❌ API access / webhooks integrations
- ❌ Batch operations / bulk export
- ❌ Priority support / SLA tiers

## Timeline i Priorytetyzacja

### Implementacja: 6-8 tygodni

**Podejście:** Wszystkie fazy po kolei według planu

### Fazy (zgodnie z planem głównym):

#### Phase 1: Backend Foundation (Tydzień 1)
- Database schema (migrations)
- SQLAlchemy models
- Stripe client wrapper
- Repository layer
- Config updates

#### Phase 2: Backend API & Webhooks (Tydzień 2)
- Service layer
- API endpoints (/checkout, /portal, /subscription)
- Webhook handler
- Grandfathered accounts logic
- Unit tests

#### Phase 3: Frontend Foundation (Tydzień 3)
- TypeScript types
- billingService (API client)
- useSubscription composable
- useCheckout composable
- Routes definition

#### Phase 4: Frontend UI (Tydzień 4)
- PricingPage.vue
- BillingPage.vue
- SubscriptionStatusCard.vue
- PricingCard, PricingTable components
- i18n (EN/PL)
- Integration with Settings

#### Phase 5: Integration & Polish (Tydzień 5-6)
- Admin panel updates
- OpenRouter token management
- Upgrade prompts/banners
- Error handling
- Loading states
- Full e2e testing
- Bug fixes

#### Phase 6: Production Setup (Tydzień 7-8)
- Stripe Dashboard setup (products, prices)
- Webhook configuration
- Environment variables
- Production deployment
- Monitoring setup
- Documentation

## Technical Notes

### Database Schema Extensions

**New field in `subscriptions` table:**
```sql
is_grandfathered BOOLEAN DEFAULT FALSE
```

**New field in `users` table:**
```sql
openrouter_api_token VARCHAR(255) NULL  -- Encrypted
```

### Environment Variables

**Backend `.env`:**
```bash
# Stripe
STRIPE_ENABLED=true
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Price IDs
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_ANNUAL_PRICE_ID=price_...
STRIPE_PRO_PLUS_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_PLUS_ANNUAL_PRICE_ID=price_...

# OpenRouter (app's key for Pro/Business)
OPENROUTER_API_KEY=sk-or-v1-...
```

**Frontend `.env`:**
```bash
VITE_STRIPE_PUBLISHABLE_KEY=pk_...
VITE_STRIPE_PRO_MONTHLY_PRICE_ID=price_...
VITE_STRIPE_PRO_ANNUAL_PRICE_ID=price_...
VITE_STRIPE_PRO_PLUS_MONTHLY_PRICE_ID=price_...
VITE_STRIPE_PRO_PLUS_ANNUAL_PRICE_ID=price_...
```

### Security Considerations

**OpenRouter Token Storage:**
- Tokens przechowywane **encrypted** w bazie danych
- Używać `cryptography.fernet` lub podobnego
- Nigdy nie logować tokenów
- Nie zwracać tokenów w API responses (tylko masked: `sk-or-...****`)

**Webhook Verification:**
- Zawsze weryfikować signature
- Odrzucać requesty bez valid signature
- Rate limiting na webhook endpoint

## Success Metrics

### Technical Metrics
- ✅ Migration sukces rate: 100% (wszyscy premium users zmigrowani)
- ✅ Webhook processing success rate: >99%
- ✅ Payment success rate: >95% (industry standard)
- ✅ API uptime: >99.9%

### Business Metrics
- 📊 Conversion rate Free → Pro: (target: 2-5%)
- 📊 Churn rate: (target: <5% monthly)
- 📊 Monthly Recurring Revenue (MRR)
- 📊 Average Revenue Per User (ARPU)

## Risk Mitigation

### Technical Risks

**Risk:** Webhook processing failures
- **Mitigation:** Retry logic, dead letter queue, alerting

**Risk:** Stripe API downtime
- **Mitigation:** Graceful degradation, cached subscription status, fallback to database

**Risk:** Migration data corruption
- **Mitigation:** Database backup before migration, rollback script, dry-run testing

### Business Risks

**Risk:** User confusion about grandfathered status
- **Mitigation:** Clear UI messaging, help documentation, support team briefing

**Risk:** Free tier abuse (excessive API calls with own token)
- **Mitigation:** Rate limiting, usage monitoring, abuse detection

**Risk:** Revenue cannibalization (users downgrade to free with BYOK)
- **Mitigation:** BYOK requires technical knowledge, limits still apply, upsell messaging

## Open Questions & Decisions Log

### Resolved ✅
- ✅ Pricing finalized: Pro $5.00/mo, Pro Plus $15.00/mo
- ✅ Feature limits finalized: AI ($1/$10/$50), Storage (100MB/5GB/50GB)
- ✅ Grandfathered strategy: Lifetime Pro for existing premium users
- ✅ Free tier AI: BYOK (own OpenRouter token required)
- ✅ Pro Plus tier: No exclusive features, only higher limits
- ✅ Timeline: 6-8 weeks, all phases sequentially

### To Decide Later 🤔
- 🤔 Tax handling (VAT, sales tax) - Stripe Tax?
- 🤔 Email notifications for subscription events (renewal, failure, cancellation)
- 🤔 Grace period duration for failed payments (3 days? 7 days?)
- 🤔 Promo codes strategy (launch discount, referral program)
- 🤔 Annual plan discount messaging ("Save $10.88/year!" vs "2 months free!")

## Next Steps

1. **Review & Approval**
   - ✅ Finalize requirements (ten dokument)
   - ⏳ Review by team/stakeholders
   - ⏳ Approval to proceed

2. **Stripe Setup**
   - Create Stripe account (if not exists)
   - Set up test mode environment
   - Create Products and Prices
   - Configure webhook endpoint (test mode)

3. **Development Start**
   - Begin Phase 1: Backend Foundation
   - Set up development branch
   - Initialize billing module structure

---

**Document Version:** 2.1
**Last Updated:** 2025-12-18
**Author:** Requirements gathered by Claude Code
**Status:** ✅ Requirements Finalized & Patterns Verified - Ready for Implementation

---

## Related Documents

- **[Implementation Plan](./stripe-subscription-implementation.md)** - Detailed technical implementation guide
- **[Pattern Verification](./stripe-pattern-verification.md)** - Codebase pattern analysis and alignment verification
