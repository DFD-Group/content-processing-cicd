# Folder & File purpose
db/
  migrations/# Flyway scans this for V*.sql (and R*.sql if you add later)
  flyway.toml # Flyway 9+ unified config
  README.md # runbook: env vars, who runs Flyway, order vs deploy

# Flyway versioning = filenames
## Every change is a new file:

- Pattern: V<version>__<short_description>.sql
- Examples: V1__init_auth_and_app.sql, V2__add_pdf_status_index.sql
- Version is typically an integer; Flyway sorts lexicographically, so use V01 vs V10 carefully — common practice is V1, V2, … V9, V10 (Flyway handles this if versions are pure numbers without weird padding mistakes). Safer habit: no padding (V1, V2, … V10) or always use consistent width if you pad (V001).
Rule: After a script has been applied in any shared environment (staging/prod), never edit that file. Fix forward with V{n+1}.