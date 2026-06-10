import pickle
import pandas
from dataset_builder import extract_features


def predict_files_roles(analyzed_project_graph):
    """
    :param: analyzed networkx project graph
    :return: analyzed networkx project graph with predicted file roles
    """
    with open("random_forest_classifier.pkl", "rb") as pkl_file:
        random_forest_classifier_pipeline = pickle.load(pkl_file)

    for node_name, node_data in analyzed_project_graph.nodes(data=True):
        if node_data["type"] != "LocalFile":
            continue
        prediction_probabilities = random_forest_classifier_pipeline.predict_proba(pandas.DataFrame([extract_features(node_name, node_data)]).drop(columns=["relative_path", "repository_url", "file_role", "role_note", "domain"]))[0]
        best_score = max(prediction_probabilities)

        if best_score >= 0.55:
            analyzed_project_graph.nodes[node_name]["file_role"] = random_forest_classifier_pipeline.classes_[list(prediction_probabilities).index(best_score)]
        else:
            analyzed_project_graph.nodes[node_name]["file_role"] = "other"
        analyzed_project_graph.nodes[node_name]["file_role_prediction_confidence"] = float(best_score)

    return analyzed_project_graph