"""Run a verifier-owned MSTest suite against the submitted production projects."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET


def command(argv, cwd, logs, name, timeout=900):
    started = time.monotonic()
    try:
        result = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b''
        if isinstance(output, bytes):
            output = output.decode(errors='replace')
        (logs / name).write_text(output)
        raise RuntimeError(f'Measurement unavailable: {name} exceeded {timeout}s') from exc
    (logs / name).write_text(result.stdout)
    return result.returncode, time.monotonic() - started


def run(config, logs):
    workspace = Path(os.environ.get('TASK_WORKSPACE', config['workspace']))
    groups = config['groups']
    if shutil.which('dotnet') is None:
        raise RuntimeError('Measurement unavailable: the .NET toolchain is absent')
    if not Path('/opt/nuget/packages/modelcontextprotocol/2.2.0').is_dir():
        raise RuntimeError('Measurement unavailable: pinned SDK 2.2.0 package cache is absent')

    def absent(reason):
        (logs / 'native-summary.json').write_text(json.dumps({
            'classification': 'migration_absent', 'reason': reason,
            'native_methods_executed': 0,
            'note': 'No native assertion verdict is claimed for this prerequisite failure.'}, indent=2)+'\n')
        return {key: {'passed': False, 'classification': 'migration_absent', 'reason': reason} for key in groups}

    production = workspace / 'src/Repl.Mcp/Repl.Mcp.csproj'
    package_versions = workspace / 'src/Directory.Packages.props'
    if not any(workspace.rglob('*.cs')):
        return absent('Empty submission: no C# implementation is present')
    if not production.is_file() or not package_versions.is_file():
        raise RuntimeError('Measurement unavailable: published Repl project interface is missing or relocated')
    try:
        manifest = ET.parse(package_versions)
    except ET.ParseError as exc:
        raise RuntimeError('Measurement unavailable: dependency manifest cannot be parsed') from exc
    versions = [e.attrib.get('Version') for e in manifest.iter('PackageVersion')
                if e.attrib.get('Include') == 'ModelContextProtocol']
    if versions == ['1.4.1']:
        return absent('Unchanged ModelContextProtocol 1.4.1 dependency: required SDK 2.2.0 migration is absent')
    if versions != ['2.2.0']:
        raise RuntimeError('Measurement unavailable: expected the published ModelContextProtocol 2.2.0 dependency')

    with tempfile.TemporaryDirectory(prefix='repl-protocol-verifier-') as scratch:
        tree = Path(scratch) / 'tree'
        shutil.copytree(workspace, tree, ignore=shutil.ignore_patterns('.git', 'bin', 'obj', 'TestResults', 'node_modules', '._*'))
        suite = tree / 'src/Repl.McpTests'
        shutil.rmtree(suite, ignore_errors=True)
        suite.mkdir(parents=True)
        for relative, source in config['source_files'].items():
            (suite / relative).write_text(source)
        # No registry access occurs while grading. Missing cache entries are ungraded.
        offline = Path(scratch) / 'offline.nuget.config'
        offline.write_text('<configuration><packageSources><clear /></packageSources></configuration>\n')
        project = str(suite / 'Repl.McpTests.csproj')
        rc, restore_seconds = command(['dotnet', 'restore', project, '--configfile', str(offline),
                                      '--disable-parallel', '-p:NuGetAudit=false'], tree, logs, 'restore.log', 180)
        if rc:
            raise RuntimeError('Measurement unavailable: offline restore failed; see restore.log')
        rc, build_seconds = command(['dotnet', 'build', project, '--no-restore', '--configuration', 'Release',
                                    '-p:NuGetAudit=false'], tree, logs, 'build.log', 300)
        if rc:
            raise RuntimeError('Measurement unavailable: verifier/project compilation is incompatible; see build.log')
        reports = logs / 'native'
        reports.mkdir()
        dll = suite / 'bin/Release/net10.0/Repl.McpTests.dll'
        rc, test_seconds = command(['dotnet', str(dll), '--report-trx', '--report-trx-filename', 'results.trx',
                                   '--results-directory', str(reports)], tree, logs, 'native.log', config['timeout_seconds'])
        report = reports / 'results.trx'
        if not report.is_file():
            raise RuntimeError(f'Measurement unavailable: native runner produced no TRX report (exit {rc})')
        document = ET.parse(report)
        ns = {'t': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
        definitions = {}
        for item in document.findall('.//t:TestDefinitions/t:UnitTest', ns):
            method = item.find('t:TestMethod', ns)
            if method is not None:
                definitions[item.attrib['id']] = method.attrib['name']
        results = {}
        for item in document.findall('.//t:UnitTestResult', ns):
            name = definitions.get(item.attrib.get('testId'))
            if name is None:
                name = item.attrib.get('testName', '').split('(')[0]
            results.setdefault(name, []).append(item.attrib.get('outcome'))
        expected = set(config['test_methods'])
        if set(results) != expected:
            raise RuntimeError('Measurement unavailable: native test discovery mismatch: '
                               f'missing={sorted(expected-set(results))}, unexpected={sorted(set(results)-expected)}')
        unexpected_states = {s for states in results.values() for s in states} - {'Passed', 'Failed'}
        if unexpected_states:
            raise RuntimeError(f'Measurement unavailable: native tests did not complete: {sorted(unexpected_states)}')
        all_passed = all(s == 'Passed' for states in results.values() for s in states)
        if rc not in (0, 2) or (rc == 0) != all_passed:
            raise RuntimeError(f'Measurement unavailable: native exit status {rc} disagrees with test outcomes')
        outcomes = {}
        for key, group in groups.items():
            failed = [name for name in group['tests'] if any(s != 'Passed' for s in results[name])]
            outcomes[key] = {'passed': not failed, 'failed_methods': failed,
                             'methods': len(group['tests']),
                             'cases': sum(len(results[name]) for name in group['tests'])}
        summary = {'classification': 'native_behavior', 'native_methods_executed': len(results),
                   'native_cases_executed': sum(map(len, results.values())),
                   'native_cases_passed': sum(s == 'Passed' for states in results.values() for s in states),
                   'native_exit_code': rc, 'restore_seconds': restore_seconds,
                   'build_seconds': build_seconds, 'test_seconds': test_seconds, 'outcomes': results}
        (logs / 'native-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
        return outcomes
