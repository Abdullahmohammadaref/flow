import pandas
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
import pickle
from scipy.stats import randint
from sklearn.pipeline import Pipeline


def stratify_and_balance_dataset(dataframe: pandas.DataFrame = pandas.read_csv("dataset_files/dataset.csv"), target_column: str = "file_role", unique_group_column: str = "repository_url", max_repository_percentage: float = 0.4, sample_size_multiplier: int = 3, random_state: int = 20, output_dataframe_name: str = "stratified_and_balanced_dataset.csv"):
    """
    Addresses class imbalance domain leakage with:
    1- Stratifying:
        - Caps data from each group to ensure getting diverse and random data from all groups
        - prevents Domain Leakage
    2- Balancing:
        - Pre-balances unique target classes by capping all classes dynamically based on the lowest sampled class
        - Solves Class Imbalance issue even after balancing model class_weights
    :param dataframe: A pandas dataframe
    :param target_column: The target column
    :param unique_group_column: The unique group column
    :param max_repository_percentage: Max target class percentage for Stratifying
    :param sample_size_multiplier: Balancing multiplier
    :param random_state: Random state
    :param output_dataframe_name: Output dataframe name
    :return: A stratified and balanced pandas dataframe.
    """
    # Calculate the target class cap
    target_class_cap = int(dataframe[target_column].value_counts().min() * sample_size_multiplier)
    # Calculate the group rows cap
    group_rows_cap = int(target_class_cap * max_repository_percentage)

    stratified_and_balanced_data = []

    # Loop over target_classes and to Stratify and Balance
    for target_class_name, target_class_group_rows in dataframe.groupby(target_column):

        target_class_samples = []

        # Loop over groups and Stratify data by maximizing group rows up to the group_rows_cap threshold
        for group_name, group_rows in target_class_group_rows.groupby(unique_group_column):
            target_class_samples.append(group_rows.sample(n=min(len(group_rows), group_rows_cap), random_state=random_state))

        combined_target_classes_dataframe = pandas.concat(target_class_samples)

        # Balance Data ensuring each class samples doesn't pass the target_class_cap threshold
        if len(combined_target_classes_dataframe) > target_class_cap:
            combined_target_classes_dataframe = combined_target_classes_dataframe.sample(n=target_class_cap, random_state=random_state)

        stratified_and_balanced_data.append(combined_target_classes_dataframe)

    # Transform rows into pandas dataframe, shuffle, and reset index
    stratified_and_balanced_dataframe = pandas.concat(stratified_and_balanced_data).sample(frac=1, random_state=random_state).reset_index(drop=True)
    # Write the `stratified_and_balanced_dataframe` in a CSV file in the case of further usage.
    stratified_and_balanced_dataframe.to_csv(f"dataset_files/{output_dataframe_name}", index=False)

    return stratified_and_balanced_dataframe

