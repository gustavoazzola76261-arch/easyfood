"""EasyFood — API inicial (Sprint 01).

Primeira versão: consulta de restaurantes em memória.
"""

from flask import Flask, jsonify

app = Flask(__name__)

restaurants = [
    {"id": 1, "name": "Pizzaria Napoli", "category": "Pizza", "rating": 4.8},
    {"id": 2, "name": "Burger House", "category": "Burger", "rating": 4.7},
    {"id": 3, "name": "Sushi House", "category": "Sushi", "rating": 4.9},
]


@app.get("/restaurants")
def list_restaurants():
    return jsonify(restaurants)


if __name__ == "__main__":
    print("EasyFood rodando na porta 3000")
    app.run(host="0.0.0.0", port=3000, debug=True)
