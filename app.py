import os
import json
import requests
from flask_cors import CORS
from bs4 import BeautifulSoup
from flask import Flask, jsonify, g

app = Flask(__name__)
CORS(app)

__url__ = "http://www.resultadosmegasena.com.br/resultados-anteriores"


@app.before_request
def scrapy_data():
    html_doc = requests.get(__url__)
    g.soup = BeautifulSoup(html_doc.text, "html.parser")


@app.route("/api/v1/numbers", methods=["GET"])
def return_all_numbers():
    data = []

    for dataBox in g.soup.find_all("tr", class_="rstable_td"):
        itens = dataBox.find_all("td")
        date = itens[0].text.strip()
        info = itens[1].text.strip().split("\t\t\t\t\t\t")
        concurse = info[0].replace("\n", "").strip()
        winners = info[1].replace("Ganhadores:", "").strip()
        value = info[2].replace("Prêmio:", "").strip()
        numbers = [item.text for item in itens[2].find_all("div")]

        data.append(
            {
                "date": date,
                "concurse": concurse,
                "winners": winners,
                "value": value,
                "numbers": numbers,
            }
        )

    return jsonify({"results": data})


@app.route("/api/v1/bestnumbers", methods=["GET"])
def return_best_numbers():
    object_list = {}
    number_list = final_list = []

    for dataBox in g.soup.find_all("tr", class_="rstable_td"):
        itens = dataBox.find_all("td")
        number = [int(item.text) for item in itens[2].find_all("div")]
        number_list.extend(number)

    object_list.update({str(item): number_list.count(item) for item in range(1, 60)})
    sorted_list = sorted(object_list.items(), key=lambda item: item[1], reverse=True)
    final_list = [sorted_list[i][0] for i in range(0, 6)]

    return jsonify({"results": final_list})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
