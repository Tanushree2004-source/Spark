from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load datasets (filenames in repo are singular)
products = pd.read_csv("product.csv")
purchases = pd.read_csv("purchase.csv")

def recommend_products(user_id):
    # Get product IDs user already purchased
    user_items = purchases[purchases["user_id"] == user_id]["product_id"].tolist()

    # Find similar users who bought the same things
    similar_users = purchases[purchases["product_id"].isin(user_items)]["user_id"].unique()

    # Recommend products they've bought but user has NOT
    recommended_ids = purchases[
        purchases["user_id"].isin(similar_users) & ~purchases["product_id"].isin(user_items)
    ]["product_id"].value_counts().index.tolist()

    # Fallback: if no similar-user recs, pick globally popular items the user does not own
    if not recommended_ids:
        global_popular = (
            purchases[~purchases["product_id"].isin(user_items)]["product_id"]
            .value_counts()
            .index.tolist()
        )
        recommended_ids = global_popular

    purchased_products = products[products["product_id"].isin(user_items)]["product_name"].tolist()
    recommended_products = products[products["product_id"].isin(recommended_ids)]["product_name"].tolist()

    return purchased_products, recommended_products


@app.route("/")
def home():
    users = sorted(purchases["user_id"].unique())
    stats = {
        "total_products": len(products),
        "total_users": purchases["user_id"].nunique(),
        "total_purchases": len(purchases),
    }
    categories = sorted(products["category"].unique())
    return render_template("index.html", users=users, stats=stats, categories=categories)


@app.route("/recommend", methods=["POST"])
def recommend():
    user_id = int(request.form["user"])
    purchased, recommended = recommend_products(user_id)
    return render_template("recommend.html", user=user_id, purchased=purchased, recommended=recommended)


if __name__ == "__main__":
    app.run(debug=True)
