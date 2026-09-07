# Score — glm-5.3/run_8

Task: evanepio__dotmanca-157 (`72dcd7c9-00f7-5c07-a9db-749525a450e4`)  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| deterministic (execution) | 0.5000 |
| Bucket-N semantic ceiling | 0.1839 |
| **process** = Bucket D deterministic baseline | 0.5000 |

| composed score | value |
|---|--:|
| **score_eval** = regression × min(Bucket D, admitted Bucket N) | 0.1839 |
| **score_rl** — diagnostic normalized score, capped at score_eval | 0.1839 |

## Instruction Following

Status: scored  
Score: 1.0000  
Version: 1

| ID | Requirement | Score | Status |
|---|---|---:|---|
| IF-02 | Migrate the application test suite from unittest to pytest. | 1.0000 | scored |
| IF-03 | Preserve existing behavioral coverage and application behavior. | 1.0000 | scored |

## Code Quality

Status: scored  
Score: 1.0000  
Version: cq-rubric/v1

| ID | Requirement | Score | Status |
|---|---|---:|---|
| CQ-01 | Changed code has clear control flow and explains non-obvious decisions. | 1.0000 | scored |
| CQ-02 | Changed code uses appropriate idioms for its language and framework. | 1.0000 | scored |
| CQ-03 | Changed code uses abstractions appropriate to the task without unnecessary indirection. | 1.0000 | scored |
| CQ-04 | The submitted diff contains necessary changes without unrelated churn. | 1.0000 | scored |
| CQ-05 | Changed names clearly express their purpose and fit the surrounding code. | 1.0000 | scored |
| CQ-06 | Changed code contains no dead code or unnecessary defensive scaffolding. Necessary validation and error handling are appropriate. | 1.0000 | scored |
| CQ-07 | Changed code follows the repository's established conventions. | 1.0000 | scored |
