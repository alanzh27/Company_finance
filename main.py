from PyQt5.QtWidgets import *
import requests


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.company_name = None

        self.infoWin = None
        self.inspectionChoices = None
        self.API_key = '4L943FWONU5HB0IU'
        self.label3 = QLabel('')

        self.dictB = None
        self.dictI = None
        self.dictC = None

        self.welcomeScreen()
        self.show()

    def welcomeScreen(self):
        self.setGeometry(450, 100, 1000, 800)
        self.setWindowTitle('Financials Calculator Welcome Screen')

        layout1 = QVBoxLayout()

        label = QLabel("Welcome! Please enter the ticker of the company you would like to inspect.")

        response_box = QLineEdit()
        response_box.setPlaceholderText('Enter your company ticker here')

        submit_btn = QPushButton('Submit')
        submit_btn.clicked.connect(lambda: self.set_company(response_box.text()))
        #submit_btn.clicked.connect(self.informationWindow)

        labelor = QLabel("OR")
        labelAPI = QLabel("Enter your own API Key (for Alpha Vantage).")

        response_box2 = QLineEdit()
        response_box2.setPlaceholderText('Enter your API key here')

        submit_btn2 = QPushButton('Submit')
        submit_btn2.clicked.connect(lambda: self.set_apiKey(response_box2.text()))

        layout1.addWidget(label)
        layout1.addWidget(response_box)
        layout1.addWidget(submit_btn)
        '''
        layout1.addWidget(labelor)
        layout1.addWidget(labelAPI)
        layout1.addWidget(response_box2)
        layout1.addWidget(submit_btn2)
        '''

        self.setLayout(layout1)

    def set_company(self, comp):
        self.company_name = comp.upper()

        urlB = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={self.company_name}&apikey={self.API_key}'
        self.dictB = requests.get(urlB).json()

        try:
            NA = self.dictB['annualReports'][0]['totalCurrentAssets']
        except Exception as e:
            if(len(self.dictB) == 0):
                self.tickerErrorMessage()
            else:
                self.apiErrorMessage()
        else:
            self.dictB = self.zero(self.dictB)

            urlI = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.company_name}&apikey={self.API_key}'
            self.dictI = requests.get(urlI).json()
            self.dictI = self.zero(self.dictI)

            urlC = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={self.company_name}&apikey={self.API_key}'
            self.dictC = requests.get(urlC).json()
            self.dictC = self.zero(self.dictC)

            self.informationWindow()


    def set_apiKey(self, key):
        self.API_key = key

        msg = QMessageBox()
        msg.setText("API Updated")
        msg.setInformativeText('Your API key is now in use. Please make sure the entered API key is a valid one.')
        msg.setWindowTitle("Message")
        msg.exec_()


    def informationWindow(self):
        self.hide()

        self.infoWin = QMainWindow()
        self.infoWin.setGeometry(450, 100, 1000, 800)
        self.infoWin.setWindowTitle('Financials Calculator')

        layout2 = QVBoxLayout()

        label2 = QLabel(f'Selected Company: {self.company_name}')

        self.inspectionChoices = QComboBox()
        self.inspectionChoices.addItem('Balance Sheet')
        self.inspectionChoices.addItem('Income Statement')
        self.inspectionChoices.addItem('Cash Flow')

        self.label3 = QLabel('')

        submit_btn = QPushButton('Submit')
        submit_btn.clicked.connect(self.onSubmit)



        back_btn = QPushButton('Back')
        back_btn.clicked.connect(self.changeWindow)

        layout2.addWidget(label2)
        layout2.addWidget(self.inspectionChoices)
        layout2.addWidget(submit_btn)
        layout2.addWidget(self.label3)
        layout2.addWidget(back_btn)

        central_widget = QWidget()
        self.infoWin.setCentralWidget(central_widget)
        central_widget.setLayout(layout2)

        self.infoWin.show()

    def changeWindow(self):
        self.show()
        self.infoWin.hide()
        self.infoWin = None

    def onSubmit(self):
        choice = self.inspectionChoices.currentText()
        result = self.infoChose(choice, self.dictB, self.dictI, self.dictC)
        str = "\n".join([f"{key}: {value}" for key, value in result.items()])

        self.label3.setText(str)

    def zero(self, dictionary):
        for report in dictionary['annualReports']:
            for key, value in report.items():
                if value == 'None' or value is None:
                    report[key] = 0
        return dictionary


    def infoChose(self, choice, dictB, dictI, dictC):

        if choice == 'Balance Sheet':
            info = {
                "Current Ratio": int(dictB['annualReports'][0]['totalCurrentAssets'])/int(
                    dictB['annualReports'][0]['totalCurrentLiabilities']),
                "Quick Ratio": (int(dictB['annualReports'][0]['totalCurrentAssets']) - int(
                    dictB['annualReports'][0]['inventory']))/int(dictB['annualReports'][0]['totalCurrentLiabilities']),
                "Debt-to-Equity Ratio": int(dictB['annualReports'][0]['totalLiabilities'])/int(
                    dictB['annualReports'][0]['totalShareholderEquity']),
                "Debt Ratio" : int(dictB['annualReports'][0]['totalLiabilities'])/int(
                    dictB['annualReports'][0]['totalAssets'])
            }
            return info
        elif choice == 'Income Statement':
            info = {
                "Gross Profit Margin": (int(dictI['annualReports'][0]['grossProfit'])/int(
                    dictI['annualReports'][0]['totalRevenue'])) * 100,
                "Operating Margin": (int(dictI['annualReports'][0]['operatingIncome'])/int(
                    dictI['annualReports'][0]['totalRevenue'])) * 100,
                "Net Profit Margin": (int(dictI['annualReports'][0]['netIncome'])/int(
                    dictI['annualReports'][0]['totalRevenue'])) * 100,
                "Return on Assets (ROA)" : (int(dictI['annualReports'][0]['netIncome'])/int(
                    dictB['annualReports'][0]['totalAssets'])) * 100,
                "Return on Equity (ROE)": (int(dictI['annualReports'][0]['netIncome']) / int(
                    dictB['annualReports'][0]['totalShareholderEquity'])) * 100
            }
            return info
        else:
            info = {
                "Operating Cash Flow Ratio": int(dictC['annualReports'][0]['operatingCashflow']) / int(
                    dictB['annualReports'][0]['totalCurrentLiabilities']),
                "Free Cash Flow": int(dictC['annualReports'][0]['operatingCashflow']) -
                                  int(dictC['annualReports'][0]['capitalExpenditures']),
                "Cash Flow to Debt Ratio": int(dictI['annualReports'][0]['costofGoodsAndServicesSold']) / int(
                    dictB['annualReports'][0]['shortLongTermDebtTotal'])
            }
            return info

    def apiErrorMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("API Limit")
        msg.setInformativeText('This program utilizes the Alpha Vantage API. '
                               'Unfortunately, the API Key has run out of requests for the day. '
                               'Please enter your own or another API key to continue using this program.')
        msg.setWindowTitle("Error")
        msg.exec_()

    def tickerErrorMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Invalid Company Ticker")
        msg.setInformativeText('The ticker you have entered is invalid. Please make sure that you have submitted '
                               'a valid ticker')
        msg.setWindowTitle("Error")
        msg.exec_()



if __name__ == '__main__':
    app = QApplication([])
    ex = MainWindow()
    app.exec_()
