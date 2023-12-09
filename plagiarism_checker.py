import os
import shutil
import logging
import mosspy
from abc import abstractmethod
from typing import List
from bs4 import BeautifulSoup
from tqdm import tqdm

from GitlabApi import GitlabApi
from google_sheets_reader import GoogleSheetsReader

from settings import retry_count


class PlagiarismChecker:
    def __init__(
            self,
            moss_user_id: int,
            moss_language: str,
            path_to_store_data: str,
            path_to_store_reports: str,
            task_names: List[str]
    ) -> None:
        self.moss_user_id = moss_user_id
        self.moss_language = moss_language
        self.path_to_store_data = path_to_store_data
        self.path_to_store_reports = path_to_store_reports
        self.task_names = task_names

    @abstractmethod
    def download_data(self):
        raise NotImplementedError()

    def create_report(self):
        if not os.path.exists(self.path_to_store_reports):
            os.mkdir(self.path_to_store_reports)

        for task_name in tqdm(self.task_names, desc='Creating report'):
            for retry in range(retry_count):
                try:
                    if os.path.exists(os.path.join(self.path_to_store_reports, task_name)):
                        shutil.rmtree(os.path.join(self.path_to_store_reports, task_name), ignore_errors=True)
                    os.mkdir(os.path.join(self.path_to_store_reports, task_name))
                    moss = mosspy.Moss(self.moss_user_id, self.moss_language)
                    moss.addFilesByWildcard(os.path.join(self.path_to_store_data, task_name, '*'))
                    url = moss.send()
                    logging.info(f'Url for problem {task_name} is {url}')
                    moss.saveWebPage(url, os.path.join(self.path_to_store_reports, task_name, 'main.html'))
                    mosspy.download_report(url, os.path.join(self.path_to_store_reports, task_name, 'reports'))
                    break
                except Exception as e:
                    logging.error(f"Can't generate report. Retry {retry + 1}")

    def create_google_sheets_report(self, table_url):
        result = self.parse_reports()
        for task_name in tqdm(self.task_names, desc='Creating google sheets report'):
            task_results = result[task_name]
            sheet = GoogleSheetsReader.create_and_return_worksheet(table_url, task_name, str(len(task_results) + 1),
                                                                   str(6))
            GoogleSheetsReader.create_header(
                sheet,
                [
                    'left_participant',
                    'left_percent',
                    'right_participant',
                    'right_percent',
                    'lines_matched',
                    'href',
                ]
            )

            cells_list = sheet.range('A2:F{}'.format(len(task_results) + 1))
            for i, task_result in enumerate(task_results):
                row = i * 6
                cells_list[row].value = self._get_participant_name_from_file(task_result['file_name1'])
                cells_list[row + 1].value = task_result['percent1']
                cells_list[row + 2].value = self._get_participant_name_from_file(task_result['file_name2'])
                cells_list[row + 3].value = task_result['percent2']
                cells_list[row + 4].value = task_result['lines_matched']
                cells_list[row + 5].value = task_result['href']
            sheet.update_cells(cells_list)

    def parse_reports(self):
        result = {}
        for task_name in self.task_names:
            task_result = []
            main_report_file = os.path.join(self.path_to_store_reports, task_name, 'main.html')
            with open(main_report_file) as fp:
                soup = BeautifulSoup(fp, 'html.parser')
            table = soup.find('table')
            table = str(table)
            table_lines = [line for line in table.split('\n') if line][2::]
            table_lines.pop()
            for i in range(0, len(table_lines), 3):
                href, file_name1, percent1 = self._parse_line_with_ref(table_lines[i])
                _, file_name2, percent2 = self._parse_line_with_ref(table_lines[i + 1])
                lines_matched = int(table_lines[i + 2].split('>')[1])
                task_result.append(dict(
                    href=href,
                    file_name1=file_name1,
                    percent1=percent1,
                    file_name2=file_name2,
                    percent2=percent2,
                    lines_matched=lines_matched,
                ))
            task_result.sort(key=lambda row: row['lines_matched'], reverse=True)
            result[task_name] = task_result

        return result

    @abstractmethod
    def _get_participant_name_from_file(self, file):
        raise NotImplementedError

    @staticmethod
    def _parse_line_with_ref(ref_line):
        ref_line_soup = BeautifulSoup(ref_line, 'html.parser')
        a_tag = ref_line_soup.find('a')
        href = a_tag['href']
        file_name = a_tag.text.split(' ')[0]
        percent = float(a_tag.text.split(' ')[1].replace('(', '').replace(')', '').replace('%', ''))
        return href, file_name, percent


class GitlabPlagiarismChecker(PlagiarismChecker):
    def __init__(
            self,
            task_to_files: dict[str, List[str]],
            repos_to_skip: List[str],
            gitlab_url: str,
            gitlab_group: str,
            gitlab_token: str,
            repo_prefix: str,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.task_to_files = task_to_files
        self.repos_to_skip = repos_to_skip
        self.repo_prefix = repo_prefix
        self._gitlab_api = GitlabApi(gitlab_group, gitlab_url, gitlab_token)

    def download_data(self):
        self._gitlab_api.download_all_task_files(
            self.path_to_store_data,
            self.task_to_files,
            self.repos_to_skip
        )

    def _get_participant_name_from_file(self, file):
        return file.split('#')[1].replace(self.repo_prefix, '').replace('_2022', '')

