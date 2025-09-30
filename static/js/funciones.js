//aqui sube el archivo xml
function subirArchivo() {
    console.warn('Uso actual: utilice el botón de submit del formulario para subir el archivo.');
}
//selecciona el invernadero
function seleccionarInvernadero(nombre) {
    console.log('Seleccionar invernadero (noop):', nombre);
}

document.addEventListener('DOMContentLoaded', function () {
    const invernaderoSelect = document.getElementById('invernadero');
    const riegoSelect = document.getElementById('riego');
    if (!invernaderoSelect || !riegoSelect) return;

    async function actualizarPlanes(nombre) {
        const filenameInput = document.querySelector('input[name="archivo_nombre"]');
        const filename = (filenameInput && filenameInput.value) || window.uploadedFilename || null;
        if (!filename) {
            console.warn('No se encontró filename en el DOM para solicitar planes.');
            return;
        }

        try {
            const res = await fetch('/obtener_planes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ invernadero: nombre, filename: filename })
            });
            if (!res.ok) {
                console.error('Error al solicitar planes:', res.status);
                return;
            }
            const data = await res.json();
            riegoSelect.innerHTML = '';
            (data.planes || []).forEach(plan => {
                const option = document.createElement('option');
                option.value = plan;
                option.textContent = plan;
                riegoSelect.appendChild(option);
            });
        } catch (err) {
            console.error('Error en fetch obtener_planes:', err);
        }
    }

    invernaderoSelect.addEventListener('change', function () {
        const nombre = invernaderoSelect.value;
        if (nombre) actualizarPlanes(nombre);
    });

    if (invernaderoSelect.value) {
        actualizarPlanes(invernaderoSelect.value);
    }
});
