# Chi-Square Tests of Independence: Violation Category vs. Grouping

H0: the distribution of ReasonGuard violation categories (NONE/V1-V5/MIXED, 
collapsed to a single label per response as in the F1/Kappa analysis) is 
independent of the grouping variable. p < 0.05 rejects H0 -- i.e. violation 
category is associated with that grouping variable.

## violation_category_vs_model

- Groups: gemini-2.5-flash-lite, gpt-4o-mini, llama3.1:8b-instruct-q4_0, mistral:7b-instruct-v0.3-q4_0, phi3:mini
- Violation labels tested: NONE, V1, V4, V5, MIXED
- Labels dropped (zero count across all groups): V2, V3
- Chi-square statistic: 649.0541
- Degrees of freedom: 16
- p-value: 0.0
- Significant at alpha=0.05: yes -- reject H0, violation category is associated with this grouping variable

## violation_category_vs_proxy_event_type

- Groups: function_code_violation_proxy_until_official_schema, network_scan_proxy_until_official_schema, normal_modbus_polling_proxy_until_official_schema, topology_change_proxy_until_official_schema
- Violation labels tested: NONE, V1, V4, V5, MIXED
- Labels dropped (zero count across all groups): V2, V3
- Chi-square statistic: 39.0946
- Degrees of freedom: 12
- p-value: 0.000102
- Significant at alpha=0.05: yes -- reject H0, violation category is associated with this grouping variable