def train_model(dataframe: pandas.DataFrame = pandas.read_csv("dataset_files/dataset.csv")):
    """
    A Machine learning pipeline to train a classification RandomForestClassifier model to predict file roles accurately then Saves train data in .pickle file.
    """
    # Data processing and splitting

    # Drop null rows with no labeled file_role
    dataframe = dataframe.dropna(subset=["file_role"])
    print(dataframe['file_role'].value_counts())

    # Prepare dataset to resolve Data Starvation and Domain Overfitting
    dataframe = stratify_and_balance_dataset(dataframe=dataframe, max_repository_percentage=0.4, sample_size_multiplier=3)

    # Prints how much role we got from each repository
    # Note: terminal text size might need to decrease in order to see the whole print
    repository_names = dataframe['repository_url'].str.replace('https://api.github.com/repos/', '', regex=False)
    print(
            (
                pandas.crosstab(
                    repository_names,
                    dataframe['file_role'],
                ).rename_axis(columns="repository_url/file_role", index=None).astype(str) +
                " (" +
                (pandas.crosstab(
                    repository_names,
                    dataframe['file_role'],
                    normalize='columns',
                ).rename_axis(columns="repository_url/file_role", index=None) * 100).round(1).astype(str) +
                "%)"
            )
    )
    print(dataframe['file_role'].value_counts())

    ## Separate data into train and test data
    train_data_features, test_data_features, train_data_targets, test_data_targets = train_test_split(dataframe.drop(columns=["file_url", "relative_path", "commit_hash", "repository_url", "file_role", "role_note", "domain", "repository_full_name", "github_status"]), dataframe["file_role"], test_size=0.2, random_state=20, stratify=dataframe["file_role"])

    # Feature engineering
    ## Separate categorical data from numerical data
    categorical_columns = train_data_features.select_dtypes(include=["object"]).columns
    numerical_columns = train_data_features.select_dtypes(include=["number"]).columns

    ## Use ColumnTransformer to apply OneHotEncoder on categorical data and StandardScaler on numerical data
    column_transformer = ColumnTransformer([
        ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ("standard_scaler", StandardScaler(), numerical_columns),
    ], remainder="passthrough")

    models = {
        "Logistic_Regression": {
            "model": LogisticRegression(random_state=20, max_iter=2000),
            "params": {
                "classifier__C": [0.1, 1.0, 10.0],
                "classifier__class_weight": ["balanced"],
            },
            "pkl_file_name": "logistic_regression_classifier.pkl"
        },
        "random_forest_classifier": {
            "model": RandomForestClassifier(random_state=20),
            "params": {
                "classifier__n_estimators": [50, 150, 300],
                "classifier__max_depth": [5, 7, 9],
                "classifier__class_weight": ["balanced"],
            },
            "pkl_file_name": "random_forest_classifier.pkl"
        },
        "LightGBM (Gradient Boosting)": {
            "model": HistGradientBoostingClassifier(random_state=20),
            "params": {
                "classifier__max_iter": [50, 150, 300],
                "classifier__max_depth": [5, 7, 9],
                "classifier__learning_rate": [0.01, 0.1, 0.2],
                "classifier__class_weight": ["balanced"],
            },
            "pkl_file_name": "lightGBM_classifier.pkl"
        }
    }

    for model, configuration in models.items():

        pipeline = Pipeline([
            ("column_transformer", column_transformer),
            ("classifier", configuration["model"])
        ])

        grid_search = GridSearchCV(
            estimator=pipeline,
            param_grid=configuration["params"],
            n_jobs=-1,
            cv=5,
        )

        # Model training
        grid_search.fit(train_data_features, train_data_targets)

        # Model evaluation
        ## Evaluation metrics

        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Cross validation score: {grid_search.best_score_}")
        print(f"Random forest classifier accuracy score: {grid_search.score(train_data_features, train_data_targets)}")

        #
        best_estimator = grid_search.best_estimator_
        classifier_step = best_estimator.named_steps["classifier"]
        features = best_estimator.named_steps["column_transformer"].get_feature_names_out()
        print(f"Best estimator: {classifier_step}")
        if hasattr(classifier_step, "feature_importances_"):
            features_importances = classifier_step.feature_importances_
            for feature in range(len(features_importances)):
                print(f"{features[feature]}: {features_importances[feature]}")
        elif hasattr(classifier_step, "coef_"):
            features_importances = classifier_step.coef_[0]
            for feature in range(len(features_importances)):
                print(f"{features[feature]}: {features_importances[feature]}")
        else:
            # LightGBM (Gradient Boosting) doesn't have feature importances
            pass

        ## Classification report
        test_data_targets_prediction_results = grid_search.predict(test_data_features)
        print(classification_report(test_data_targets, test_data_targets_prediction_results))

        ## Confusion matrix
        print(pandas.crosstab(test_data_targets, test_data_targets_prediction_results).rename_axis(columns="Actual/Predicted", index=None))
        print(confusion_matrix(test_data_targets, test_data_targets_prediction_results))

        # Saving classifier model into a .pkl file
        with open(f"ml_models/{configuration["pkl_file_name"]}", "wb") as classifier:
            pickle.dump(grid_search, classifier)


