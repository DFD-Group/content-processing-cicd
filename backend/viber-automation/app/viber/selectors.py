"""UI Automation selectors used by the Viber client."""


search_container_id_pattern = (
    r"\.ApplicationWindowContentControl"
    r"\.SearchItem_QMLTYPE_\d+(?:_QML_\d+)?$"
)

split_view_id_pattern = (
    r"^QGuiApplication"
    r"\.MainWindow_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.ApplicationWindowContentControl"
    r"\.SplitView_QMLTYPE_\d+(?:_QML_\d+)?$"
)

chat_pane_id_pattern = (
    r"^QGuiApplication"
    r"\.MainWindow_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.ApplicationWindowContentControl"
    r"\.SplitView_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.StackView_QMLTYPE_\d+(?:_QML_\d+)?$"
)

search_input_id_pattern = (
    r"\.TextFieldItem_QMLTYPE_\d+(?:_QML_\d+)?$"
)

message_input_id_pattern = (
    r"\.QQuickTextEdit_QML_\d+$"
)

info_button_id_pattern = (
    r"\.InfoButton_QMLTYPE_\d+(?:_QML_\d+)?$"
)

info_sidebar_id_pattern = (
    r"\.SideBarContent_QMLTYPE_\d+(?:_QML_\d+)?$"
)

edit_group_name_button_id_pattern = (
    r"\.SideBarContent_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.IconButton_QMLTYPE_\d+(?:_QML_\d+)?$"
)

group_name_input_id_pattern = (
    r"\.SideBarContent_QMLTYPE_\d+(?:_QML_\d+)?"
    r"\.TextFieldItem_QMLTYPE_\d+(?:_QML_\d+)?$"
)

chat_message_id_pattern = (
    r"\.FeedDelegate_QMLTYPE_\d+(?:_QML_\d+)?$"
)

main_content_id_suffix = (
    ".ApplicationWindowContentControl"
)

search_result_automation_id = "delegateLoader"