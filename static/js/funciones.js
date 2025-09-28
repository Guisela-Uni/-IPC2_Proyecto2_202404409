function subirArchivo() {
    const archivo = document.getElementById('fileXML').files[0];
    console.log("Archivo seleccionado:", archivo); // Verifica que no sea undefined

    if (!archivo) {
        alert("Por favor selecciona un archivo XML.");
        return;
    }

    const formData = new FormData();
    formData.append('archivo', archivo);

    fetch('/procesar_xml', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        console.log("Respuesta del servidor:", data); // verifica la respuesta del servidor
        if (data.invernaderos) {
                const contenedor = document.getElementById('listaInvernaderos');
                const invernaderoSelect = document.getElementById('invernadero');
                contenedor.innerHTML = '<h3>Invernaderos cargados:</h3>';
                // Si existe un <select id="invernadero"> en la plantilla, lo rellenamos
                if (invernaderoSelect) {
                    invernaderoSelect.innerHTML = '';
                    data.invernaderos.forEach(nombre => {
                        const opt = document.createElement('option');
                        opt.value = nombre;
                        opt.textContent = nombre;
                        invernaderoSelect.appendChild(opt);
                    });
                }
                // Mostrar botones para selección si el contenedor existe
                data.invernaderos.forEach(nombre => {
                    const btn = document.createElement('button');
                    btn.textContent = nombre;
                    btn.onclick = () => seleccionarInvernadero(nombre);
                    contenedor.appendChild(btn);
                });
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error("Error en fetch:", error);
    });
}

function seleccionarInvernadero(nombre) {
    fetch('/seleccionar_invernadero', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({nombre})
    })
    .then(res => res.json())
    .then(data => {
        const el = document.getElementById('mensajeSeleccion') || document.getElementById('mensaje1Seleccion');
        if (el) el.textContent = data.mensaje;
    });
}

document.addEventListener('DOMContentLoaded', function () {
  const invernaderoSelect = document.getElementById('invernadero');
  const riegoSelect = document.getElementById('riego');

  invernaderoSelect.addEventListener('change', function () {
    const nombre = invernaderoSelect.value;
    // Enviar también el nombre del archivo subido para que el servidor pueda cargarlo
    const filename = window.uploadedFilename || document.getElementById('fileXML')?.files?.[0]?.name;
    fetch('/obtener_planes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ invernadero: nombre, filename: filename })
    })
    .then(response => response.json())
    .then(data => {
        riegoSelect.innerHTML = '';
        (data.planes || []).forEach(plan => {
            const option = document.createElement('option');
            option.value = plan;
            option.textContent = plan;
            riegoSelect.appendChild(option);
        });
    });
    });
});