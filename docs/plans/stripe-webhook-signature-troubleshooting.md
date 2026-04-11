# Stripe Webhook Signature Verification Troubleshooting

**Status:** ✅ RESOLVED - Completed
**Created:** 2025-12-23
**Last Updated:** 2025-12-23 (verified and completed)
**Priority:** CRITICAL - Blocking production deployment

## Problem Summary

Stripe webhook signature verification is **consistently failing** with error:
```
SignatureVerificationError: No signatures found matching the expected signature for payload
```

All webhooks from `stripe listen --forward-to localhost:8000/api/billing/webhooks/stripe` return HTTP 500.

## Environment

- **Backend:** FastAPI in Docker container (auto-reload enabled)
- **Stripe CLI:** Local forwarding with `stripe listen`
- **Webhook Secret:** `whsec_e59...92490d` (70 chars)
- **Test Mode:** Using Stripe test API keys
- **Stripe API Version:** 2025-12-15.clover

## What We've Verified ✅

### 1. Request Body Handling
- ✅ Using `await request.body()` to get raw bytes
- ✅ NOT parsing JSON before signature verification
- ✅ Payload type is `<class 'bytes'>` (confirmed in logs)
- ✅ No automatic Pydantic model parsing on webhook endpoint

### 2. Webhook Secret Configuration
- ✅ Secret in `.env` matches Stripe CLI output (70 characters)
- ✅ Secret correctly loaded into settings (verified with `docker exec`)
- ✅ No trailing whitespace or newlines (verified with `cat -A`)
- ✅ Secret length: 70 characters (correct format)
- ✅ Secret format: `whsec_e595c4009d12c8...a5dd8f11822f4792490d`

### 3. Signature Header
- ✅ `stripe-signature` header is present
- ✅ Header format is correct: `t=timestamp,v1=signature,v0=signature`
- ✅ Signature has 3 components (t, v1, v0)
- ✅ Timestamp is valid Unix timestamp

### 4. Code Implementation
- ✅ Using native Stripe SDK: `stripe.Webhook.construct_event()`
- ✅ Passing correct parameter types:
  - `payload`: `bytes`
  - `sig_header`: `str`
  - `webhook_secret`: `str`

## Test Results ❌

### Manual Signature Calculation

We implemented manual HMAC-SHA256 signature verification to isolate the issue:

```python
signed_payload_bytes = timestamp.encode('utf-8') + b'.' + payload
computed_signature = hmac.new(
    webhook_secret.encode('utf-8'),
    signed_payload_bytes,
    hashlib.sha256
).hexdigest()
```

**Results (from latest test - 2025-12-23 10:05:45):**
```
Timestamp from header: 1766484345
Expected signature (v1): 3f7bd0cb98dc4987a5d4f01f1f59d119c49c98a70c44fb43cd5f91cf7d423687
Computed signature:     41406fc797c491612a524805149769e235bcae20ed7e025cbb45474632ce983f
Signatures match: False ❌
```

**Observation:** Our computed signature does NOT match the expected signature from Stripe.

### Sample Webhook Event

```json
{
  "id": "evt_1ShSTNGh26qUGGFoiHIUTuSb",
  "object": "event",
  "api_version": "2025-12-15.clover",
  "created": 1766484344,
  "data": {...}
}
```

- Payload length: 4095 bytes
- Signature header: `t=1766484345,v1=3f7bd0cb...,v0=449e3d12...`

## Root Cause Identified 🔍

### **PRIMARY CAUSE: Middleware Modifying Payload**

**Problem:** `ConvertEmptyStringsToNoneMiddleware` was parsing and re-serializing JSON payloads, which modified the raw bytes before webhook signature verification.

**Details:**
- Middleware processes all `POST` requests with `application/json` content-type
- It performs: `json.loads()` → modify data → `json.dumps()` → encode back to bytes
- `json.dumps()` changes the exact byte representation (formatting, spacing, key ordering)
- Stripe signature is computed on **original payload bytes**, but middleware delivers **modified bytes**
- Result: Signature verification fails because payload bytes don't match

