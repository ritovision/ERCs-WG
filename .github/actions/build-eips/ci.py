#!/usr/bin/env python3
"""GitHub/local CI adapter for the V2 workspace contract (Python 3.11+).

All checkout/build state is created under a fresh RUNNER_TEMP directory. The
input repository is read-only: CI evaluates its exact HEAD, not uncommitted or
untracked local files. No shell evaluation is used for tool arguments.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import tomllib
import uuid
from pathlib import Path


def command(args: list[str | Path], *, capture: bool = False, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([str(arg) for arg in args], cwd=cwd, check=True,
                          text=True, encoding='utf-8', errors='replace',
                          stdout=subprocess.PIPE if capture else sys.stderr,
                          stderr=sys.stderr)


def git(repo: Path, *args: str) -> str:
    return command(['git', '-c', 'core.hooksPath=/dev/null', '-C', repo, *args], capture=True).stdout.strip()


def output(name: str, value: str) -> None:
    destination = os.environ.get('GITHUB_OUTPUT')
    if not destination:
        return
    delimiter = 'BUILD_EIPS_' + uuid.uuid4().hex
    while delimiter in value.splitlines():
        delimiter = 'BUILD_EIPS_' + uuid.uuid4().hex
    with open(destination, 'a', encoding='utf-8') as stream:
        stream.write(f'{name}<<{delimiter}\n{value}\n{delimiter}\n')


def fresh_root(prefix: str) -> Path:
    parent = Path(os.environ.get('RUNNER_TEMP', tempfile.gettempdir())).resolve()
    if not parent.is_dir():
        raise ValueError(f'Runner temporary directory does not exist: {parent}')
    return Path(tempfile.mkdtemp(prefix=prefix, dir=parent))


def fetch_tool(repository: str, revision: str) -> Path:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository) or any(
            part in ('.', '..') for part in repository.split('/')):
        raise ValueError('tool-repository must be a GitHub owner/repository')
    if not re.fullmatch(r'[0-9a-fA-F]{40}', revision):
        raise ValueError('tool-ref must be a complete immutable 40-hex commit, not latest/a branch/tag')
    source = fresh_root('build-eips-tool-') / 'source'
    command(['git', 'init', '--quiet', source])
    git(source, 'remote', 'add', 'origin', f'https://github.com/{repository}.git')
    git(source, 'fetch', '--depth=1', 'origin', revision)
    fetched = git(source, 'rev-parse', 'FETCH_HEAD^{commit}')
    if fetched.lower() != revision.lower():
        raise ValueError(f'Fetched tool commit {fetched} did not match {revision}')
    git(source, 'checkout', '--quiet', '--detach', fetched)
    output('source', str(source))
    output('revision', fetched)
    return source


def run_workspace(source: Path, binary: Path, raw_args: str) -> int:
    args = shlex.split(raw_args, posix=True)
    if not args or args[0] not in {'build', 'check', 'changed', 'editorial'}:
        raise ValueError('CI supports build, check, changed, and editorial commands only')
    source = Path(git(source.resolve(), 'rev-parse', '--show-toplevel')).resolve()
    revision = git(source, 'rev-parse', 'HEAD^{commit}')
    manifest = tomllib.loads(git(source, 'show', f'{revision}:Build.toml'))
    name = manifest.get('name')
    if not isinstance(name, str) or not name or name in {'.', '..', 'theme', 'build', 'WORKSPACE.md'} or any(
            char in name for char in '/\\\x00\r\n:') or name.startswith('.'):
        raise ValueError('The committed Build.toml name is not a safe proposal checkout directory name')
    binary = binary.resolve(strict=True)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise ValueError(f'build-eips is not an executable file: {binary}')
    root = fresh_root('build-eips-ci-')
    active = root / name
    print(f'CI workspace: {root}; exact source commit: {revision}', file=sys.stderr)
    command(['git', '-c', 'core.hooksPath=/dev/null', 'clone', '--no-hardlinks', '--no-checkout', source, active])
    git(active, 'checkout', '--quiet', '--detach', revision)
    if git(active, 'rev-parse', 'HEAD') != revision:
        raise ValueError('CI source clone does not match the requested source commit')
    if (active / '.build-eips.toml').exists() or (active / '.build-eips.toml').is_symlink():
        raise ValueError('A proposal checkout must not override the CI-owned workspace config')
    command([binary, '-C', active, 'init', root])
    # init's starter config is for local development. CI deliberately has no
    # site override or target filter: Build.toml supplies the publication URL.
    (root / '.build-eips.toml').write_text('# CI: manifest publication URL, all proposals, local committed siblings.\n', encoding='utf-8')
    if git(active, 'status', '--porcelain=v1'):
        raise ValueError('Workspace initialization unexpectedly dirtied the active CI checkout')
    if args[0] in {'build', 'check'} and '--clean' not in args:
        args.append('--clean')
    # Editorial has no --clean option. Its source is nevertheless the freshly
    # checked-out, verified-clean exact commit above, with no user-edit overlay.
    build_root = root / 'build'
    with binary.open('rb') as stream:
        binary_digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    metadata = {'active': name, 'source_commit': revision, 'command': args,
                'build_root': str(build_root), 'output': str(build_root / 'output'),
                'binary_sha256': binary_digest,
                'repository_heads': {}}
    for child in root.iterdir():
        if child.is_dir() and (child / '.git').exists():
            metadata['repository_heads'][child.name] = git(child, 'rev-parse', 'HEAD')
    (root / 'workspace-evidence.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    output('workspace-root', str(root))
    output('theme-path', str(root / 'theme'))
    output('source-commit', revision)
    result = subprocess.run([str(binary), '-C', str(active), '--build-root', str(build_root), *args],
                            text=True, encoding='utf-8', errors='replace', stdout=subprocess.PIPE)
    sys.stdout.write(result.stdout)
    output('stdout', result.stdout.rstrip('\n'))
    if result.returncode:
        return result.returncode
    if args[0] == 'build':
        site = build_root / 'output'
        if not site.is_dir() or not any(site.iterdir()):
            raise ValueError('Build returned success without creating the expected nonempty output directory')
        output('output-path', str(site))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='operation', required=True)
    fetch = sub.add_parser('fetch-tool')
    fetch.add_argument('--repository', required=True)
    fetch.add_argument('--revision', required=True)
    run = sub.add_parser('run')
    run.add_argument('--repo', required=True, type=Path)
    run.add_argument('--build-eips', required=True, type=Path)
    run.add_argument('--args', required=True)
    args = parser.parse_args()
    try:
        if args.operation == 'fetch-tool':
            fetch_tool(args.repository, args.revision)
            return 0
        return run_workspace(args.repo, args.build_eips, args.args)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'build-eips CI failed: {error}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
