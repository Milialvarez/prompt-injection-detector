import os
import pandas as pd
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: No se encontraron las credenciales de Supabase.")
    exit(1)

supabase: Client = create_client(url, key)

def fetch_new_data():
    print("Buscando nuevos prompts validados y sin entrenar...")
    response = supabase.table("prompt_logs")\
        .select("*")\
        .eq("is_reviewed", True)\
        .eq("is_trained", False)\
        .execute()
    return response.data

def main():
    nuevos_datos = fetch_new_data()
    
    if not nuevos_datos:
        print("No hay datos nuevos para entrenar hoy. Saliendo...")
        return
        
    print(f"Se encontraron {len(nuevos_datos)} prompts nuevos. Actualizando dataset...")
    
    df_nuevos = pd.DataFrame(nuevos_datos)
    df_nuevos = df_nuevos[["id", "prompt_text", "human_label"]].copy()
    df_nuevos = df_nuevos.rename(columns={"prompt_text": "prompt", "human_label": "category"})
    
    LABEL_MAP = {
        "safe": 0,
        "data_exfiltration": 1,
        "jailbreak": 2,
        "obfuscation": 3,
        "prompt_injection": 4
    }
    
    df_nuevos["label"] = df_nuevos["category"].map(LABEL_MAP)
    
    df_nuevos = df_nuevos.dropna(subset=["label"])
    df_nuevos["label"] = df_nuevos["label"].astype(int) 
    ruta_dataset = "dataset/prompts_multiclass.csv" 
    df_old = pd.read_csv(ruta_dataset)

    df_nuevos_filtrados = df_nuevos[~df_nuevos['prompt'].isin(df_old['prompt'])]
    df_combined = pd.concat([df_old, df_nuevos_filtrados[["prompt", "label", "category"]]], ignore_index=True)
    
    df_combined.to_csv(ruta_dataset, index=False)
    print(f"Dataset actualizado. Total de filas ahora: {len(df_combined)}.")
    
    print("Iniciando el horno (entrenamiento)...")
    
    codigo_salida = os.system("python src/train.py") 
    
    if codigo_salida != 0:
        print("Hubo un error durante el entrenamiento. Abortando.")
        exit(1)
    
    print("Entrenamiento exitoso. Marcando registros en Supabase...")
    for row in nuevos_datos:
        supabase.table("prompt_logs").update({"is_trained": True}).eq("id", row['id']).execute()
        
    print("¡Todo el proceso de actualización ha finalizado con éxito!")

if __name__ == "__main__":
    main()