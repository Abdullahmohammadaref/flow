# Flow - (Backend)

## Overview

This is the Main project housing core project analysis and file role prediction logic.

## Requirements
- Python 3.13.13
## Structure

### Files:

**Core Files:**
- `flow.py`: Core file for executing all functionalities including: 
  - Building a dataset.
  - Training model.
  - Analyzing projects.
- `code_analyzer.py`: Uses ast library to parse python files and extract code features
- `graph_builder.py`: Transform a dictionary of parsed code features into a directed graph with nodes and edges using the networkx library.
- `graph_analyzer.py`: Extract further features from the directed graph of the code including: 
  - entry points node
  - runtime import execution order of edges
  - dependency order form the entry point of edges
  - circular dependencies
  - node pagerank score
- `dataset_builder.py`: Scrape selected repositories with GitHub api, call relevant functions to analyze them, then builds a dataset with these features or adds new rows to the existing dataset.
- `model_trainer.py`: The Machine learning pipeline for training model and storing it in .plk file.
- `file_role_predictor.py`: Loads the model inside the .pkl file to predict file roles of a selected project.

**Generated Files:**

- `dataset_files/dataset.csv`: The dataset that `dataset_builder.py` generates (file is already provided roles,domain,notes are labeled manually for convenience).
- `dataset_files/stratified_and_balanced_dataset.csv`: Dataset That is stratified and balanced then fed to Model pipeline.
- `ml_models/random_forest_classifier.pkl`: Random Forest Classifier model
- `ml_models/logistic_regression_classifier.pkl`: Logistic Regression Classifier model
- `ml_models/lightGBM_classifier.pkl`: LightGBM Classifier model
- `plots/LightGBM (Gradient Boosting)_confusion_matrix.png`: Confusion matrix plot for LightGBM Classifier model
- `plots/Logistic_Regression_confusion_matrix.png`: Confusion matrix plot for Logistic Regression Classifier model
- `plots/random_forest_classifier_confusion_matrix.png`: Confusion matrix plot for Random Forest Classifier model
- `plots/Logistic_Regression_feature_importances.png`: Feature Importance plot for Logistic Regression Classifier model
- `plots/random_forest_classifier_feature_importances.png`: Feature Importance plot for Random Forest Classifier model

**Other files/directories:**
- `dataset_files/repositories.csv`: Contains a list of repositories and their domain. This will be used to build dataset or add rows to an existing one.

    | Column Name            | Data Type | Description |
    |:-----------------------| :--- |:-------|
    | `repository_full_name` | string | The full name of the repository in `owner/repository` format |
    | `domain`               | string | The domain from which this repository comes from (optional) | 
    | `commit_hash`          | string | The Commit hash from which the repository came from (optional, latest commit is addes automatically) |


- `/sample_projects`: Directory containing Sample projects to use for analysis.
    
### Dataset

**Columns**

Note: Each represents a python file with its features 

