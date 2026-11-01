import pytest

TECLADO = {"nombre": "Teclado", "precio": 25000, "stock": 10}

@pytest.mark.parametrize("precio, esperado", [(0, 422), (1, 201)])
def test_precio_en_el_limite(client, precio, esperado):
    r = client.post("/productos", json={**TECLADO, "precio": precio})
    assert r.status_code == esperado

def test_health(client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").json() == {"status": "ready"}


def test_crear_y_obtener(client):
    r = client.post("/productos", json=TECLADO)
    assert r.status_code == 201
    producto_id = r.json()["id"]

    r = client.get(f"/productos/{producto_id}")
    assert r.status_code == 200
    assert r.json()["nombre"] == "Teclado"


def test_precio_negativo_es_422(client):
    r = client.post("/productos", json={**TECLADO, "precio": -5})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["body", "precio"]


def test_nombre_duplicado_es_409(client):
    client.post("/productos", json=TECLADO)
    assert client.post("/productos", json=TECLADO).status_code == 409


def test_actualizar(client):
    producto_id = client.post("/productos", json=TECLADO).json()["id"]
    r = client.put(f"/productos/{producto_id}", json={**TECLADO, "precio": 30000})
    assert r.json()["precio"] == 30000


def test_eliminar_y_luego_404(client):
    producto_id = client.post("/productos", json=TECLADO).json()["id"]
    assert client.delete(f"/productos/{producto_id}").status_code == 204
    assert client.get(f"/productos/{producto_id}").status_code == 404