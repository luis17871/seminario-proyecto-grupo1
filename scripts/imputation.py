 #%%
import os
import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer

# -------------------------------------------------------------
# Función para imputar datos
# -------------------------------------------------------------
def imputar_datos(df):
    # 1️⃣ Imputación para columnas numéricas
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    imputer_num = SimpleImputer(strategy='mean')
    df[num_cols] = imputer_num.fit_transform(df[num_cols])
    
    # 2️⃣ Imputación para columnas categóricas (texto)
    cat_cols = df.select_dtypes(include=['object']).columns
    imputer_cat = SimpleImputer(strategy='most_frequent')
    df[cat_cols] = imputer_cat.fit_transform(df[cat_cols])
    
    return df

# -------------------------------------------------------------
# Flujo principal
# -------------------------------------------------------------
if __name__ == "__main__":
    print("Visualizando valores nulos antes y después de la imputación...")

    # 📁 Ruta automática que funciona desde cualquier ubicación
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base_dir, "..", "data", "Retail.csv")
    ruta = os.path.normpath(ruta)

    # ✅ Verifica si el archivo existe
    if not os.path.exists(ruta):
        print(f"❌ No se encontró el archivo en: {ruta}")
    else:
        print(f"✅ Archivo encontrado en: {ruta}")

        # Cargar CSV
        df = pd.read_csv(ruta)

        # Visualización antes de imputar
        plt.figure()
        msno.matrix(df)
        plt.title("Antes de imputar")
        plt.show()

        # Imputar los datos
        df_imputado = imputar_datos(df)

        # Visualización después de imputar
        plt.figure()
        msno.matrix(df_imputado)
        plt.title("Después de imputar")
        plt.show()

        # Guardar resultado en la misma carpeta data/
        salida = os.path.join(base_dir, "..", "data", "Retail_imputed.csv")
        df_imputado.to_csv(salida, index=False)
        print(f"✅ Archivo imputado guardado como: {salida}")
