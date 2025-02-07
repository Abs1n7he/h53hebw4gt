import glob
import os
import shutil
import stat

import yaml
import hashlib
if __name__ == '__main__':
    config=glob.glob('*.yaml')
    for i in range(len(config)):
        print(f'{i} : {config[i]}')
    switch=int(input('选择配置运行:'))
    configFile=config[switch]


    with open(configFile, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        f.close()

    black_file = config['black_file']
    black_suffix = config['black_suffix']

    for _, i in config['doit'].items():
        dirCompare(i['raw_root'], i['backup_root'], i['blacklist'])
        Emptyfolder(i['backup_root'])

    print("\ndone!")