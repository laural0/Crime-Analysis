import matplotlib.pyplot as plt
import seaborn as sns

def find_outliers_iqr_all(df, col):
    """
    Funcție care calculează limitele inferioare și superioare folosind metoda IQR pentru o coloană numerică
    și returnează valorile limite și un DataFrame cu outlierii respectivi.
    """
    Q1 = df[col].quantile(0.25)       # Calculăm Quartila 1
    Q3 = df[col].quantile(0.75)       # Calculăm Quartila 3
    IQR = Q3 - Q1                   # Intervalul intercuartilic
    lower_bound = Q1 - 1.5 * IQR      # Limita inferioară
    upper_bound = Q3 + 1.5 * IQR      # Limita superioară
    outliers_df = df[(df[col] < lower_bound) | (df[col] > upper_bound)]  # Selectăm valorile care ies din interval
    return lower_bound, upper_bound, outliers_df


def find_outliers_iqr_df_only(df, col):
    """
    Identifică outlierii într-o coloană numerică folosind Metoda IQR.
    Returnează un DataFrame cu outlierii respectivi.
    """
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers_df = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    return outliers_df


def plot_pairplot_numeric(df, numeric_cols):
    """
    Creează un pairplot pentru variabilele numerice.
    - diag_kind='kde' -> pe diagonală se afișează grafic de densitate
    - corner=True -> afișează doar jumătate din matrice (opțional)
    """
    sns.pairplot(df[numeric_cols], diag_kind='kde')
    plt.suptitle("Pairplot pentru variabilele numerice", y=1.02)
    plt.show()

