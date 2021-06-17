from PyQt5 import QtWidgets
from project import *
import sys
import sqlite3
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate

###### 함수들 ######
class FnClass(Ui_Dialog):

    # 학생 등록시 신규인지 수정인지 체크하는 전역변수 0이면 신규, 1이면 수정
    studentNew = 0

    # 이벤트나 load 초기화
    def init(self):
        # 두번째 탭에서 반 콤보박스 리스트 가져오기
        self.init_cboClass()

        # 이벤트 걸기
        self.btnSearch.clicked.connect(self.fn_search)
        self.tableWidget_2.clicked.connect(self.fn_cellclicked)
        self.btnSaveStudent.clicked.connect(self.fn_saveStudent)
        self.btnNewStudent.clicked.connect(self.fn_newStudent)
        self.btnDelStudent.clicked.connect(self.fn_delStudent)
        self.cboClass.currentTextChanged.connect(self.fn_searchStudent)
        self.btnMoveClass.clicked.connect(self.fn_moveClass)

        #숨김처리
        self.studentIdHidden.setVisible(False)
        self.classIdHidden.setVisible(False)

    # 두번째 탭에서 반 콤보박스 리스트 가져오기 
    def init_cboClass(self):
        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        cur.execute("SELECT class_name from CLASS")
        data = cur.fetchall()

        for i, v in enumerate(data):
            self.cboClass.addItem(data[i][0])
            self.cboClass_2.addItem(data[i][0])

        self.fn_searchStudent()


    # 첫번째 '조회' 탭 조회 함수
    def fn_search(self):
        class_name = self.inputSearchClass.text()
        student_name = self.inputSearchName.text()
        dateFr = self.dateFr.text()
        dateTo = self.dateTo.text()
        print(class_name, student_name, dateFr, dateTo)
        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        cur.execute("SELECT count(*) from INFO i join STUDENT s on i.STUDENT_ID = s.STUDENT_ID join CLASS c on s.CLASS_ID = c.CLASS_ID WHERE c.CLASS_NAME LIKE ? AND s.STUDENT_NAME LIKE ? AND (i.PAY_DAY >= ? AND i.PAY_DAY <= ?)", (['%'+class_name+'%', '%'+student_name+'%', dateFr, dateTo]))
        rowCnt = (cur.fetchall())[0][0]
        print(rowCnt)
        # 조회해서 나온 row개수를 테이블의 row개수로 설정
        self.tableWidget.setRowCount(rowCnt)

        cur.execute("SELECT c.CLASS_NAME, s.STUDENT_NAME, i.LECTURE_FEE, i.BOOK_FEE, i.HOW_FEE, i.CASH_YN, i.PAY_DAY from INFO i join STUDENT s on i.STUDENT_ID = s.STUDENT_ID join CLASS c on s.CLASS_ID = c.CLASS_ID WHERE c.CLASS_NAME LIKE ? AND s.STUDENT_NAME LIKE ? AND (i.PAY_DAY >= ? AND i.PAY_DAY <= ?)", (['%'+class_name+'%', '%'+student_name+'%', dateFr, dateTo]))
        data = cur.fetchall()
        print(data)

        for idx,tuples in enumerate(data):
            for i, val in enumerate(tuples):
                self.tableWidget.setItem(idx,i,QTableWidgetItem(val))

    # 두번째 '학생 개인정보' 탭, 조회함수
    def fn_searchStudent(self):
        #cbobox text
        cboText = self.cboClass.currentText()

        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        cur.execute("SELECT s.STUDENT_ID, s.STUDENT_NAME from CLASS c JOIN STUDENT s ON c.CLASS_ID = s.CLASS_ID WHERE CLASS_NAME = ?", (cboText,))
        data = cur.fetchall()
        print("data", data)

        cur.execute("SELECT count(*) from CLASS c JOIN STUDENT s ON c.CLASS_ID = s.CLASS_ID WHERE CLASS_NAME = ?", (cboText,))
        rowCnt = (cur.fetchall())[0][0]
        print("rowCnt=",rowCnt)

        self.tableWidget_2.setRowCount(rowCnt)

        self.tableWidget_2.setColumnHidden(0, True)

        for idx, tuples in enumerate(data):
            for i, val in enumerate(tuples):
                if(type(val) == int):
                    val = str(val)
                self.tableWidget_2.setItem(idx,i,QTableWidgetItem(val))
    
    # 두번째 '학생 개인정보' 탭, 좌측 테이블 셀 클릭시 이벤트
    def fn_cellclicked(self):
        self.studentNew = 1
        studentId = self.tableWidget_2.item(self.tableWidget_2.currentRow(), 0).text()
        studentName = self.tableWidget_2.currentItem().text()
        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM STUDENT s JOIN CLASS c ON s.CLASS_ID=c.CLASS_ID where STUDENT_ID = ?", (studentId,))
        data = cur.fetchall()
        print(data)

        self.studentIdHidden.setText(studentId)
        self.classIdHidden.setText(str(data[0][6]))
        self.lineEdit_2.setText(data[0][7])
        self.lineEdit_3.setText(data[0][1])
        self.lineEdit_4.setText(data[0][3])
        self.textEdit.setText(data[0][5])

        reg_date = data[0][4]
        year = int(reg_date[0:4])
        month = int(reg_date[5:7])
        day = int(reg_date[9:])

        self.dateEdit.setDate(QDate(year, month, day))

        self.lineEdit_2.setDisabled(True)
        self.lineEdit_3.setDisabled(True)
        

    # 두번째 '학생 개인정보' 탭, 저장 버튼 클릭 이벤트
    def fn_saveStudent(self):
        studentId= self.studentIdHidden.text()
        className = self.lineEdit_2.text()
        studentName = self.lineEdit_3.text()
        tel = self.lineEdit_4.text()
        regDate = self.dateEdit.text()
        etc = self.textEdit.toPlainText()

        if(className == '' or studentName == '' or tel ==''):
            self.alert_warnig("빈칸없이 입력해주세요.")
        else:
            conn = sqlite3.connect("project.db")
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM CLASS WHERE CLASS_NAME = ?", (className,))
            isExistClass = cur.fetchone()[0]
            cur.execute("SELECT CLASS_ID FROM CLASS WHERE CLASS_NAME = ?", (className,))
            classId = cur.fetchone()[0]
            if(isExistClass == 0):
                self.alert_warnig("존재하지않는 반입니다.")
                self.lineEdit_2.setFocus()
            else:
                # 신규 등록시
                if(self.studentNew == 0):
                    conn = sqlite3.connect("project.db")
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) from STUDENT s join CLASS c on s.CLASS_ID = c.CLASS_ID where STUDENT_NAME = ? AND CLASS_NAME = ?", ([studentName, className]))
                    isExistStudent = cur.fetchone()[0]
                    if(isExistStudent == 1):
                        self.alert_warnig("동명이인의 학생이 존재합니다.")
                        self.lineEdit_3.setFocus()
                    else:
                        conn = sqlite3.connect("project.db")
                        cur = conn.cursor()
                        cur.execute("INSERT INTO STUDENT(CLASS_ID, STUDENT_NAME, TEL, REG_DATE, ETC) VALUES (?,?,?,?,?)", ([classId, studentName, tel, regDate, etc]))
                        conn.commit()
                        self.alert_warnig("저장되었습니다!")
                        self.fn_searchStudent()
                # 수정 시
                else:
                    conn = sqlite3.connect("project.db")
                    cur = conn.cursor()
                    cur.execute("UPDATE STUDENT SET TEL = ?, REG_DATE = ?, ETC = ? WHERE STUDENT_ID = ?",([tel, regDate, etc, studentId]))
                    conn.commit()
                    self.alert_warnig("수정되었습니다!")
                    self.fn_searchStudent()

            print(isExistClass)
            
        print(regDate)
        

    # 두번째 '학생 개인정보' 탭, 신규 버튼 클릭 이벤트
    def fn_newStudent(self):
        self.studentNew = 0
        self.lineEdit_2.setText(self.cboClass.currentText())
        self.lineEdit_2.setDisabled(True)
        self.lineEdit_3.setText("")
        self.lineEdit_3.setDisabled(False)
        self.lineEdit_4.setText("")
        self.dateEdit.setDate(QDate.currentDate())
        self.textEdit.setText("")

    # 두번째 '학생 개인정보' 탭, 삭제 버튼 클릭 이벤트
    def fn_delStudent(self):
        try:
            studentId= self.studentIdHidden.text()
            studentName = self.tableWidget_2.currentItem().text()
            retval = self.alert_question(studentName+' 학생정보를 삭제하시겠습니까?')
            print(retval)
            # 삭제 조건
            if(retval == 16384):
                conn = sqlite3.connect("project.db")
                cur = conn.cursor()
                cur.execute("DELETE FROM STUDENT WHERE STUDENT_ID = ?", (studentId,))
                conn.commit()
                self.fn_searchStudent()
            else:
                return
        except:
            self.alert_warnig('삭제하실 학생을 선택해주세요.')
    
    def fn_moveClass(self):
        studentId = self.studentIdHidden.text()
        studentName= self.lineEdit_3.text()
        cboText = self.cboClass_2.currentText()
        conn = sqlite3.connect("project.db")
        cur = conn.cursor()
        cur.execute("SELECT CLASS_ID FROM CLASS WHERE CLASS_NAME = ?", (cboText,))
        classId = cur.fetchone()[0]
        print(classId)
        if(studentId == ''):
            self.alert_warnig("학생을 선택해주세요.")
        else:
            retval = self.alert_question(studentName+"을(를) "+cboText+"반으로 이동하시겠습니까?")
            if(retval == 16384):
                conn = sqlite3.connect("project.db")
                cur = conn.cursor()
                cur.execute("UPDATE STUDENT SET CLASS_ID = ? WHERE STUDENT_ID = ?", ([classId, studentId]))
                conn.commit()
                self.fn_searchStudent()
            else:
                return
        

    # Warning msg BOX
    def alert_warnig(self, msg):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.msg.setWindowTitle("!")
        self.msg.setText(msg)
        self.msg.setStandardButtons(QMessageBox.Ok)
        retval = self.msg.exec_()
    
    # Question msg Box
    def alert_question(self, msg):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Question)
        self.msg.setWindowTitle("?")
        self.msg.setText(msg)
        self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = self.msg.exec_()
        return retval


##############   Main   ##################
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    fn = FnClass()
    fn.setupUi(MainWindow)
    fn.init()
    MainWindow.show()
    sys.exit(app.exec_())