import sys

from github import Github, Auth
from github.Repository import Repository
from github import GithubObject
import pandas
import os
import requests
from dotenv import load_dotenv

class DatasetBuilder:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN")
        # Connect to GitHub api
        self.github_api = self.connect_to_github_api()
        # self.files_analyzing_limit = number_of_files
        # self.currently_analyzed_files = 0
        self.dataset_file_name = "dataset_files/dataset.csv"
        # Scrape selected repositories using GitHub api
        self.scraped_repositories = pandas.read_csv("dataset_files/repositories.csv")

    def connect_to_github_api(self):
        """
        Connect to GitHub api with github_token and auth method
        """
        if self.github_token:
            github_auth = Auth.Token(self.github_token)
            return Github(auth=github_auth)
        else:
            return Github()

    def get_repository_zip_bytes(self, repository: Repository, commit_hash: str = GithubObject.NotSet):
        """
        Get the repository from GitHub as a zip file in bytes format
        """
        latest_commit_hash = repository.get_branch(repository.default_branch).commit.sha[:7]

        response = requests.get(
            repository.get_archive_link('zipball', ref=commit_hash),
            headers={"Authorization": f"token {self.github_token}"} if self.github_token else {},
        )
        if response.status_code == 200:
            return (response.content, commit_hash)
        elif response.status_code == 404:
            if commit_hash != latest_commit_hash:
                print(f"{repository.full_name} with {commit_hash} commit hash not found. Trying latest commit.")
                return self.get_repository_zip_bytes(repository, commit_hash=latest_commit_hash)
            else:
                print(f"{repository.full_name} with latest commit hash not found. Repository might have been deleted or became private.")
                sys.exit()
        else:
            print(f"Extracting zip folder for {repository.full_name} failed: Connection might have been lost.")
            sys.exit()

    def build_dataset(self, analyzer, build_mode: str = "current"):
        """
        Gather repositories with GitHub API and create a .csv data frame.
        :param: extract_build_analyze function from flow.py
        :param: mode of building (either "update" or "current"
        :return: pandas dataframe
        """
        # Open or create dataset
        try:
            dataset = pandas.read_csv(self.dataset_file_name)
        except FileNotFoundError:
            columns = {
                "relative_path": "string",
                "file_role": "string",
                "role_note": "string",
                "domain": "string",
                "file_url": "string",
                "repository_full_name": "string",
                "repository_url": "string",
                "github_status": "string",
                "number_of_imports": "Int64",
                "number_of_external_imports": "Int64",
                "number_of_internal_imports": "Int64",
                "number_of_standard_imports": "Int64",
                "number_of_classes": "Int64",
                "number_of_functions": "Int64",
                "is_entry_point": "Int64",
                "has_wait_state": "Int64",
                "number_of_decorators": "Int64",
                "number_of_base_classes": "Int64",
                "has_model_in_path": "Int64",
                "has_view_in_path": "Int64",
                "has_test_in_path": "Int64",
                "has_util_in_path": "Int64",

                "has_migration_in_path": "Int64",
                "has_script_in_path": "Int64",
                "has_middleware_in_path": "Int64",
                "has_enum_in_path": "Int64",
                "has_config_in_path": "Int64",

                "path_depth": "Int64",
                # "pagerank_score": "float64",
                "functions_to_classes_ratio": "float64",
                "external_import_ratio": "float64",
                "code_complexity": "int64",
                "commit_hash": "string",


            }
            dataset = pandas.DataFrame(columns=list(columns.keys())).astype(columns)

        current_values = {}
        for i, row in dataset.iterrows():
            current_values[(row["relative_path"], row["repository_url"])] = {
                "file_role": row["file_role"],
                "domain": row["domain"],
                "role_note": row["role_note"],
            }

        # Loop over repositories, skip already analyzed repositories, skip local files
        for repository_data in self.scraped_repositories.to_dict("records"):

            repository = self.github_api.get_repo(repository_data["repository_full_name"])
            domain = repository_data["domain"]
            commit_hash = repository_data["commit_hash"]


            if repository.full_name != repository_data["repository_full_name"]:
                self.scraped_repositories.loc[self.scraped_repositories["repository_full_name"] == repository_data["repository_full_name"], "repository_full_name"] = repository.full_name

            if not commit_hash:
                commit_hash = repository.get_branch(repository.default_branch).commit.sha[:7]
                self.scraped_repositories.loc[self.scraped_repositories["repository_full_name"] == repository.full_name, "commit_hash"] = commit_hash

            # Skip already analyzed repositories
            if build_mode == "current":
                if ((dataset["repository_url"] == repository.url) & (dataset["commit_hash"] == commit_hash)).any():
                    print(f"{repository.url} with {commit_hash} have already been analyzed")
                    continue

            try:
                # Analyze repository
                zip_bytes, commit_hash = self.get_repository_zip_bytes(repository,commit_hash= commit_hash)
                self.scraped_repositories.loc[self.scraped_repositories["repository_full_name"] == repository.full_name, "commit_hash"] = commit_hash

                analyzed_project_graph = analyzer(zip_bytes)

                files_data = []

                for node_name, node_data in analyzed_project_graph.nodes(data=True):
                    # Only include local files in the csv
                    if node_data["type"] != "LocalFile":
                        continue

                    file_url = f"https://github.com/{repository.full_name}/blob/{commit_hash}/{node_name}"

                    row_data = extract_features(node_name, node_data, repository.url, domain, file_url, commit_hash, repository.full_name)

                    if build_mode == "update":
                        saved_data_key = current_values.get((node_name, repository.url))
                        if saved_data_key:
                            for column_name in ["file_role", "domain", "role_note"]:
                                saved_column_value = saved_data_key[column_name]
                                if saved_column_value is not None and str(saved_column_value) != "nan":
                                    row_data[column_name] = saved_column_value

                    files_data.append(row_data)

                print(f"Analyzed {repository.url}")

                if build_mode == "update":
                    dataset = dataset[dataset["repository_url"] != repository.url].reset_index(drop=True)

                # Combine loaded csv file with new dataframe
                dataset = pandas.concat([dataset, pandas.DataFrame(files_data)], ignore_index=True)

            except Exception as exception:
                print(f"Parsing {repository.full_name} failed: {exception}")

        if build_mode == "update":
            previous_dataset = pandas.read_csv(self.dataset_file_name)

            for _, old_file in previous_dataset[previous_dataset["file_role"].notna()].iterrows():
                if not ((dataset["relative_path"] == old_file["relative_path"]) & (dataset["repository_url"] == old_file["repository_url"])).any():
                    new_file = old_file.copy()
                    new_file["github_status"] = "file not available or path changed or file content changed and became useless"
                    dataset = pandas.concat([dataset, pandas.DataFrame([new_file])], ignore_index=True)

        # Save dataset as csv in case of a crash or need for data analysis with jupyter notebook
        dataset.to_csv(self.dataset_file_name, index=False)
        self.scraped_repositories.to_csv("dataset_files/repositories.csv", index=False)

        return dataset

