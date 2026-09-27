# Rubric grader

The source of the rubric grader that produced the `rubric`, `rubric_if`, `rubric_cq` and `rubric_process`
rewards in every run of this sample. It is shipped here so the rubric scoring can be read without pulling an
image; nothing in this folder is needed to run a task.

| File | What it is |
| :--- | :--- |
| `rubric_grader.py` | The grader: Python 3, standard library only (sha256 `6567023d294748400ebc7a77b5838c13e56749acac7679af79c8540b40d997be`) |
| `Dockerfile` | The grader kit image: this one file at `/opt/grader/rubric_grader.py` |

The same bytes are inside the kit image (`thanatos-envs@sha256:e1cfac1a…`) and inside each task's grader
image, the digest-pinned `[verifier.environment].docker_image` in its `task.toml`.

## How a task uses it

Each task grades in a separate verifier container (Harbor `environment_mode = "separate"`). Its grader image is
built from `tests/Dockerfile`: the task image, plus this kit copied to `/opt/grader/`, plus a copy of the
original workspace at `/opt/grader/original`. `tests/test.sh` then runs:

1. `rubric_grader.py snapshot`: copies the delivered `/workspace` before the tests run, so the rubric reviews
   what the agent delivered and nothing the tests write.
2. The task's tests, unchanged. Their `reward.json` is kept as `reward.tests.json`.
3. `rubric_grader.py judge`: an LLM judge answers each criterion in `tests/rubrics.json` with yes, no or
   cannot tell. Code criteria see the delivered code next to the original; process criteria see the agent
   trajectory (`/logs/agent/trajectory.json`). Every answer, explanation and piece of evidence is written to
   `verifier/rubric-judge.json`.
4. `rubric_grader.py finalize`: rewrites `reward.json` with `reward` and `score` copied unchanged from the
   tests, plus the rubric shares that were measured. Only numbers stay in the file, as Harbor 0.23 requires.

The grader never changes `reward` or `score`, and never modifies `/workspace`. A rubric key is written only
when every criterion in that group was answered yes or no. If anything fails, or the grader is absent, the
test reward is kept byte for byte.

## Running the judge

The judge is any OpenAI-compatible chat-completions endpoint, passed to the verifier:

```bash
harbor run ... --ve RUBRIC_JUDGE_BASE_URL=https://api.openai.com/v1 --ve RUBRIC_JUDGE_API_KEY=<key>
```

`RUBRIC_JUDGE_MODEL` overrides the model named in `tests/rubrics.json` (`gpt-6-sol` for these runs). Without an
endpoint and key the rubric is skipped and the reward is the test reward alone. An LLM judge can answer a few
criteria differently on a rerun, so each run's `verifier/rubric-judge.json` is the record of how its rubric
scores were reached.
