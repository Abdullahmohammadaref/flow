import sys

from github import Github, Auth
from github.Repository import Repository
import pandas
import os
import requests
from dotenv import load_dotenv

class DatasetBuilder:
    def __init__(self, number_of_repositories):
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN")
        # Connect to GitHub api
        self.github_api = self.connect_to_github_api()
        self.repository_analyzing_limit = number_of_repositories
        self.currently_analyzed_repositories = 0
        self.dataset_file_name = "dataset.csv"
        # Scrape repositories using GitHub api
        self.scraped_repositories = self.github_api.search_repositories(query="language:python stars:>400")

    def connect_to_github_api(self):
        """
        Connect to GitHub api with github_token and auth method
        """
        if self.github_token:
            github_auth = Auth.Token(self.github_token)
            return Github(auth=github_auth)
        else:
            return Github()

    def get_repository_zip_bytes(self, repository: Repository):
        """
        Get the repository from GitHub as a zip file in bytes format
        """
        response = requests.get(
            repository.get_archive_link('zipball'),
            headers={"Authorization": f"token {self.github_token}"} if self.github_token else {},
        )
        if response.status_code == 200:
            return response.content
        else:
            print(f"Extracting zip folder for {repository.full_name} failed: Connection might have been lost.")
            sys.exit()

    def build_dataset(self, analyzer):
        """
        Gather repositories with GitHub API and create a .csv data frame.
        :param: extract_build_analyze function from flow.py
        :return: pandas dataframe
        """
        # Open or create dataset
        try:
            dataset = pandas.read_csv(self.dataset_file_name)
        except FileNotFoundError:
            dataset = pandas.DataFrame(
                columns=[
                    "repository_name",
                    "repository_url",
                    "number_of_imports",
                    "number_of_classes",
                    "number_of_functions",
                    "is_entry_point",
                    "has_wait_state",
                    "number_of_decorators",
                    "file_role"
                ]
            )
        # Loop over repositories, skip already analyzed repositories, skip local files
        for repository in self.scraped_repositories:
            if self.currently_analyzed_repositories >= self.repository_analyzing_limit:
                break
            if repository.url in set(dataset["repository_url"]):
                continue
            try:
                # Analyze repository
                analyzed_project_graph = analyzer(self.get_repository_zip_bytes(repository))

                files_data = []
                for node_name, node_data in analyzed_project_graph.nodes(data=True):
                    # Only include local files in the csv
                    if node_data["type"] != "LocalFile":
                        continue

                    files_data.append({
                        "repository_name": repository.full_name,
                        "repository_url": repository.url,
                        "number_of_imports": len(node_data["imports"]),
                        "number_of_classes": len(node_data["classes"]),
                        "number_of_functions": len(node_data["functions"]),
                        "is_entry_point": node_data["is_entry_point"],
                        "has_wait_state": node_data["has_wait_state"],
                        "number_of_decorators": len(node_data["decorators"]),
                        "file_role": node_data["file_role"]
                    })

                # Combine loaded csv file with new dataframe
                dataset = pandas.concat([dataset, pandas.DataFrame(files_data)], ignore_index=True)
                self.currently_analyzed_repositories += 1
                print(f"Analyzed {self.currently_analyzed_repositories} out of {self.repository_analyzing_limit}")

            except Exception as exception:
                print(f"Parsing {repository.full_name} failed: {exception}")

        # Save dataset as csv in case of a crash or need for data analysis with jupyter notebook
        dataset.to_csv(self.dataset_file_name, index=False)

        return dataset