import sys
import json
import os
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *

STORAGE_DIR = "browyer_data"
TABS_FILE = os.path.join(STORAGE_DIR, "tabs.json")

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.profile = QWebEngineProfile("MyProfile", self)
        self.profile.setPersistentStoragePath(os.path.abspath(STORAGE_DIR))
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QTabWidget::pane { border: 0; background-color: #1e1e1e; }
            QTabBar::tab {
                background: #2d2d2d; color: #b1b1b1;
                padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px;
                margin-right: 2px; font-family: 'Segoe UI', sans-serif;
            }
            QTabBar::tab:selected { background: #3d3d3d; color: white; border-bottom: 2px solid #0078d4; }
            QToolBar { background: #252526; border: none; padding: 5px; spacing: 10px; }
            QLineEdit { 
                background: #3c3c3c; color: white; border-radius: 15px; 
                padding: 5px 15px; border: 1px solid #555; font-size: 14px;
            }
            QPushButton { background: transparent; color: white; font-size: 18px; padding: 5px; }
            QPushButton:hover { background: #444; border-radius: 5px; }
        """)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        navbar = QToolBar()
        self.addToolBar(navbar)

        for text, func in [("←", self.go_back), ("→", self.go_forward), ("↻", self.reload)]:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            navbar.addWidget(btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        new_tab_btn = QPushButton("+")
        new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        navbar.addWidget(new_tab_btn)

        self.load_session()

        self.setWindowTitle("browyer")
        self.resize(1200, 800)

    def add_new_tab(self, qurl=None, label="google"):
        if qurl is None:
            qurl = QUrl("https://google.com")

        browser = QWebEngineView()
        # Use the persistent profile
        page = QWebEnginePage(self.profile, browser)
        browser.setPage(page)
        browser.setUrl(qurl)
        
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda q: self.update_url(q, browser))
        browser.loadFinished.connect(lambda: self.tabs.setTabText(self.tabs.indexOf(browser), browser.page().title()[:15]))
        
        browser.urlChanged.connect(self.save_session)

    def go_back(self): self.tabs.currentWidget().back()
    def go_forward(self): self.tabs.currentWidget().forward()
    def reload(self): self.tabs.currentWidget().reload()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if "." not in url: url = f"https://google.com={url}"
        elif not url.startswith("http"): url = "http://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self, q, browser):
        if browser == self.tabs.currentWidget():
            self.url_bar.setText(q.toString())

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
            self.save_session()

    def save_session(self):
        urls = [self.tabs.widget(i).url().toString() for i in range(self.tabs.count())]
        with open(TABS_FILE, "w") as f:
            json.dump(urls, f)

    def load_session(self):
        if os.path.exists(TABS_FILE):
            with open(TABS_FILE, "r") as f:
                urls = json.load(f)
                for url in urls:
                    self.add_new_tab(QUrl(url))
        if self.tabs.count() == 0:
            self.add_new_tab()

app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec())
