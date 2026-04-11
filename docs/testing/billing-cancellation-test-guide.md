# Billing Cancellation Test Guide

## Prerequisites

- Backend running in Docker: `docker-compose -f backend/docker-compose.dev.yml up`
- Frontend running: `pnpm dev`
- Stripe CLI installed and logged in: `stripe login`
- Test mode API keys configured in `.env`

## Test Scenarios

### Scenario 1: Cancel Subscription at Period End

**Goal:** Verify that user can schedule cancellation at the end of billing period.

**Steps:**
1. Log in as a user with an active Pro subscription
2. Navigate to Billing page (`/billing`)
3. Click "Manage Subscription" button
   - Should redirect to Stripe Billing Portal
4. In Stripe Portal, click "Cancel subscription"
5. Choose "Cancel at period end"
6. Confirm cancellation
7. Return to app (use return URL)
8. Verify on Billing page:
   - ✅ Subscription status shows "Active"
   - ✅ Warning banner shows "Subscription will cancel on [date]"
   - ✅ `cancelAtPeriodEnd` is `true`
9. Check database:
   ```sql
   SELECT * FROM subscriptions WHERE user_id = 'user_id';
   -- Should show: cancel_at_period_end = true
   ```
10. Check webhook events:
    ```sql
    SELECT event_type, processed FROM stripe_webhook_events
    WHERE event_type = 'customer.subscription.updated'
    ORDER BY created_at DESC LIMIT 1;
    -- Should show: processed = true
    ```

**Expected Behavior:**
- User retains access until period end
- UI shows cancellation warning
- Database reflects scheduled cancellation
- Webhook processed successfully

---

### Scenario 2: Immediate Cancellation

**Goal:** Verify immediate cancellation via Stripe Portal.

**Steps:**
1. Log in as a user with an active Pro subscription
2. Navigate to Billing page
3. Click "Manage Subscription" → Stripe Portal
4. Click "Cancel subscription"
5. Choose "Cancel immediately" (if available)
6. Confirm cancellation
7. Return to app
8. Verify on Billing page:
   - ✅ Subscription status shows "Canceled"
   - ✅ No access to premium features
   - ✅ Upgrade prompt appears
9. Check database:
   ```sql
   SELECT status, canceled_at FROM subscriptions WHERE user_id = 'user_id';
   -- Should show: status = 'canceled', canceled_at = [timestamp]
   ```

**Expected Behavior:**
- User loses access immediately
- UI shows FREE tier
- Database reflects cancellation
- Subscription history logged

---

### Scenario 3: Reactivate Canceled Subscription

**Goal:** Verify that user can reactivate a scheduled cancellation.

**Steps:**
1. Start with subscription scheduled for cancellation (Scenario 1)
2. Navigate to Billing page
3. Click "Manage Subscription" → Stripe Portal
4. Click "Reactivate subscription" or "Resume subscription"
5. Confirm reactivation
6. Return to app
7. Verify on Billing page:
   - ✅ Warning banner removed
   - ✅ `cancelAtPeriodEnd` is `false`
   - ✅ Subscription shows as fully active

**Expected Behavior:**
- Cancellation canceled
- Full access restored
- UI reflects active status

---

### Scenario 4: Cancellation with Stripe CLI

**Goal:** Test webhook handling for cancellation events.

**Setup:**
```bash
# Terminal 1: Start webhook forwarding
stripe listen --forward-to localhost:8000/api/billing/webhooks/stripe

# Terminal 2: Trigger cancellation event
stripe trigger customer.subscription.deleted
```

**Steps:**
1. Run trigger command
2. Check backend logs for webhook processing
3. Check database:
   ```sql
   SELECT * FROM stripe_webhook_events
   WHERE event_type = 'customer.subscription.deleted'
   ORDER BY created_at DESC LIMIT 1;
   ```
4. Verify subscription status updated

**Expected Behavior:**
- Webhook received and processed
- Subscription marked as canceled
- Subscription history entry created
- User premium status synced

---

### Scenario 5: Grandfathered User Cancellation Attempt

**Goal:** Verify that grandfathered users cannot cancel their subscription.

**Steps:**
1. Log in as user with grandfathered subscription
2. Navigate to Billing page
3. Verify:
   - ✅ "Manage Subscription" button is disabled or hidden
   - ✅ Crown icon shows next to plan name
   - ✅ "Lifetime Pro Access" badge displayed
4. Attempt API call to cancel (via DevTools):
   ```javascript
   fetch('/api/billing/subscription/cancel', { method: 'POST' })
   ```
5. Verify error response:
   - ✅ Status: 403 Forbidden
   - ✅ Message: "Cannot cancel grandfathered subscription"

**Expected Behavior:**
- UI prevents cancellation
- API rejects cancellation
- Grandfathered status preserved

---

## Webhook Verification Checklist

After each test scenario, verify webhooks:

1. **Check webhook logs:**
   ```bash
   docker exec gear-stack-app tail -f /app/logs/app.log | grep "webhook"
   ```

2. **Check database:**
   ```sql
   -- Webhook events
   SELECT event_type, processed, error_message, created_at
   FROM stripe_webhook_events
   ORDER BY created_at DESC LIMIT 10;

   -- Subscription history
   SELECT event_type, old_status, new_status, created_at
   FROM subscription_history
   ORDER BY created_at DESC LIMIT 10;
   ```

3. **Expected webhook events for cancellation:**
   - `customer.subscription.updated` (when cancel_at_period_end = true)
   - `customer.subscription.deleted` (when subscription actually ends)

---

## Common Issues & Troubleshooting

### Issue: Webhook not received

**Solution:**
- Check Stripe CLI is running: `stripe listen --forward-to localhost:8000/api/billing/webhooks/stripe`
- Verify webhook endpoint is accessible: `curl -X POST http://localhost:8000/api/billing/webhooks/stripe`
- Check backend logs for errors

### Issue: Cancellation doesn't reflect in UI

**Solution:**
- Hard refresh page (Ctrl+Shift+R)
- Check browser console for errors
- Verify TanStack Query cache invalidation
- Check API response: `/api/billing/subscription`

### Issue: Database not updated

**Solution:**
- Check webhook processing logs
- Verify database connection
- Check for constraint violations
- Review subscription_history table for errors

---

## Test Data Cleanup

After testing, clean up test data:

```sql
-- Remove test subscriptions
DELETE FROM subscription_history WHERE user_id = 'test_user_id';
DELETE FROM subscriptions WHERE user_id = 'test_user_id';
DELETE FROM stripe_webhook_events WHERE created_at < NOW() - INTERVAL '1 hour';
```

Or use Stripe Dashboard to delete test customers and subscriptions.

---

## Success Criteria

✅ All 5 scenarios pass without errors
✅ Webhooks processed successfully (200 OK)
✅ Database reflects all state changes
✅ UI updates correctly after each action
✅ Subscription history logged for all changes
✅ User premium status synced correctly

---

## Next Steps

After completing manual tests:
1. Document any bugs found
2. Create tickets for issues
3. Update test plan if needed
4. Consider automating critical paths with E2E tests (future)