**Solution Implemented:** Added exclusion for Stripe webhook endpoints in middleware:
```python
# Skip Stripe webhook endpoints - they require raw body for signature verification
path = scope.get("path", "")
if path.startswith("/api/billing/webhook") or path.startswith("/api/billing/webhooks"):
    await self.app(scope, receive, send)
    return
```

**Files Modified:**
- `backend/app/core/convert_empty_strings_middleware.py` - Added webhook path exclusion

**Status:** ⏳ **AWAITING VERIFICATION** - Fix has been implemented but needs to be tested with actual Stripe webhook to confirm resolution.

## Additional Hypotheses (Secondary Issues) 🔍

### Hypothesis 1: Stripe CLI Secret Mismatch ⚠️
**Theory:** Stripe CLI might be using a different signing secret than displayed in `stripe listen` output.

**Evidence:**
- Documentation warns: "You should not verify signatures on events forwarded by the CLI using the secret from a Dashboard-managed endpoint"
- Each Stripe endpoint (CLI, Dashboard, test vs live) has its own unique secret

**Status:** Less likely to be the issue if middleware fix resolves the problem

### Hypothesis 2: Payload Modification During Forwarding ⚠️
**Theory:** Stripe CLI might modify the payload during localhost forwarding (encoding, newlines, whitespace).

**Status:** Resolved - middleware was the culprit modifying payload

### Hypothesis 3: HMAC Algorithm or Encoding Issue ⚠️
**Theory:** Mismatch in encoding or algorithm parameters.

**Status:** Resolved - Stripe SDK handles encoding correctly, issue was payload modification

## Debug Logs Added 📝

### 1. Router Level (`router.py`)
```python
- Request method, URL, headers
- Content-Type, User-Agent
- Payload type, length, first 300 bytes
- Signature header full content
- Timestamp of verification start
```

### 2. Stripe Client Level (`stripe_client.py`)
```python
- Webhook secret (start/end, length)
- Signature components (t, v1, v0)
- Payload validation (type, is_bytes, length)
- Manual signature computation
- Comparison: expected vs computed
- Test scenarios with different secrets
```

### 3. Error Handling
```python
- Detailed exception info
- ValueError vs SignatureVerificationError
- Stripe error codes and params
- Full traceback for unexpected errors
```

### 4. Debug Files
Saved to `/tmp/stripe_webhook_debug/` in container:
- `payload.bin` - Raw payload bytes
- `signed_payload.bin` - Timestamp + payload (what gets signed)
- `signature_info.txt` - All signature metadata

## Research Findings 📚

### From Stripe Documentation & Community

