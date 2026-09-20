"""EasyFood — API com consulta e cadastro (Sprint 02).

GET e POST /restaurants com armazenamento em memória.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

restaurants = [
    {"id": 1, "name": "Pizzaria Napoli", "category": "Pizza", "rating": 4.8},
    {"id": 2, "name": "Burger House", "category": "Burger", "rating": 4.7},
    {"id": 3, "name": "Sushi House", "category": "Sushi", "rating": 4.9},
]
_next_id = 4


@app.get("/restaurants")
def list_restaurants():
    return jsonify(restaurants)


@app.post("/restaurants")
def create_restaurant():
    global _next_id
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    category = data.get("category")
    rating = data.get("rating", 0)

    if not name or not category:
        return jsonify({"error": "Nome e categoria são obrigatórios"}), 400

    restaurant = {
        "id": _next_id,
        "name": name,
        "category": category,
        "rating": rating,
    }
    _next_id += 1
    restaurants.append(restaurant)
    return jsonify(restaurant), 201


if __name__ == "__main__":
    print("EasyFood rodando na porta 3000")
    app.run(host="0.0.0.0", port=3000, debug=True)
