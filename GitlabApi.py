import gitlab
import logging
import os
from tqdm import tqdm
import shutil


class GitlabApi:
    def __init__(self, gitlab_group, gitlab_url, token, main_branch_name='master'):
        self.gitlab_group = gitlab_group
        self.gitlab_url = gitlab_url
        self.token = token
        self.main_branch_name = main_branch_name
        self._gitlab_api = gitlab.Gitlab(gitlab_url, token)
        self._gitlab_api_splitted = gitlab_url.split('https://')[1]
        self._logger = logging.getLogger('gitlab_api')

    def download_all_task_files(self, path_to_store, tasks_to_files: dir, names_to_skip=()):
        if not os.path.exists(path_to_store):
            os.mkdir(path_to_store)

        for task in tqdm(tasks_to_files.keys(), desc='Tasks loop'):
            if os.path.exists(os.path.join(path_to_store, task)):
                shutil.rmtree(path_to_store, ignore_errors=True)
            os.mkdir(os.path.join(path_to_store, task))

            projects = self._get_projects()
            for project in tqdm(projects, desc='Projects loop'):
                if project.name in names_to_skip:
                    continue
                self._get_task_files(project, task, tasks_to_files[task],
                                     os.path.join(path_to_store, task))

    def _get_task_files(self, project, branch_name, branch_files, path_to_store):
        project = self._gitlab_api.projects.get(project.id)
        files_content = b''
        for file in branch_files:
            try:
                gl_file = project.files.get(file_path=os.path.join(branch_name, file), ref=branch_name)
                files_content += gl_file.decode()
                files_content += b'\n'
                continue
            except Exception as e:
                self._logger.error(
                    f"Can't get file {os.path.join(branch_name, file)} from branch {branch_name}. Error: {e}.Try master_branch")

            try:
                gl_file = project.files.get(file_path=os.path.join(branch_name, file), ref=self.main_branch_name)
                files_content += gl_file.decode()
                files_content += b'\n'
                continue
            except Exception as e:
                self._logger.error(
                    f"Can't get file {os.path.join(branch_name, file)} in project {project.name}. Error: {e}")
                continue
        with open(os.path.join(path_to_store, f'{branch_name}#{project.name}'), 'wb') as f:
            f.write(files_content)

    def _get_projects(self):
        gitlab_group = self._get_group(self.gitlab_group)
        if gitlab_group is None:
            self._logger.error('Gitlab group is None. Abort')
            return []

        projects = gitlab_group.projects.list(all=True)

        return projects

    def _get_url_to_clone_with_token(self, project):
        project_url = project.http_url_to_repo.split(self.gitlab_url)[1]
        return f'https://oauth2:{self.token}@{self._gitlab_api_splitted}/{project_url}'

    def _get_group(self, group):
        try:
            group = self._gitlab_api.groups.get(group)
        except:
            self._logger.error(f"Can't get gitlab group {group}")
            group = None
        return group

    def _get_project(self, gitlab_group, project_name):
        projects = list(filter(lambda project: project.name == project_name,
                               gitlab_group.projects.list(search=project_name)))

        if len(projects) > 0:
            return self._gitlab_api.projects.get(projects[0].id)

        return None
