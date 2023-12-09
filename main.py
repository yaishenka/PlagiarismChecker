from plagiarism_checker import GitlabPlagiarismChecker
import sys
import settings


sys.setrecursionlimit(1000000)

checker = GitlabPlagiarismChecker(
    settings.task_to_files,
    settings.repos_to_exclude,
    settings.gitlab_url,
    settings.gitlab_group,
    settings.gitlab_token,
    'cpp_course22_',
    moss_user_id=settings.moss_user_id,
    moss_language=settings.moss_language,
    path_to_store_data=settings.path_to_store_data,
    path_to_store_reports=settings.path_to_store_reports,
    task_names=settings.task_to_files.keys(),
)

checker.download_data()
checker.create_report()
checker.create_google_sheets_report('https://docs.google.com/spreadsheets/d/1oKbaxYTApsOSPtsjRqxkjhbIWuuV7eVemsJFJ3M4sss/edit#gid=0')