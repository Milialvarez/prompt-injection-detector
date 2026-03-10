import pandas as pd

df_old = pd.read_csv("../dataset/prompts_multiclass.csv")
print(f"Dataset original: {len(df_old)} filas.")

# 2. Cargar los datos nuevos exportados de Supabase
df_new = pd.read_csv("../dataset/prompt_logs_rows.csv")

# 3. Filtrar y limpiar los datos nuevos
# Nos quedamos solo con los que revisaste y que tienen una etiqueta humana válida
df_new_clean = df_new[(df_new["is_reviewed"] == True) & (df_new["human_label"].notna())].copy()

# Renombrar las columnas de Supabase para que coincidan con tu dataset original
df_new_clean = df_new_clean.rename(columns={
    "prompt_text": "prompt",
    "human_label": "category"
})

# Seleccionar solo las columnas que importan
df_new_clean = df_new_clean[["prompt", "category"]]
print(f"Nuevos prompts validados a inyectar: {len(df_new_clean)} filas.")

# 4. Unir ambos datasets
df_combined = pd.concat([df_old, df_new_clean], ignore_index=True)

# Eliminar posibles duplicados (por si alguien envió el mismo ataque dos veces)
df_combined = df_combined.drop_duplicates(subset=["prompt"])

# 5. Guardar la Versión 2.0 del dataset
df_combined.to_csv("../dataset/prompts_multiclass_v2.csv", index=False)
print(f"¡Éxito! Dataset V2 guardado con {len(df_combined)} filas en total.")