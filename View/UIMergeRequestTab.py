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
    QMessageBox
)
from PySide6.QtCore import Qt, QSize, Signal
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.UICommitWindow import CommitWindow
from View.UIDiffsWidget import DiffsWidget
from Utils.UserSession import UserSession
from Utils.Environment import RoleID
Mr_Status = [
    "Opened",
    "Closed",
    "Merged",
    "Locked",
    "Draft",
    "Work in Progress",
    "Approved",
    "Checking",
    "Conflict",
    "Ready"
    "Pending",
    "Cannot Merge"
]


class MergeRequestTab(QWidget):
    selected_mr_changed = Signal(int)
    add_comment = Signal(str, int)
    accept_and_merge = Signal(int, str)
    q_list_space = 3

    def __init__(self):
        super().__init__()
        self.all_merge_requests = []
        self._initialize_control_variables()
        self._create_widgets()
        self._set_layouts()
        self.build_mr_filter()
        self._build_interface()
        self._apply_styles()
        self._connect_ui_signals()

    def _initialize_control_variables(self):
        """Initialize control variables."""
        self.commit_window = None
        self.change_list_open_files = []

    def _create_widgets(self):
        """Create and configure all widgets."""
        self._create_header_widgets()
        self._create_change_list_tab()
        self._create_commits_tab()
        self._create_discussion_tab()
        self._create_buttons()
        self._create_tabs()

    def _create_header_widgets(self):
        """Create header-related widgets."""
        self.header_layout = QVBoxLayout()
        self.merge_request_label = self._create_label("Merge request", "background: transparent;")
        self.merge_request_cb = self._create_combobox(40)
        self.merge_request_filter = self._create_combobox(25)

    def _create_change_list_tab(self):
        """Create Change List tab."""
        self.change_list = self._create_list_widget()
        self.change_list_tab = self._create_tab_widget("ChangeListTab")
        self._set_tab_style(self.change_list_tab)

    def _create_commits_tab(self):
        """Create Commits tab."""
        self.commits_list = self._create_list_widget()
        self.commits_tab = self._create_tab_widget("CommitsTab")
        self._set_tab_style(self.commits_tab)

    def _create_discussion_tab(self):
        """Create Discussion tab."""
        self.discussion_tab = self._create_tab_widget("DiscussionTab")
        self._set_tab_style(self.discussion_tab)
        self.discussion_layout = QVBoxLayout()
        self.comments_list = self._create_list_widget()
        self.add_comment_layout = QHBoxLayout()
        self.add_comment_text = QTextEdit()
        self.add_comment_text.setObjectName("CommentTextEdit")
        self.add_comment_btn = QPushButton("Comment")

    def _create_buttons(self):
        """Create action buttons."""
        self.accept_btn = self._create_button("Accept and Merge", QSize(150, 30))
        self.refresh_btn = self._create_button("Refresh", QSize(100, 30))
        self.buttons_layout = QHBoxLayout()

    def _create_tabs(self):
        """Create tabs."""
        self.tabs = QTabWidget()
        self.tabs.setObjectName("MergeRequestInsideTabs")
        self.tabs.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout()

    @staticmethod
    def _create_combobox(min_height: int) -> QComboBox:
        """Create a combobox with a minimum height."""
        combo_box = QComboBox()
        combo_box.setMinimumHeight(min_height)
        return combo_box

    def _create_list_widget(self) -> QListWidget:
        """Create a QListWidget with spacing."""
        list_widget = QListWidget()
        list_widget.setSpacing(self.q_list_space)
        return list_widget

    @staticmethod
    def _create_tab_widget(object_name: str) -> QWidget:
        """Create a QWidget for a tab with a given object name."""
        tab_widget = QWidget()
        tab_widget.setObjectName(object_name)
        return tab_widget

    @staticmethod
    def _set_tab_style(tab_widget: QWidget):
        """Set style for a tab."""
        tab_widget.setStyleSheet("background: transparent;"
                                 "border: 1px solid white;"
                                 "border-radius: 10px;")

    @staticmethod
    def _create_label(text: str, style: str) -> QLabel:
        """Create a QLabel with text and style."""
        label = QLabel(text)
        label.adjustSize()
        label.setStyleSheet(style)
        return label

    @staticmethod
    def _create_button(text: str, size: QSize) -> QPushButton:
        """Create a QPushButton with text and a fixed size."""
        button = QPushButton(text)
        button.setFixedSize(size)
        return button

    def _set_layouts(self):
        """Set layouts for different parts of the UI."""
        self._set_header_layout()
        self._set_change_list_tab_layout()
        self._set_commits_tab_layout()
        self._set_discussion_tab_layout()
        self._set_buttons_layout()

    def _set_header_layout(self):
        """Set layout for the header."""
        self.header_layout.addWidget(self.merge_request_filter, 0, Qt.AlignmentFlag.AlignLeft)
        self.header_layout.addWidget(self.merge_request_cb)

    def _set_change_list_tab_layout(self):
        """Set layout for Change List tab."""
        change_list_layout = QVBoxLayout()
        change_list_layout.addWidget(self.change_list)
        self.change_list_tab.setLayout(change_list_layout)

    def _set_commits_tab_layout(self):
        """Set layout for Commits tab."""
        commits_list_layout = QVBoxLayout()
        commits_list_layout.addWidget(self.commits_list)
        self.commits_tab.setLayout(commits_list_layout)

    def _set_discussion_tab_layout(self):
        """Set layout for Discussion tab."""
        self.add_comment_layout.addWidget(self.add_comment_text)
        self.add_comment_layout.addWidget(self.add_comment_btn)
        self.discussion_layout.addWidget(self.comments_list)
        self.discussion_layout.addLayout(self.add_comment_layout)
        self.discussion_tab.setLayout(self.discussion_layout)

    def _set_buttons_layout(self):
        """Set layout for action buttons."""
        self.buttons_layout.addWidget(self.accept_btn, 0, Qt.AlignmentFlag.AlignCenter)
        self.buttons_layout.addWidget(self.refresh_btn, 0, Qt.AlignmentFlag.AlignCenter)
        self.buttons_layout.setSpacing(0)

    def _build_interface(self):
        """Build the main interface layout."""
        self.tabs.addTab(self.discussion_tab, "Discussion")
        self.tabs.addTab(self.change_list_tab, "Change List")
        self.tabs.addTab(self.commits_tab, "Commits")
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

    def build_mr_filter(self):
        for status in Mr_Status:
            self.merge_request_filter.addItem(status, userData=status)

        self.merge_request_filter.addItems(Mr_Status)
        self.merge_request_filter.currentIndexChanged.connect(self.on_mr_filter_change)

    def on_mr_filter_change(self, filter_index: int):
        filter_data = self.merge_request_filter.itemData(filter_index, Qt.ItemDataRole.UserRole)
        self.apply_filter(filter_data)

    def apply_filter(self, filter_data: str):
        after_filter = []
        for mr in self.all_merge_requests:
            if mr['state'].lower() == filter_data.lower():
                after_filter.append(mr)

        self._add_merge_requests(after_filter)

    def _apply_styles(self):
        """ Combo Box """
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.merge_request_cb, colour="White")
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.merge_request_filter, colour="Brown")
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
        self.change_list.itemClicked.connect(self._on_change_file_clicked)
        self.accept_btn.clicked.connect(self._on_accept_clicked)

    def _refresh(self):
        self._on_merge_request_changed(self.merge_request_cb.currentIndex())

    def _on_merge_request_changed(self, index):
        merge_request_data = self.merge_request_cb.itemData(index, Qt.ItemDataRole.UserRole)
        error = False
        if merge_request_data is not None:
            merge_request_id = merge_request_data["iid"]
            if merge_request_id is not None:
                self.selected_mr_changed.emit(merge_request_id)
                self.check_merge_request_state(merge_request_data)
            else:
                error = True
        else:
            error = True

        if error:
            self.change_list.clear()
            self.comments_list.clear()
            self.commits_list.clear()

    def check_merge_request_state(self, merge_request_data: dict):
        user_session = UserSession()
        if user_session is None:
            return
        self.accept_btn.setVisible(merge_request_data['state'] != 'merged' and
                                   user_session.role_id == RoleID.ADMIN.value)

    def _on_accept_clicked(self):
        self.commit_window = CommitWindow("Insert merge message")
        self.commit_window.accept_clicked_signal.connect(self._on_commit_window_accept)
        self.commit_window.cancel_clicked_signal.connect(self._on_commit_window_cancel)
        self.commit_window.show()

    def _on_commit_window_accept(self, message: str):
        self.accept_and_merge.emit(self._get_merge_request_id(), message)
        self.close_commit_window()

    def _on_commit_window_cancel(self):
        self.close_commit_window()

    def close_commit_window(self):
        if self.commit_window is not None:
            self.commit_window.close()
            self.commit_window = None

    def _on_change_file_clicked(self, file: QListWidgetItem):
        data = file.data(Qt.ItemDataRole.UserRole)
        if data is not None:
            diff_widget = DiffsWidget(data['diff'], data['new_path'])
            diff_widget.show()
            diff_widget.widget_closed.connect(lambda widget: self.change_list_open_files.remove(widget))
            self.change_list_open_files.append(diff_widget)

    def add_merge_requests(self, merge_requests: list):
        self.all_merge_requests = merge_requests
        current_index = self.merge_request_filter.currentIndex()
        self.on_mr_filter_change(current_index)

    def _add_merge_requests(self, merge_requests):
        self.merge_request_cb.clear()
        for merge_request in merge_requests:
            self.merge_request_cb.addItem(
                f"Merge request: {merge_request['title']} "
                f" id: {merge_request['id']}"
                f"\n[{merge_request['source_branch']} -> {merge_request['target_branch']}]"
                f" status: {merge_request['state']}"
            )
            self.merge_request_cb.setItemData(
                self.merge_request_cb.count() - 1,
                merge_request,
                Qt.ItemDataRole.UserRole
            )

        self._on_merge_request_changed(self.merge_request_cb.currentIndex())
        if self.merge_request_cb.count() == 0:
            self.merge_request_cb.addItem("NO MERGE REQUESTS")
            self.commits_list.addItem("NO COMMITS IN THIS MERGE REQUESTS")
            self.change_list.addItem("NO CHANGES IN THIS MERGE REQUESTS")
            self.comments_list.addItem("NO DISCUSSION IN THIS MERGE REQUEST")

    def add_commits(self, commits: list):
        self.commits_list.clear()
        for commit in commits:
            commit_item = QListWidgetItem(f"[{commit['short_id']}]: {commit['message']} @{commit['created_at']}")
            commit_item.setData(Qt.ItemDataRole.UserRole, commit)
            self.commits_list.addItem(commit_item)
        if self.commits_list.count() == 0:
            self.commits_list.addItem("NO COMMITS IN THIS MERGE REQUESTS")

    def add_changes(self, changes: list):
        self.change_list.clear()
        for change in changes:
            change_item = QListWidgetItem()
            if change['renamed_file']:
                change_item.setText(f"{change['old_path']} --> {change['new_path']}")
            elif change['deleted_file']:
                change_item.setText(f"{change['new_path']} --> (Deleted)")
            else:
                change_item.setText(f"{change['new_path']}")

            change_item.setData(Qt.ItemDataRole.UserRole, change)
            self.change_list.addItem(change_item)

        if self.change_list.count() == 0:
            self.change_list.addItem("NO CHANGES IN THIS MERGE REQUESTS")

    def add_comments(self, comments: list):
        self.comments_list.clear()
        for comment in comments:
            comment_item = QListWidgetItem()
            comment_item.setText(f"{comment['body']} \n created: {comment['created_at']} "
                                 f"updated: {comment['updated_at']}")
            comment_item.setData(Qt.ItemDataRole.UserRole, comment)
            self.comments_list.addItem(comment_item)

        if self.comments_list.count() == 0:
            self.comments_list.addItem("NO DISCUSSION IN THIS MERGE REQUEST")

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
            comment = self.add_username(comment)
            self.add_comment.emit(comment, self._get_merge_request_id())
            self.add_comment_text.clear()

    def add_username(self, comment: str) -> str:
        return f"[{self.get_username()}] :: {comment}"

    def _get_merge_request_id(self):
        merge_request_data = self.merge_request_cb.currentData(Qt.ItemDataRole.UserRole)
        if merge_request_data and merge_request_data['iid']:
            return merge_request_data['iid']

    @staticmethod
    def get_username():
        user_name = UserSession()
        if user_name:
            return user_name.username

    def show_no_merge_request(self):
        return

    def set_main_branch(self, main_branch: str):
        return

    def set_all_branches(self, branches: list):
        return

    def _on_commit_clicked(self, commit_item: QListWidgetItem):
        return


