import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

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

def split_data(X, y