1. **Common Causes** ([Stripe Docs](https://docs.stripe.com/webhooks/signature)):
   - Using wrong endpoint secret (Dashboard vs CLI vs test vs live)
   - Request body parsed before verification
   - Payload modified by middleware/proxy
   - Incorrect encoding of payload or secret

2. **FastAPI Specific** ([GitHub Issues](https://github.com/vercel/nextjs-subscription-payments/issues/176)):
   - Must use `await request.body()` for raw bytes
   - Cannot use automatic JSON parsing
   - Body can only be read once

3. **Stripe CLI Behavior** ([Stripe CLI Docs](https://docs.stripe.com/stripe-cli/use-cli)):
   - CLI generates unique webhook secret per session
   - Secret shown in terminal during `stripe listen`
   - Different from Dashboard-managed endpoints

## Current Workaround (Development Only) ⚠️

**Status:** TEMPORARY - Not production-safe

**Location:** `backend/app/modules/billing/router.py` (removed in latest version)

**Previous Implementation:**
- Used custom `dict_to_obj()` to bypass signature verification
- Parsed JSON directly instead of using Stripe SDK
- **Security Risk:** No signature validation!

**Current Status:**
- Workaround removed
- Native Stripe SDK verification active
- All webhooks failing (500 errors)

## Next Actions 🎯

### Immediate (Today)
1. ✅ Added comprehensive debug logging
2. 🔄 Test with hardcoded CLI secret (in progress)
3. ⏳ Analyze debug files in `/tmp/stripe_webhook_debug/`
4. ⏳ Manual HMAC calculation verification
5. ⏳ Compare with working webhook examples online

### Short-term
1. Test with Dashboard webhook endpoint (instead of CLI)
2. Try Stripe webhook testing service (webhook.site)
3. Contact Stripe support if issue persists
4. Consider alternative: Accept webhooks unsigned in dev (with warnings)

### Production Readiness
- ❌ **BLOCKER:** Cannot deploy without working signature verification
- ❌ Security risk: Accepting unsigned webhooks
- ✅ All other functionality working (checkout, subscriptions, admin)

## Files Modified

### Backend
- `app/modules/billing/router.py` - Added extensive request logging
- `app/modules/billing/stripe_client.py` - Added manual signature verification
- `app/modules/billing/webhook_handler.py` - Fixed object access patterns

### Documentation
- `docs/plans/stripe-subscription-implementation.md` - Updated status
- `docs/plans/stripe-webhook-signature-troubleshooting.md` - This file

## Related Issues

- [Stripe Node Issue #1254](https://github.com/stripe/stripe-node/issues/1254) - Similar signature errors
- [Next.js Payments Issue #176](https://github.com/vercel/nextjs-subscription-payments/issues/176) - FastAPI-like framework issues
- [Stripe Java Issue #919](https://github.com/stripe/stripe-java/issues/919) - CLI signature verification

## Test Commands

```bash
# Start Stripe CLI forwarding
stripe listen --forward-to localhost:8000/api/billing/webhooks/stripe

# Trigger test webhook
stripe trigger checkout.session.completed

# Check backend logs
docker logs gear-stack-app -f | grep -i webhook

# Check debug files
docker exec gear-stack-app ls -la /tmp/stripe_webhook_debug/
docker exec gear-stack-app cat /tmp/stripe_webhook_debug/signature_info.txt

# Verify webhook secret in container
docker exec gear-stack-app python -c "from app.core.config import settings; print(settings.stripe.webhook_secret)"
```

## Expected vs Actual Behavior

### Expected ✅
```
1. Stripe CLI forwards webhook
2. Backend receives raw bytes
3. Signature computed: timestamp + "." + payload
4. HMAC-SHA256 with webhook_secret
5. Computed signature matches v1 signature
6. Event processed successfully
7. HTTP 200 OK returned
```

### Actual ❌
```
1. Stripe CLI forwards webhook ✅
2. Backend receives raw bytes ✅
3. Signature computed correctly ✅
4. HMAC-SHA256 with webhook_secret ✅
5. Computed signature DOES NOT match v1 ❌
6. SignatureVerificationError raised ❌
7. HTTP 500 returned ❌
```

## Conclusion

**Root Cause:** The `ConvertEmptyStringsToNoneMiddleware` was modifying JSON payloads by parsing and re-serializing them, which changed the raw bytes used for signature verification. Stripe webhook signatures are computed on the exact original payload bytes, so any modification (even formatting changes from `json.dumps()`) invalidates the signature.

**Solution Implemented:** Added path exclusion in middleware to skip processing Stripe webhook endpoints (`/api/billing/webhook*`), ensuring raw payload bytes remain unchanged for signature verification.

**Status:** ✅ **RESOLVED** - Fix verified and working.

**Verification Steps Completed:**
1. ✅ Fix implemented in `convert_empty_strings_middleware.py`
2. ✅ Tested webhook with `stripe trigger checkout.session.completed`
3. ✅ Signature verification succeeds (verified in logs)
4. ✅ Webhook processing works end-to-end
5. ✅ Removed excessive debug logging
6. ✅ Fixed invoice subscription field access (handles both object and string ID)

**Final Solution:**
- Added webhook path exclusion in `ConvertEmptyStringsToNoneMiddleware`
- Webhook paths defined in `app.modules.billing.constants.WEBHOOK_PATHS`
- Middleware now skips processing webhook endpoints, preserving raw payload bytes
- Stripe SDK signature verification works correctly
