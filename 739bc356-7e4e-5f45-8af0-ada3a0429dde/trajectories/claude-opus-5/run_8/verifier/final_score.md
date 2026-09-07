# Score — claude-opus-5/run_8

Task: MorAlekss__cli-migration-test-3-5 (`739bc356-7e4e-5f45-8af0-ada3a0429dde`)  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| deterministic (execution) | 1.0000 |
| Bucket-N semantic ceiling | 0.3615 |
| **process** = Bucket D deterministic baseline | 1.0000 |

| composed score | value |
|---|--:|
| **score_eval** = regression × min(Bucket D, admitted Bucket N) | 0.2892 |
| **score_rl** — diagnostic normalized score, capped at score_eval | 0.3615 |

## Instruction Following

Status: scored  
Score: 1.0000  
Version: 1

| ID | Requirement | Score | Status |
|---|---|---:|---|
| IF-01 | Migrate currency and news HTTP requests from requests to asynchronous httpx. | 1.0000 | scored |

## Code Quality

Status: scored  
Score: 0.7329  
Version: cq-rubric/v1

| ID | Requirement | Score | Status |
|---|---|---:|---|
| CQ-01 | Changed code has clear control flow and explains non-obvious decisions. | 0.5000 | scored |
| CQ-02 | Changed code uses appropriate idioms for its language and framework. | 0.5000 | scored |
| CQ-03 | Changed code uses abstractions appropriate to the task without unnecessary indirection. | 1.0000 | scored |
| CQ-04 | The submitted diff contains necessary changes without unrelated churn. | 0.8800 | scored |
| CQ-05 | Changed names clearly express their purpose and fit the surrounding code. | 0.7500 | scored |
| CQ-06 | Changed code contains no dead code or unnecessary defensive scaffolding. Necessary validation and error handling are appropriate. | 0.5000 | scored |
| CQ-07 | Changed code follows the repository's established conventions. | 1.0000 | scored |
