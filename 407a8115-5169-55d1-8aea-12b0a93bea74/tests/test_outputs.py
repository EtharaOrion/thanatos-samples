"""Run immutable integration fixtures against a disposable submitted source tree."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import time


def command(argv, cwd, logs, name, env=None, timeout=600):
    try:
        result = subprocess.run(argv, cwd=cwd, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b''
        (logs / name).write_text(output.decode(errors='replace') if isinstance(output, bytes) else output)
        raise RuntimeError(f'Measurement unavailable: {name} exceeded {timeout}s') from exc
    (logs / name).write_text(result.stdout)
    return result.returncode


def source_digest(tree):
    records = []
    for root, dirs, files in os.walk(tree):
        dirs[:] = sorted(d for d in dirs if d not in {'.git', 'node_modules', 'dist', '.nx', '__pycache__'})
        for name in sorted(files):
            if name.startswith('._'):
                continue
            path = Path(root) / name
            if path.relative_to(tree).as_posix() in {'.yarn/install-state.gz', '.yarn/build-state.yml'}:
                continue
            contents = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
            records.append(str(path.relative_to(tree)) + '\0' + hashlib.sha256(contents).hexdigest())
    return hashlib.sha256('\n'.join(sorted(records)).encode()).hexdigest()


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def run(config, logs):
    workspace = Path(os.environ.get('TASK_WORKSPACE', '/workspace'))
    cache = Path('/opt/twenty-cache')
    pg = Path('/usr/lib/postgresql/15/bin')
    for tool in ('node', 'redis-server', 'runuser'):
        if shutil.which(tool) is None:
            raise RuntimeError(f'Measurement unavailable: required tool {tool} is absent')
    if not (pg / 'initdb').is_file() or not (cache / 'node_modules/jest/bin/jest.js').is_file():
        raise RuntimeError('Measurement unavailable: PostgreSQL or pinned external dependency cache is absent')

    def absent(reason):
        (logs / 'native-summary.json').write_text(json.dumps({
            'classification': 'migration_absent', 'reason': reason,
            'native_groups_executed': 0,
            'note': 'No native assertion verdict is claimed for an empty or byte-identical source prerequisite.'}, indent=2)+'\n')
        return {key: {'passed': False, 'classification': 'migration_absent', 'reason': reason} for key in config['groups']}

    current = source_digest(workspace)
    if not any(p.is_file() and p.suffix in ('.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs')
               for p in workspace.rglob('*') if 'node_modules' not in p.parts):
        return absent('Empty submission: no JavaScript or TypeScript implementation is present')
    if current == config['base_source_digest']:
        return absent('The submitted source tree is byte-identical to the unmigrated base')
    for relative in config['required_files']:
        if not (workspace / relative).is_file():
            raise RuntimeError(f'Measurement unavailable: published interface is missing or relocated: {relative}')
    if hashlib.sha256((workspace / 'yarn.lock').read_bytes()).hexdigest() != config['lock_sha256']:
        raise RuntimeError('Measurement unavailable: dependency lock differs from the published offline environment')

    with tempfile.TemporaryDirectory(prefix='twenty-session-verifier-') as scratch_name:
        scratch = Path(scratch_name)
        scratch.chmod(0o755)
        tree = scratch / 'tree'
        shutil.copytree(workspace, tree, symlinks=True,
                        ignore=shutil.ignore_patterns('.git', 'node_modules', 'dist', '.nx', '._*'))
        # Relative workspace symlinks must resolve into submitted source, never image source.
        if command(['cp', '-a', str(cache) + '/.', str(tree)], scratch, logs, 'dependencies.log'):
            raise RuntimeError('Measurement unavailable: external dependency staging failed')
        native = scratch / 'native'
        native.mkdir()
        (native / 'node_modules').symlink_to(tree / 'node_modules', target_is_directory=True)
        def rewrite_paths(value):
            if isinstance(value, dict):
                return {k: rewrite_paths(v) for k, v in value.items()}
            if isinstance(value, list):
                return [rewrite_paths(v) for v in value]
            if isinstance(value, str):
                for old, new in (('/workspace', str(tree)), ('/verify-work', str(native))):
                    if value == old or value.startswith(old + '/'):
                        return new + value[len(old):]
            return value
        for relative, contents in config['source_files'].items():
            path = native / relative
            path.write_text(json.dumps(rewrite_paths(json.loads(contents))) if relative.endswith('.json') else contents)
        env = dict(os.environ, NODE_OPTIONS='--max-old-space-size=16384', NX_DAEMON='false',
                   YARN_ENABLE_NETWORK='0', NODE_PATH=str(tree / 'node_modules'),
                   TWENTY_PG_PORT=str(free_port()), TWENTY_REDIS_PORT=str(free_port()),
                   TWENTY_HTTP_PORT=str(free_port()))
        for package in ('twenty-shared', 'twenty-emails', 'twenty-client-sdk'):
            rc = command(['node', str(tree / 'node_modules/vite/bin/vite.js'), 'build'],
                         tree / 'packages' / package, logs, package + '-build.log', env)
            if rc:
                raise RuntimeError(f'Measurement unavailable: submitted {package} runtime build failed')
        data = scratch / 'postgres'
        data.mkdir()
        shutil.chown(data, user='postgres', group='postgres')
        pg_prefix = ['runuser', '-u', 'postgres', '--']
        if command(pg_prefix + [str(pg / 'initdb'), '-D', str(data), '--auth=trust', '--no-locale', '--encoding=UTF8'],
                   scratch, logs, 'postgres-init.log', env):
            raise RuntimeError('Measurement unavailable: isolated PostgreSQL initialization failed')
        pg_handle = (logs / 'postgres.log').open('w')
        redis_handle = (logs / 'redis.log').open('w')
        processes = []
        try:
            processes.append(subprocess.Popen(pg_prefix + [str(pg / 'postgres'), '-D', str(data),
                             '-h', '127.0.0.1', '-p', env['TWENTY_PG_PORT'], '-k', str(data)],
                             stdout=pg_handle, stderr=subprocess.STDOUT, cwd=scratch, env=env))
            processes.append(subprocess.Popen(['redis-server', '--bind', '127.0.0.1', '--port',
                             env['TWENTY_REDIS_PORT'], '--save', '', '--appendonly', 'no', '--dir', str(scratch)],
                             stdout=redis_handle, stderr=subprocess.STDOUT, cwd=scratch, env=env))
            for _ in range(100):
                pg_ready = subprocess.run([str(pg / 'pg_isready'), '-h', '127.0.0.1', '-p', env['TWENTY_PG_PORT']],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
                redis_ready = subprocess.run(['redis-cli', '-h', '127.0.0.1', '-p', env['TWENTY_REDIS_PORT'], 'PING'],
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
                if pg_ready and redis_ready:
                    break
                if any(p.poll() is not None for p in processes):
                    raise RuntimeError('Measurement unavailable: local database process exited during startup')
                time.sleep(0.1)
            else:
                raise RuntimeError('Measurement unavailable: local PostgreSQL/Redis readiness timeout')
            if command([str(pg / 'createdb'), '-h', '127.0.0.1', '-p', env['TWENTY_PG_PORT'], '-U', 'postgres', 'twenty_verifier'],
                       scratch, logs, 'postgres-createdb.log', env):
                raise RuntimeError('Measurement unavailable: isolated test database creation failed')
            outcomes = {}
            for suite in ('backend', 'frontend'):
                ready = scratch / 'native-ready'
                ready.unlink(missing_ok=True)
                env['TWENTY_READY_FILE'] = str(ready)
                report = logs / (suite + '-results.json')
                rc = command(['node', str(tree / 'node_modules/jest/bin/jest.js'), '--config',
                              str(native / (suite + '-jest.json')), '--runInBand', '--json', '--outputFile', str(report)],
                             tree, logs, suite + '.log', env, config['timeout_seconds'])
                if not report.is_file():
                    raise RuntimeError(f'Measurement unavailable: {suite} produced no structured report')
                result = json.loads(report.read_text())
                if not ready.is_file() or result.get('numRuntimeErrorTestSuites', 0):
                    raise RuntimeError(f'Measurement unavailable: {suite} setup or module import failed; see {suite}.log')
                observed = {}
                for test_file in result.get('testResults', []):
                    for item in test_file.get('assertionResults', []):
                        match = re.match(r'^(C\d+)\b', item['title'])
                        if not match or match[1] in observed or item['status'] not in ('passed', 'failed'):
                            raise RuntimeError(f'Measurement unavailable: {suite} test discovery/status mismatch')
                        if item['status'] == 'failed' and not any(isinstance(x, dict) and isinstance(x.get('matcherResult'), dict)
                                                                for x in item.get('failureDetails', [])):
                            # 1.0.4: a test that fails by crashing before its first assertion (for example, the submission's own
                            # code throws) is a measured failure of that group, not an unavailable measurement of the whole run.
                            observed[match[1]] = {'passed': False, 'title': item['title'], 'crashed_before_assertion': True}
                            continue
                        observed[match[1]] = {'passed': item['status'] == 'passed', 'title': item['title']}
                expected = {k for k, v in config['groups'].items() if v['suite'] == suite + '.spec.' + ('tsx' if suite == 'frontend' else 'ts')}
                if set(observed) != expected or rc not in (0, 1) or (rc == 0) != all(v['passed'] for v in observed.values()):
                    raise RuntimeError(f'Measurement unavailable: {suite} incomplete or contradictory native results')
                outcomes.update(observed)
            (logs / 'native-summary.json').write_text(json.dumps({
                'classification': 'native_behavior', 'native_groups_executed': len(outcomes),
                'native_groups_passed': sum(x['passed'] for x in outcomes.values()),
                'frontend_environment': 'Node-hosted JSDOM, real local HTTP, submitted Apollo/React/Jotai',
                'outcomes': outcomes}, indent=2)+'\n')
            return outcomes
        finally:
            for p in reversed(processes):
                if p.poll() is None:
                    p.terminate()
                    try:
                        p.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        p.wait()
            pg_handle.close()
            redis_handle.close()
