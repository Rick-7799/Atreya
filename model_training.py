import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib  # For saving the model

def load_data(patient_data.csv):
    data = pd.read_csv(patient_data.csv)
    return data

def handle_missing_values(data):
    num_cols = data.select_dtypes(include=['float64', 'int']).columns
    for col in num_cols:
        data[col].fillna(data[col].median(), inplace=True)

    cat_cols = data.select_dtypes(include=['object']).columns
    for col in cat_cols:
        data[col].fillna(data[col].mode()[0], inplace=True)

    return data

def preprocess_data(data):
    X = data.drop(columns=['target_variable'])
    y = data['target_variable']

    num_cols = X.select_dtypes(include=['float64', 'int']).columns
    cat_cols = X.select_dtypes(include=['object']).columns

    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)
        ]
    )

    X_processed = preprocessor.fit_transform(X)

    return X_processed, y

def split_data(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    print(f"Accuracy: {accuracy}")
    print("Classification Report:\n", report)

def save_model(model, file_path):
    joblib.dump(model, file_path)
    print(f"Model saved to {file_path}")

if __name__ == "__main__":
    file_path = 'data/random_patient_data.csv'
    data = load_data(file_path)
    data = handle_missing_values(data)
    X_processed, y = preprocess_data(data)
    X_train, X_test, y_train, y_test = split_data(X_processed, y)
    
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    save_model(model, 'models/trained_model.joblib')
