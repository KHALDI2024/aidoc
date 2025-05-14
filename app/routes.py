from app.home import blueprint
from flask import render_template, request

# from flask_login import login_required, current_user
from jinja2 import TemplateNotFound


@blueprint.route("/")
@blueprint.route("/index")
def index():

    return render_template(
        "home/index.html",
        segment="index",
        #    user_id=current_user.id
    )


@blueprint.route("/charts")
def charts():
    return render_template("pages/charts-chartjs.html", segment='charts')


@blueprint.route("/icons")
def icons():
    return render_template("pages/icons-feather.html", segment='icons')


@blueprint.route("/maps")
def maps():
    return render_template("pages/maps-google.html", segment='maps')


@blueprint.route("/blank")
def blank():
    return render_template("pages/pages-blank.html", segment='blank')


@blueprint.route("/profile")
def profile():
    return render_template("pages/pages-profile.html", segment='profile')


@blueprint.route("/signin")
def signin():
    return render_template("pages/pages-sign-in.html")


@blueprint.route("/signup")
def signup():
    return render_template("pages/pages-sign-up.html")


@blueprint.route("/uibuttons")
def uibuttons():
    return render_template("pages/ui-buttons.html", segment='uibuttons')


@blueprint.route("/uicards")
def uicards():
    return render_template("pages/ui-cards.html", segment='uicards')


@blueprint.route("/uiforms")
def uiforms():
    return render_template("pages/ui-forms.html", segment='uiforms')


@blueprint.route("/uitypography")
def uitypography():
    return render_template("pages/ui-typography.html", segment='uitypography')


@blueprint.route("/<template>")
# @login_required
def route_template(template):
    try:
        if not template.endswith(".html"):
            template += ".html"

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template("home/page-404.html"), 404

    except:
        return render_template("home/page-500.html"), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except:
        return None
