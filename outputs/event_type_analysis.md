# Per-Event-Type Violation Breakdown

Counts and rates of ReasonGuard verdicts grouped by model and proxy event type.

| Model | Event type | Total | Clean | Clean rate | V1 | V2 | V3 | V4 | V5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.1:8b-instruct-q4_0 | function_code_violation_proxy_until_official_schema | 10 | 6 | 60.00% | 3 | 0 | 0 | 2 | 0 |
| llama3.1:8b-instruct-q4_0 | network_scan_proxy_until_official_schema | 10 | 4 | 40.00% | 6 | 0 | 0 | 0 | 0 |
| phi3:mini | function_code_violation_proxy_until_official_schema | 10 | 2 | 20.00% | 8 | 0 | 0 | 3 | 0 |
| phi3:mini | network_scan_proxy_until_official_schema | 10 | 0 | 0.00% | 10 | 0 | 0 | 1 | 1 |
| synthetic_rule_based | function_code_violation_proxy_until_official_schema | 50 | 10 | 20.00% | 10 | 10 | 10 | 40 | 0 |
| synthetic_rule_based | network_scan_proxy_until_official_schema | 50 | 10 | 20.00% | 10 | 0 | 10 | 40 | 0 |
| synthetic_rule_based | normal_modbus_polling_proxy_until_official_schema | 50 | 10 | 20.00% | 10 | 10 | 10 | 40 | 0 |
| synthetic_rule_based | topology_change_proxy_until_official_schema | 50 | 10 | 20.00% | 10 | 10 | 10 | 40 | 0 |
