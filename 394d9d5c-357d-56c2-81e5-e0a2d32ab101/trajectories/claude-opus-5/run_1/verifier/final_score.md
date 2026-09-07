# Score — claude-opus-5/run_1

Task: dan-nor98__pypostboy-45 (`394d9d5c-357d-56c2-81e5-e0a2d32ab101`)  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| deterministic (execution) | 0.5584 |
| Bucket-N semantic ceiling | 0.6411 |
| **process** = Bucket D deterministic baseline | 0.5584 |

| composed score | value |
|---|--:|
| **score_eval** = regression × min(Bucket D, admitted Bucket N) | 0.5584 |
| **score_rl** — diagnostic normalized score, capped at score_eval | 0.5584 |

## Instruction Following

Status: scored  
Score: 0.2500  
Version: 1

| ID | Requirement | Score | Status |
|---|---|---:|---|
| IF-01 | Migrate the PostBoy backend from Flask to Django 5.0.6. | 0.5000 | scored |
| IF-02 | Preserve existing behavioral coverage and application behavior. Existing tests must keep passing. | 0.0000 | scored |

## Code Quality

Status: scored  
Score: 0.8071  
Version: cq-rubric/v1

| ID | Requirement | Score | Status |
|---|---|---:|---|
| CQ-01 | Changed code has clear control flow and explains non-obvious decisions. | 0.9000 | scored |
| CQ-02 | Changed code uses appropriate idioms for its language and framework. | 0.5000 | scored |
| CQ-03 | Changed code uses abstractions appropriate to the task without unnecessary indirection. | 1.0000 | scored |
| CQ-04 | The submitted diff contains necessary changes without unrelated churn. | 1.0000 | scored |
| CQ-05 | Changed names clearly express their purpose and fit the surrounding code. | 0.7500 | scored |
| CQ-06 | Changed code contains no dead code or unnecessary defensive scaffolding. Necessary validation and error handling are appropriate. | 0.5000 | scored |
| CQ-07 | Changed code follows the repository's established conventions. | 1.0000 | scored |
