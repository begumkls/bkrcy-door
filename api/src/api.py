import auth
from json import dumps, loads
from db import rd
from app import (
    app,
    request,
    asgi_app,
    login_required,
    flash,
    redirect,
    url_for,
    get_flashed_messages,
    render_template,
    render_template_string,
    Markup,
)
from error import Error


@app.route("/")
def home():
    go_to_login_page_button = "<a href='/login'>Go to login page</a>"
    return f"<h1>usage: /user, /user/{{uid}}, /login</h1>{go_to_login_page_button}"


@app.route("/user")
@login_required
def user():
    flash_messages_html = render_template("flash.html")
    flash_messages_html += "".join(
        [
            f'<div class="alert">{message}<span class="closebtn" onclick="closeFlashMessage(event)">&times;</span></div>'
            for message in get_flashed_messages()
        ]
    )
    page = ""
    for door in rd.smembers("doors"):
        page += (
            f'<div class="checkbox-container">'
            f'<label for="{door}">'
            f'<input type="checkbox" name="door_access" value="{door}">{door}'
            f"</label>"
            f"</div>\n"
        )
    page = Markup(page)

    return render_template(
        "user_form.html", doors=page, flash_messages=flash_messages_html
    )


@app.route("/user/<uid>")
def get_user(uid):
    id = f"user:{uid}"
    if rd.exists(id):
        data = rd.hgetall(id)
        data["doors"] = loads(data["doors"])
        return data
    raise Error(f"User {uid} not found")


@app.route("/user", methods=["POST"])
@login_required
def post_user():
    data = request.form
    if rd.exists(f"user:{data['uid']}"):
        flash("User already exists", "error")
        return redirect(url_for("user"))

    rd.hset(
        name=f"user:{data['uid']}",
        mapping={
            "name": data["name"],
            "school_number": data["school_number"],
            "expiration_date": data["expiration_date"],
            "doors": dumps(data.getlist("door_access")),
        },
    )
    flash("User created successfully", "success")

@app.route("/delete")
@login_required
def delete():
    return render_template("delete_form.html") 

@app.route("/delete", methods=["POST"])
@login_required
def delete_user():
    uid = request.form.get("uid")

    id = f"user:{uid}"
    if rd.exists(id):
        rd.delete(id)
        flash(f"User {uid} deleted successfully", "success")
        return redirect(url_for("delete"))
    
    flash(f"User {uid} not found", "error")
    return redirect(url_for("delete"))

app.run()
