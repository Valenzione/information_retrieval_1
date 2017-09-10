import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIntValidator

import search_engine as se
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit,
                             QGridLayout, QApplication, QTreeView, QPushButton, QAbstractItemView,
                             QTextEdit, QHeaderView)


def wrap_string(string, words_in_row=10):
    wrapped_string = ""
    i = 0
    for word in string.split(" "):
        i += 1
        wrapped_string = wrapped_string + " " + word
        if i == words_in_row:
            wrapped_string += '\n'
            i = 0
    return wrapped_string


class SearchEngineInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = se.SearchEngine()
        self.initUI()

    def searchClicked(self):
        sender = self.sender()

        self.tree_view.model().clear()
        self.tree_view.model().setHorizontalHeaderLabels(['File', 'Title', 'Date', 'Author', 'Total Amount'])

        query_text = self.query_edit.text()


        #If no value was entered, or value is incorrect, change it to default
        try:
            number_of_results=int(self.results_num.text())
            if number_of_results<=0:
                self.results_num.setText("10")
                number_of_results=10
        except ValueError:
            number_of_results=10

        #Test whether query is logical or not
        if " AND " in query_text or "NOT " in query_text or " OR " in query_text:
            search_results,number_of_entries = self.engine.search_boolean(query_text,number_of_results)
        else:
            search_results,number_of_entries = self.engine.search_simple(query_text, number_of_results)

        if len(search_results) == 0:
            self.tree_view.model().appendRow(QStandardItem("No records found"))
        else:
            self.results_found.setText(str(number_of_entries)+" found. "+str(min(number_of_results,number_of_entries))+" displayed.")

        for result in search_results:
            file_id = QStandardItem(result["File"])
            title = QStandardItem(result["Title"])
            date = QStandardItem(result["Date"])
            author = QStandardItem(result["Prgm Manager"])
            abstract = QStandardItem(wrap_string(result['Abstract']))
            file_id.appendRow([QStandardItem(""), abstract])
            money_amount = QStandardItem(result["Total Amt"])
            self.tree_view.model().appendRow([file_id, title, date, author, money_amount])

    def initUI(self):
        query = QLabel('Enter query:')
        num_results = QLabel('Enter number of results:')

        results = QLabel('Results')
        self.results_found = QLabel('')

        self.query_edit = QLineEdit()
        self.results_num = QLineEdit()
        self.results_num.setValidator(QIntValidator(0, 100))

        self.tree_view = QTreeView()
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['File', 'Title', 'Date', 'Author', 'Total Amount'])
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree_view.setModel(model)

        searchButton = QPushButton(text="Search")
        searchButton.clicked.connect(self.searchClicked)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(query, 1, 0)
        grid.addWidget(self.query_edit, 1, 1)

        grid.addWidget(num_results, 2, 0)
        grid.addWidget(self.results_num, 2, 1)

        grid.addWidget(searchButton, 1, 3)

        grid.addWidget(results, 3, 0)
        grid.addWidget(self.results_found,4,0)
        grid.addWidget(self.tree_view, 3, 1, 10, 2)

        self.setLayout(grid)
        self.setGeometry(600, 600, 350, 300)
        self.setWindowTitle('Abstract Search')
        self.showMaximized()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SearchEngineInterface()
    sys.exit(app.exec_())
