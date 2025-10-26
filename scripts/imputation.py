import pandas as pd
from sklearn.impute import SimpleImputer

def imputar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza imputación de valores faltantes sobre un DataFrame ya cargado.
    - Reemplaza valores nulos en columnas numéricas con la media.
    - Reemplaza valores nulos en columnas categóricas con el valor más frecuente.
    """

    # Mensaje inicial para saber que el proceso de imputación comenzó
    print("[INFO] Iniciando imputación de valores faltantes...")

    # IDENTIFICAR Y COMPLETAR COLUMNAS NUMÉRICAS
    # df.select_dtypes() filtra las columnas del DataFrame según su tipo de dato
    # 'int64' y 'float64' son tipos numéricos (enteros y decimales)
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns

    # Si hay al menos una columna numérica...
    if len(num_cols) > 0:
        # SimpleImputer(strategy='mean') crea un "rellenador" que usará la media
        # de cada columna para completar los valores faltantes (NaN)
        imputer_num = SimpleImputer(strategy='mean')

        # .fit_transform() entrena el imputador y reemplaza los valores faltantes
        # df[num_cols] se actualiza con los valores ya corregidos
        df[num_cols] = imputer_num.fit_transform(df[num_cols])

        # Muestra en pantalla las columnas que fueron imputadas
        print(f"[OK] Imputadas columnas numéricas: {list(num_cols)}")

    # IDENTIFICAR Y COMPLETAR COLUMNAS CATEGÓRICAS (de texto)
    # De nuevo usamos .select_dtypes(), pero esta vez para buscar columnas de texto
    # En pandas, las columnas de texto suelen ser del tipo 'object'
    cat_cols = df.select_dtypes(include=['object']).columns

    if len(cat_cols) > 0:
        # SimpleImputer con 'most_frequent' usa el valor más común (moda)
        # para completar los datos faltantes en las columnas de texto
        imputer_cat = SimpleImputer(strategy='most_frequent')

        # Se aplica la imputación a las columnas categóricas
        df[cat_cols] = imputer_cat.fit_transform(df[cat_cols])

        # Mensaje para confirmar que se imputaron correctamente
        print(f"[OK] Imputadas columnas categóricas: {list(cat_cols)}")

    # FINALIZACIÓN
    # Mensaje final para confirmar que todo el proceso fue exitoso
    print("[OK] Imputación completada correctamente.\n")

    # Retorna (devuelve) el DataFrame ya limpio y sin valores nulos
    return df
