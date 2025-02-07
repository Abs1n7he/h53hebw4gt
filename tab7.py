import os
import stat
import yaml
import shutil
import base64
import sys
import hashlib
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class Tab(QMainWindow):
    def __init__(self, config: str, configFile: str):
        super().__init__()
        self.config = config
        self.configFile = configFile
        self.current_file = ''
        self.initUI()
        self.menu()
        self.show()

    def Refresh_menu(self):  # 刷新 生成新的“打开”
        self.open_menu.clear()
        encs = list(self.config['tab7'].keys())  # 当前目录下所有enc文件
        actions = []
        for i in encs:
            action = QAction(i, self)
            actions.append(action)
            # 连接每个 QAction 的触发信号到相应的槽函数
            action.triggered.connect(lambda checked, item=i: self.selected_enc(item))
            # 使用 addActions() 一次性添加多个 QAction
        self.open_menu.addActions(actions)

    def menu(self):
        ############## 菜单栏 ##############
        bar = self.menuBar()
        # 往菜单栏添加菜单项目
        caidan = bar.addMenu("菜单")
        self.open_menu = QMenu("打开", self)
        self.Refresh_menu()
        caidan.addMenu(self.open_menu)

        savefile = caidan.addAction("保存")
        savefile.setShortcut("CTRL+S")  # 设置快捷键
        savefile.triggered.connect(lambda: self.save_file(self.current_file, False))

        savefile = caidan.addAction("修改密码")
        savefile.triggered.connect(lambda: self.save_file(self.current_file, True))

        addfile = caidan.addAction("另存为")
        addfile.triggered.connect(self.save_new_file)

    def initUI(self):
        self.setWindowTitle("文本加密与解密工具")
        self.setGeometry(200, 200, 800, 800)
        grid = QGridLayout()

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        grid.addWidget(self.label)
        # 文本编辑器
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("请输入或解密后查看文本...")
        grid.addWidget(self.text_edit)

        ############## 创建主界面窗口并设置为中心窗口 ##############
        mainwidget = QWidget()
        mainwidget.setLayout(grid)
        self.setCentralWidget(mainwidget)

    def selected_enc(self, selected_file):
        self.current_file = selected_file  ################################# 打开时，刷新文件名的全局变量
        """当用户选择文件时，弹出密码输入框并尝试解密"""
        # 弹出密码输入框
        password, ok = QInputDialog.getText(self, "输入密码", f"请输入解密密码以打开 {selected_file}：",
                                            QLineEdit.EchoMode.Password)
        if not ok:
            return

        self.key = self.password_to_key(password)  ################################# 打开时，刷新密码的全局变量
        try:
            encrypted_data = self.config['tab7'][selected_file]
            encrypted_data = base64.b64decode(encrypted_data)
            encrypted_data = self.decrypt_text(encrypted_data, self.key)
            self.text_edit.setPlainText(encrypted_data)
            self.label.setText(f'加密文件> {selected_file}')
        except:
            self.text_edit.clear()
            QMessageBox.critical(self, "错误", f"解密失败！")

    def save_file(self, file, AsNewPasswd):
        if file == '':
            return
        else:
            """保存加密后的文件"""
            text = self.text_edit.toPlainText()  # 需要加密的内容
            if AsNewPasswd:
                # 弹出密码输入框
                password, ok = QInputDialog.getText(self, "输入密码", "请输入保存的加密密码：",
                                                    QLineEdit.EchoMode.Password)
                if not ok or not password:
                    QMessageBox.warning(self, "警告", "密码不能为空！")
                    return
                self.key = self.password_to_key(password)

            try:
                encrypted_data = self.encrypt_text(text, self.key)
                encrypted_data = base64.b64encode(encrypted_data)
                self.save_config(file, encrypted_data)
                QMessageBox.information(self, "成功", "文件已成功保存！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加密失败: {str(e)}")

    def save_new_file(self):
        filename, ok = QInputDialog.getText(self, "输入文件名", "文件名:", )
        if not ok:
            return
        elif not filename:
            QMessageBox.warning(self, "警告", "文件名不能为空！")
        else:
            password, ok = QInputDialog.getText(self, "输入密码", "请输入保存的加密密码：", QLineEdit.EchoMode.Password)
        self.current_file = filename
        text = self.text_edit.toPlainText()  # 需要加密的内容

        if not ok or not password:
            QMessageBox.warning(self, "警告", "密码不能为空！")
            return
        self.key = self.password_to_key(password)

        try:
            encrypted_data = self.encrypt_text(text, self.key)
            encrypted_data = base64.b64encode(encrypted_data)
            self.save_config(filename, encrypted_data)
            QMessageBox.information(self, "成功", "文件已成功保存！")
            self.label.setText(f'加密文件> {filename}')
            self.Refresh_menu()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加密失败: {str(e)}")

  
  
    def save_config(self, key, data):
        self.config['tab7'][key] = data
        with open(self.configFile, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True)
            f.close()
