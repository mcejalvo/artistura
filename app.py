
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests
import time
import csv
import config 

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to calculate the next Reto number based on existing files
def get_next_reto_number(name):
    reto_number = 1  # Default to 1 if no files are found
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith(f"reto-") and f"-{name}" in filename:
                try:
                    current_number = int(filename.split("-")[1])
                    reto_number = max(reto_number, current_number + 1)
                except (ValueError, IndexError):
                    pass  # Ignore invalid filenames
    except Exception as e:
        print(f"Error in get_next_reto_number: {e}")
    return reto_number

# Route to fetch the next Reto number
@app.route('/get_next_reto_number')
def get_next_reto_number_route():
    name = request.args.get('name')
    print(f"Received name: {name}")  # Debugging
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400
    try:
        next_reto = get_next_reto_number(name)
        print(f"Next reto calculated: {next_reto}")  # Debugging
        return jsonify(next_reto=next_reto)
    except Exception as e:
        print(f"Error in /get_next_reto_number: {e}")  # Debugging
        return jsonify({"error": "Server error"}), 500


def send_discord_notification(user_name, reto_number, image_name):
    # Modify the image file name to add the "SPOILER_" prefix
    spoiler_image_name = f"SPOILER_{image_name}"
    image_path = f"static/uploads/{image_name}"  # Local path to the original image
    gallery_link = "https://artistura.micuquantic.cc"

    # Prepare the main message without the image
    main_message = {
        "content": f"**{user_name}** ha entregado su artistura del **Reto {reto_number}**!!"
    }

    # Send the first POST request with the image file marked as a spoiler
    with open(image_path, "rb") as image_file:
        files = {"file": (spoiler_image_name, image_file)}
        response = requests.post(config.DISCORD_WEBHOOK_URL, data=main_message, files=files)

    # Prepare and send the follow-up message with the gallery link
    follow_up_message = {
        "content": f"\n\nSigue el proceso en la galería: {gallery_link}"
    }
    requests.post(config.DISCORD_WEBHOOK_URL, json=follow_up_message)

# Root route (Gallery page)
@app.route('/')
def gallery():
    images = os.listdir(app.config['UPLOAD_FOLDER'])

    # Dynamically compute NUM_RETOS based on retos.csv
    with open("retos.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        reto_details = {f"Reto {int(row['id'])}": {
            "nombre": row["nombre"],
            "descripcion": row["descripcion"]
        } for row in reader}
        NUM_RETOS = len(reto_details)

    retos = {f"Reto {i}": [] for i in range(1, NUM_RETOS + 1)}
    bonus_images = []  # New list for images not within "Reto" sections

    for image in images:
        if image.startswith("reto-"):
            try:
                reto_number = int(image.split("-")[1])
                if 1 <= reto_number <= NUM_RETOS:
                    retos[f"Reto {reto_number}"].append(image)
                else:
                    bonus_images.append(image)
            except (ValueError, IndexError):
                bonus_images.append(image)
        else:
            bonus_images.append(image)

    return render_template(
        'gallery.html',
        retos=retos,
        bonus_images=bonus_images,
        reto_details=reto_details,
        upload_button_label="Subir dibujo",
        image_size_label="Zoom",
        gallery_title="Club de Artistura",
        title_color="#8B4513"
    )

# Upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        name = request.form.get('name')
        file = request.files.get('file')
        
        if name and file and file.filename:
            reto_number = get_next_reto_number(name)
            filename = f"reto-{reto_number}-{name}{os.path.splitext(file.filename)[1]}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Send Discord notification
            send_discord_notification(name, reto_number, filename)
            
            return redirect(url_for('gallery'))
    
    return render_template(
        'upload.html',
        names=["Winnie", "Astrotortuga", "Hely", "Deparki", "Guille", "Casino", "Potajito", "Safe", "Mono"],
        page_title="Entrega 📓",
        name_label="Artista",
        reto_label="Reto",
        choose_image_label="Subir dibujo",
        button_label="Subir dibujo",
        title_color="#8B4513"
    )

# Delete image route
@app.route('/delete/<filename>')
def delete_image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for('gallery'))
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
