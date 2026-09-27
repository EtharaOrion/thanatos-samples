"""Score frozen conformance groups; safe to import for host recomputation."""
import json
import os
from pathlib import Path
import traceback
SCORING_PROFILE='native-conformance/v1'
def score_details(states,weights,integrity=(),requires=None):
    graded=bool(weights) and set(states)==set(weights) and all(v in {'passed','failed'} for v in states.values())
    total=sum(weights.values());earned=sum(w for k,w in weights.items() if states.get(k)=='passed')
    return {'graded':graded,'reward':earned/total if graded else 0.0,'weight_earned':earned,'weight_total':total,'weight_penalty':0.0}
def main():
    from test_outputs import run
    logs=Path(os.environ.get('ASSAY_LOG_DIR','/logs/verifier'));logs.mkdir(parents=True,exist_ok=True)
    here=Path(__file__).resolve().parent
    reward={'score':None,'reward':0.0,'graded':False,'status':'ungraded'}
    try:
        config=json.loads((here/'config.json').read_text());weights=json.loads((here/'test_weights.json').read_text())
        outcomes=run(config,logs)
        assert set(outcomes)==set(weights) and weights
        states={k:'passed' if v['passed'] else 'failed' for k,v in outcomes.items()}
        details=score_details(states,weights)
        reward.update(details,score=details['reward'],status='graded',passed_groups=sum(v['passed'] for v in outcomes.values()),total_groups=len(weights))
        (logs/'outcomes.json').write_text(json.dumps(outcomes,indent=2)+'\n')
        (logs/'suite_states.json').write_text(json.dumps(states,indent=2)+'\n')
    except Exception:
        (logs/'verifier-error.txt').write_text(traceback.format_exc())
    finally:
        for name in ['reward.json','score.json']:(logs/name).write_text(json.dumps(reward,indent=2)+'\n')
    print(json.dumps(reward))
if __name__=='__main__':main()