def extract_features(node_name: str, node_data: dict, repository_url: str, domain: str, file_url: str, commit_hash: str, repository_name: str):
    return {
            "relative_path": node_name,
            "file_role": None,
            "role_note": None,
            "domain": domain,
            "repository_url": repository_url,
            "commit_hash": commit_hash,
            "file_url": file_url,
            "github_status": "available_on_github",
            "repository_full_name": repository_name,

            "number_of_imports": len(node_data["imports"]),
            "number_of_external_imports": list(node_data["imports"].values()).count("external_import"),
            "number_of_internal_imports": list(node_data["imports"].values()).count("internal_import"),
            "number_of_standard_imports": list(node_data["imports"].values()).count("standard_import"),

            "number_of_classes": len(node_data["classes"]),
            "number_of_functions": len(node_data["functions"]),
            "is_entry_point": int(node_data["is_entry_point"]),
            "has_wait_state": int(node_data["has_wait_state"]),
            "number_of_decorators": len(node_data["decorators"]),
            "number_of_base_classes": len(node_data.get("base_classes", [])),

            "has_model_in_path": int("model" in node_name.lower() or "schema" in node_name.lower()),
            "has_view_in_path": int("view" in node_name.lower() or "controller" in node_name.lower() or "route" in node_name.lower() or "api" in node_name.lower() or "endpoint" in node_name.lower() or "handler" in node_name.lower()),
            "has_test_in_path": int("test" in node_name.lower()),
            "has_util_in_path": int("util" in node_name.lower() or "helper" in node_name.lower()),

            "has_migration_in_path": int("migration" in node_name.lower()),
            "has_config_in_path": int("conf" in node_name.lower() or "setting" in node_name.lower()),
            "has_script_in_path": int("script" in node_name.lower() or "task" in node_name.lower()),
            "has_middleware_in_path": int("middleware" in node_name.lower()),
            "has_enum_in_path": int("enum" in node_name.lower() or "constant" in node_name.lower()),
            
            "path_depth": node_name.count("/"),
            # "pagerank_score": node_data["pagerank_score"],
            "functions_to_classes_ratio": len(node_data["functions"]) / len(node_data["classes"]) if len(node_data["classes"]) > 0 else 0.0,
            "external_import_ratio": list(node_data["imports"].values()).count("external_import") / len(node_data["imports"]) if len(node_data["imports"]) > 0 else 0.0,
            "code_complexity": len(node_data["decorators"]) + len(node_data.get("base_classes", [])) + (3 if node_data["has_wait_state"] else 0),
        }