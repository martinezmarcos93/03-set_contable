import subprocess

def run(cmd):
    return subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)

def obtener_branch_actual():
    result = run("git branch --show-current")
    return result.stdout.strip()

def subir_a_github():
    try:
        # 🔍 Detectar branch actual
        branch = obtener_branch_actual()
        print(f"🌿 Branch actual detectada: {branch}")

        # 1. Preparar commit
        print("📦 Preparando archivos...")
        run("git add .")

        try:
            run(f'git commit -m "Sync en {branch}"')
        except:
            print("✔ Nada nuevo para commit.")

        # 2. Pull sobre la MISMA branch
        print(f"🔄 Sincronizando con GitHub ({branch})...")
        run(f"git pull origin {branch} --rebase")

        # 3. Push a la MISMA branch
        print(f"⬆️ Subiendo a GitHub ({branch})...")
        run(f"git push -u origin {branch}")

        print(f"\n✅ Todo actualizado en la branch: {branch}")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error de Git: {e}")
        print("HINT: Si hay conflictos, resolvelos manualmente y volvé a correr el script.")

if __name__ == "__main__":
    subir_a_github()