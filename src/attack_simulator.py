import os
from firewall import analyze_prompt

def load_attacks(folder):

    prompts = []

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8") as f:

            lines = f.readlines()

            for line in lines:

                line = line.strip()

                if line:
                    prompts.append(line)

    return prompts

def run_simulation():

    attack_prompts = load_attacks("attacks")

    total = len(attack_prompts)

    detected = 0
    bypassed = 0

    for prompt in attack_prompts:

        score, decision = analyze_prompt(prompt)

        print(f"{score:.3f} -> {decision} | {prompt}")

        if decision in ["BLOCK", "FLAG"]:
            detected += 1
        else:
            bypassed += 1

    print("\n--- Attack Simulation Results ---")

    print("Total attacks tested:", total)
    print("Detected attacks:", detected)
    print("Bypassed attacks:", bypassed)

    detection_rate = detected / total

    print("Detection rate:", round(detection_rate, 2))

if __name__ == "__main__":

    run_simulation()