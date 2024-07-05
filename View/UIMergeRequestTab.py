from PySide6.QtWidgets import (
    QComboBox,
    QTabWidget,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
    QMessageBox
)
from PySide6.QtGui import QTextDocument
from PySide6.QtCore import Qt, QSize, Signal
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.UICommitWindow import CommitWindow


class MergeRequestTab(QWidget):
    selected_mr_changed = Signal(int)
    add_comment = Signal(str, int)
    accept_and_merge = Signal(int, str)

    def __init__(self):
        super().__init__()
        """ Combo Box """
        self.header_layout = QVBoxLayout()
        self.merge_request_label = QLabel("Merge request")
        self.merge_request_label.adjustSize()
        self.merge_request_label.setStyleSheet("background: transparent;")
        self.merge_request_cb = QComboBox()
        self.merge_request_cb.setMinimumHeight(40)
        """ Change List Tab """
        self.change_list = QListWidget()
        self.change_list_tab = QWidget()
        self.change_list_tab.setObjectName("ChangeListTab")
        self.change_list_tab.setStyleSheet("background: transparent;"
                                           "border: 1px solid white;"
                                           "border-radius: 10px;")
        """ Commits Tab """
        self.commits_list = QListWidget()
        self.commits_tab = QWidget()
        self.commits_tab.setObjectName("CommitsTab")
        self.commits_tab.setStyleSheet("background: transparent;"
                                       "border: 1px solid white;"
                                       "border-radius: 10px;")
        """ Discussion Tab """
        self.discussion_tab = QWidget()
        self.discussion_tab.setObjectName("DiscussionTab")
        self.discussion_tab.setStyleSheet("background: transparent;"
                                          "border: 1px solid white;"
                                          "border-radius: 10px;")
        self.discussion_layout = QVBoxLayout()
        self.comments_list = QListWidget()
        self.add_comment_layout = QHBoxLayout()
        self.add_comment_text = QTextEdit()
        self.add_comment_text.setObjectName("CommentTextEdit")
        self.add_comment_btn = QPushButton("Comment")
        """Buttons"""
        self.accept_btn = QPushButton("Accept and Merge")
        self.refresh_btn = QPushButton("Refresh")
        self.buttons_layout = QHBoxLayout()
        """ Other Widgets """
        self.tabs = QTabWidget()
        self.tabs.setObjectName("MergeRequestInsideTabs")
        self.tabs.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout()
        """ End Constructor """
        self._build()
        self._apply_styles()
        self._connect_ui_signals()

    def _build(self):
        """Header"""
        self.header_layout.addWidget(self.merge_request_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.header_layout.addWidget(self.merge_request_cb)
        """ Change list tab """
        change_list_layout = QVBoxLayout()
        change_list_layout.addWidget(self.change_list)
        self.change_list_tab.setLayout(change_list_layout)
        """ Commits Tab """
        commits_list_layout = QVBoxLayout()
        commits_list_layout.addWidget(self.commits_list)
        self.commits_tab.setLayout(commits_list_layout)
        """ Discussion Tab """
        self.add_comment_layout.addWidget(self.add_comment_text)
        self.add_comment_layout.addWidget(self.add_comment_btn)
        self.discussion_layout.addWidget(self.comments_list)
        self.discussion_layout.addLayout(self.add_comment_layout)
        self.discussion_tab.setLayout(self.discussion_layout)
        """ Buttons """
        self.buttons_layout.addWidget(self.accept_btn)
        self.buttons_layout.addWidget(self.refresh_btn)
        """ Tabs """
        self.tabs.addTab(self.discussion_tab, "Discussion")
        self.tabs.addTab(self.change_list_tab, "Change List")
        self.tabs.addTab(self.commits_tab, "Commits")
        """ Main Layout """
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

    def _apply_styles(self):
        """ Combo Box """
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.merge_request_cb, colour="White")
        """ Buttons """
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.accept_btn, colour="Blue")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.refresh_btn, colour="White")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.add_comment_btn, colour="Yellow")
        """ List Widget """
        CustomStyleSheetApplier.set_qlist_widget_style_and_colour(self.comments_list, colour="White")
        CustomStyleSheetApplier.set_qlist_widget_style_and_colour(self.change_list, colour="White")
        CustomStyleSheetApplier.set_qlist_widget_style_and_colour(self.commits_list, colour="White")
        CustomStyleSheetApplier.set_q_text_edit_style_and_colour(self.add_comment_text, colour="White")

    def _connect_ui_signals(self):
        self.add_comment_btn.clicked.connect(self.upload_comment)
        self.refresh_btn.clicked.connect(self._refresh)
        self.merge_request_cb.currentIndexChanged.connect(self._on_merge_request_changed)
        self.commits_list.currentItemChanged.connect(self._on_commit_clicked)
        self.accept_btn.clicked.connect(self._on_accept_clicked)

    def _refresh(self):
        self._on_merge_request_changed(self.merge_request_cb.currentIndex())

    def _on_merge_request_changed(self, index):
        merge_request_id = self.merge_request_cb.itemData(index, Qt.ItemDataRole.UserRole)
        if merge_request_id is not None:
            self.selected_mr_changed.emit(merge_request_id)

    def _on_accept_clicked(self):
        self.commit_window = CommitWindow("Insert merge message")
        self.commit_window.accept_clicked_signal.connect(
            lambda commit_message: self.accept_and_merge.emit(self._get_merge_request_id(), commit_message))
        self.commit_window.cancel_clicked_signal.connect(self._on_commit_window_accept)
        self.commit_window.show()

    def _on_commit_window_accept(self):
        return

    def _on_commit_window_cancel(self):
        if self.commit_window:
            self.commit_window.close()
            self.commit_window = None

    def _on_commit_clicked(self, commit_item: QListWidgetItem):
        return

    def _on_change_file_clicked(self, file):
        return

    def set_main_branch(self, main_branch: str):
        return

    def set_all_branches(self, branches: list):
        return

    def add_merge_requests(self, merge_requests: list):
        self.merge_request_cb.clear()
        for merge_request in merge_requests:
            self.merge_request_cb.addItem(
                f"Merge request: {merge_request['title']} "
                f"\n[{merge_request['source_branch']} -> {merge_request['target_branch']}]"
                f" status: {merge_request['state']}"
            )
            self.merge_request_cb.setItemData(
                self.merge_request_cb.count() - 1,
                merge_request['iid'],
                Qt.ItemDataRole.UserRole
            )

        self._on_merge_request_changed(self.merge_request_cb.currentIndex())

    def add_commits(self, commits: list):
        self.commits_list.clear()
        for commit in commits:
            commit_item = QListWidgetItem(f"[{commit['short_id']}]: {commit['message']} @{commit['created_at']}")
            commit_item.setData(Qt.ItemDataRole.UserRole, commit['id'])
            self.commits_list.addItem(commit_item)

    def add_changes(self, changes: list):
        self.change_list.clear()
        for change in changes:
            if change['renamed_file']:
                change_item = QListWidgetItem(f"{change['old_path']} --> {change['new_path']}")
            else:
                change_item = QListWidgetItem(f"{change['new_path']}")
            change_item.setData(Qt.ItemDataRole.UserRole, change['new_path'])
            change_item.setToolTip(change['diff'])
            self.change_list.addItem(change_item)

    def add_comments(self, comments: list):
        self.comments_list.clear()
        for comment in comments:
            comment_item = QListWidgetItem()
            comment_item.setText(f"{comment['body']} \n created: {comment['created_at']} updated: {comment['updated_at']}")
            comment_item.setData(Qt.ItemDataRole.UserRole, comment['id'])
            self.comments_list.addItem(comment_item)

    def upload_comment(self):
        comment = self.add_comment_text.toPlainText()
        """ TODO: ADD USER INSIDE THE COMMENT { [USER]: COMMENT } """
        if comment == "":
            self.add_comment_text.setPlaceholderText("Insert some comment")
            return

        reply = QMessageBox.question(
            self,
            "Add Comment",
            "Are you sure to add comment?",
            QMessageBox.Yes | QMessageBox.No,  #answer options
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.add_comment.emit(comment, self._get_merge_request_id())
            self.add_comment_text.clear()

    def _get_merge_request_id(self):
        merge_id = self.merge_request_cb.currentData(Qt.ItemDataRole.UserRole)
        return merge_id

    def show_no_merge_request(self):
        return
