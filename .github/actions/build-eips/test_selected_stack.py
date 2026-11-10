#!/usr/bin/env python3
"""Verify the actual checked-in tool/theme selectors via scoped local Git remotes.

Requires Python 3.11+, PyYAML, Cargo, Git and Zola. Network/hosted Actions/Pages
are intentionally not asserted: declared URLs are rewritten to explicit local
repositories in this process only. No project/global Git configuration is edited.
"""
from __future__ import annotations
import argparse,fcntl,hashlib,importlib.util,json,os,shutil,subprocess,sys,tomllib
from pathlib import Path
import yaml
sys.dont_write_bytecode=True


def execute(args, *, capture=False, env=None):
    p=subprocess.run([str(a) for a in args],env=env,check=True,text=True,
                     stdout=subprocess.PIPE if capture else sys.stdout,stderr=sys.stderr)
    return p.stdout.strip() if capture else ''


def load_module(path):
    spec=importlib.util.spec_from_file_location('selected_ci',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def outputs(path):
    result={};lines=iter(path.read_text().splitlines())
    for line in lines:
        name,delimiter=line.split('<<',1);parts=[]
        for part in lines:
            if part==delimiter:break
            parts.append(part)
        result[name]='\n'.join(parts)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',type=Path,required=True);parser.add_argument('--evidence',type=Path,required=True);parser.add_argument('--cargo-target',type=Path,required=True)
    args=parser.parse_args();workspace=args.workspace.resolve();out=args.evidence.resolve();out.mkdir(parents=True,exist_ok=False)
    home=out/'home';home.mkdir();(out/'runner').mkdir();gitconfig=home/'.gitconfig';gitconfig.write_text('')
    env=os.environ.copy();env.update(HOME=str(home),XDG_CONFIG_HOME=str(out/'xdg'),CARGO_HOME=os.environ.get('CARGO_HOME',str(Path.home()/'.cargo')),RUSTUP_HOME=os.environ.get('RUSTUP_HOME',str(Path.home()/'.rustup')),GIT_CONFIG_GLOBAL=str(gitconfig),GIT_CONFIG_NOSYSTEM='1',GIT_TERMINAL_PROMPT='0',GIT_ALLOW_PROTOCOL='file',RUNNER_TEMP=str(out/'runner'),PYTHONDONTWRITEBYTECODE='1')
    # Unmapped HTTP must fail on loopback rather than fetching a different stack.
    env.update(http_proxy='http://127.0.0.1:9',https_proxy='http://127.0.0.1:9',HTTP_PROXY='http://127.0.0.1:9',HTTPS_PROXY='http://127.0.0.1:9',NO_PROXY='')
    head=lambda p:execute(['git','-C',p,'rev-parse','HEAD'],capture=True)
    tool_head=head(workspace/'build-eips');theme_head=head(workspace/'theme')
    selections={};mapping={}
    for repo in ('EIPs','ERCs'):
        source=workspace/repo;action=source/'.github/actions/build-eips'
        config=yaml.safe_load((action/'action.yml').read_text());manifest=tomllib.loads((source/'Build.toml').read_text())
        tool_repo=config['inputs']['tool-repository']['default'];tool_ref=config['inputs']['tool-ref']['default']
        assert tool_ref==tool_head,(repo,tool_ref,tool_head)
        assert manifest['theme']['commit']==theme_head,(repo,manifest['theme']['commit'],theme_head)
        mapping[f'https://github.com/{tool_repo}.git']=workspace/'build-eips'
        mapping[manifest['theme']['repository']]=workspace/'theme'
        for name,location in manifest['locations'].items():mapping[location['repository']]=workspace/name
        selections[repo]={'source_head':head(source),'tool_repository':tool_repo,'tool_commit':tool_ref,'theme_repository':manifest['theme']['repository'],'theme_commit':theme_head,'publication_url':manifest['locations'][repo]['base-url']}
    assert (workspace/'EIPs/.github/actions/build-eips/ci.py').read_bytes()==(workspace/'ERCs/.github/actions/build-eips/ci.py').read_bytes()
    for url,path in mapping.items():
        execute(['git','config','--file',gitconfig,'--add',f'url.{path.as_uri()}.insteadOf',url],env=env)
    (out/'selections.json').write_text(json.dumps(selections,indent=2)+'\n')
    original_env=os.environ.copy();os.environ.clear();os.environ.update(env)
    try:
        ci=load_module(workspace/'EIPs/.github/actions/build-eips/ci.py')
        chosen=selections['EIPs'];os.environ['GITHUB_OUTPUT']=str(out/'fetch-outputs.txt')
        fetched=ci.fetch_tool(chosen['tool_repository'],chosen['tool_commit'])
        assert head(fetched)==tool_head
        target=args.cargo_target.resolve();target.mkdir(parents=True,exist_ok=True)
        with (target.parent/'.cargo-candidate.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            build_env=os.environ.copy();build_env['CARGO_TARGET_DIR']=str(target)
            execute(['cargo','clean','--manifest-path',fetched/'Cargo.toml','-p','build-eips'],env=build_env)
            execute(['cargo','build','--locked','--offline','--manifest-path',fetched/'Cargo.toml','-j','2','--bin','build-eips'],env=build_env)
            binary=out/'build-eips';shutil.copy2(target/'debug/build-eips',binary)
        result={'selectors':selections,'fetched_tool_commit':head(fetched),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'local_transport_remapping_only':True,'build_profile':'debug, same locked source; hosted release profile not asserted','cases':[]}
        for repo in ('EIPs','ERCs'):
            source=workspace/repo;output=out/f'{repo}-outputs.txt';output.write_text('');os.environ['GITHUB_OUTPUT']=str(output)
            os.environ['PATH']=str(binary.parent)+os.pathsep+env['PATH']
            original_status=execute(['git','-C',source,'status','--porcelain=v1'],capture=True)
            assert not original_status
            code=ci.run_workspace(source,binary,'build');assert code==0,(repo,code)
            got=outputs(output);metadata=json.loads((Path(got['workspace-root'])/'workspace-evidence.json').read_text())
            assert got['source-commit']==selections[repo]['source_head']
            assert metadata['repository_heads']['theme']==theme_head
            assert metadata['binary_sha256']==result['binary_sha256']
            for name in ('EIPs','ERCs'):assert metadata['repository_heads'][name]==selections[name]['source_head']
            site=Path(got['output-path']);index=(site/'index.html').read_text();assert selections[repo]['publication_url'] in index
            assert not execute(['git','-C',source,'status','--porcelain=v1'],capture=True)
            case={'repo':repo,'exit':code,'workspace':got['workspace-root'],'output':str(site),'files':len([p for p in site.rglob('*') if p.is_file()]),'exact_source_heads':metadata['repository_heads'],'publication_url_matches':True,'input_unchanged':True}
            result['cases'].append(case);(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS EXACT CHECKED-IN SELECTORS',repo,flush=True)
        print('SELECTED STACK VERIFIED LOCALLY; NO HOSTED RUN OR PUBLICATION CLAIMED',flush=True)
    finally:
        os.environ.clear();os.environ.update(original_env)


if __name__=='__main__':main()
