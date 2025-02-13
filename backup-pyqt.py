import os
import ast
import stat
import yaml
import shutil
import hashlib
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

def get_file_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()

def getAllFiles(path, black_dir,black_file,black_suffix):  # 获取全部文件
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

def list_to_dict_with_md5(root,list1):
    dict1={}
    for i in list1:
        md5=get_file_md5(os.path.normpath(os.path.join(root,i)))
        if md5 in dict1.keys():
            dict1[md5].append(i)
        else:
            dict1[md5]=[i]
    return dict1

def read_table_data(table):
    data={}
    for row in range(table.rowCount()):
        row_data=[]
        for col in range(table.columnCount()):
            item=table.item(row, col)
            if item:
                row_data.append(item.text()) #获取单元格的文本
            else:
                row_data.append('')
        data[row]=row_data
    return data
def Stage(n):
    def grey(str):
        return f'<span style="color:#999999;">{str}</span>'
    def red(str):
        return f'<span style="color:#DC143C;">{str}</span>'
    if n==0:
        return grey(f'开始 ➡️️️ 更新文件 ➡️ 重命名文件 ➡️ 备份新文件 ➡️ 删除文件')
    elif n==1:
        return grey(f'{red("开始")} ➡️️️ 更新文件 ➡️ 重命名文件 ➡️ 备份新文件 ➡️ 删除文件')
    elif n==2:
        return grey(f'开始 ➡️️️ {red("更新文件")} ➡️ 重命名文件 ➡️ 备份新文件 ➡️ 删除文件')
    elif n==3:
        return grey(f'开始 ➡️️️ 更新文件 ➡️ {red("重命名文件")} ➡️ 备份新文件 ➡️ 删除文件')
    elif n==4:
        return grey(f'开始 ➡️️️ 更新文件 ➡️ 重命名文件 ➡️ {red("备份新文件")} ➡️ 删除文件')
    elif n==5:
        return grey(f'开始 ➡️️️ 更新文件 ➡️ 重命名文件 ➡️ 备份新文件 ➡️ {red("删除文件")}')
    else:
        return grey(f'开始 ➡️️️ 更新文件 ➡️ 重命名文件 ➡️ 备份新文件 ➡️ 删除文件')

class CenterAlignDelegate(QStyledItemDelegate):#设置居中对齐
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment=Qt.AlignmentFlag.AlignCenter

################# 线程 #################
class thread_backup(QThread): #备份 文件操作
    def __init__(self, table1):
        super().__init__()
        self.table1 = table1
    def run(self):
        table_data = read_table_data(self.table1)
        for n,list1 in table_data.items():
            if list1[2] in ['更新','复制'] and list1[3] != '成功':
                raw=list1[0]
                backup=list1[1]
                if os.path.exists(raw): #源文件存在
                    if not os.path.exists(os.path.dirname(backup)):# 不存在文件夹就创建
                        os.makedirs(os.path.dirname(backup))
                    try:
                        shutil.copy2(raw,backup) #复制替换文件
                        table_data[n][3]='成功'
                    except:
                        os.chmod(raw,stat.S_IWRITE) #取消只读权限
                        if os.path.isfile(backup):
                            os.chmod(backup, stat.S_IWRITE)
                        try:
                            shutil.copy2(raw, backup)
                            table_data[n][3] = '成功'
                        except:
                            table_data[n][3] = '失败'
                else:
                    table_data[n][3] = '失败'
                self.show_new_table(table_data)
            elif list1[2]=='重命名':
                raw = list1[0]
                backup = list1[1]
                if os.path.exists(raw):  # 源文件存在
                    if not os.path.exists(os.path.dirname(backup)):# 不存在文件夹就创建
                        os.makedirs(os.path.dirname(backup))
                    try:
                        shutil.move(raw,backup) #复制替换文件
                        table_data[n][3]='成功'
                    except:
                        os.chmod(raw, stat.S_IWRITE)  # 取消只读权限
                        try:
                            shutil.move(raw, backup)  # 复制替换文件
                            table_data[n][3] = '成功'
                        except:
                            table_data[n][3] = '失败'
                else:
                    table_data[n][3] = '失败'
                self.show_new_table(table_data)
            elif list1[2]=='删除':
                file = list1[1]
                if os.path.exists(raw):  # 源文件存在
                    try:
                        os.remove(raw)
                        table_data[n][3] = '成功'
                    except:
                        try:
                            os.chmod(raw, stat.S_IWRITE)  # 取消只读权限
                            os.remove(raw)
                            table_data[n][3] = '成功'
                        except:
                            table_data[n][3] = '失败'
                else:
                    table_data[n][3] = '失败'
                self.show_new_table(table_data)
    def show_new_table(self, table_data):
        for n,list1 in table_data.items():
            self.table1.setItem(n,3,QTableWidgetItem(list1[3]))
            if list1[3] == '成功':
                self.table1.item(n,3).setBackground((QColor(0,255,0)))
            elif list1[3] == '失败':
                self.table1.item(n, 3).setBackground((QColor(255, 0, 0)))

