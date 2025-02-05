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

def my_copy(TempUpdate):
    for key, value in TempUpdate.items():
        if not os.path.exists(os.path.dirname(value)):  # 不存在文件夹就创建文件夹
            os.makedirs(os.path.dirname(value))
        try:
            shutil.copy2(key, value)  # 复制替换文件
        except:
            os.chmod(key, stat.S_IWRITE)  # 取消只读权限
            if os.path.exists(value):
                os.chmod(value, stat.S_IWRITE)  # 取消只读权限
            try:
                shutil.copy2(key, value)
            except:
                print(red(f'复制失败{key} > {value}'))

def my_delete(TempRemove):
    for key in TempRemove:
        try:
            os.remove(key)
        except:
            os.chmod(key, stat.S_IWRITE)  # 取消只读权限
            os.remove(key)

def my_move(TempRename):
    for key, value in TempRename.items():
        if not os.path.exists(os.path.dirname(value)):  # 不存在文件夹就创建文件夹
            os.makedirs(os.path.dirname(value))
        try:
            shutil.move(key, value)
        except:
            os.chmod(key, stat.S_IWRITE)  # 取消只读权限
            try:
                shutil.move(key, value)
            except:
                print(red(f'重命名失败{key} > {value}'))
def list_to_dict_with_md5(root,list1):
    dict1={}
    for i in list1:
        md5=get_file_md5(os.path.normpath(os.path.join(root,i)))
        if md5 in dict1.keys():
            dict1[md5].append(i)
        else:
            dict1[md5]=[i]
    return dict1
def red(str):
    return f'\033[91m{str}\033[0m'
def green(str):
    return f'\033[32m{str}\033[0m'
def yellow(str):
    return f'\033[33m{str}\033[0m'
def blue(str):
    return f'\033[34m{str}\033[0m'
def dirCompare(raw_root, backup_root, blacklist):
    print(green(f'--------------------- {raw_root} ---------------------'))

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
        # elif get_file_md5(l) == get_file_md5(r):  # md5 相同，则 #文件大小不同，应该不需要再比较md5
        #     os.utime(r, (t1, t2))  # 修改：修改日期
        else:
            print(green(f'更新:{l} > {r}'))
            TempUpdate[l] = r

    if len(TempUpdate) > 0:
        if input("Update?(Y/N):") in ['Y', 'y']:
            my_move(TempUpdate)
    ################### rename ###################
    onlyIn_Raw = list(setA - setB)
    onlyIn_backup = list(setB - setA)
    onlyIn_Raw_d = list_to_dict_with_md5(raw_root, onlyIn_Raw)
    onlyIn_backup_d= list_to_dict_with_md5(backup_root, onlyIn_backup)
    renamelist=set(onlyIn_Raw_d.keys()) & set(onlyIn_backup_d.keys())#从只在一边的里面找是否有重命名的情况
    # print(onlyIn_Raw,onlyIn_backup)
    # print(onlyIn_Raw_d,onlyIn_backup_d)
    # print(renamelist)
    TempRename = {}
    TempCopy = {}
    TempRemove = []
    for md5 in renamelist: #遍历需要重命名的onlyIn_Raw文件的md5
        len1 = len(onlyIn_Raw_d[md5])
        len2 = len(onlyIn_backup_d[md5])
        list1 = [os.path.normpath(os.path.join(backup_root,i)) for i in onlyIn_Raw_d[md5]]#重命名后的 文件名
        list2 = [os.path.normpath(os.path.join(backup_root, i)) for i in onlyIn_backup_d[md5]]#重命名前的 文件
        if len1 == len2:
            for i in range(len1):
                TempRename[list2[i]] = list1[i]
                print(yellow(f'重命名:{list2[i]} > {list1[i]}'))
                onlyIn_Raw.remove(os.path.relpath(list1[i], backup_root))
                onlyIn_backup.remove(os.path.relpath(list2[i], backup_root))
        elif len1 > len2:
            for i in range(len1):
                try:
                    TempRename[list2[i]] = list1[i]
                    print(yellow(f'重命名:{list2[i]} > {list1[i]}'))
                    onlyIn_Raw.remove(os.path.relpath(list1[i], backup_root))
                    onlyIn_backup.remove(os.path.relpath(list2[i], backup_root))
                except:
                    TempCopy[list1[0]] = list1[i]#len1 > len2，所以肯定存在list1[0]，把第一个拿来复制
                    print(green(f'复制:{list1[0]} > {list1[i]}'))
                    onlyIn_Raw.remove(os.path.relpath(list1[i], backup_root))
        elif len1 < len2:
            for i in range(len2):
                try:
                    TempRename[list2[i]] = list1[i]
                    print(yellow(f'重命名:{list2[i]} > {list1[i]}'))
                    onlyIn_Raw.remove(os.path.relpath(list1[i], backup_root))
                    onlyIn_backup.remove(os.path.relpath(list2[i], backup_root))
                except:
                    TempRemove.append(list2[i])
                    print(green(f'删除:{list2[i]}'))
                    onlyIn_backup.remove(os.path.relpath(list2[i], backup_root))
        if len(TempRename) > 0 or len(TempCopy) > 0 or len(TempRemove) > 0:
            if input("Rename?(Y/N):") in ['Y', 'y']:
                my_move(TempRename)
                my_copy(TempCopy)
                my_delete(TempRemove)





    ################### onlyIn_Raw ： copy ###################
    TempCopy = {}
    if len(onlyIn_Raw) > 0:
        for of in sorted(onlyIn_Raw):  # 遍历列表，复制到备份文件夹
            l = os.path.normpath(os.path.join(raw_root, of))
            r = os.path.normpath(os.path.join(backup_root, of))
            print(green(f'复制:{l} > {r}'))
            TempCopy[l] = r
        if input("Copy?(Y/N):") in ['Y', 'y']:
            my_copy(TempCopy)

    ################### onlyIn_backup ： remove ###################
    TempRemove = []
    if len(onlyIn_backup) > 0:
        for of in sorted(onlyIn_backup):  # 遍历列表删除
            r = os.path.normpath(os.path.join(backup_root, of))
            print(red(f'删除:{r}'))
            TempRemove.append(r)
        if input("Delete?(Y/N):") in ['Y', 'y']:
            my_delete(TempRemove)


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
