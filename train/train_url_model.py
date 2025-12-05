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
    # Expect file: data/url_dataset.csv with columns: url,label (1=phishing,0=legit)
    df = pd.read_csv(BASE_DIR / "data" / "url_dataset.csv")
    X = df["url"].astype(str)
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 5),   # character-level patterns
            min_df=2
        )),
        ("clf", LogisticRegression(max_iter=300))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    models_dir = BASE_DIR / "app" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, models_dir / "url_pipeline.joblib")
    print("Saved url_pipeline.joblib")

if __name__ == "__main__":
    main()
