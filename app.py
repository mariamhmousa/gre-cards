from flask import Flask, render_template, request, redirect, url_for
from db import init_db, get_due_cards, add_card, get_card, DEFAULT_DB_PATH
from review import review
from wtforms import Form, StringField, TextAreaField, validators

init_db()

app = Flask(__name__)

@app.route("/")
def home():
    cards = get_due_cards()
    # if there are no cards, return a message instead
    if not cards:
        return "All done, take a break!"
    # otherwise, take the first card and unpack it
    card_id, word, definition, example, _, _, _ = cards[0]
    show = request.args.get("show") == "1"
    # pass its word and definition to the template
    return render_template("card.html", word=word, definition=definition, example=example, card_id=card_id, show=show)

@app.route("/review", methods=["POST"])
def review_route():
    card_id = int(request.form["card_id"])
    rating = int(request.form["rating"])
    if rating not in [1, 3, 4, 5]:
        return "Rating has to be 1, 3, 4, or 5!"

    card = get_card(card_id, DEFAULT_DB_PATH)
    
    if card is None:
        return "404: card doesn't exist!"
    
    review(card, rating, DEFAULT_DB_PATH)
    return redirect(url_for("home"))

class CardAdditionForm(Form):
    word = StringField('Word', [validators.DataRequired()],
                       filters=[lambda s: s.strip() if s else s])
    definition = TextAreaField('Definition', [validators.DataRequired()],
                               filters=[lambda s: s.strip() if s else s])
    example = TextAreaField('Example sentence',
                            [validators.Length(max=100, message="Example must be 100 characters or fewer.")],
                            filters=[lambda s: s.strip() if s else s])
@app.route("/add", methods=["GET", "POST"])
def add_route():
    form = CardAdditionForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            add_card(form.word.data, form.definition.data, form.example.data)
        except sqlite3.IntegrityException:
            form.word.errors = list(form.word.errors) + ["This word already exists!"]
        else:
            return redirect(url_for("add_route"))
    return render_template("add.html", form=form)