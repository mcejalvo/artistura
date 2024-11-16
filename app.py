from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests
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
        print(f"Checking existing files for user: {name}")  # Debugging
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith("reto-") and f"-{name}" in filename:
                print(f"Found file: {filename}")  # Debugging
                try:
                    current_number = int(filename.split("-")[1])
                    reto_number = max(reto_number, current_number + 1)
                except (ValueError, IndexError) as e:
                    print(f"Error parsing filename {filename}: {e}")  # Debugging
    except Exception as e:
        print(f"Error in get_next_reto_number: {e}")
    print(f"Next Reto number for {name}: {reto_number}")  # Debugging
    return reto_number


# Route to fetch the next Reto number
@app.route('/get_next_reto_number')
def get_next_reto_number_route():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400
    try:
        next_reto = get_next_reto_number(name)
        return jsonify(next_reto=next_reto)
    except Exception as e:
        print(f"Error in /get_next_reto_number: {e}")
        return jsonify({"error": "Server error"}), 500

# Function to send Discord notifications
def send_discord_notification(user_name, reto_number, image_name, is_bonus=False):
    spoiler_image_name = f"SPOILER_{image_name}"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)  # Local path to the original image
    gallery_link = "https://artistura.micuquantic.cc"

    if is_bonus:
        main_message = {
            "content": f"**{user_name}** ha subido puro arte 🚬"
        }
    else:
        main_message = {
            "content": f"**{user_name}** ha entregado su artistura del **Reto {reto_number}**!!"
        }

    try:
        # Debugging step
        print(f"Sending Discord notification. Image path: {image_path}, Webhook URL: {config.DISCORD_WEBHOOK_URL}")
        
        # First message with the image
        with open(image_path, "rb") as image_file:
            files = {"file": (spoiler_image_name, image_file)}
            response = requests.post(config.DISCORD_WEBHOOK_URL, data=main_message, files=files, timeout=10)
            print(f"Discord response (main message): {response.status_code}, {response.text}")  # Debugging

        # Follow-up message with the gallery link
        follow_up_message = {
            "content": f"\n\nGalería: {gallery_link}"
        }

        response = requests.post(config.DISCORD_WEBHOOK_URL, json=follow_up_message, timeout=10)
        print(f"Discord response (follow-up): {response.status_code}, {response.text}")  # Debugging")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord notification: {e}")

    print(f"Sending notification for user: {user_name}, reto: {reto_number}, image: {image_name}")




# Root route (Gallery page)
@app.route('/')
def gallery():
    images = os.listdir(app.config['UPLOAD_FOLDER'])

    # Load reto details from retos.csv
    with open("retos.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        reto_details = {f"Reto {int(row['id'])}": {
            "nombre": row["nombre"],
            "descripcion": row["descripcion"]
        } for row in reader}
        NUM_RETOS = len(reto_details)

    retos = {f"Reto {i}": [] for i in range(1, NUM_RETOS + 1)}
    bonus_images = []

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
    # Load max retos count from retos.csv
    with open("retos.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        max_retos = sum(1 for row in reader)

    # Calculate the number of retos for each user
    retos = {}
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith("reto-"):
            try:
                # Extract the user name from the filename
                user = filename.split("-")[2].split(".")[0]
                retos[user] = retos.get(user, 0) + 1
            except IndexError:
                continue

    if request.method == 'POST':
        name = request.form.get('name')
        file = request.files.get('file')
        is_bonus = request.form.get('bonus') == 'on'

        print(f"Upload received. Name: {name}, Bonus: {is_bonus}, File: {file}")  # Debugging

        if name and file and file.filename:
            try:
                # Check number of retos already submitted for the selected user
                reto_count = retos.get(name, 0)
                print(f"{name} has submitted {reto_count} retos out of {max_retos}.")  # Debugging

                if reto_count >= max_retos:
                    is_bonus = True  # Automatically set as Bonus if max retos reached
                    print(f"Max retos reached for {name}. Setting to Bonus.")  # Debugging

                if is_bonus:
                    # Bonus file logic
                    bonus_number = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(f"{name}-")]) + 1
                    filename = f"{name}-{bonus_number}{os.path.splitext(file.filename)[1]}"
                    print(f"Generated Bonus Filename: {filename}")  # Debugging
                else:
                    # Reto file logic
                    reto_number = get_next_reto_number(name)
                    filename = f"reto-{reto_number}-{name}{os.path.splitext(file.filename)[1]}"
                    print(f"Generated Reto Filename: {filename}")  # Debugging

                # Save the file
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(f"Saving file to: {full_path}")  # Debugging
                file.save(full_path)
                print(f"File saved successfully: {full_path}")  # Debugging

                # Send Discord notification
                if is_bonus:
                    print("Sending Discord notification for Bonus...")  # Debugging
                    send_discord_notification(name, "Bonus", filename, is_bonus=True)
                else:
                    print("Sending Discord notification for Reto...")  # Debugging
                    send_discord_notification(name, reto_number, filename, is_bonus=False)
                print("Discord notification sent.")  # Debugging

                return redirect(url_for('gallery'))
            except Exception as e:
                print(f"Error in upload_image: {e}")
                return f"Error in upload_image: {e}", 500
        else:
            print("Missing name, file, or filename")
            return "Missing name, file, or filename", 400

    return render_template(
        'upload.html',
        names=config.NAMES_LIST,
        retos=retos,  # Pass the retos dictionary to the template
        page_title=config.UPLOAD_PAGE_TITLE,
        name_label=config.NAME_LABEL,
        reto_label=config.RETO_LABEL,
        choose_image_label=config.CHOOSE_IMAGE_LABEL,
        button_label=config.UPLOAD_BUTTON_LABEL,
        title_color=config.TITLE_COLOR,
        max_retos=max_retos  # Pass max retos count to the template
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