""" Json data structures 

++++++++++Merge Request data+++++++++
{
  'id': 307795786,
  'iid': 3,
  'project_id': 58753861,
  'title': 'Test',
  'description': 'Test',
  'state': 'merged',
  'created_at': '2024-06-12T02:31:55.415Z',
  'updated_at': '2024-06-12T02:33:56.053Z',
  'merged_by': {
    'id': 20070318,
    'username': 'm-correa',
    'name': 'Correa Miguel',
    'state': 'active',
    'locked': False,
    'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/20070318/avatar.png',
    'web_url': 'https://gitlab.com/m-correa'
  },
  'merge_user': {
    'id': 20070318,
    'username': 'm-correa',
    'name': 'Correa Miguel',
    'state': 'active',
    'locked': False,
    'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/20070318/avatar.png',
    'web_url': 'https://gitlab.com/m-correa'
  },
  'merged_at': '2024-06-12T02:33:55.742Z',
  'closed_by': None,
  'closed_at': None,
  'target_branch': 'main',
  'source_branch': 'Vlad',
  'user_notes_count': 0,
  'upvotes': 0,
  'downvotes': 0,
  'author': {
    'id': 20132980,
    'username': 'v.afanasjevs',
    'name': 'Afanasjevs Vladlens',
    'state': 'active',
    'locked': False,
    'avatar_url': 'https://secure.gravatar.com/avatar/86b9dffd809ed331afe89d127eadf9573b973f64fb4196c86bae7c3cc4b94713?s=80&d=identicon',
    'web_url': 'https://gitlab.com/v.afanasjevs'
  },
  'assignees': [
    
  ],
  'assignee': None,
  'reviewers': [
    
  ],
  'source_project_id': 58753861,
  'target_project_id': 58753861,
  'labels': [
    
  ],
  'draft': False,
  'imported': False,
  'imported_from': 'none',
  'work_in_progress': False,
  'milestone': None,
  'merge_when_pipeline_succeeds': False,
  'merge_status': 'can_be_merged',
  'detailed_merge_status': 'not_open',
  'sha': '2d2a7c966e72105384886136675bddaac4417a34',
  'merge_commit_sha': '562ee1bdc8db9df487e6bbd16841ed3c8dfb5f22',
  'squash_commit_sha': None,
  'discussion_locked': None,
  'should_remove_source_branch': True,
  'force_remove_source_branch': True,
  'prepared_at': '2024-06-12T02:31:56.641Z',
  'reference': '!3',
  'references': {
    'short': '!3',
    'relative': '!3',
    'full': 'm-correa/testrespository!3'
  },
  'web_url': 'https://gitlab.com/m-correa/testrespository/-/merge_requests/3',
  'time_stats': {
    'time_estimate': 0,
    'total_time_spent': 0,
    'human_time_estimate': None,
    'human_total_time_spent': None
  },
  'squash': False,
  'squash_on_merge': False,
  'task_completion_status': {
    'count': 0,
    'completed_count': 0
  },
  'has_conflicts': False,
  'blocking_discussions_resolved': True,
  'approvals_before_merge': None
}
++++++++++++++++++++++++++++++++

++++++++Comment structure+++++++
  {
    'id': '3b5bfba353073433d097d9ab6e7708b4bb6d995d',
    'short_id': '3b5bfba3',
    'created_at': '2024-06-18T06:42:45.000Z',
    'parent_ids': [
      
    ],
    'title': 'Changing HelloSumanth.py',
    'message': 'Changing HelloSumanth.py\n',
    'author_name': 'm-correa',
    'author_email': 'm-correa@soleilgamestudios.com',
    'authored_date': '2024-06-18T06:42:45.000Z',
    'committer_name': 'm-correa',
    'committer_email': 'm-correa@soleilgamestudios.com',
    'committed_date': '2024-06-18T06:42:45.000Z',
    'trailers': {
      
    },
    'extended_trailers': {
      
    },
    'web_url': 'https://gitlab.com/m-correa/testrespository/-/commit/3b5bfba353073433d097d9ab6e7708b4bb6d995d'
  },
++++++++++++++++++++++++++++++++
+++++++Commit Structure+++++++++
  {
    'id': 1954722804,
    'type': None,
    'body': 'mentioned in commit 231cfcddddc23efa97ca0b0a1860d87becbc5f42',
    'attachment': None,
    'author': {
      'id': 20070318,
      'username': 'm-correa',
      'name': 'Correa Miguel',
      'state': 'active',
      'locked': False,
      'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/20070318/avatar.png',
      'web_url': 'https://gitlab.com/m-correa'
    },
    'created_at': '2024-06-18T06:43:50.584Z',
    'updated_at': '2024-06-18T06:43:50.591Z',
    'system': True,
    'noteable_id': 309046290,
    'noteable_type': 'MergeRequest',
    'project_id': 58753861,
    'resolvable': False,
    'confidential': False,
    'internal': False,
    'imported': False,
    'imported_from': 'none',
    'noteable_iid': 4,
    'commands_changes': {
      
    }
  }
++++++++++++++++++++++++++++++++
+++++++++Changes structure++++++
{
  'a_mode': '100644',
  'b_mode': '100644',
  'deleted_file': False,
  'diff': '@@ -1,4 +1,3 @@\n print("Hello World Vladen")\n print(\'Migueeeeel\')\n-print("modifing the file from the cloud")\n-print("aaaaaaaaaaaaaaaaaaaa")\n+print("Helooooooooooooo")\n',
  'generated_file': False,
  'new_file': False,
  'new_path': 'HelloVladen.py',
  'old_path': 'HelloVladen.py',
  'renamed_file': False
}
++++++++++++++++++++++++++++++++
"""
