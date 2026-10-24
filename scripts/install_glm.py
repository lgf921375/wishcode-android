"""Stage GLM builtin into the pinned upstream deployment contracts; no network/build."""
import json
import shutil
import subprocess
from pathlib import Path

def install(root):
    root = Path(root)
    assets = root / 'app/src/main/assets'
    name = 'dsh-wishcode-glm'
    plugin = Path(__file__).resolve().parents[1] / 'plugins' / name
    registry_path = assets / 'builtin-plugins.json'
    registry = json.loads(registry_path.read_text())
    if registry['schema'] != 1 or any(p['name'] == name for p in registry['plugins']):
        raise ValueError('GLM_REGISTRY_DRIFT')
    contract_path = assets / 'managed-runtime-inputs.json'
    contract = json.loads(contract_path.read_text())
    if contract['schema'] != 1: raise ValueError('GLM_DEPLOYMENT_DRIFT')
    target = assets / 'builtin-plugins' / name
    if target.exists(): raise ValueError('GLM_ALREADY_STAGED')
    registry['plugins'].append(dict(name=name,guestDirectory='/root/dsha-wishcode-glm',entrypoint='lib/index.js',internal=False))
    for path in sorted(plugin.rglob('*')):
        if path.is_file():
            relative = path.relative_to(plugin).as_posix()
            contract['installs'].append(dict(asset=f'builtin-plugins/{name}/{relative}',target=f'root/dsha-wishcode-glm/{relative}',executable=False))
    gradle = root / 'app/build.gradle'
    build = gradle.read_text()
    # customize.py already sets this new parallel-install APK to versionCode 192.
    # GLM must not bump it again or silently rewrite the package identity.
    before_name = 'versionName "0.5-preview-002-dsh0.2.1-rc.2"'
    after_name = 'versionName "0.5-preview-002-glm53-dsh0.2.1-rc.2"'
    if build.count('versionCode 192') != 1 or build.count(before_name) != 1:
        raise ValueError('GLM_VERSION_DRIFT')
    if build.count('applicationId "app.wishcode.harnessmobile.v05trial2"') != 1:
        raise ValueError('GLM_PACKAGE_DRIFT')
    gradle.write_text(build.replace(before_name, after_name))
    shutil.copytree(plugin,target)
    shutil.copyfile(Path(__file__).with_name('WishCodeGlmSettings.java'),root / 'app/src/main/java/com/deepseekharness/app/ui/WishCodeGlmSettings.java')
    registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    contract_path.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
    subprocess.run(['python3',str(root/'tools/generate-builtin-plugins.py')],check=True)

if __name__ == '__main__':
    import sys
    install(sys.argv[1])
