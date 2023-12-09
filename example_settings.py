# moss settings

moss_user_id = 1234
moss_language = 'cc'

# Checker settings
path_to_store_data = 'downloaded_tasks'
path_to_store_reports = 'reports'

# Gitlab settings
gitlab_token = 'token'  # Access token for gitlab api
gitlab_url = 'https://gitlab.akhcheck.ru'
gitlab_group = 'cpp_course_2022'
repos_to_exclude = ['testing_repo', ]
task_to_files = {
    # 'deque_pt1_cpp_yaishenka': ['deque.hpp', ],
    'list_cpp_yaishenka': ['list.hpp', ],
    'deque_pt2_cpp_yaishenka': ['deque.hpp', ],
    'smart_pointers_cpp_yaishenka': ['smart_pointers.hpp', ],
}

# Google sheets settings
account_credentials_file = 'acc2.json'

retry_count = 3
