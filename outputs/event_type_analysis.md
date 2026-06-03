# Per-Event-Type Violation Breakdown

Counts and rates of ReasonGuard verdicts grouped by model and proxy event type.

| Model | Event type | Total | Clean | Clean rate | V1 | V2 | V3 | V4 | V5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.1:8b-instruct-q4_0 | function_code_violation_proxy_until_official_schema | 25 | 12 | 48.00% | 2 | 0 | 0 | 12 | 0 |
| llama3.1:8b-instruct-q4_0 | network_scan_proxy_until_official_schema | 25 | 21 | 84.00% | 3 | 0 | 0 | 1 | 0 |
| llama3.1:8b-instruct-q4_0 | normal_modbus_polling_proxy_until_official_schema | 25 | 17 | 68.00% | 4 | 0 | 0 | 5 | 0 |
| llama3.1:8b-instruct-q4_0 | topology_change_proxy_until_official_schema | 25 | 18 | 72.00% | 5 | 0 | 0 | 2 | 0 |
| mistral:7b-instruct-v0.3-q4_0 | function_code_violation_proxy_until_official_schema | 25 | 22 | 88.00% | 3 | 0 | 0 | 0 | 0 |
| mistral:7b-instruct-v0.3-q4_0 | network_scan_proxy_until_official_schema | 25 | 24 | 96.00% | 1 | 0 | 0 | 0 | 0 |
| mistral:7b-instruct-v0.3-q4_0 | normal_modbus_polling_proxy_until_official_schema | 25 | 23 | 92.00% | 2 | 0 | 0 | 0 | 0 |
| mistral:7b-instruct-v0.3-q4_0 | topology_change_proxy_until_official_schema | 25 | 22 | 88.00% | 3 | 0 | 0 | 0 | 0 |
| phi3:mini | function_code_violation_proxy_until_official_schema | 25 | 16 | 64.00% | 5 | 0 | 0 | 4 | 1 |
| phi3:mini | network_scan_proxy_until_official_schema | 25 | 1 | 4.00% | 21 | 0 | 0 | 5 | 1 |
| phi3:mini | normal_modbus_polling_proxy_until_official_schema | 25 | 15 | 60.00% | 3 | 0 | 0 | 8 | 0 |
| phi3:mini | topology_change_proxy_until_official_schema | 25 | 18 | 72.00% | 1 | 0 | 0 | 6 | 0 |
| synthetic_rule_based | function_code_violation_proxy_until_official_schema | 125 | 25 | 20.00% | 25 | 25 | 25 | 100 | 0 |
| synthetic_rule_based | network_scan_proxy_until_official_schema | 125 | 25 | 20.00% | 25 | 0 | 25 | 100 | 0 |
| synthetic_rule_based | normal_modbus_polling_proxy_until_official_schema | 125 | 25 | 20.00% | 25 | 25 | 25 | 100 | 0 |
| synthetic_rule_based | topology_change_proxy_until_official_schema | 125 | 25 | 20.00% | 25 | 25 | 25 | 100 | 0 |
