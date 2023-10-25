from flask import Flask, render_template
from radio import available_radios
from spotify import SpotifySong

radios = available_radios()
radio_indices = {radio.name: n for n, radio in enumerate(radios)}

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", radios=radios)


@app.route("/radio/<string:radio_name>", methods=["GET"])
def update_data(radio_name):
    radio = radios[radio_indices[radio_name]]
    radio.fetch()

    return render_template("song.html", radio_name=radio_name, song=radio.current_song)


if __name__ == "__main__":
    app.run()
