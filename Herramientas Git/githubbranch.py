import subprocess

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def crear_branch_y_subir(nombre_branch):
    try:
        print("📦 Preparando archivos...")
        run("git add .")

        try:
            run(f'git commit -m "Checkpoint antes de nueva rama: {nombre_branch}"')
        except:
            print("✔ Nada nuevo para commitear.")

        print(f"🌿 Creando y cambiando a la branch: {nombre_branch}")
        run(f"git checkout -b {nombre_branch}")

        print("⬆️ Subiendo branch a GitHub...")
        run(f"git push -u origin {nombre_branch}")

        print(f"\n✅ Listo. Ahora estás trabajando en la branch: {nombre_branch}")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error de Git: {e}")
        print("HINT: Puede que la branch ya exista o haya conflictos.")

if __name__ == "__main__":
    nombre = input("Nombre de la nueva branch: ")
    crear_branch_y_subir(nombre)