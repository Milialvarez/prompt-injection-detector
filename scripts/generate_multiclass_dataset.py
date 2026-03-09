import os
import certifi
import pandas as pd

# ¡El truco de los certificados para evitar bloqueos de red!
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

def generate_robust_dataset():
    data = []
    
    # 1. Cargar prompts seguros (Clase 0)
    print("Descargando prompts seguros de Hugging Face...")
    try:
        from datasets import load_dataset
        safe_dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train[:2000]")
        for row in safe_dataset:
            text = row["text"].strip()
            if len(text) > 20: # Filtrar textos muy cortos
                data.append({"prompt": text, "label": 0, "category": "safe"})
        print("✅ Prompts seguros descargados correctamente.")
        
    except Exception as e:
        print(f"⚠️ ¡Atención! No se pudo conectar a Hugging Face: {e}")
        print("⚠️ Pasando al Plan B: Usando dataset seguro de emergencia...")
        
        # Textos seguros de respaldo por si tu internet bloquea la descarga
        textos_seguros = [
            "Explain how photosynthesis works in simple terms.",
            "Write a python script to calculate the fibonacci sequence.",
            "Summarize the plot of the movie Inception.",
            "What are the main differences between Python and JavaScript?",
            "Give me a recipe for a classic margherita pizza.",
            "How does a CPU process information?",
            "Translate 'Good morning, how are you?' to French.",
            "Create a list of 5 tips for better time management.",
            "Who was Albert Einstein and what did he discover?",
            "Describe the water cycle."
        ]
        # Multiplicamos para tener volumen (no es lo ideal para evitar overfitting, 
        # pero te desatasca si no hay internet)
        for i in range(150): 
            for text in textos_seguros:
                data.append({"prompt": f"{text} (Variante {i})", "label": 0, "category": "safe"})

    # 2. Mapear tus archivos de ataques a clases numéricas
    # Usamos os.path.join para evitar problemas de rutas en Windows
    base_dir = os.path.dirname(os.path.abspath(__file__))
    attack_folder = os.path.join(base_dir, "..", "attacks")
    
    class_map = {"safe": 0}
    current_label_id = 1
    
    print("\nProcesando archivos de ataques locales...")
    
    # Verificamos si la carpeta existe antes de intentar leerla
    if not os.path.exists(attack_folder):
        print(f"❌ ERROR: No se encontró la carpeta 'attacks' en {attack_folder}")
        return

    for filename in os.listdir(attack_folder):
        if filename.endswith(".txt"):
            category_name = filename.replace(".txt", "")
            class_map[category_name] = current_label_id
            
            filepath = os.path.join(attack_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    clean_line = line.strip()
                    if clean_line:
                        data.append({
                            "prompt": clean_line, 
                            "label": current_label_id, 
                            "category": category_name
                        })
            current_label_id += 1

    # 3. Crear el DataFrame
    df = pd.DataFrame(data)

    print("\n--- DISTRIBUCIÓN ORIGINAL ---")
    print(df['category'].value_counts())

    # --- NUEVO: BALANCEO DE CLASES (OVERSAMPLING) ---
    print("\nBalanceando el dataset para evitar overfitting a la clase 'safe'...")
    # Buscamos cuál es la clase con más ejemplos (probablemente 'safe')
    max_size = df['category'].value_counts().max()
    
    balanced_data = []
    # Agrupamos por categoría y clonamos los ejemplos hasta que todos tengan el mismo tamaño
    for class_name, group in df.groupby('category'):
        oversampled_group = group.sample(max_size, replace=True)
        balanced_data.append(oversampled_group)
        
    # Juntamos todo de nuevo y mezclamos
    df = pd.concat(balanced_data).sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\n--- DISTRIBUCIÓN BALANCEADA ---")
    print(df['category'].value_counts())
    # ------------------------------------------------

    # Guardar CSV
    dataset_folder = os.path.join(base_dir, "..", "dataset")
    os.makedirs(dataset_folder, exist_ok=True)
    
    output_path = os.path.join(dataset_folder, "prompts_multiclass.csv")
    df.to_csv(output_path, index=False)
    
    print(f"\n¡Dataset generado con éxito! Total de muestras: {len(df)}")
    print("Mapeo de clases (guarda esto para tu firewall):")
    for cat, num in class_map.items():
        print(f" - {num}: {cat}")

if __name__ == "__main__":
    generate_robust_dataset()