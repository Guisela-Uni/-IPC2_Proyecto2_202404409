import xml.etree.ElementTree as ET
from ListaSimple import ListaSimple

def leer_configuracion(ruta_xml):
    tree = ET.parse(ruta_xml)
    root = tree.getroot()

    drones = ListaSimple()
    invernaderos = ListaSimple()

    # Leer listaDrones
    for dron in root.find('listaDrones'):
        datos_dron = {
            'id': int(dron.attrib['id']),
            'nombre': dron.attrib['nombre']
        }
        drones.agregar(datos_dron)

    # Leer listaInvernaderos
    for inv in root.find('listaInvernaderos'):
        datos_inv = {
            'nombre': inv.attrib['nombre'],
            'numero_Hileras': int(inv.find('numero_Hileras').text),
            'Plantas_por_Hilera': int(inv.find('Plantas_por_Hilera').text),
            'plantas': ListaSimple(),
            'asignaciones': ListaSimple(),
            'planes': ListaSimple()
        }

        # Leer listaPlantas
        for planta in inv.find('listaPlantas'):
            datos_planta = {
                'hilera': int(planta.attrib['hilera']),
                'posicion': int(planta.attrib['posicion']),
                'litrosAgua': int(planta.attrib['litrosAgua']),
                'gramosFertilizante': int(planta.attrib['gramosFertilizante']),
                'tipo': planta.text.strip()
            }
            datos_inv['plantas'].agregar(datos_planta)

        # Leer asignacionDrones
        for asignacion in inv.find('asignacionDrones'):
            datos_asignacion = {
                'id': int(asignacion.attrib['id']),
                'hilera': int(asignacion.attrib['hilera'])
            }
            datos_inv['asignaciones'].agregar(datos_asignacion)

        # Leer planesRiego
        for plan in inv.find('planesRiego'):
            datos_plan = {
                'nombre': plan.attrib['nombre'],
                'acciones': plan.text.strip()
            }
            datos_inv['planes'].agregar(datos_plan)

        invernaderos.agregar(datos_inv)

    return drones, invernaderos