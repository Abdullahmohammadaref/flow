import pandas
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
from scipy.stats import randint


def train_model(dataframe: pandas.DataFrame):
    """

    """
    # Data processing and splitting

    ## Convert all booleans to 0 and 1 format
    boolean_columns = dataframe.select_dtypes(include="bool").columns
    dataframe[boolean_columns] = dataframe[boolean_columns].astype(int)

    ## Remove useless data so the model doesn't learn how to say other most of the time when it gets confused
    dataframe = dataframe[dataframe["file_role"] != "other"]

    ## Separate data into train and test data
    train_data_features, test_data_features, train_data_targets, test_data_targets = train_test_split(dataframe.drop(columns=["repository_name", "repository_url", "file_role"]), dataframe["file_role"], test_size=0.2, random_state=20)

    # Feature engineering

    ## Separate categorical data from numerical data
    categorical_columns = train_data_features.select_dtypes(include=["object"]).columns
    numerical_columns = train_data_features.select_dtypes(include=["float64"]).columns

    ## Use ColumnTransformer to apply OneHotEncoder on categorical data and StandardScaler on numerical data
    column_transformer = ColumnTransformer([
        ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ("standard_scaler", StandardScaler(), numerical_columns),
    ], remainder="passthrough")
    train_data_features = column_transformer.fit_transform(train_data_features)
    test_data_features = column_transformer.transform(test_data_features)

    # Model initialization
    random_forest_classifier = RandomForestClassifier(random_state=20)
    random_forest_classifier_param_grid = {
        "n_estimators" : randint(50, 300),
        "max_depth" : randint(5, 30),
        "class_weight" : ["balanced"],
    }
    # cross validation and hyperparameter tuning
    random_forest_classifier_random_search = RandomizedSearchCV(
        estimator=random_forest_classifier,
        param_distributions=random_forest_classifier_param_grid,
        n_jobs=-1,
        cv=5,
        random_state=20
    )

    # Model training
    random_forest_classifier_random_search.fit(train_data_features, train_data_targets)

    # Model evaluation

    ## Evaluation metrics
    print(f"Best parameters: {random_forest_classifier_random_search.best_params_}")
    print(f"Best score: {random_forest_classifier_random_search.best_score_}")
    print(f"Best estimator: {random_forest_classifier_random_search.best_estimator_}")
    print(f"Random forest classifier accuracy score: {random_forest_classifier_random_search.score(train_data_features, train_data_targets)}")

    ## Classification report
    test_data_targets_prediction_results = random_forest_classifier_random_search.predict(test_data_features)
    print(classification_report(test_data_targets, test_data_targets_prediction_results))

    ## Confusion matrix
    print(confusion_matrix(test_data_targets, test_data_targets_prediction_results))

    # Saving classifier model into a .pkl file
    with open("file_role_classifier.pkl", "wb") as classifier:
        pickle.dump(random_forest_classifier_random_search, classifier)


