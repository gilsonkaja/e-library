# 🚀 Cloud eLibrary - Render Deployment Guide

## Quick Start

Your deployment folder is ready at: `c:\Users\Gilson K\Downloads\mycloudproj\render_deploy`

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub, GitLab, or email

### Step 2: Deploy to Render

**Option A: Via GitHub (Recommended)**
1. Create a new GitHub repository
2. Upload the contents of `render_deploy` folder
3. On Render dashboard, click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will auto-detect the configuration

**Option B: Direct Upload**
1. Zip the `render_deploy` folder
2. On Render dashboard, click "New +" → "Web Service"
3. Choose "Deploy from Git" or use Render's manual deploy option

### Step 3: Configure Environment Variables

In Render dashboard, go to "Environment" tab and add:

```
SECRET_KEY=your-random-secret-key-min-32-chars
JWT_SECRET_KEY=your-random-jwt-secret-min-32-chars
GEMINI_API_KEY=your-gemini-api-key (optional)
PORT=10000
```

**Generate Random Keys:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Step 4: Deploy Settings

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: (auto-detected from Procfile)
- **Instance Type**: Free tier is fine for testing

### Step 5: Access Your App

After deployment completes (2-3 minutes):
- Your app will be at: `https://your-service-name.onrender.com`
- Default login: `admin@demo.com` / `password`

## 📁 Folder Structure

```
render_deploy/
├── Procfile                 # Render startup configuration
├── requirements.txt         # Python dependencies
├── runtime.txt             # Python version
├── README.md               # Deployment instructions
├── .gitignore              # Files to exclude
├── app.py                  # Main Flask application
├── config.py               # Configuration
├── data_store.py           # Data management
├── routes/                 # API routes
│   ├── ai.py              # AI summarization
│   ├── auth.py            # Authentication
│   ├── books.py           # Book management
│   ├── upload.py          # File uploads
│   ├── admin.py           # Admin dashboard
│   └── payment.py         # Razorpay integration
├── utils/                  # Utilities
│   └── pdf_extract.py     # PDF text extraction
├── static_ui/              # Frontend files
│   ├── index.html         # Main UI
│   ├── app.js             # JavaScript logic
│   └── style.css          # Styling
├── data/                   # JSON data storage
│   ├── users.json
│   ├── books.json
│   ├── purchases.json
│   └── payments.json
└── static_uploads/         # Upload directory
```

## ✨ Features Included

✅ **3D Page-Flip Animation** - Realistic book reading experience
✅ **Search & Filter** - Find books by title, author, or category
✅ **AI Categorization** - Automatic genre detection with Gemini AI
✅ **Payment Integration** - Razorpay for paid books
✅ **Admin Dashboard** - Manage users and transactions
✅ **PDF Reader** - Two-page spread with zoom controls

## ⚠️ Important Notes

### File Storage
- Render's free tier has **ephemeral storage**
- Uploaded files will be deleted on restart/redeploy
- For production, use cloud storage (AWS S3, Cloudinary, etc.)

### Database
- Currently uses JSON files in `data/` folder
- Data persists between restarts but not redeployments
- For production, consider PostgreSQL or MongoDB

### Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- 750 hours/month free (enough for 1 app 24/7)

## 🔧 Troubleshooting

### Build Fails
- Check `requirements.txt` for typos
- Ensure Python version in `runtime.txt` is supported

### App Crashes
- Check Render logs in dashboard
- Verify environment variables are set
- Ensure `PORT` environment variable exists

### Static Files Not Loading
- Verify `static_ui/` folder was copied
- Check browser console for 404 errors
- Ensure paths in `app.py` are correct

## 🎯 Next Steps

1. **Deploy** the app to Render
2. **Test** all features (login, upload, search, AI summary)
3. **Change** default admin password
4. **Add** your Gemini API key for AI features
5. **Configure** Razorpay keys for payments
6. **Consider** upgrading to paid tier for production use

## 📞 Support

- Render Docs: https://render.com/docs
- Flask Docs: https://flask.palletsprojects.com/
- Gemini AI: https://ai.google.dev/

---

**Ready to deploy!** 🎉

Just zip the `render_deploy` folder and upload to Render, or push to GitHub and connect the repository.
