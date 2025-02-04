import os
import shutil
import stat
from colorama import init
import hashlib
init(autoreset=True)
def get_file_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()


def whereisit(l, r):
    l = set(l)
    r = set(r)
    return list(l - r), list(l & r), list(r - l), list(l ^ r)  # 只在左，共有，只在右,不共有


def getAllFiles(path, black_dir):  # 获取全部文件
    black_dir = list(filter(None, black_dir))  # 去除空值
    file_list = []
    for root, dirs, files in os.walk(path):  # root,dirs,files 目录、文件夹、文件名(列表)
        if not any(i in root for i in black_dir):  # 排除的目录
            for f in files:  # 每个文件名
                if f not in black_file and os.path.splitext(f)[1] not in black_suffix:  # 文件名、扩展名不在黑名单
                    # f: 1.docx
                    f_fullpath = os.path.join(root, f)  # D:\work\tool\Project\备份文件\1\1.docx
                    file_list.append(f_fullpath[len(path) + 1:])  # 相对路径s
    return file_list


def dirCompare(raw_root, backup_root, blacklist):
    print(f'\033[1;32m--------------------- {raw_root} --------------------- \033[0m')

    ################### 获取全部文件，去重 ###################
    raw_files = getAllFiles(raw_root, blacklist)
    backup_files = getAllFiles(backup_root, blacklist)
    setA = set(raw_files)
    setB = set(backup_files)

    ################### 共有文件 update ###################
    commonfiles = setA & setB
    TempUpdate = {}
    for of in sorted(commonfiles):  # 对比共有文件
        l = os.path.normpath(os.path.join(raw_root, of))  # 文件完整路径
        r = os.path.normpath(os.path.join(backup_root, of))
        t1 = os.stat(l).st_mtime  # 文件修改时间
        t2 = os.stat(r).st_mtime
        if t1 == t2 or os.stat(l).st_size == os.stat(r).st_size:  # 修改日期 或 文件大小 相同
            continue
        elif get_file_md5(l) == get_file_md5(r):  # md5 相同，则
            os.utime(r, (t1, t2))  # 修改：修改日期
        else:
            print('\033[1;32m%s\033[0m' % r)
            TempUpdate[l] = r

    if len(TempUpdate) > 0:
        if input("Update?(Y/N):") in ['Y', 'y']:
            for key, value in TempUpdate.items():
                try:
                    shutil.copy2(key, value)  # 复制替换文件
                except:
                    os.chmod(key, stat.S_IWRITE)  # 取消只读权限
                    os.chmod(value, stat.S_IWRITE)  # 取消只读权限
                    shutil.copy2(key, value)

                    ################### onlyIn_Raw ： copy ###################
    onlyIn_Raw = list(setA - setB)
    TempCopy = {}
    if len(onlyIn_Raw) > 0:
        for of in sorted(onlyIn_Raw):  # 遍历列表，复制到备份文件夹
            l = os.path.normpath(os.path.join(raw_root, of))
            r = os.path.normpath(os.path.join(backup_root, of))
            print('\033[1;32m%s\033[0m' % r)
            TempCopy[l] = r
        if input("Copy?(Y/N):") in ['Y', 'y']:
            for key, value in TempCopy.items():
                if not os.path.exists(os.path.dirname(value)):  # 不存在文件夹就创建文件夹
                    os.makedirs(os.path.dirname(value))
                try:
                    shutil.copy2(key, value)  # 复制
                except:
                    print(f'复制失败：{key}')

    ################### onlyIn_backup ： remove ###################
    onlyIn_backup = list(setB - setA)
    TempRemove = []
    if len(onlyIn_backup) > 0:
        for of in sorted(onlyIn_backup):  # 遍历列表删除
            r = os.path.normpath(os.path.join(backup_root, of))
            print('\033[1;31m%s\033[0m' % r)
            TempRemove.append(r)
        if input("Delete?(Y/N):") in ['Y', 'y']:
            for key in TempRemove:
                try:
                    os.remove(key)
                except:
                    os.chmod(key, stat.S_IWRITE)  # 取消只读权限
                    os.remove(key)


################### 删除空文件夹 ###################
def Emptyfolder(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):  # 检查文件夹是否为空
                try:
                    os.rmdir(dir_path)  # 删除
                except:
                    os.chmod(dir_path, 0x1F0FF)  # 取消文件夹只读权限
                    os.rmdir(dir_path)


if __name__ == '__main__':
    black_file = ["desktop.ini", ".idea","__pycache__"]  # 文件名黑名单
    black_suffix = [".pyc"]  # 后缀黑名单

    raw_root = input('源文件目录:')  # 对比文件夹
    backup_root = input('备份目录:')  # 参考文件夹
    dirCompare(raw_root, backup_root, ['\\.idea'])
    Emptyfolder(backup_root)
    print("\ndone!")
