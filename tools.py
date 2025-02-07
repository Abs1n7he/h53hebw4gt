

class TabWidgetDemo(QWidget):
    def __init__(self):
        super().__init__()
        #################### 获取配置文件 ####################
        self.configFile = 'config.yaml'
        with open(self.configFile, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            f.close()
        #print(self.config)
        self.initUI()


   

