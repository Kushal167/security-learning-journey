# Race Conditions — Notes

## What is a Race Condition?
When a server processes multiple requests at the same time and they interact with the same data, causing unintended behavior. The server has a tiny gap between steps that can be exploited.

---

## Types of Race Conditions

### 1. Limit Overrun
Send the same request many times simultaneously to bypass a rate limit or counter.
```
POST /login × 100 at the same time → bypass lockout
```

### 2. Multi-Endpoint
Two different endpoints hit simultaneously, colliding on shared data.
```
POST /cart/checkout  ↘  simultaneously
POST /cart            ↗
→ sneaks expensive item past the payment check
```

### 3. Single-Endpoint
Same endpoint, different data, sent simultaneously. Confuses the server's read/write order.
```
POST /change-email (carlos@...)  ↘  simultaneously
POST /change-email (yours@...)   ↗
→ receive carlos's confirmation email at your address
```

### 4. Partial Construction
An object is created in multiple steps, leaving a temporary uninitialized state that can be exploited.
```
Step 1: User created in DB     → exists but token = NULL
Step 2: Token set              → token = "abc123"
→ send token[]= during the gap to match NULL state
```

### 5. Time-Sensitive Attack
Not a logic race — the token itself is predictable because it's based on a timestamp.
```
Two requests at same millisecond → same token generated
→ use your token to reset someone else's password
```

---

## Key Concepts

### Single-Packet Attack
Holds all requests back and sends them in one TCP packet burst so they all arrive at the server at the exact same time. Eliminates network jitter.
- Use `Engine.BURP2` in Turbo Intruder
- Use `concurrentConnections=1`
- Use gates to hold and release requests

### Gates
A gate holds requests until `openGate()` is called, then releases them all simultaneously.
```python
engine.queue(req, payload, gate='1')  # hold
engine.openGate('1')                  # release all at once
```

### Connection Warming
First request on a connection is always slow (sets up the route). Send a throwaway request first to warm the connection so subsequent requests travel at the same speed.
```
GET /  → warms connection
Then send real attack requests in parallel
```

### Atomic Operations
All or nothing — no gap between steps. The fix for most race conditions.
```sql
BEGIN TRANSACTION
  CHECK credit
  CONFIRM order
COMMIT  -- both happen together, no gap
```

### Sub-States
Hidden temporary states a server passes through while processing a single request.
```
Request hits → [authenticated] → [mfa not enforced yet] → [mfa enforced]
                                         ↑
                               attack here during this sub-state
```

---

## How to Hunt Race Conditions

1. **Predict** — find endpoints that read/write the same data
2. **Probe** — send simultaneous requests, look for anomalies
3. **Prove** — narrow down to minimum requests needed to trigger reliably

---

## Prevention

| Strategy | What it Fixes |
|----------|--------------|
| Atomic DB transactions | Gaps between multi-step operations |
| DB uniqueness constraints | Duplicate object creation |
| One storage system | Data sync issues |
| Batch session updates | Auth/MFA bypass via session gaps |
| Don't mix storage layers | Session can't protect database |
| Client-side state (JWT) | Server-side race windows |
