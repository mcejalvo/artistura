
# **Club de Artistura**

## **Welcome!**
¡Bienvenidos al **Club de Artistura**! 🎨 This is a joyful space where artists can upload and share their creations as part of our drawing challenges. Think of it as your digital sketchbook gallery—simple, clean, and fun to use.

---

## **What’s Inside?**
- **Challenge Management**: A Flask app to organize and deliver drawing challenges automatically.  
- **Gallery View**: Browse uploaded works in a stylish, minimalist gallery.
- **Secure and Local**: Your uploads stay private on your machine.

---

## **How It’s Built**
This app is powered by:
- **Flask**: The friendly web framework.
- **HTML/CSS**: For a simple, clean user interface.
- **Python**: For all the magic behind the scenes.
- **Docker**: Easy deployment in a containerized environment.

---

## **How to Get Started**

### **1. Clone the Club**
```bash
git clone <repository-url>
cd club-de-artistura
```

### **2. Activate Your Creative Space**
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### **3. Set Up Secrets (Shhh 🤫)**
Create a `.secrets` file in the root folder:
```
CHALLENGE_API=your_api_key
GALLERY_SECRET=your_secret_key
```

### **4. Launch the Gallery**
```bash
python app.py
```
Head over to `http://localhost:5000` and start creating!

---

## **For Docker Fans**
Prefer containers? We've got you covered:
1. **Build the Clubhouse**:
   ```bash
   docker build -t club-de-artistura .
   ```
2. **Enter the Gallery**:
   ```bash
   docker run -p 5000:5000 --env-file .secrets club-de-artistura
   ```

---

## **A Peek Behind the Canvas**
- **app.py**: The brain behind the app.
- **templates/**: The heart of the gallery design (`gallery.html`, `upload.html`).
- **static/**: The style brushstrokes—CSS and images.
- **uploads/**: Where your masterpieces are stored (kept local, don’t worry!).
- **.secrets**: Safeguard your sensitive keys here (not tracked by Git).

---

## **Get Creative, Stay Inspired**
This is more than code—it’s a space to celebrate creativity. Whether you're sharing your weekly sketches or admiring others, **Club de Artistura** is your artistic playground. Let’s make something amazing together! 🌟
