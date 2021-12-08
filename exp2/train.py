"""train explosion explorer model"""

import pickle

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def main() -> None:
    """train model"""

    data = pd.read_csv("../data/training_data.csv")
    cols = data.columns
    data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")
    data.drop(
        columns=[
            "Unnamed: 0",
            "SAR_p75",
            "SAR_min",
            "SAR_p50",
            "SAR_p25",
            "NDVI_stdDev",
        ],
        inplace=True,
    )
    data.dropna(how="any", axis=0, inplace=True)

    x = data.iloc[:, :-2]
    y = data.iloc[:, -1]

    classifier = Pipeline(
        [
            ("Scale", StandardScaler()),
            ("PCA", PCA(n_components=14, random_state=1)),
            (
                "Classifier",
                MLPClassifier(
                    (400, 200),
                    "relu",
                    "sgd",
                    0.01,
                    50,
                    "adaptive",
                    0.1,
                    250,
                    random_state=0,
                    early_stopping=True,
                    n_iter_no_change=5,
                ),
            ),
        ]
    )

    classifier.fit(x, y)

    print(f"Model score: {classifier.score(x, y)}")

    filename = "../app/model.sav"
    with open(filename, "wb") as out_file:
        pickle.dump(classifier, out_file)


if __name__ == "__main__":

    main()
