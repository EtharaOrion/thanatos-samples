"""Execute the frozen conformance suites against the submitted Rust packages."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def run(config, logs):
    repo = Path(os.environ.get('THANATOS_WORKSPACE', '/workspace'))
    suites = config['suites']
    results = {}
    manifests = config['required_manifests']
    missing = [p for p in manifests if not (repo/p).is_file()]
    legacy = []
    for pattern in config['legacy_patterns']:
        for p in repo.glob(pattern):
            if not p.is_file():
                continue
            if any(part in {'target', 'node_modules', '.git', 'tests', 'test', 'testdata', 'examples', 'fixtures'} for part in p.relative_to(repo).parts):
                continue
            if p.name.endswith(('_test.go', '.test.ts', '.spec.ts', '.d.ts')):
                continue
            legacy.append(str(p.relative_to(repo)))
    if missing or legacy:
        reason = {'missing_target_manifests': missing, 'remaining_production_source': legacy[:40]}
        for suite in suites:
            results[suite['id']] = {'passed': False, 'reason': reason}
        return results
    if not shutil.which('cargo'):
        raise RuntimeError('Runtime image is missing cargo')
    work = Path(tempfile.mkdtemp(prefix='hard-conformance-'))
    try:
        subject = work/'subject'
        shutil.copytree(repo, subject, symlinks=True, ignore=shutil.ignore_patterns('.git','target','node_modules','.venv','__pycache__'))
        private = work/'suite'; private.mkdir()
        for name, text in config['assets'].items():
            path = private/name
            assert '..' not in Path(name).parts and not Path(name).is_absolute()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        (private/'Cargo.toml').write_text(config['manifest'].replace('__SUBJECT__',str(subject)))
        for rel in config.get('root_fixtures',[]):
            if (subject/rel).is_file():
                path=private/rel;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(subject/rel,path)
        target=work/'target';target.mkdir()
        # Test source is host-owned. Candidate build scripts/test processes run
        # without root privileges and cannot rewrite the frozen suite or logs.
        work.chmod(0o755)
        for p in subject.rglob('*'):
            if p.is_symlink():continue
            if p.is_dir():p.chmod(0o755)
            elif p.is_file():p.chmod(0o755 if os.access(p,os.X_OK) else 0o644)
        subject.chmod(0o755)
        env=dict(os.environ, CARGO_NET_OFFLINE='true', CARGO_TARGET_DIR=str(target), CARGO_BUILD_JOBS='2', HOME='/tmp', RUST_BACKTRACE='0')
        generated=subprocess.run(['cargo','generate-lockfile','--offline','--manifest-path',str(private/'Cargo.toml')],cwd=private,env=env,capture_output=True,text=True,timeout=120)
        (logs/'dependency-resolution.log').write_text(generated.stdout+generated.stderr)
        if generated.returncode:
            return {s['id']:{'passed':False,'reason':'Submitted package dependencies do not resolve in the documented offline runtime'} for s in suites}
        if os.geteuid()==0:
            os.chown(target,65534,65534)
            # Subject code may produce fixture files; it cannot change the verifier.
            for p in [subject,*subject.rglob('*')]:
                if not p.is_symlink():os.chown(p,65534,65534)
        def unprivileged():
            if os.geteuid()==0:
                os.setgroups([]);os.setgid(65534);os.setuid(65534)
                if os.geteuid()!=65534:os._exit(71)
        for suite in suites:
            command=['cargo','test','--locked','--offline','--manifest-path',str(private/'Cargo.toml'),'--test',suite['target'],'--','--test-threads=1','--exact']
            for skipped in suite.get('skip', []):command.extend(['--skip', skipped])
            try:
                proc=subprocess.run(command,cwd=private,env=env,capture_output=True,text=True,errors='replace',timeout=suite.get('timeout',600),preexec_fn=unprivileged)
                output=proc.stdout+'\n'+proc.stderr
                summaries=re.findall(r'test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored;',output)
                count=int(summaries[-1][1]) if summaries else 0
                passed=proc.returncode==0 and bool(summaries) and summaries[-1][0]=='ok' and count>=suite['minimum_tests'] and summaries[-1][3]=='0'
                results[suite['id']]={'passed':passed,'native_passed':count,'minimum_tests':suite['minimum_tests'],'exit_code':proc.returncode}
            except subprocess.TimeoutExpired as exc:
                output=(exc.stdout or b'').decode(errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
                results[suite['id']]={'passed':False,'reason':'Verifier case timeout'}
            (logs/(suite['id']+'.log')).write_text(output)
            print(suite['id'],results[suite['id']],flush=True)
        return results
    finally:
        shutil.rmtree(work,ignore_errors=True)
