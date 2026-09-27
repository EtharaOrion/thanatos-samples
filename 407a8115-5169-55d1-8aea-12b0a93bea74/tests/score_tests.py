"""One equal share per declared behavior; infrastructure failures are unavailable."""
import json
import os
from pathlib import Path
import shutil
import sys
import traceback

SCORING_PROFILE = 'native-conformance/v1'


def score_details(states, weights, integrity=(), requires=None):
    valid = bool(weights) and set(states) == set(weights) and all(s in {'passed', 'failed'} for s in states.values())
    total = sum(weights.values())
    earned = sum(w for key, w in weights.items() if states.get(key) == 'passed')
    return dict(graded=valid, reward=earned / total if valid else 0.0,
                weight_earned=earned, weight_total=total, weight_penalty=0.0)


def main():
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    logs = Path(os.environ.get('ASSAY_LOG_DIR', '/logs/verifier'))
    logs.mkdir(parents=True, exist_ok=True)
    reward = dict(score=None, reward=0.0, graded=False, status='ungraded')
    for name in ('outcomes.json', 'suite_states.json', 'verifier-error.txt', 'native-summary.json', 'restore.log', 'build.log', 'native.log', 'backend-results.json', 'frontend-results.json', 'backend.log', 'frontend.log', 'postgres.log', 'redis.log', 'dependencies.log', 'postgres-init.log', 'postgres-createdb.log', 'twenty-shared-build.log', 'twenty-emails-build.log', 'twenty-client-sdk-build.log'):
        (logs / name).unlink(missing_ok=True)
    shutil.rmtree(logs / 'native', ignore_errors=True)
    try:
        from test_outputs import run
        config = json.loads((here / 'config.json').read_text())
        weights = json.loads((here / 'test_weights.json').read_text())
        if weights != dict.fromkeys(config['groups'], 1):
            raise ValueError('Every behavior group must have one equal share')
        outcomes = run(config, logs)
        if set(outcomes) != set(weights):
            raise ValueError('Missing behavioral verdicts')
        states = {key: 'passed' if value['passed'] else 'failed' for key, value in outcomes.items()}
        details = score_details(states, weights)
        reward.update(details, score=details['reward'], status='graded',
                      passed_groups=sum(value['passed'] for value in outcomes.values()), total_groups=len(weights))
        (logs / 'outcomes.json').write_text(json.dumps(outcomes, indent=2)+'\n')
        (logs / 'suite_states.json').write_text(json.dumps(states, indent=2)+'\n')
    except Exception as exc:
        reward['reason'] = str(exc)
        (logs / 'verifier-error.txt').write_text(traceback.format_exc())
    finally:
        for name in ('reward.json', 'score.json'):
            (logs / name).write_text(json.dumps(reward, indent=2)+'\n')
        (logs / 'reward.txt').write_text(str(reward['reward'])+'\n')
    print(json.dumps(reward), flush=True)


if __name__ == '__main__':
    main()
