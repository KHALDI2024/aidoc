from functools import cache
from unittest import result

from sympy import false
from app.home import blueprint
from flask import (
    render_template,
    request,
    current_app,
    send_from_directory,
    abort,
    jsonify,
)
from jinja2 import TemplateNotFound
import os

@blueprint.route("/")
@blueprint.route("/index")
def index():
    folder_path = os.path.join(current_app.root_path, "uploads")
    file_list = []

    try:
        # Get the list of files in the folder
        # files = os.listdir(folder_path)
        ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if (
                os.path.isfile(file_path)
                and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
            ):
                size_bytes = os.path.getsize(file_path)
                size_bytes = os.path.getsize(file_path)
                size_mb = round(size_bytes / (1024 * 1024), 2)  # Convert to MB
                extension = os.path.splitext(filename)[1].lower()

                file_list.append(
                    {"name": filename, "size": size_mb, "extension": extension}
                )
    except Exception as e:
        file_list = []
        print(f"Error reading files: {e}")

    return render_template("home/index.html", segment="index", files=file_list)


@blueprint.route("/preview/<filename>")
def preview_file(filename):
    folder_path = os.path.join(current_app.root_path, "uploads")
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        abort(404)

    # Return file for inline display (preview in browser if supported)
    return send_from_directory(folder_path, filename, as_attachment=False)


@blueprint.route("/process")
def show_process_page():
    return render_template("pages/process.html", segment="index")


# @blueprint.route("/process", methods=["POST"])
# def show_process_page():
#     file_name = request.form.get("uploaded_file")
#     lang = request.form.get("lang")
#     detectOrientation = request.form.get("detectOrientation")

#     return render_template(
#         "pages/process.html",
#         uploaded_file=file_name,
#         lang=lang,
#         detectOrientation=detectOrientation,
#         segment="index",
#     )


@blueprint.route("/process-task", methods=["POST"])
def process_task():
    from app.utils.pdf_utils import (
        check_exiting_poppler,
        convert_pdf_to_images,
        recognising_text_from_images,
        check_file_extension,
        recognising_text_from_image,
    )

    try:
        file_name = request.form.get("uploaded_file")
        language = request.form.get("lang")
        detectOrientation = request.form.get("detectOrientation")
        # Fake progress stages
        # status = {"progress": 0}
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
        output_path = os.path.join(
            current_app.config["OUTPUT_FOLDER"], "output_text.txt"
        )
        poppler_path = check_exiting_poppler()

        is_pdf = check_file_extension(file_path)
        if is_pdf:
            image_counter = convert_pdf_to_images(file_path, poppler_path)
            result = recognising_text_from_images(image_counter, language, output_path)
        else:
            result = recognising_text_from_image(file_path, language, output_path)
        return (
            jsonify(
                {
                    "ok": True,
                    "result": result,
                    # "progress": 100,
                    "file_name": file_name,
                    "file_path": file_path,
                    "lang": language,
                    "detectOrientation": detectOrientation,
                }
            ),
            200,
        )  # Success
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Bad request
    except Exception as e:
        return (
            jsonify({"error": "Message d'erreur : " + str(e)}),
            500,
        )  # Internal server error

# @blueprint.route("/get-progress", methods=["GET"])
# def get_progress():
#     # Get the current progress from the session
#     progress = session.get('progress', 0)
#     return jsonify({"progress": progress})

@blueprint.route("/blank", methods=["POST"])
def blank():
    file_path = request.form.get("uploaded_file")
    lang = request.form.get("lang")
    detectOrientation = request.form.get("detectOrientation")
    return render_template(
        "pages/pages-blank.html",
        segment="blank",
        file_path=file_path,
        lang=lang,
        detectOrientation=detectOrientation,
    )


@blueprint.route("/charts")
def charts():
    return render_template("pages/charts-chartjs.html", segment="charts")


@blueprint.route("/icons")
def icons():
    return render_template("pages/icons-feather.html", segment="icons")


@blueprint.route("/maps")
def maps():
    return render_template("pages/maps-google.html", segment="maps")


@blueprint.route("/profile")
def profile():
    return render_template("pages/pages-profile.html", segment="profile")


@blueprint.route("/signin")
def signin():
    return render_template("pages/pages-sign-in.html")


@blueprint.route("/signup")
def signup():
    return render_template("pages/pages-sign-up.html")


@blueprint.route("/uibuttons")
def uibuttons():
    return render_template("pages/ui-buttons.html", segment="uibuttons")


@blueprint.route("/uicards")
def uicards():
    return render_template("pages/ui-cards.html", segment="uicards")


@blueprint.route("/uiforms")
def uiforms():
    return render_template("pages/ui-forms.html", segment="uiforms")


@blueprint.route("/uitypography")
def uitypography():
    return render_template("pages/ui-typography.html", segment="uitypography")


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
