# 🚀 Deploy Mentora to PythonAnywhere

## Step 1: Create Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click **"Start running Python online"** → create a **free** account
3. Confirm your email

## Step 2: Upload Your Code

### Option A: Upload from GitHub (Recommended)
1. Open a **Bash console**: Dashboard → Consoles → **"$ Bash"**
2. Run:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Mentora1.git
   ```
   *(replace `YOUR_USERNAME` with your actual GitHub username)*

### Option B: Upload Files Manually
1. Go to **Files** tab
2. Create folder: `/home/YOUR_USERNAME/Mentora1/`
3. Upload all project files into that folder

## Step 3: Create Virtual Environment
In the **Bash console**, run:
```bash
cd ~/Mentora1
mkvirtualenv mentora --python=python3.10
pip install -r requirements.txt
```

## Step 4: Download NLTK Data
Still in the Bash console:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt_tab')"
```

## Step 5: Configure Web App
1. Go to **Web** tab → click **"Add a new web app"**
2. Choose **"Manual configuration"** (NOT Flask)
3. Select **Python 3.10**

### Set Virtualenv
- In the **Virtualenv** section, enter: `/home/YOUR_USERNAME/.virtualenvs/mentora`

### Edit WSGI File
1. Click the WSGI configuration file link (something like `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`)
2. **Delete everything** in that file
3. Replace with:
   ```python
   import sys
   import os

   # Add your project directory
   project_home = '/home/YOUR_USERNAME/Mentora1'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   
   os.chdir(project_home)

   from server import app as application
   ```
4. Save the file

### Set Static Files
In the **Static files** section, add:

| URL | Directory |
|-----|-----------|
| `/` | `/home/YOUR_USERNAME/Mentora1` |

> ⚠️ Replace `YOUR_USERNAME` everywhere with your actual PythonAnywhere username

## Step 6: Reload & Test
1. Click the green **"Reload"** button on the Web tab
2. Visit `https://YOUR_USERNAME.pythonanywhere.com`
3. Login with password: `123`
4. Test the chatbot and admin panel at `/admin`

## Troubleshooting

### "Something went wrong" / Error log
- Check the **Error log** on the Web tab
- Common fix: Path typo in the WSGI file

### "Module not found" errors
- Make sure virtualenv path is correct
- Re-run: `pip install -r requirements.txt`

### NLTK errors
- Re-run the NLTK download command from Step 4

### Files not loading
- Make sure the static files mapping is set correctly
- Reload the web app after changes
