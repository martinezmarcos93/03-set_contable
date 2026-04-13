import subprocess

def run(cmd):
    return subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)

def merge_a_main(branch_origen):
    try:
        # 1. Asegurarse de que todo está commiteado en la branch actual
        print(f"📦 Guardando cambios en {branch_origen}...")
        run("git add .")
        try:
            run(f'git commit -m "Checkpoint final en {branch_origen} antes de merge"')
        except:
            print("✔ Nada nuevo para commitear.")

        # 2. Push de la branch por las dudas
        print(f"⬆️ Sincronizando {branch_origen} con GitHub...")
        run(f"git push -u origin {branch_origen}")

        # 3. Cambiar a main
        print("🔄 Cambiando a main...")
        run("git checkout main")

        # 4. Pull de main para estar actualizado
        print("⬇️ Actualizando main desde GitHub...")
        run("git pull origin main")

        # 5. Merge
        print(f"🔀 Mergeando {branch_origen} → main...")
        run(f"git merge {branch_origen} --no-ff -m \"Merge: {branch_origen} → main\"")

        # 6. Push de main
        print("⬆️ Subiendo main a GitHub...")
        run("git push origin main")

        print(f"\n✅ Merge exitoso. {branch_origen} está integrada en main.")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante el merge: {e}")
        print("HINT: Si hay conflictos, resolvelos en VS Code y corré 'git merge --continue'")
        raise

def borrar_branches_viejas():
    try:
        # Listar branches locales (excepto main y la actual)
        result = run("git branch")
        branches = [
            b.strip().replace("* ", "")
            for b in result.stdout.strip().split("\n")
            if b.strip() and "main" not in b
        ]

        if not branches:
            print("\n✔ No hay branches locales para borrar.")
            return

        print("\n🌿 Branches disponibles para borrar:")
        for i, b in enumerate(branches):
            print(f"  {i+1}. {b}")

        print("\n¿Cuáles querés borrar? (números separados por coma, o 'todas', o 'ninguna')")
        respuesta = input("> ").strip().lower()

        if respuesta == "ninguna":
            print("✔ No se borró nada.")
            return

        if respuesta == "todas":
            seleccion = branches
        else:
            indices = [int(x.strip()) - 1 for x in respuesta.split(",")]
            seleccion = [branches[i] for i in indices]

        for branch in seleccion:
            print(f"🗑️ Borrando local: {branch}")
            run(f"git branch -d {branch}")

            print(f"🗑️ Borrando remota: origin/{branch}")
            try:
                run(f"git push origin --delete {branch}")
            except:
                print(f"  ⚠️ No se pudo borrar origin/{branch} (puede que ya no exista en GitHub)")

        print("\n✅ Limpieza completada.")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al borrar branches: {e}")

if __name__ == "__main__":
    print("=== MERGE A MAIN ===\n")
    branch = input("Branch a mergear en main (Enter para 'nuevo_menu_y_sistema_final'): ").strip()
    if not branch:
        branch = "nuevo_menu_y_sistema_final"

    merge_a_main(branch)
    borrar_branches_viejas()
