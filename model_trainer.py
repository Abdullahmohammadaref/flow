import pandas
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
from scipy.stats import randint


def train_model(dataframe: pandas.DataFrame):

    # Data processing and splitting
    dataframe["is_entry_point"] = dataframe["is_entry_point"].astype(int)
    dataframe["has_wait_state"] = dataframe["has_wait_state"].astype(int)
    train_data_features, test_data_features, train_data_targets, test_data_targets = train_test_split(dataframe.drop(columns=["repository_name", "repository_url", "file_role"]), dataframe["file_role"], test_size=0.2, random_state=20)
    categorical_columns = train_data_features.select_dtypes(include=["object"]).columns
    numerical_columns = train_data_features.select_dtypes(include=["float64"]).columns

    # Feature engineering
    column_transformer = ColumnTransformer([
        ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ("standard_scaler", StandardScaler(), numerical_columns),
    ], remainder="passthrough")
    train_data_features = column_transformer.fit_transform(train_data_features)
    test_data_features = column_transformer.transform(test_data_features)


    # Model training
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
    random_forest_classifier_random_search.fit(train_data_features, train_data_targets)

    # Model evaluation
    print(f"Best parameters: {random_forest_classifier_random_search.best_params_}")
    print(f"Best score: {random_forest_classifier_random_search.best_score_}")
    print(f"Best estimator: {random_forest_classifier_random_search.best_estimator_}")
    print(f"Random forest classifier accuracy score: {random_forest_classifier_random_search.score(train_data_features, train_data_targets)}")

    test_data_targets_prediction_results = random_forest_classifier_random_search.predict(test_data_features)

    print(classification_report(test_data_targets, test_data_targets_prediction_results))
    print(confusion_matrix(test_data_targets, test_data_targets_prediction_results))

    # Saving classifier model into a .pkl file
    with open("file_role_classifier.pkl", "wb") as classifier:
        pickle.dump(random_forest_classifier_random_search, classifier)


