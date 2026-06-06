import pandas
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
from scipy.stats import randint
from sklearn.pipeline import Pipeline


def train_model(dataframe: pandas.DataFrame = pandas.read_csv("dataset.csv")):
    """
    A Machine learning pipeline to train a classification RandomForestClassifier model to predict file roles accurately then Saves train data in .pickle file.
    """
    # Data processing and splitting

    # TODO: keep this temporarily removed during the model testing and enhancement phase
    ## Remove useless data so the model doesn't learn how to say other most of the time when it gets confused
    # dataframe = dataframe[dataframe["file_role"] != "other"]

    # Drop null rows with no labeled file_role
    dataframe = dataframe.dropna(subset=["file_role"])

    ## Separate data into train and test data
    train_data_features, test_data_features, train_data_targets, test_data_targets = train_test_split(dataframe.drop(columns=["relative_path", "repository_url", "file_role", "role_note","file_domain"]), dataframe["file_role"], test_size=0.2, random_state=20)

    # Feature engineering
    ## Separate categorical data from numerical data
    categorical_columns = train_data_features.select_dtypes(include=["object"]).columns
    numerical_columns = train_data_features.select_dtypes(include=["number"]).columns

    ## Use ColumnTransformer to apply OneHotEncoder on categorical data and StandardScaler on numerical data
    column_transformer = ColumnTransformer([
        ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ("standard_scaler", StandardScaler(), numerical_columns),
    ], remainder="passthrough")

    pipeline = Pipeline([
        ("column_transformer", column_transformer),
        ("random_forest_classifier", RandomForestClassifier(random_state=20))
    ])

    random_forest_classifier_param_grid = {
        "random_forest_classifier__n_estimators" : randint(50, 300),
        "random_forest_classifier__max_depth" : [5, 7, 9],
        "random_forest_classifier__class_weight" : ["balanced"],
    }
    # cross validation and hyperparameter tuning
    random_forest_classifier_random_search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=random_forest_classifier_param_grid,
        n_jobs=-1,
        cv=5,
        random_state=20
    )

    # Model training
    random_forest_classifier_random_search.fit(train_data_features, train_data_targets)

    # Model evaluation
    ## Evaluation metrics

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

    print(f"Best parameters: {random_forest_classifier_random_search.best_params_}")
    print(f"Best score: {random_forest_classifier_random_search.best_score_}")
    print(f"Random forest classifier accuracy score: {random_forest_classifier_random_search.score(train_data_features, train_data_targets)}")

    best_estimator = random_forest_classifier_random_search.best_estimator_
    features_importances = best_estimator.named_steps["random_forest_classifier"].feature_importances_
    features = best_estimator.named_steps["column_transformer"].get_feature_names_out()
    for feature in range(len(features_importances)):
        print(f"{features[feature]}: {features_importances[feature]}")
    print(f"Best estimator: {best_estimator.named_steps['random_forest_classifier']}")

    ## Classification report
    test_data_targets_prediction_results = random_forest_classifier_random_search.predict(test_data_features)
    print(classification_report(test_data_targets, test_data_targets_prediction_results))

    ## Confusion matrix
    print(pandas.crosstab(test_data_targets, test_data_targets_prediction_results).rename_axis(columns="Actual/Predicted", index=None))
    print(confusion_matrix(test_data_targets, test_data_targets_prediction_results))


    # Saving classifier model into a .pkl file
    with open("file_role_classifier.pkl", "wb") as classifier:
        pickle.dump(random_forest_classifier_random_search, classifier)


