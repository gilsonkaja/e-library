# Cloud eLibrary - Render Deployment

## Environment Variables Required

Set these in your Render dashboard:

```
SECRET_KEY=your-secret-key-here-change-this-to-random-string
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this-to-random-string
GEMINI_API_KEY=your-gemini-api-key-here (optional, for AI features)
PORT=10000
```

## Deployment Steps

1. **Create a new Web Service on Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository or upload this folder

2. **Configure the service:**
   - **Name**: cloud-elibrary (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: (automatically detected from Procfile)
   - **Instance Type**: Free or Starter

3. **Add Environment Variables:**
   - Go to "Environment" tab
   - Add all the variables listed above
   - Generate random strings for SECRET_KEY and JWT_SECRET_KEY

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your app will be available at: `https://your-service-name.onrender.com`

## Features Included

✅ 3D Book-Flipping Animation
✅ Search Functionality
✅ AI-Powered Categorization
✅ Razorpay Payment Integration
✅ Admin Dashboard
✅ PDF Reader with Two-Page Spread

## Default Admin Account

- Email: admin@demo.com
- Password: password

**⚠️ IMPORTANT**: Change the admin password after first login!

## Notes

- The app uses in-memory JSON storage (data/ folder)
- For production, consider using a proper database
- Upload folder is temporary on Render (files reset on restart)
- Consider using cloud storage (AWS S3, Cloudinary) for persistent file storage
