import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier


def plot_decision_boundary(ax, X, model):
    h = .02  # step size in the mesh
    # create a mesh to plot in
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))


    # Plot the decision boundary. For that, we will assign a color to each
    # point in the mesh [x_min, m_max]x[y_min, y_max].
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    ax.contour(xx, yy, Z, cmap=plt.cm.Paired)


class BaggedTreeRegressor:
    def __init__(self, n_estimators):
        '''
        @param B(int):
            Sampling time
        '''
        self.B = n_estimators

    def fit(self, X, Y):
        N = len(X)
        self.models = []
        for b in range(self.B):
            idx = np.random.choice(N, size=N, replace=True)
            Xb = X[idx]
            Yb = Y[idx]

            model = DecisionTreeRegressor()
            model.fit(Xb, Yb)
            self.models.append(model)

    def predict(self, X):
        predictions = np.zeros(len(X))
        for model in self.models:
            predictions += model.predict(X)
            
        return predictions / self.B

    def score(self, X, Y):
        d1 = Y - self.predict(X)
        d2 = Y - Y.mean()
        return 1 - d1.dot(d1) / d2.dot(d2)


class BaggedTreeClassifier:
    def __init__(self, n_estimators, max_depth=2):
        r'''
        @param B:
            Number of sampling in building bagged dt classifier
        @param max_depth:
            Hyperparameter `max_depth` of DecisionTreeClassifier
        '''
        self.B = n_estimators
        self.max_depth = max_depth

    def fit(self, X, Y):
        N = len(X)
        self.models = []
        for b in range(self.B):
            idx = np.random.choice(N, size=N, replace=True)
            Xb = X[idx]
            Yb = Y[idx]

            model = DecisionTreeClassifier(max_depth=self.max_depth)
            model.fit(Xb, Yb)
            self.models.append(model)

    def predict(self, X):
        # no need to keep a dictionary since we are doing binary classification
        predictions = np.zeros(len(X))
        for model in self.models:
            predictions += model.predict(X)
        return np.round(predictions / self.B)

    def score(self, X, Y):
        P = self.predict(X)
        return np.mean(Y == P)


def replace_missing(df):
    # standard method of replacement for numerical columns is median
    for col in NUMERICAL_COLS:
        if np.any(df[col].isnull()):
            med = np.median(df[ col ][ df[col].notnull() ])
            df.loc[ df[col].isnull(), col ] = med

    # set a special value = 'missing'
    for col in CATEGORICAL_COLS:
        if np.any(df[col].isnull()):
            print(col)
            df.loc[ df[col].isnull(), col ] = 'missing'
            

def get_mushroom_data():
    df = pd.read_csv('datas/agaricus-lepiota.data', header=None)

    # replace label column: e/p --> 0/1
    # e = edible = 0, p = poisonous = 1
    df[0] = df.apply(lambda row: 0 if row[0] == 'e' else 1, axis=1)

    # check if there is missing data
    replace_missing(df)

    # transform the data
    transformer = DataTransformer()

    X = transformer.fit_transform(df)
    Y = df[0].values
    return X, Y
