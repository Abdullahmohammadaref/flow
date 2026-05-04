import pkgutil
import sys
import networkx

def build_graph(project_files_data: dict):
    """
    Handles building a directed graph using netwrokx nodes and edges
    :param: dictionary of project_files_data
    :return: a flow diagram in JSON format that are ready for machine learning and visualization
    """

    global_contents = create_global_state(project_files_data)

    project_files_data = label_imports(project_files_data, global_contents)

    # Initialize graph with networkx
    graph = networkx.DiGraph()

    for python_file in project_files_data.keys():
        graph.add_node(python_file, type="LocalFile")

    for python_file, contents in project_files_data.items():
        for content_import, import_type in contents["imports"].items():
            if import_type in ["external_import","standard_import" ]:
                if not graph.has_node(content_import):
                    graph.add_node(content_import, type=import_type)
                graph.add_edge(python_file, content_import)
            elif import_type == "internal_import":
                expected_python_file_path = content_import.replace(".","/") + ".py"
                if expected_python_file_path in project_files_data:
                    graph.add_edge(python_file, expected_python_file_path)
                elif content_import in global_contents:
                    file = global_contents[content_import]["file"]
                    graph.add_edge(python_file, file)

    json_graph = networkx.readwrite.json_graph.node_link_data(graph)

    return json_graph

def label_imports(project_files_data, global_contents):
    """
    Lable imported libraries as external, internal, or standard
    :param: dictionary of project_files_data
    :param: dictionary global_contents
    :return project_files_data dictionary with imports labeled:
    """

    # Collect all python standard libraries (including builtin modules)
    python_standard_libraries = {module.name for module in pkgutil.iter_modules()}
    python_standard_libraries.update(sys.builtin_module_names)

    internal_modules = {key.replace("/", ".").replace(".py", "") for key in project_files_data.keys()}

    for python_file in project_files_data:
        imports = {}

        for imported_library in project_files_data[python_file]["imports"]:

            main_import = imported_library.split(".")[-1]
            base_import = imported_library.split(".")[0]

            if imported_library in internal_modules:
                imports[imported_library] = "internal_import"
            elif main_import in global_contents:
                imports[main_import] = "internal_import"
            elif base_import in python_standard_libraries:
                imports[imported_library] = "standard_import"
            else:
                imports[imported_library] = "external_import"

        project_files_data[python_file]["imports"] = imports

    return project_files_data

def create_global_state(project_files_data: dict):
    """
    Adds type label and adds file name to `project_files_data` track the global state of the whole project files.
    :params: dictionary of project_files_data
    "return: dictionary global_contents
    """
    global_contents = {}

    for python_file, content in project_files_data.items():
        global_contents[python_file] = {"type":"file"}
        for content_class in content["classes"]:
            global_contents[content_class] = {"type":"class", "file": python_file}
        for content_function in content["functions"]:
            global_contents[content_function] = {"type":"function", "file": python_file}

    return global_contents