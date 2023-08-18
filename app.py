from flask import Flask, flash, request, redirect, url_for, render_template
from dotenv import load_dotenv
import db
import datetime
import plotly.graph_objs as go
from twitter_scraper import scrape_user_data

load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        name = request.form.get("name")
        scrape_user_data(f"@{name}")
        return redirect(url_for("user"))

    return render_template("index.html")


@app.route("/user/<user_name>/<user_id>")
def user_id_query(user_name, user_id):
    db_tweet = db.tweet()
    all_tweets = db_tweet.get_all_tweets(user_id)
    temp_date = []
    temp_replies = []
    temp_retweets = []
    temp_likes = []
    temp_views = []
    for i in range(len(all_tweets)):
        curr_tweet = all_tweets[i]
        pg_datetime = curr_tweet[-1]
        # Convert to a specific timezone, for example, UTC
        utc_datetime = pg_datetime.astimezone(datetime.timezone.utc)

        # Preserve the same time and date but without a specific timezone
        regular_datetime = utc_datetime.replace(tzinfo=None).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        # curr_tweet[-1] = regular_datetime
        temp_date.append(regular_datetime)
        temp_replies.append(curr_tweet[2])
        temp_retweets.append(curr_tweet[3])
        temp_likes.append(curr_tweet[4])
        temp_views.append(curr_tweet[5] if curr_tweet[5] is not None else 0)

    trace1 = go.Scatter(
        x=temp_date,
        y=temp_replies,
        mode="lines+markers",
        name="reply",
        line=dict(color="blue"),
    )
    trace2 = go.Scatter(
        x=temp_date,
        y=temp_retweets,
        mode="lines+markers",
        name="retweet",
        line=dict(color="red"),
    )
    trace3 = go.Scatter(
        x=temp_date,
        y=temp_likes,
        mode="lines+markers",
        name="like",
        line=dict(color="green"),
    )
    trace4 = go.Scatter(
        x=temp_date,
        y=temp_views,
        mode="lines+markers",
        name="view",
        line=dict(color="purple"),
    )

    layout = go.Layout(
        title="Summary Chart with Time",
        xaxis=dict(type="category"),
        yaxis=dict(title="Values"),
    )
    layout_1 = go.Layout(
        title="Reply Chart with Time",
        xaxis=dict(type="category"),
        yaxis=dict(title="Number of Replies"),
    )
    layout_2 = go.Layout(
        title="Retweet Chart with Time",
        xaxis=dict(type="category"),
        yaxis=dict(title="Number of Reweets"),
    )
    layout_3 = go.Layout(
        title="Like Chart",
        xaxis=dict(type="category"),
        yaxis=dict(title="Number of Likes"),
    )
    layout_4 = go.Layout(
        title="View Chart with Time",
        xaxis=dict(
            type="category",
            tickformat="%Y-%m-%d %H:%M",  # Custom date format
            #   dtick='M1',                  # Tick interval (every month)
            tickangle=-45,  # Rotate tick labels
        ),
        yaxis=dict(title="Number of Views"),
    )

    fig = go.Figure(data=[trace1, trace2, trace3, trace4], layout=layout)
    fig_1 = go.Figure(data=[trace1], layout=layout_1)
    fig_2 = go.Figure(data=[trace2], layout=layout_2)
    fig_3 = go.Figure(data=[trace3], layout=layout_3)
    fig_4 = go.Figure(data=[trace4], layout=layout_4)

    graph_json = fig.to_json()
    graph_json_1 = fig_1.to_json()
    graph_json_2 = fig_2.to_json()
    graph_json_3 = fig_3.to_json()
    graph_json_4 = fig_4.to_json()

    # return render_template('user_plot.html', graphJSON=graph_json, graphJSON_1=graph_json_1, graphJSON_2=graph_json_2, graphJSON_3=graph_json_3, graphJSON_4=graph_json_4)
    return render_template(
        "user_plot.html",
        graphJSONs=[graph_json, graph_json_1, graph_json_2, graph_json_3, graph_json_4],
    )
    # return f"{temp_date}, {temp_replies}"


@app.route("/user/", methods=["GET", "POST"])
def user():
    db_user = db.user()
    total_users = db_user.get_all_users()
    user_table = {}
    for id, name in total_users:
        user_table[str(id)] = name
    # print(total_users)
    if request.method == "POST":
        user_id = request.form.get("selected-user")
        return redirect(
            url_for("user_id_query", user_name=user_table[user_id], user_id=user_id)
        )
        # return redirect(url_for('player_id_query', player_id = player_id))
    return render_template("users_query.html", total_users=total_users)
