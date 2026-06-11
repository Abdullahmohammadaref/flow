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
- `server.py`: A Flask server for hosting api endpoints for the application

**Generated Files:**

- `dataset_files/dataset.csv`: The dataset that `dataset_builder.py` generates (file is already provided roles,domain,notes are labeled manually for convenience).
- `dataset_files/stratified_and_balanced_dataset.csv`: Dataset That is stratified and balanced then fed to Model pipeline.
- `ml_models/random_forest_classifier.pkl`: Random Forest Classifier model
- `ml_models/logistic_regression_classifier.pkl`: Logistic Regression Classifier model
- `ml_models/lightGBM_classifier.pkl`: LightGBM Classifier model

**Other files/directories:**
- `dataset_files/repositories.csv`: Contains a list of repositories and their domain. This will be used to build dataset or add rows to an existing one.

    | Column Name            | Data Type | Description                                                |
    |:-----------------------| :--- |:-----------------------------------------------------------|
    | `repository_full_name` | string | The full name of the repository in `owner/repository` format |
    | `domain`               | string | The domain from which this repository comes from           | 

- `.env.example`: exampl `.env` file.
- `/sample_projects`: Directory containing Sample projects to use for analysis.
    
### Dataset

**Columns**

Note: Each represents a python file with its features 

| Column Name                  | Data Type | Description                                                                                                                                                                                                                     |
|:-----------------------------| :--- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `relative_path`              | string | The relative path of the file from the root directory of the repository                                                                                                                                                         |
| `file_role`                  | string | The target value that represents the role of the file (This column is labeled manually for each row).                                                                                                                           |
| `role_note`                  | string | A column for writing personal notes if needed during the manual process of labeling the `file_role` column.                                                                                                                     |
| `file_domain`                | string | The domain from which this repository came from (e.g., e-commerce store, python library, framework, etc) (This column is labeled manually for each repository).                                                                 |
| `repository_url`             | string | The absolute repository URL from where this file row was extracted from.                                                                                                                                                        |
| `number_of_imports`          | Int64 | Total Number of all type of imports.                                                                                                                                                                                            |
| `number_of_external_imports` | Int64 | Total Number of imports from external libraries.                                                                                                                                                                                |
| `number_of_internal_imports` | Int64 | Total Number of imports from internal project libraries.                                                                                                                                                                        |
| `number_of_standard_imports` | Int64 | Total Number of imports from python standard libraries.                                                                                                                                                                         |
| `number_of_classes`          | Int64 | Total Number of defined classes.                                                                                                                                                                                                |
| `number_of_functions`        | Int64 | Total Number of defined functions (Excluding async functions and class methods).                                                                                                                                                |
| `is_entry_point`             | Int64 | If `graph_analyzer.GraphAnalyzer.detect_entry_points` have labeled the node of this file as an entry point or not.                                                                                                              |
| `has_wait_state`             | Int64 | If `code_analyzer.CodeAnalyzer.visit_Call` have detected a wait state inside this file or not.                                                                                                                                  |
| `number_of_decorators`       | Int64 | Total Number of decorators.                                                                                                                                                                                                     |
| `number_of_base_classes`     | Int64 | Total Number of base classes.                                                                                                                                                                                                   |
| `has_model_in_path`          | Int64 | If `relative_path` string have the keyword `model` inside it.                                                                                                                                                                   |
| `has_view_in_path`           | Int64 | If `relative_path` string have the keyword `view` inside it.                                                                                                                                                                    |
| `has_test_in_path`           | Int64 | If `relative_path` string have the keyword `test` inside it.                                                                                                                                                                    |
| `has_util_in_path`           | Int64 | If `relative_path` string have the keyword `util` inside it.                                                                                                                                                                    |
| `has_migration_in_path`      | Int64 | If `relative_path` string have the keyword `migration` inside it.                                                                                                                                                               |
| `has_script_in_path`         | Int64 | If `relative_path` string have the keyword `script` inside it.                                                                                                                                                                  |
| `has_middleware_in_path`     | Int64 | If `relative_path` string have the keyword `middleware` inside it.                                                                                                                                                              |
| `has_enum_in_path`           | Int64 | If `relative_path` string have the keyword `enum` inside it.                                                                                                                                                                    |
| `has_config_in_path`         | Int64 | If `relative_path` string have the keyword `config` inside it.                                                                                                                                                                  |
| `path_depth`                 | Int64 | How deep this is this file in the directory tree relative to the repository project root directory.                                                                                                                             |
| `functions_to_classes_ratio` | float64 | The ratio of `number_of_functions / number_of_classes`(a derived feature)                                                                                                                                                       |
| `external_import_ratio`      | float64 | The ratio of `number_of_external_imports / number_of_imports`(a derived feature)                                                                                                                                                |
| `code_complexity`            | Int64 | A score for assessing code complexity (a derived feature). <br/> Calculated by adding all points in this point system:<br/> <ul> <li> `number_of_decorators` * 1<li>`number_of_base_classes` * 1 <li>`has_wait_state` * 3 <ul/> |

**Target Value Classes (File Roles)**

- `test`: Files that are used for testing.
- `model`: Files that define the schema model of a database.
- `script`: Standalone script files.
- `utility`: Files that contain utility functions that are used by multiple other files inside the project.
- `config`: Files that contains global settings and configurations for the whole project.
- `view`: Files that contain controllers which a router routes to.
- `router`: File that contains web api endpoints.
- `migration`: Files that represent database migrations.
- `enum`: Files that are strictly used to define enum values.
- `middleware`: Middleware files that intercept api requests.
- `entry_point`: A file that runs the program or starts a server.
- `command-line-interface_command`: Files that primarily contain CLI commands for interacting with the application.
- `prediction_model`: Files that contain a model pipeline or contribute to a model(e.g., creating or engineering features for a dataset that the model will use).
- `other`: Files that don't fit into any of the other file roles.

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
5. `file_role_predictor.py` loads prediction model from `.pkl` file to predict the role of each file in the graph .
6.  The final output graph is printed in json format and returned. `server.py` hosts the API endpoint that sends the returned graph.

Building dataset and training model follows the same steps above but without strictly relying on `flow.py`.
1. `dataset_builder.py` scrapes selected repositories from the `dataset_files/repositories.csv` file 
2. Then steps above are followed to generate a `networkx` graph that was returned by `graph_analyzer.py`
3. Builds a `dataset_files/dataset.csv` with all necessary features
4. `model_trainer.py` uses `dataset_files/dataset.csv` to train and generate `.pkl` files that house models.

## How to use (CLI commands)
You can Run different functionalities using the following command line commands:
- `py flow.py build`: Scrape selected repositories inside `dataset_files/repositories.csv`, analyze them, then build or add rows to a `dataset.csv` using analyzed features.
- `py flow.py analyze <file_name.zip>`: Analyze a selected project zip file, predicts file roles, then prints fully analyzed project in json format (the same json that the api returns).
- `py flow.py train`: Trains our models on `dataset_files/dataset.csv` and output `dataset_files/stratified_and_balanced_dataset.csv`, `ml_models/random_forest_classifier.pkl`, `ml_models/logistic_regression_classifier.pkl`, `ml_models/lightGBM_classifier.pkl`.
- `py server.py`: Starts the flask server on http://127.0.0.1:5000
