from dotenv import load_dotenv
import os


load_dotenv(".secrets")

#Ops
PORT=os.getenv("PORT")

# List of names for the dropdown
NAMES_LIST = os.getenv("NAMES_LIST")

# Labels for UI elements
UPLOAD_BUTTON_LABEL = "Subir dibujo"
IMAGE_SIZE_LABEL = "Zoom"
UPLOAD_PAGE_TITLE = "Entrega 📓"
NAME_LABEL = "Artista"
RETO_LABEL = "Reto"
CHOOSE_IMAGE_LABEL = "Subir dibujo"
GALLERY_TITLE = "Club de Artistura"

# Colors
TITLE_COLOR = "#8B4513"  # Light brown color for the title
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")