| Column Name                    | Data Type | Description                                                                                                                                                                                                                     |
|:-------------------------------| :--- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `relative_path`                | string | The relative path of the file from the root directory of the repository                                                                                                                                                         |
| `file_role`                    | string | The target value that represents the role of the file (This column is labeled manually for each row).                                                                                                                           |
| `role_note`                    | string | A column for writing personal notes if needed during the manual process of labeling the `file_role` column.                                                                                                                     |
| `file_domain`                  | string | The domain from which this repository came from (e.g., e-commerce store, python library, framework, etc) (This column is labeled manually for each repository).                                                                 |
| `repository_url`               | string | The absolute repository URL from where this file row was extracted from.                                                                                                                                                        |
| `number_of_imports`            | Int64 | Total Number of all type of imports.                                                                                                                                                                                            |
| `number_of_external_imports`   | Int64 | Total Number of imports from external libraries.                                                                                                                                                                                |
| `number_of_internal_imports`   | Int64 | Total Number of imports from internal project libraries.                                                                                                                                                                        |
| `number_of_standard_imports`   | Int64 | Total Number of imports from python standard libraries.                                                                                                                                                                         |
| `number_of_classes`            | Int64 | Total Number of defined classes.                                                                                                                                                                                                |
| `number_of_functions`          | Int64 | Total Number of defined functions (Excluding async functions and class methods).                                                                                                                                                |
| `is_entry_point`               | Int64 | If `graph_analyzer.GraphAnalyzer.detect_entry_points` have labeled the node of this file as an entry point or not.                                                                                                              |
| `has_wait_state`               | Int64 | If `code_analyzer.CodeAnalyzer.visit_Call` have detected a wait state inside this file or not.                                                                                                                                  |
| `number_of_decorators`         | Int64 | Total Number of decorators.                                                                                                                                                                                                     |
| `number_of_base_classes`       | Int64 | Total Number of base classes.                                                                                                                                                                                                   |
| `has_model_in_path`            | Int64 | If `relative_path` string have the keyword `model` or `schema` inside it.                                                                                                                                                       |
| `has_view_in_path`             | Int64 | If `relative_path` string have the keyword `view`, `controller`, `route` inside it.                                                                                                                                             |
| `has_test_in_path`             | Int64 | If `relative_path` string have the keyword `test` inside it.                                                                                                                                                                    |
| `has_util_in_path`             | Int64 | If `relative_path` string have the keyword `util`, or `helper` inside it.                                                                                                                                                       |
| `has_migration_in_path`        | Int64 | If `relative_path` string have the keyword `migration` inside it.                                                                                                                                                               |
| `has_script_in_path`           | Int64 | If `relative_path` string have the keyword `script` or `task` inside it.                                                                                                                                                        |
| `has_middleware_in_path`       | Int64 | If `relative_path` string have the keyword `middleware` inside it.                                                                                                                                                              |
| `has_enum_in_path`             | Int64 | If `relative_path` string have the keyword `enum` inside it.                                                                                                                                                                    |
| `has_config_in_path`           | Int64 | If `relative_path` string have the keyword `conf`or `setting` inside it.                                                                                                                                                        |
| `has_route_in_path`            | Int64 | If `relative_path` string have the keyword `route` inside it.                                                                                                                                                                   |
| `has_url_in_path`              | Int64 | If `relative_path` string have the keyword `url` inside it.                                                                                                                                                                     |
| `has_command_in_path`          | Int64 | If `relative_path` string have the keyword `command`, `cmd`, or `cli` inside it.                                                                                                                                                |
| `has_interceptor_in_path`      | Int64 | If `relative_path` string have the keyword `interceptor` inside it.                                                                                                                                                             |
| `has_type_in_path`             | Int64 | If `relative_path` string have the keyword `type` inside it.                                                                                                                                                                    |
| `has_controller_in_path`       | Int64 | If `relative_path` string have the keyword `controller` inside it.                                                                                                                                                              |
| `has_core_in_path`             | Int64 | If `relative_path` string have the keyword `core` inside it.                                                                                                                                                                    |
| `has_ml_in_path`               | Int64 | If `relative_path` string have the keyword `predict, `/ml/`, or `train` inside it.                                                                                                                                              |
| `path_depth`                   | Int64 | How deep this is this file in the directory tree relative to the repository project root directory.                                                                                                                             |
| `functions_to_classes_ratio`   | float64 | The ratio of `number_of_functions / number_of_classes`(a derived feature)                                                                                                                                                       |
| `external_import_ratio`        | float64 | The ratio of `number_of_external_imports / number_of_imports`(a derived feature)                                                                                                                                                |
| `code_complexity`              | Int64 | A score for assessing code complexity (a derived feature). <br/> Calculated by adding all points in this point system:<br/> <ul> <li> `number_of_decorators` * 1<li>`number_of_base_classes` * 1 <li>`has_wait_state` * 3 <ul/> |
| `has_setting_in_name`          | Int64 | If file name string have the keyword `setting` inside it.                                                                                                                                                                       |
| `has_conf_in_name`             | Int64 | If file name string have the keyword `conf` inside it.                                                                                                                                                                          |
| `has_main_in_name`             | Int64 | If file name string have the keyword `main` inside or file name is `__main__`.                                                                                                                                                  |
| `has_type_in_name`             | Int64 | If file name string have the keyword `type` inside it.                                                                                                                                                                          |
| `has_route_in_name`            | Int64 | If file name string have the keyword `route` inside it.                                                                                                                                                                         |
| `has_url_in_name`              | Int64 | If file name string have the keyword `url` inside it.                                                                                                                                                                           |
| `has_view_in_name`             | Int64 | If file name string have the keyword `view` inside it.                                                                                                                                                                          |
| `has_util_in_name`             | Int64 | If file name string have the keyword `util` or `helper` inside it.                                                                                                                                                              |
| `has_migration_prefix_in_name` | Int64 | If file name string starts with 4 numbers and the first two are zero                                                                                                                                                            |
| `imports_testing_library`      | Int64 | If file imports any of the following testing libraries: `pytest`, `unittest`, `mock`, `fixture`, `testcase`                                                                                                                     |
| `imports_db_orm`               | Int64 | If file imports any of the following Database or Object relational modeling libraries: `models`, `sqlalchemy`, `peewee`, `tortoise`, `mongoengine`                                                                              |
| `imports_enum_lib`             | Int64 | If file imports the `enum` Library.                                                                                                                                                                                             |
| `imports_cli_lib`              | Int64 | If file imports any of the following command line interface libraries: `click`, `typer`, `rgparse`, `optparse`, `fire`                                                                                                          |
| `imports_http_framework`       | Int64 | If file imports any of the following http libraries: `fastapi`, `flask`, `django`, `starlette`, `aiohttp`, `tornado`                                                                                                            |
| `imports_migration_lib`        | Int64 | If file imports a library that have the word `migration` inside it                                                                                                                                                              |
| `imports_ml_lib`               | Int64 | If file imports any of the following machine learning libraries: `sklearn`, `tensorflow`, `torch`, `keras`, `xgboost`, `lightgbm`                                                                                               |
| `imports_config_lib`           | Int64 | If file imports any of the configurations libraries: `pydantic`, `dataclasses`, `environ`, `dotenv`, `configparser`, `dynaconf`                                                                                                 |
| `inherits_model_class`         | Int64 | If file contains a base class whose name have the word `model` inside its string.                                                                                                                                               |
| `inherits_view_class`          | Int64 | If file contains a base class whose name have any of these words inside its string: `view`, `viewset`, `apiview`, `genericview`.                                                                                                |
| `inherits_serializer_class`    | Int64 | If file contains a base class whose name have the word `serializer` inside its string.                                                                                                                                          |
| `inherits_enum_class`          | Int64 | If file contains a base class whose name have any of these words inside its string: `enum`, `intenum`, `strenum`, `flag`.                                                                                                       |
| `inherits_migration_class`     | Int64 | If file contains a base class whose name have the word `migration` inside its string.                                                                                                                                           |
| `inherits_test_class`          | Int64 | If file contains a base class whose name have any of these words inside its string: `testcase`, `testmixin`.                                                                                                                    |
| `inherits_middleware_class`    | Int64 | If file contains a base class whose name have the word `middleware` inside its string.                                                                                                                                          |
| `inherits_exception_class`     | Int64 | If file contains a base class whose name have any of these words inside its string: `exception`, `error`.                                                                                                                       |
| `has_cli_decorator`            | Int64 | If file contains a decorator whose name have any of these command-line-interface keywords inside its string: `command`, `group`, `option`, `argument`                                                                           |
| `has_route_decorator`          | Int64 | If file contains a decorator whose name have any of these route keywords inside its string: `route`, `get`, `post`, `put`, `delete`, `patch`                                                                                    |
| `has_test_decorator`           | Int64 | If file contains a decorator whose name have any of these route keywords inside its string: `pytest`, `mark`, `fixture`, `parametrize`                                                                                          |
| `has_dataclass_decorator`      | Int64 | If file contains a decorator whose name have the keyword `dataclass`                                                                                                                                                            |
| `has_test_prefix_in_names`     | Int64 | If a file have a function that starts with `test_`                                                                                                                                                                              |
| `has_http_method_in_names`     | Int64 | If a file have a function that have any of these keywords in its string: `get`, `post`, `put`, `delete`, `patch`                                                                                                                |
| `has_setup_teardown_in_names`  | Int64 | If a file have a funtion that have any of these keywords in its string: `setup`, `teardown`, `setupclass`                                                                                                                       |
| `ratio_test_functions`         | float64 | The ratio of tests functions to all functions inside the file                                                                                                                                                                   |
| `has_migrate_func_in_names`    | Int64 | If a file have one of the following migration keyword in one of its functions: `migrations`, `runsql`, `runpython`                                                                                                              |
| `import_count`                 | Int64 | How many times this file was used by other files                                                                                                                                                                                |


**Target Value Classes (File Roles)**

- `test`: Files that are used for testing.
- `model`: Files that define the schema model of a database.
- `script`: Standalone script files.
- `utility`: Files that contain utility functions that are used by multiple other files inside the project.
- `config`: Files that contains global settings and configurations for the whole project or specific parts of it.
- `view`: Files that contain controllers which a router routes to.
- `router`: File that contains web api endpoints.
- `migration`: Files that represent database migrations.
- `enum`: Files that are strictly used to define enum values.
- `middleware`: Middleware files that intercept api requests.
- `entry_point`: A file that runs the program or starts a server.
- `command-line-interface_command`: Files that primarily contain CLI commands for interacting with the application.
- `prediction_model`: Files that contain a model pipeline or contribute to a model(e.g., creating or engineering features for a dataset that the model will use).
- `other`: Files that don't fit into any of the other file roles.
- `core`: Files that doesn't fit into any other category and contain essential code that is used in the project.

## Architecture

The application process starts with `flow.py` which forwards data by calling functions from different files in the correct order:
1. `flow.py` takes a project zip file then:
   - converts it to bytes format (if it's not already)
   - unzips the project, removes non-python and junk files, and puts all python files with their contents in a list of dictionaries.
   - Loops over each file, parses it using `ast` library, then hands over parsed code data to `backend.code_analyzer.CodeAnalyzer`.
2. `code_analyzer.py` works by defining a `backend.code_analyzer.CodeAnalyzer` class that inherits functionalities from base class `ast.NodeVisitor`.
This allows the `backend.code_analyzer.CodeAnalyzer` class to scan for specific parts of code that we are 
looking for automatically by using the overridden ast methods that must follow this naming format visit_{ast node type}.
3. After all files are analyzed a list of dictionaries containing all the parsed data is formed. 
This list is then passed to `backend.graph_builder.build_graph` to be converted into a directed `networkx` graph with nodes and edges.
    - Different types of imports are labeled accordingly during the process
    - Label each node type as either file, function, or class.
4. The graph is passed to `graph_analyzer.py` to further analyze the graph and create more features.
    - Detect circular dependencies using strongly connected components
    - Detect entry point nodes 
    - Mark dependency order in edges based on runtime import execution order with breadth first graph traversal algorithm     
    - Mark node execution order in edges based on their depth from the entry point with depth first graph traversal algorithm
5. `file_role_predictor.py` loads prediction model from `.pkl` file to predict the role of each file in the graph. 
If file prediction probability is  less than 55% then it is automatically labeled as "Other".
6.  The final output graph is printed in json format and returned. A Flask server runs to host a GET API enabling any fronten to fetch the JSON.

Building dataset and training model follows the same steps above but without strictly relying on `flow.py`.
1. `dataset_builder.py` scrapes selected repositories from the `dataset_files/repositories.csv` file 
2. Then steps above are followed to generate a `networkx` graph that was returned by `graph_analyzer.py`
3. Builds a `dataset_files/dataset.csv` with all necessary features
4. `model_trainer.py` uses `dataset_files/dataset.csv` to train and generate `.pkl` files that house models.

## How to use (CLI commands)
You can Run different functionalities using the following command line commands:
- `py flow.py build`: Scrape selected repositories inside `dataset_files/repositories.csv`, analyze them, then build or add rows to a `dataset.csv` using analyzed features.
- `py flow.py build update`: Same as `py flow.py build but it doesn't skip already analzyed files but rather keepsl ooping for them at a certian comiit to see if the commit have ha some changes.`
- `py flow.py analyze <file_name.zip>`: Analyze a selected project zip file, predicts file roles, then prints fully analyzed project in json format and a Flask GET API returns the same JSON for frontend applications to fetch).
- `py flow.py train`: Trains our models on `dataset_files/dataset.csv` and output `dataset_files/stratified_and_balanced_dataset.csv`, `ml_models/random_forest_classifier.pkl`, `ml_models/logistic_regression_classifier.pkl`, `ml_models/lightGBM_classifier.pkl`.
