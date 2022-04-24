from logging import setLogRecordFactory
from sqlite3 import Timestamp
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QWidget, QApplication, QLabel, \
    QTabWidget, QComboBox, QFileDialog, QMessageBox, QGroupBox
import sys
from can.io import BLFReader
import cantools
import pyqtgraph as pg
from PyQt5.QtGui import QIcon
from datetime import datetime
import time
"""
修复bug：增加对信号值是否为NamedSignalValue的判断，如是，则将str转为int
为提升大blf文件的解析速度，试图尝试更新解析算法，正在优化中，未完成
参考265行
"""
class CAN(QTabWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 200, 1500, 700)
        self.setWindowTitle('CAN报文解析')
        self.setWindowIcon(QIcon('vwlogo.png'))
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.addTab(self.tab1, 'Tab 1')
        self.addTab(self.tab2, 'Tab 2')
        self.tab1UI()
        self.tab2UI()
        self.show()

    def tab1UI(self):
        self.setTabText(0, '报文解析')
        self.grid_Select_Message = QGridLayout()
        self.grid_Message_Info = QGridLayout()
        self.grid_Signal_Info = QGridLayout()

        self.gropubox_select_message = QGroupBox('Select')
        self.groupbox_info_message = QGroupBox('Message Info')
        self.gropubox_info_signal = QGroupBox('Signal Info')

        self.le_Choice_BLF_File = QLineEdit(self)
        self.le_Choice_DBC_File = QLineEdit(self)

        self.btn_Choice_BLF_File = QPushButton('选择BLF文件', self)
        self.btn_Choice_DBC_File = QPushButton('选择DBC文件', self)
        self.btn_Read_BLF = QPushButton('解析BLF', self)
        self.btn_Read_DBC = QPushButton('解析DBC', self)
        """Message名称选择下拉框"""
        self.lb_Message = QLabel('Message', self)
        self.combobox_Message = QComboBox()

        """Message ID显示"""
        self.lb_Message_ID = QLabel('Message ID (int)', self)
        self.lb_Message_ID_hex = QLabel('Message ID (hex)', self)
        self.le_Message_ID = QLineEdit(self)
        self.le_Message_ID_hex = QLineEdit(self)

        """Message字节长度"""
        self.lb_Message_Length = QLabel('报文长度 (Bytes)', self)
        self.le_Message_Length = QLineEdit(self)

        """Signal名称选择下拉框"""
        self.lb_Signal = QLabel('Signal', self)
        self.combobox_Signal = QComboBox()

        """Signal编码格式"""
        self.lb_Signal_CodeType = QLabel('编码格式', self)
        self.le_Signal_CodeType = QLineEdit(self)

        """Signal起始位/长度/放大系数/偏移/单位/"""
        self.lb_Signal_Start_bit = QLabel('起始位', self)
        self.le_Signal_Start_bit = QLineEdit(self)

        self.lb_Signal_Length = QLabel('长度', self)
        self.le_Signal_Length = QLineEdit(self)

        self.lb_Signal_Scale = QLabel('放大系数', self)
        self.le_Signal_Scale = QLineEdit(self)

        self.lb_Signal_Offset = QLabel('偏移', self)
        self.le_Signal_Offset = QLineEdit(self)

        self.lb_Signal_Minimum = QLabel('最小值', self)
        self.le_Signal_Minimum = QLineEdit(self)
        self.lb_Signal_Maximum = QLabel('最大值', self)
        self.le_Signal_Maximum = QLineEdit(self)

        self.lb_Signal_Unit = QLabel('单位')
        self.le_Signal_Unit = QLineEdit(self)
        self.txt_Signal_Comment = QTextEdit(self)

        """布局:选择Message和Signal的下拉框"""
        self.grid_Select_Message.addWidget(self.lb_Message, 1, 1)
        self.grid_Select_Message.addWidget(self.combobox_Message, 1, 2, 1, 3)
        # self.combobox_Message.setMinimumWidth()
        self.grid_Select_Message.addWidget(self.lb_Signal, 2, 1)
        self.grid_Select_Message.addWidget(self.combobox_Signal, 2, 2, 1, 3)

        """布局:显示Message的Information"""
        self.grid_Message_Info.addWidget(self.lb_Message_ID, 1, 1)
        self.grid_Message_Info.addWidget(self.le_Message_ID, 1, 2)
        self.grid_Message_Info.addWidget(self.lb_Message_ID_hex, 1, 3)
        self.grid_Message_Info.addWidget(self.le_Message_ID_hex, 1, 4)
        self.grid_Message_Info.addWidget(self.lb_Message_Length, 2, 1)
        self.grid_Message_Info.addWidget(self.le_Message_Length, 2, 2)

        """布局:显示Signal的information"""
        self.grid_Signal_Info.addWidget(self.lb_Signal_CodeType, 1, 1)
        self.grid_Signal_Info.addWidget(self.le_Signal_CodeType, 1, 2)
        self.grid_Signal_Info.addWidget(self.lb_Signal_Unit, 1, 3)
        self.grid_Signal_Info.addWidget(self.le_Signal_Unit, 1, 4)
        self.grid_Signal_Info.addWidget(self.lb_Signal_Start_bit, 2, 1)
        self.grid_Signal_Info.addWidget(self.le_Signal_Start_bit, 2, 2)
        self.grid_Signal_Info.addWidget(self.lb_Signal_Length, 2, 3)
        self.grid_Signal_Info.addWidget(self.le_Signal_Length, 2, 4)
        self.grid_Signal_Info.addWidget(self.lb_Signal_Scale, 3, 1)
        self.grid_Signal_Info.addWidget(self.le_Signal_Scale, 3, 2)
        self.grid_Signal_Info.addWidget(self.lb_Signal_Offset, 3, 3)
        self.grid_Signal_Info.addWidget(self.le_Signal_Offset, 3, 4)
        self.grid_Signal_Info.addWidget(self.lb_Signal_Minimum, 4, 1)
        self.grid_Signal_Info.addWidget(self.le_Signal_Minimum, 4, 2)
        self.grid_Signal_Info.addWidget(self.lb_Signal_Maximum, 4, 3)
        self.grid_Signal_Info.addWidget(self.le_Signal_Maximum, 4, 4)
        self.grid_Signal_Info.addWidget(self.txt_Signal_Comment, 5, 1, 2, 4)

        """将三个Grid布局放入三个GroupBox中"""
        self.gropubox_select_message.setLayout(self.grid_Select_Message)
        self.groupbox_info_message.setLayout(self.grid_Message_Info)
        self.gropubox_info_signal.setLayout(self.grid_Signal_Info)

        self.vbox_1 = QVBoxLayout()
        self.vbox_1.addWidget(self.gropubox_select_message)
        self.vbox_1.addWidget(self.groupbox_info_message)
        self.vbox_1.addWidget(self.gropubox_info_signal)

        """实例化绘图窗口"""
        self.pw1 = pg.PlotWidget()  # 实例化一个pyqtgraph图形插件
        self.pw1.setBackground('w')
        self.pw1.setAntialiasing(True)
        self.vbox_2 = QVBoxLayout()
        self.vbox_2.addWidget(self.pw1)

        """主界面布局"""
        self.grid_main = QGridLayout()
        self.grid_main.addWidget(self.le_Choice_DBC_File, 1, 1, 1, 10)
        self.grid_main.addWidget(self.btn_Choice_DBC_File, 1, 11)
        self.grid_main.addWidget(self.btn_Read_DBC, 1, 12)
        self.grid_main.addWidget(self.le_Choice_BLF_File, 2, 1, 1, 10)
        self.grid_main.addWidget(self.btn_Choice_BLF_File, 2, 11)
        self.grid_main.addWidget(self.btn_Read_BLF, 2, 12)

        # self.grid_main.addWidget(self.gropubox_select_message,3,1,2,2)
        # self.grid_main.addWidget(self.groupbox_info_message,5,1,2,2)
        # self.grid_main.addWidget(self.gropubox_info_signal,7,1,6,2)
        self.grid_main.addLayout(self.vbox_1, 3, 1, 11, 2)
        self.grid_main.addLayout(self.vbox_2, 3, 3, 11, 10)
        # self.grid_main.addWidget(self.pw1,3,3,11,10)

        self.tab1.setLayout(self.grid_main)

        self.btn_Choice_DBC_File.clicked.connect(self.file_choice_dbc)
        self.btn_Choice_BLF_File.clicked.connect(self.file_choice_blf)
        self.btn_Read_DBC.clicked.connect(self.read_dbc)
        self.btn_Read_BLF.clicked.connect(self.read_blf)

        self.combobox_Message.currentIndexChanged.connect(self.refresh_message)
        self.combobox_Signal.currentIndexChanged.connect(self.refresh_signal)

    def tab2UI(self):
        self.setTabText(1, '报文导出')
        grid_tab2 = QGridLayout()
        btn_save_signal = QPushButton('导出信号')

        #grid_tab2.addWidget(self.combobox_Message,1,1)
        #grid_tab2.addWidget(self.combobox_Signal,2,1)

        grid_tab2.addWidget(btn_save_signal,3,1)

        self.tab2.setLayout(grid_tab2)

    def file_choice_dbc(self):
        self.combobox_Signal.clear()
        self.combobox_Message.clear()
        self.le_Message_ID.clear()
        self.le_Message_ID_hex.clear()
        self.le_Message_Length.clear()
        self.le_Signal_CodeType.clear()
        self.le_Signal_Length.clear()
        self.le_Signal_Maximum.clear()
        self.le_Signal_Minimum.clear()
        self.le_Signal_Offset.clear()
        self.le_Signal_Scale.clear()
        self.le_Signal_Start_bit.clear()
        self.le_Signal_Unit.clear()
        self.txt_Signal_Comment.clear()
        file = QFileDialog.getOpenFileName(None, '请选择dbc文件：', './', ('DBC文件 (*.dbc)'))
        if file[0]:  # 如果用户点击取消，则返回主程序继续运行
            self.dbc_file_path = file[0]  # 提取文件的绝对路径
            self.le_Choice_DBC_File.setText(self.dbc_file_path)

    def file_choice_blf(self):
        file = QFileDialog.getOpenFileName(None, '请选择blf文件：', './', ('BLF文件 (*.blf)'))
        if file[0]:
            self.blf_file_path = file[0]
            self.le_Choice_BLF_File.setText(self.blf_file_path)

    def read_dbc(self):
        if self.le_Choice_DBC_File.text() == '':
            QMessageBox.warning(self, '警告', '请先选择dbc文件！')
        else:
            self.db = cantools.db.load_file(self.dbc_file_path)
            dbc_messages_list = []
            for msg in self.db.messages:
                dbc_message = msg.name
                dbc_messages_list.append(dbc_message)

            self.combobox_Message.addItems(dbc_messages_list)  # 括号内添加一个list
            self.combobox_Message.setCurrentIndex(0)

            self.selected_message_name = self.combobox_Message.currentText()
            self.selected_message = self.db.get_message_by_name(self.selected_message_name)
            signal_list = self.selected_message.signal_tree  # 选择的Message的Signals列表
            self.combobox_Signal.addItems(signal_list)
            self.combobox_Signal.setCurrentIndex(0)

            selected_message_id = self.selected_message.frame_id
            selected_message_length = self.selected_message.length
            self.le_Message_ID.setText(str(selected_message_id))
            self.le_Message_ID_hex.setText(str(hex(selected_message_id)))
            self.le_Message_Length.setText(str(selected_message_length))

            selected_signal = self.selected_message.get_signal_by_name(self.combobox_Signal.currentText())
            selected_signal_codetype = selected_signal.byte_order  # 编码格式，'little_endian'=Intel
            selected_signal_start = selected_signal.start
            selected_signal_length = selected_signal.length
            selected_signal_scale = selected_signal.scale
            selected_signal_offset = selected_signal.offset
            selected_signal_minimum = selected_signal.minimum
            selected_signal_maximum = selected_signal.maximum
            selected_signal_unit = selected_signal.unit
            selected_signal_Comment = selected_signal.comment

            self.le_Signal_CodeType.setText(selected_signal_codetype)
            self.le_Signal_Start_bit.setText(str(selected_signal_start))
            self.le_Signal_Length.setText(str(selected_signal_length))
            self.le_Signal_Scale.setText(str(selected_signal_scale))
            self.le_Signal_Offset.setText(str(selected_signal_offset))
            self.le_Signal_Minimum.setText(str(selected_signal_minimum))
            self.le_Signal_Maximum.setText(str(selected_signal_maximum))
            self.le_Signal_Unit.setText(selected_signal_unit)
            self.txt_Signal_Comment.setText(selected_signal_Comment)

    def read_blf(self):
        if self.le_Message_ID.text() == '' or self.le_Message_Length.text() == '' or self.le_Signal_Start_bit.text() == '' or self.le_Signal_Length.text() == '' or self.le_Signal_Scale.text() == '' or self.le_Signal_Offset.text() == '':
            QMessageBox.warning(self, '警告', '请先选择dbc并解析信号！')
        elif self.le_Choice_BLF_File.text() == '':
            QMessageBox.warning(self, '警告', '请选择blf文件！')
        else:
            heute=time.time()
            log = BLFReader(self.blf_file_path)
            #log = list(log)                             #此步骤非常占用内存，需要优化！
            message_id = int(self.le_Message_ID.text())  # 获取Message ID
            """
            研究这里★★★★★
            selected_message不能使用列表生成器，因为生成器被调用一次后就清空了，但是语句中需要被调用两次，所以第二次的返回值会是空
            """
            selected_message = [msg for msg in log if msg.arbitration_id == message_id]  # 使用列表生成器生成选择的信号列表，减少内存占用，提升速度
            selected_signal = [self.db.decode_message(message_id, msg2.data)[self.combobox_Signal.currentText()] for
                               msg2 in selected_message]
            timestamp = [msg.timestamp for msg in selected_message]
            #timeline = [datetime.fromtimestamp(msg.timestamp) for msg in selected_message]
            time_duration = (i - timestamp[0] for i in timestamp)
            # dict_data={msg.timestamp:self.db.decode_message(message_id, msg.data)[self.combobox_Signal.currentText()] for msg in selected_message}
            if isinstance(selected_signal[0],cantools.database.can.signal.NamedSignalValue):  #判断信号是否是NamedSignalValue,如果是，就要转换成对应的int值
                selected_signal=[i.value for i in selected_signal]
            self.pw1.clear()
            curve_1 = self.pw1.plot(list(time_duration), list(selected_signal), name='时域信号')
            curve_1.setPen('r', width=2)
            self.pw1.setLabel('left', 'Amptitude')
            self.pw1.setLabel('bottom', 'Time', units='s')  # 使用units会a
            self.pw1.showGrid(x=True, y=True)
            self.pw1.addLegend()
            QMessageBox.information(self, '完成', '解析完成，耗时{:.2f}秒！'.format(time.time()-heute))

    def refresh_message(self):
        try:
            self.selected_message = self.db.get_message_by_name(self.combobox_Message.currentText())
            selected_message_id = self.selected_message.frame_id
            selected_message_length = self.selected_message.length
            self.le_Message_ID.setText(str(selected_message_id))
            self.le_Message_Length.setText(str(selected_message_length))

            new_signal_list = self.selected_message.signal_tree  # 选择的Message的Signals列表
            self.combobox_Signal.clear()
            self.combobox_Signal.addItems(new_signal_list)
            # self.combobox_Signal.setCurrentIndex(0)
        except:
            pass

    def refresh_signal(self):
        try:
            new_selected_signal = self.selected_message.get_signal_by_name(self.combobox_Signal.currentText())
            selected_signal_codetype = new_selected_signal.byte_order  # 编码格式，'little_endian'=Intel
            selected_signal_start = new_selected_signal.start
            selected_signal_length = new_selected_signal.length
            selected_signal_scale = new_selected_signal.scale
            selected_signal_offset = new_selected_signal.offset
            selected_signal_minimum = new_selected_signal.minimum
            selected_signal_maximum = new_selected_signal.maximum
            selected_signal_unit = new_selected_signal.unit
            selected_signal_comment = new_selected_signal.comment
            self.le_Signal_CodeType.setText(selected_signal_codetype)
            self.le_Signal_Start_bit.setText(str(selected_signal_start))
            self.le_Signal_Length.setText(str(selected_signal_length))
            self.le_Signal_Scale.setText(str(selected_signal_scale))
            self.le_Signal_Offset.setText(str(selected_signal_offset))
            self.le_Signal_Minimum.setText(str(selected_signal_minimum))
            self.le_Signal_Maximum.setText(str(selected_signal_maximum))
            self.le_Signal_Unit.setText(selected_signal_unit)
            self.txt_Signal_Comment.setText(selected_signal_comment)
        except:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = CAN()
    app.exit(app.exec_())