class thread_select(QThread): #备份 文件查询
    def __init__(self, raw_root,backup_root,black_file,black_suffix,blacklist,table1,steps,txt1,txt2):
        super().__init__()
        self.raw_root = raw_root
        self.backup_root = backup_root
        self.black_file = black_file
        self.black_suffix = black_suffix
        self.blacklist = blacklist
        self.table1 = table1
        self.steps = steps #进度
        self.txt1 = txt1
        self.txt2 = txt2

    def run(self):
        self.table1.setRowCount(1)
        self.table1.clearContents()
        if self.steps.text() == Stage(0):
            self.steps.setText(Stage(1))

        elif self.steps.text() == Stage(1):
            self.steps.setText(Stage(2))
            setA,setB = self.shou1() #展示需要更新的文件
            self.txt1.setText(str(setA))
            self.txt2.setText(str(setB))

        elif self.steps.text() == Stage(2):
            self.steps.setText(Stage(3))
            onlyIn_Raw,onlyIn_backup=self.shou2(ast.literal_eval(self.txt1.text()),ast.literal_eval(self.txt2.text()))#展示需要重命名的文件
            self.txt1.setText(str(onlyIn_Raw))
            self.txt2.setText(str(onlyIn_backup))

        elif self.steps.text() == Stage(3):
            self.steps.setText(Stage(4))
            self.show3(ast.literal_eval(self.txt1.text()))#展示要备份的文件

        elif self.steps.text() == Stage(4):
            self.steps.setText(Stage(5))
            self.show4(ast.literal_eval(self.txt2.text()))#展示要备份的文件

        elif self.steps.text() == Stage(5):
            self.steps.setText(Stage(0))
    def shou1(self):
        ################## 获取全部文件，去重 ##################
        raw_files = getAllFiles(self.raw_root,self.blacklist,self.black_file,self.black_suffix)
        backup_files = getAllFiles(self.backup_root,self.blacklist,self.black_file,self.black_suffix)
        setA=set(raw_files)
        setB=set(backup_files)
        ################## 共有文件 update ##################
        commonfiles = setA & setB
        TempUpdate = {}
        for of in sorted(commonfiles):  # 对比共有文件
            l = os.path.normpath(os.path.join(self.raw_root, of))  # 文件完整路径
            r = os.path.normpath(os.path.join(self.backup_root, of))
            t1 = os.stat(l).st_mtime  # 文件修改时间
            t2 = os.stat(r).st_mtime
            if t1 == t2 or os.stat(l).st_size == os.stat(r).st_size:  # 修改日期 或 文件大小 相同
                continue
            # elif get_file_md5(l) == get_file_md5(r):  # md5 相同，则 #文件大小不同，应该不需要再比较md5
            #     os.utime(r, (t1, t2))  # 修改：修改日期
            else:
                TempUpdate[l] = r
        self.table1.setRowCount(len(TempUpdate)+1)
        i=0
        for key,value in TempUpdate.items():
            self.table1.setItem(i, 0, QTableWidgetItem(key))
            self.table1.setItem(i, 1, QTableWidgetItem(value))
            self.table1.setItem(i, 2, QTableWidgetItem('更新'))
            self.table1.item(i, 2).setBackground(QColor(0,255,0))
            i+=1
        return setA,setB
    def show2(self,setA,setB):
        ################### rename ###################
        onlyIn_Raw = list(setA - setB)
        onlyIn_backup = list(setB - setA)
        onlyIn_Raw_d = list_to_dict_with_md5(self.raw_root, onlyIn_Raw)
        onlyIn_backup_d = list_to_dict_with_md5(self.backup_root, onlyIn_backup)
        renamelist = set(onlyIn_Raw_d.keys()) & set(onlyIn_backup_d.keys())  # 从只在一边的里面找是否有重命名的情况

        TempRename = {}
        TempCopy = {}
        TempRemove = []
        for md5 in renamelist:  # 遍历需要重命名的onlyIn_backup文件的md5
            len1 = len(onlyIn_Raw_d[md5])
            len2 = len(onlyIn_backup_d[md5])
            list1 = [os.path.normpath(os.path.join(self.backup_root, i)) for i in onlyIn_Raw_d[md5]]  # 重命名后的 文件名
            list2 = [os.path.normpath(os.path.join(self.backup_root, i)) for i in onlyIn_backup_d[md5]]  # 重命名前的 文件
            if len1 == len2:
                for i in range(len1):
                    TempRename[list2[i]] = list1[i]
                    onlyIn_Raw.remove(os.path.relpath(list1[i], self.backup_root))
                    onlyIn_backup.remove(os.path.relpath(list2[i], self.backup_root))
            elif len1 > len2:
                for i in range(len1):
                    try:
                        TempRename[list2[i]] = list1[i]
                        onlyIn_Raw.remove(os.path.relpath(list1[i], self.backup_root))
                        onlyIn_backup.remove(os.path.relpath(list2[i], self.backup_root))
                    except:
                        TempCopy[list1[0]] = list1[i]  # len1 > len2，所以肯定存在list1[0]，把第一个拿来复制
                        onlyIn_Raw.remove(os.path.relpath(list1[i], self.backup_root))
            elif len1 < len2:
                for i in range(len2):
                    try:
                        TempRename[list2[i]] = list1[i]
                        onlyIn_Raw.remove(os.path.relpath(list1[i], self.backup_root))
                        onlyIn_backup.remove(os.path.relpath(list2[i], self.backup_root))
                    except:
                        TempRemove.append(list2[i])
                        onlyIn_backup.remove(os.path.relpath(list2[i], self.backup_root))
        self.table1.setRowCount(len(TempRename)+len(TempCopy)+len(TempRemove)+1)
        i=0
        for key,value in TempRename.items():
            self.table1.setItem(i, 0, QTableWidgetItem(key))
            self.table1.setItem(i, 1, QTableWidgetItem(value))
            self.table1.setItem(i, 2, QTableWidgetItem('重命名'))
            self.table1.item(i, 2).setBackground(QColor(0, 255, 0))
            i += 1
        for key,value in TempCopy.items():
            self.table1.setItem(i, 0, QTableWidgetItem(key))
            self.table1.setItem(i, 1, QTableWidgetItem(value))
            self.table1.setItem(i, 2, QTableWidgetItem('复制'))
            self.table1.item(i, 2).setBackground(QColor(0, 255, 0))
            i += 1
        for value in TempRemove:
            self.table1.setItem(i, 1, QTableWidgetItem(value))
            self.table1.setItem(i, 2, QTableWidgetItem('删除'))
            self.table1.item(i, 2).setBackground(QColor(255, 0, 0))
            i += 1
        return onlyIn_Raw,onlyIn_backup

    def show3(self,onlyIn_Raw):
        ################### onlyIn_Raw ： copy ###################
        TempCopy = {}
        if len(onlyIn_Raw) > 0:
            for of in sorted(onlyIn_Raw):  # 遍历列表，复制到备份文件夹
                l = os.path.normpath(os.path.join(self.raw_root, of))
                r = os.path.normpath(os.path.join(self.backup_root, of))
                TempCopy[l] = r
            self.table1.setRowCount(len(TempCopy)+1)
            i = 0
            for key, value in TempCopy.items():
                self.table1.setItem(i, 0, QTableWidgetItem(key))
                self.table1.setItem(i, 1, QTableWidgetItem(value))
                self.table1.setItem(i, 2, QTableWidgetItem('复制'))
                self.table1.item(i, 2).setBackground(QColor(0, 255, 0))
                i += 1
    def show4(self,onlyIn_backup):
        ################### onlyIn_backup ： remove ###################
        TempRemove = []
        if len(onlyIn_backup) > 0:
            for of in sorted(onlyIn_backup):  # 遍历列表删除
                r = os.path.normpath(os.path.join(self.backup_root, of))
                TempRemove.append(r)
            self.table1.setRowCount(len(TempRemove) + 1)
            i = 0
            for value in TempRemove:
                self.table1.setItem(i, 1, QTableWidgetItem(value))
                self.table1.setItem(i, 2, QTableWidgetItem('删除'))
                self.table1.item(i, 2).setBackground(QColor(255, 0, 0))
                i += 1
