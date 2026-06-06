import sys
import zipfile
import io
import ast

import pandas as pd

from code_analyzer import CodeAnalyzer
from graph_builder import build_graph
from graph_analyzer import GraphAnalyzer
from dataset_builder import DatasetBuilder
from model_trainer import train_model

from file_role_predictor import predict_files_roles
import networkx



def encode_zip(zip_folder_path: str):
    """
    Encode a zip file

    :param: zip_folder_path:
    :return: a zip folder in bytes format
    """
    try:
        with open(zip_folder_path, "rb") as zip_folder_bytes:
            return zip_folder_bytes.read()
    except FileNotFoundError:
        print(f"Zip folder not found at {zip_folder_path}")
        sys.exit()

def unzip_project(zip_folder_bytes: bytes):
    """
    - Encode zip folder bytes into a folder object
    - Extract only relevant .py files
    - Reads file content as string

    :param: a zip folder in bytes format
    :return: a list of .py file paths and their content as strings
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_folder_bytes)) as folder:
            files = {}

            for file_name in folder.namelist():
                # Remove unwanted folders that contain .py files
                if any(i in file_name for i in ["venv", "__pycache__", "__version__.py", "__about__.py"]):
                    continue
                if file_name.endswith(".py"):
                    files[file_name] = folder.read(file_name).decode("utf-8")
            return files
    except zipfile.BadZipFile:
        print("Couldn't unzip project folder: the zip file is corrupt")
        sys.exit()

def analyze_project_data(project):
    """
    Analyze project files using ast library

    :param: a dictionary of file paths and their content as strings
    :return: a dictionary of file data
    """
    data = {}
    for file_name, file_content in project.items():
        try:
            # Use ast to parse the python file code
            file_tree = ast.parse(file_content)

            code_analyzer = CodeAnalyzer()

            # Visit only created "visit_nodeName" methods
            code_analyzer.visit(file_tree)

            # Detect noisy files and skip them
            if (
                len(code_analyzer.imports) == 0
                and len(code_analyzer.functions) == 0
                and len(code_analyzer.classes) == 0
                and len(list(code_analyzer.global_variables)) == 0
                and len(list(code_analyzer.decorators)) == 0
                and len(list(code_analyzer.inherited_classes)) == 0
                ):
                continue
            data[file_name] = {
                "imports": code_analyzer.imports,
                "functions": code_analyzer.functions,
                "classes": code_analyzer.classes,

                "is_entry_point": code_analyzer.is_entry_point,
                "has_wait_state": code_analyzer.has_wait_state,

                "decorators": list(code_analyzer.decorators),

                "base_classes": list(code_analyzer.inherited_classes),
                "global_variables": list(code_analyzer.global_variables),
                # "file_role": guess_file_role(file_name.lower(), code_analyzer)
                "file_role": None,
                "role_note": None,
                "file_domain": None

            }
        except SyntaxError:
            # Skip files with invalid python code
            continue
    return data

def extract_build_analyze(project_zip_folder_bytes: bytes):
    """
    Main function for analyzing project by calling relevant function in the right order
    1- Unzip project and parse its content with ast parser
    2- Build a graph object using networkx
    3- Analyze the graph for circular dependencies, entrypoints, and order edges based on import order and depth from entry point
    """
    # Step 1: Unzipping project and extracting data using ast
    project = unzip_project(project_zip_folder_bytes)
    project_data = analyze_project_data(project)

    # Step 2: Build graph with networkx
    project_graph = build_graph(project_data)

    # Step 3: Analyze graph
    graph_analyzer = GraphAnalyzer(project_graph)

    analyzed_project_graph = graph_analyzer.analyze_graph(train=True) if len(sys.argv) > 2 else graph_analyzer.analyze_graph()

    return analyzed_project_graph

def visualize(project_zip_folder_bytes: bytes):
    analyze(project_zip_folder_bytes)

def analyze(project_zip_folder_bytes: bytes):
    """
    Main function for handling all analysis steps in order by calling functions for the visualization process:
    1- Unzipping project and extracting data using ast
    2- Build graph with networkx
    3- Further Analyze graph
    4- Runs the graph in our Prediction model after loading .pkl training data.
    5- Output the final graph in json format

    :param: project_zip_folder_bytes:
    :return: a JSON project flow diagram that is ready for drawing/visualizing
    """
    analyzed_project_graph = extract_build_analyze(project_zip_folder_bytes)
    # print(networkx.node_link_data(analyzed_project_graph))
    analyzed_project_graph = predict_files_roles(analyzed_project_graph)

    print(networkx.node_link_data(analyzed_project_graph))



def main():
     if len(sys.argv) > 1:
        if sys.argv[1].lower() == "train":
            train_model()
            print("Model trained successfully")
        if sys.argv[1].lower() == "build":
            dataset_builder = DatasetBuilder()
            # pass needed function in build_dataset function as a parameter instead of importing it in dataset_builder.py to avoid circular imports
            dataset_builder.build_dataset(extract_build_analyze)
            print("Dataset built successfully")
        elif sys.argv[1].lower() == "visualize":
            visualize(encode_zip(sys.argv[2]))
        elif sys.argv[1].lower() == "analyze":
            analyze(encode_zip(sys.argv[2]))
            print("Project analysis complete")
     else:
        print("No argument provided")

if __name__ == "__main__":
    main()
