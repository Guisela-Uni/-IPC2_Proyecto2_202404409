from Invernadero_Clases import PlanRiego
import os

def generar_dot_plan(plan: PlanRiego, nombre_archivo: str):
    acciones = plan.acciones.split(",")
    acciones = [a.strip() for a in acciones if a.strip()]

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("digraph PlanRiego {\n")
        f.write(f'  label="{plan.nombre}"; labelloc="t"; fontsize=20;\n')
        f.write("  node [shape=box, style=filled, color=lightblue];\n")

        for i in range(len(acciones) - 1):
            f.write(f'  "{acciones[i]}" -> "{acciones[i+1]}";\n')

        f.write("}\n")

def generar_imagen_dot(nombre_dot, nombre_png):
    os.system(f'dot -Tpng {nombre_dot} -o {nombre_png}')