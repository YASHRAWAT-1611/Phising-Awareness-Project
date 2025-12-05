import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    # Expect file: data/text_dataset.csv with columns: text,label (1=scam,0=legit)
    df = pd.read_csv(BASE_DIR / "data" / "text_dataset.csv")
    X = df["text"].astype(str)
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.9
        )),
        ("clf", LogisticRegression(max_iter=200))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    models_dir = BASE_DIR / "app" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, models_dir / "text_pipeline.joblib")
    print("Saved text_pipeline.joblib")

if __name__ == "__main__":
    main()
