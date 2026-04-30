import sys
import zipfile
import io
import ast
from code_analyzer import CodeAnalyzer

def encode_zip(zip_folder_path: str):
    with open(zip_folder_path, "rb") as zip_folder_bytes:
        return zip_folder_bytes.read()

def unzip_project(zip_folder_bytes: bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(zip_folder_bytes)) as folder:
            files = {}
            for file_name in folder.namelist():
                if file_name in ["venv", "__pycache__", "mirations"]:
                    continue
                if file_name.endswith(".py"):
                    files[file_name] = folder.read(file_name).decode("utf-8")
            return files
    except zipfile.BadZipfile:
        return {}

def visualize(project_zip_folder_bytes: bytes):
    project = unzip_project(project_zip_folder_bytes)

    project_data = {}
    for file_name, file_content in project.items():

        file_tree = ast.parse(file_content)
        code_analyzer = CodeAnalyzer()
        code_analyzer.visit(file_tree)

        project_data[file_name] = {
            "imports": code_analyzer.imports,
            "functions": code_analyzer.functions,
            "classes": code_analyzer.classes,

            "is_entry_point": code_analyzer.is_entry_point,
            "has_wait_state": code_analyzer.has_wait_state,

            "decorators": list(code_analyzer.decorators),
        }


def main(project_zip_folder_path: str):
    visualize(encode_zip(project_zip_folder_path))

if __name__ == "__main__":
    main(sys.argv[1])