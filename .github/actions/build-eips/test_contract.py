#!/usr/bin/env python3
"""Run the real V2 CI adapter against tiny local Git repositories.

No releases, hosted Actions, or remote proposal sources are required. Supply the
exact candidate binary and an empty evidence directory. Zola must be on PATH.
"""
from __future__ import annotations
import argparse
import importlib.util
import html as html_module
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SCHEMA = '0.10.0+793e8459b9ab9b4d955d2f98bf4283b94926f6a3e94d5462e392d98b67ac9729'


def cmd(*args, cwd=None):
    return subprocess.check_output([str(x) for x in args], cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def commit(path):
    cmd('git', '-C', path, 'add', '-A')
    cmd('git', '-C', path, 'commit', '-qm', 'contract fixture')
    return cmd('git', '-C', path, 'rev-parse', 'HEAD')


def init(path):
    cmd('git', 'init', '-q', '-b', 'master', path)
    cmd('git', '-C', path, 'config', 'user.name', 'CI contract test')
    cmd('git', '-C', path, 'config', 'user.email', 'ci@example.invalid')
    return commit(path)


def outputs(path):
    lines=path.read_text().splitlines(); result={}; index=0
    while index < len(lines):
        name, delimiter=lines[index].split('<<', 1); index += 1; value=[]
        while index < len(lines) and lines[index] != delimiter:
            value.append(lines[index]); index += 1
        assert index < len(lines), 'unterminated Actions output'
        result[name]='\n'.join(value); index += 1
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--build-eips', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args=parser.parse_args(); binary=args.build_eips.resolve(strict=True)
    root=args.evidence.resolve(); root.mkdir(parents=True, exist_ok=False)
    runner=root/'runner';runner.mkdir()
    theme=root/'theme'
    write(theme/'theme.toml','name="CI contract"\n')
    write(theme/'config/zola.toml','base_url="https://unused.invalid/"\ntheme="eips-theme"\ncompile_sass=false\nbuild_search_index=false\n')
    write(theme/'config/eipw.toml',f'schema-version="{SCHEMA}"\n[fetch]\nproposal-format="{{:05}}"\n[lints.preamble-file-name]\nformat="{{:05}}"\n')
    for template in ['index.html','section.html','page.html','eip.html']:
        write(theme/'templates'/template,'<html><link rel="canonical" href="{{ current_url }}">{{ page.content | default(value=section.content) | safe }}</html>')
    # Define separate page/section templates; undefined fallback arguments should
    # not make the fixture rely on special Tera missing-value handling.
    for template in ['index.html','section.html']:
        write(theme/'templates'/template,'<html><link rel="canonical" href="{{ current_url }}">{{ section.content | safe }}</html>')
    for template in ['page.html','eip.html']:
        write(theme/'templates'/template,'<html><link rel="canonical" href="{{ current_url }}">{{ page.content | safe }}</html>')
    write(theme/'config/config.markdownlint.yaml','default: false\n')
    pin=init(theme)
    sibling=root/'ERCs';write(sibling/'content/00002.md','---\neip: 2\ntitle: Sibling\n---\nSIBLING\n');init(sibling)
    active=root/'EIPs'
    def manifest():
        return f'name="EIPs"\n[locations.EIPs]\nrepository="{active.as_uri()}"\nbase-url="https://publish.example.test/EIPs/"\n[locations.ERCs]\nrepository="{sibling.as_uri()}"\nbase-url="https://publish.example.test/ERCs/"\n[theme]\nrepository="{theme.as_uri()}"\ncommit="{pin}"\n'
    write(active/'Build.toml',manifest())
    write(active/'content/_index.md','+++\ntitle="Home"\n+++\nHome\n')
    write(active/'content/00001.md','---\neip: 1\ntitle: Active\n---\nCOMMITTED INPUT\n');head=init(active)
    # The adapter must use the exact committed snapshot, not local dirt.
    write(active/'content/00001.md','LOCAL DIRTY INPUT MUST NOT BE PUBLISHED')
    write(active/'content/00003.md','UNTRACKED MUST NOT BE PUBLISHED')
    before_status=cmd('git','-C',active,'status','--porcelain=v1')
    before_index=(active/'.git/index').read_bytes()
    rows=[]
    for i, arguments in enumerate(['build', 'check', 'editorial check --against-upstream --format github', 'changed', 'build --definitely-not-an-option']):
        output=root/f'outputs-{i}.txt';output.write_text('')
        env=os.environ.copy();env.update(RUNNER_TEMP=str(runner), GITHUB_OUTPUT=str(output), GIT_TERMINAL_PROMPT='0')
        env['PATH']=str(binary.parent)+os.pathsep+env['PATH']
        with (root/f'command-{i}.log').open('w') as stream:
            process=subprocess.run([sys.executable,str(HERE/'ci.py'),'run','--repo',str(active),'--build-eips',str(binary),'--args',arguments],
                env=env,stdout=stream,stderr=subprocess.STDOUT)
        got=outputs(output)
        expect_success=i<4
        assert (process.returncode==0)==expect_success, (arguments,(root/f'command-{i}.log').read_text())
        assert got['source-commit']==head
        assert cmd('git','-C',got['theme-path'],'rev-parse','HEAD')==pin
        workspace=Path(got['workspace-root'])
        assert '127.0.0.1' not in (workspace/'.build-eips.toml').read_text()
        if i==0:
            site=Path(got['output-path'])
            assert site==workspace/'build/output'
            html=(site/'1/index.html').read_text()
            assert 'COMMITTED INPUT' in html and 'LOCAL DIRTY INPUT' not in html
            assert 'https://publish.example.test/EIPs/1/' in html_module.unescape(html)
            assert (site/'2/index.html').is_file() and not (site/'3/index.html').exists()
        else:
            assert 'output-path' not in got, 'Non-build or failed command must not advertise a successful artifact'
        if arguments=='changed':
            assert not got['stdout'], 'Setup output must not pollute changed-file paths'
        assert cmd('git','-C',active,'rev-parse','HEAD')==head
        assert cmd('git','-C',active,'status','--porcelain=v1')==before_status
        assert (active/'.git/index').read_bytes()==before_index
        rows.append({'args':arguments,'exit':process.returncode,'outputs':got,'source_unchanged':True})
        (root/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
        print('PASS',arguments,flush=True)
    # Exercise nonempty changed-file output and actual editorial lint, not just
    # the no-change fast path. Keep master at the original upstream baseline.
    cmd('git', '-C', active, 'restore', 'content/00001.md')
    (active/'content/00003.md').unlink()
    cmd('git', '-C', active, 'checkout', '--quiet', '--detach', head)
    write(active/'content/00001.md', '---\neip: 1\ntitle: Active\n---\nCHANGED COMMITTED INPUT\n')
    changed_head=commit(active)
    for i, arguments in enumerate(['changed', 'editorial check --against-upstream --format github'], start=5):
        output=root/f'outputs-{i}.txt';output.write_text('')
        env=os.environ.copy();env.update(RUNNER_TEMP=str(runner), GITHUB_OUTPUT=str(output), GIT_TERMINAL_PROMPT='0')
        env['PATH']=str(binary.parent)+os.pathsep+env['PATH']
        with (root/f'command-{i}.log').open('w') as stream:
            process=subprocess.run([sys.executable,str(HERE/'ci.py'),'run','--repo',str(active),'--build-eips',str(binary),'--args',arguments], env=env,stdout=stream,stderr=subprocess.STDOUT)
        got=outputs(output)
        expected_exit=0 if arguments=='changed' else 1
        # This deliberately minimal proposal violates editorial requirements.
        # A real lint failure must preserve GitHub annotations AND its exit code;
        # the earlier no-change case separately proves the success path.
        assert process.returncode==expected_exit, (arguments,(root/f'command-{i}.log').read_text())
        assert got['source-commit']==changed_head
        if arguments=='changed':
            assert got['stdout'].splitlines()==['content/00001.md'], got['stdout']
        else:
            assert '::error ' in got['stdout'] and 'file=content/00001.md' in got['stdout'], got['stdout']
        assert not cmd('git','-C',active,'status','--porcelain=v1')
        rows.append({'args':arguments,'scenario':'nonempty-upstream-diff','exit':process.returncode,'expected_exit':expected_exit,'outputs':got,'source_unchanged':True})
        (root/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
        print('PASS nonempty upstream diff:',arguments,flush=True)
    spec=importlib.util.spec_from_file_location('ci_adapter',HERE/'ci.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    for repo,revision in [('owner/repo','latest'),('owner/repo','main'),('../repo','a'*40),('owner/repo;id','a'*40)]:
        try: module.fetch_tool(repo,revision)
        except ValueError: pass
        else: raise AssertionError('Unsafe/mutable tool ref was accepted')
    # Round-trip adversarial multiline output; no reserved EOF sentinel exists.
    output=root/'roundtrip-output.txt';output.write_text('');old=os.environ.get('GITHUB_OUTPUT');os.environ['GITHUB_OUTPUT']=str(output)
    module.output('stdout','first\nEOF\nlast')
    if old is None: del os.environ['GITHUB_OUTPUT']
    else: os.environ['GITHUB_OUTPUT']=old
    assert outputs(output)['stdout']=='first\nEOF\nlast'
    print('PASS immutable ref validation and multiline outputs',flush=True)

if __name__=='__main__':
    main()