class MainWindows(QMainWindow):
    def __init__(self):
        super().__init__()
        self.configFile='config.yaml'
        try:
            with open(self.configFile, 'r',encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
                f.close()
        except:
            self.config = {}
        self.status=0
        self.initUI()
        self.menu()
        self.show()

    def menu(self):
        ############## 菜单栏 ##############
        bar = self.menuBar()
        # 往菜单栏添加菜单项目
        caidan = bar.addMenu("菜单")
        self.open_menu=QMenu("打开",self)
        self.Refresh_menu()
        caidan.addMenu(self.open_menu)

        savefile1 = caidan.addAction("保存")
        savefile1.setShortcut("CTRL+S")
        savefile1.triggered.connect(lambda: self.save_file(False))

        savefile2 = caidan.addAction("另存为")
        savefile2.setShortcut("CTRL+ALT+S")
        savefile2.triggered.connect(lambda: self.save_file(True))

        readme = caidan.addAction("关于使用")
        readme.triggered.connect(lambda: QMessageBox.about(self,"关于",""))


    def initUI(self):
        self.setWindowTitle(f'备份')
        self.windows = app.primaryScreen().availableGeometry()
        self.resize(int(self.windows.width() * 0.88), int(self.windows.height() * 0.9))
        grid = QGridLayout()

        ############################ 表格 ############################
        self.table1 = QTableWidget()
        self.table1.setColumnCount(4) #列数
        self.table1.setHorizontalHeaderLabels(['源文件','备份文件','动作','结果'])
        self.table1.setColumnWidth(0, int(self.windows.width() * 0.3))#宽度
        self.table1.setColumnWidth(1, int(self.windows.width() * 0.3))
        self.table1.setColumnWidth(2, int(self.windows.width() * 0.03))
        self.table1.setColumnWidth(3, int(self.windows.width() * 0.03))
        self.table1.setRowCount(1) #设置行数
        # 创建代理对象,设置居中
        self.center=CenterAlignDelegate()
        self.table1.setItemDelegateForColumn(2, self.center)
        self.table1.setItemDelegateForColumn(3, self.center)
        grid.addWidget(self.table1, 0, 0,6,1) #6

        ############################ 入参 ############################
        self.raw_root_edit = QLineEdit(self)
        self.backup_root_edit = QLineEdit(self)
        grid.addWidget(QLabel('源目录'), 0, 1)
        grid.addWidget(QLabel('备份目录'), 1, 1)
        grid.addWidget(self.raw_root_edit, 0, 2,1,3)
        grid.addWidget(self.backup_root_edit, 1, 2, 1, 3)

        ############################ 隐藏，用于主程序和子进程之间传递 ############################
        self.txt1 = QLineEdit(self)
        self.txt2 = QLineEdit(self)
        self.txt1.hide()
        self.txt2.hide()

        ############################ 进度、按钮 ############################
        self.steps=QLabel(Stage(0))
        self.select = QPushButton('列出文件',clicked=lambda: self.thread_select())
        self.do_backup = QPushButton('动作执行',clicked=lambda: self.thread_backup())
        grid.addWidget(self.steps, 4, 1, 1, 4)
        grid.addWidget(self.select, 5, 1)
        grid.addWidget(self.do_backup, 5, 2)

        ############################ 黑名单 ############################
        self.table2=QTableWidget(self)
        self.table2.setColumnCount(2)
        self.table2.setHorizontalHeaderLabels(['文件名黑名单', '后缀黑名单'])
        self.table2.setColumnWidth(0, int(self.windows.width() * 0.085))
        self.table2.setColumnWidth(1, int(self.windows.width() * 0.085))
        self.table2.setRowCount(1)
        grid.addWidget(self.table2, 2, 1, 1, 4)

        self.table3 = QTableWidget(self)
        self.table3.setColumnCount(1)
        self.table3.setHorizontalHeaderLabels(['目录名黑名单'])
        self.table3.setColumnWidth(0, int(self.windows.width() * 0.17))
        self.table3.setRowCount(1)
        grid.addWidget(self.table3, 3, 1, 1, 4)

        ############################ 布局 ############################
        grid.setColumnStretch(0, 15)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(4, 1)

        ############################ table 编辑后添加一行 ############################
        self.table1.cellChanged.connect(lambda row,col:self.check_and_add_row(self.table1,row,col))
        self.table2.cellChanged.connect(lambda row, col: self.check_and_add_row(self.table2, row, col))
        self.table3.cellChanged.connect(lambda row, col: self.check_and_add_row(self.table3, row, col))

        mainwidget = QWidget()
        mainwidget.setLayout(grid)
        self.setCentralWidget(mainwidget)

    def Refresh_menu(self):  # 刷新 生成新的“打开”
        self.open_menu.clear()
        try:
            list_config=list(self.config.keys())
            actions = []
            for i in list_config:
                action = QAction(i, self)
                actions.append(action)
                # 连接每个 QAction 的触发信号到相应的槽函数
                action.triggered.connect(lambda checked, item=i: self.selected_config(item))
                # 使用 addActions() 一次性添加多个 QAction
            self.open_menu.addActions(actions)
        except:pass
    def selected_config(self,selected):
        self.selected = selected
        self.raw_root_edit.clear()
        self.backup_root_edit.clear()
        self.table1.clearContents()
        self.table2.clearContents()
        self.table3.clearContents()
        self.steps.setText(Stage(1))

        #填入配置
        try:
            config = self.config[selected]
            self.raw_root_edit.setText(config['raw_root'])
            self.backup_root_edit.setText(config['backup_root'])

            len1 = len(config['blacklist'])
            len2 = len(config['black_file'])
            len3 = len(config['black_suffix'])
            self.table3.setRowCount(len3+1)
            self.table2.setRowCount(max(len1,len2)+1)
            for i in range(len1):
                self.table3.setItem(i, 0, QTableWidgetItem(config['blacklist'][i]))
            for i in range(len2):
                self.table2.setItem(i, 0, QTableWidgetItem(config['black_file'][i]))
            for i in range(len3):
                self.table2.setItem(i, 1, QTableWidgetItem(config['black_suffix'][i]))
        except:
            QMessageBox.critical(self,'错误','获取配置错误！')
    def read_table(self):
        blacklist=[]
        black_file=[]
        black_suffix=[]

        for _,i in read_table_data(self.table2).items():
            black_file.append(i[0])
            black_suffix.append(i[1])
        for _, i in read_table_data(self.table3).items():
            blacklist.append(i[0])

        blacklist = list(filter(None, blacklist))
        black_file = list(filter(None, black_file))
        black_suffix = list(filter(None, black_suffix))
        return blacklist,black_file,black_suffix
    def save_file(self,add):
        if add==True:
            name,ok = QInputDialog.getText(self,'另存为','配置名:')
            if not ok:
                return
        else:
            try:
                name =self.selected
            except:
                QMessageBox.critical(self,'错误','未打开任何备份配置')
                return
        raw_root = self.raw_root_edit.text()
        backup_root = self.backup_root_edit.text()
        blacklist,black_file,black_suffix = self.read_table()

        self.config[name]={'raw_root':raw_root,'backup_root':backup_root,'blacklist':black_list,
                           'black_file':black_file,'black_suffix':black_suffix}
        with open(self.configFile,'w+',encoding='utf-8') as f:
            yaml.dump(self.config,f,allow_unicode=True)
            f.close()
        self.Refresh_menu()
    def check_and_add_row(self,table,row,column):
        row_count=table.rowCount()
        # 检查最后一行是否有内容
        last_row=table.item(row_count-1,column)
        if last_row and last_row.text().strip()!='':
            table.insertRow(row_count)
    def thread_backup(self):
        self.thread1 =thread_backup(self.table1)
        self.thread1.start()
    def thread_select(self):
        blacklist,black_file,black_suffix = self.read_table()
        self.thread2 = thread_select(self.raw_root_edit.text(),self.backup_root_edit.text(),black_file,black_suffix,blacklist,self.table1,self.steps,self.txt1,self.txt2)
        self.thread2.start()



if __name__ == '__main__':
    app = QApplication([])
    windows = MainWindows()
    app.exec()