# Hosting Guide for Vicharak - NEP-2020 Timetable Generator

This guide covers multiple hosting options for the timetable generator, from simple local hosting to cloud deployment.

## 🌐 Hosting Options

### 1. **Local Development Server** (Quick Start)

**Run locally for testing:**
```bash
# Install dependencies
pip install -r requirements_web.txt

# Run the web app
python web_app.py
```

**Access:** http://localhost:5000

---

### 2. **Heroku** (Easiest Cloud Hosting)

**Prerequisites:**
- Heroku account (free tier available)
- Heroku CLI installed

**Steps:**
```bash
# Login to Heroku
heroku login

# Create a new app
heroku create your-timetable-app

# Set Python version
echo "python-3.11.0" > runtime.txt

# Deploy
git add .
git commit -m "Deploy timetable generator"
git push heroku main

# Open the app
heroku open
```

**Files needed:**
- `Procfile` ✅ (already created)
- `runtime.txt` ✅ (already created)
- `requirements_web.txt` ✅ (already created)

---

### 3. **Railway** (Modern Alternative)

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect Python and install dependencies
4. Deploy automatically

**Configuration:**
- Port: 5000 (auto-detected)
- Start command: `python web_app.py`

---

### 4. **Render** (Free Tier Available)

**Steps:**
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements_web.txt`
   - **Start Command:** `python web_app.py`
   - **Environment:** Python 3

---

### 5. **DigitalOcean App Platform**

**Steps:**
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Create new app from GitHub
3. Configure:
   - **Source:** Your GitHub repo
   - **Type:** Web Service
   - **Build Command:** `pip install -r requirements_web.txt`
   - **Run Command:** `python web_app.py`
   - **HTTP Port:** 5000

---

### 6. **AWS Elastic Beanstalk**

**Steps:**
1. Install AWS CLI and EB CLI
2. Initialize EB:
   ```bash
   eb init
   eb create production
   eb deploy
   ```

**Files needed:**
- `.ebextensions/python.config` (create this)

---

### 7. **Google Cloud Run** (Container-based)

**Steps:**
1. Install Google Cloud CLI
2. Build and push container:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/timetable-generator
   gcloud run deploy --image gcr.io/PROJECT-ID/timetable-generator --platform managed
   ```

---

### 8. **Docker Deployment** (Any Platform)

**Build and run locally:**
```bash
# Build the Docker image
docker build -t timetable-generator .

# Run the container
docker run -p 5000:5000 timetable-generator
```

**Deploy to any Docker-compatible platform:**
- AWS ECS
- Azure Container Instances
- Google Cloud Run
- DigitalOcean App Platform
- Self-hosted VPS

---

## 🔧 Configuration Files

### For Heroku/Railway/Render:
- `Procfile` - Process definition
- `runtime.txt` - Python version
- `requirements_web.txt` - Dependencies

### For Docker:
- `Dockerfile` - Container definition
- `requirements_web.txt` - Dependencies

### For AWS Elastic Beanstalk:
Create `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: web_app.py
```

---

## 🌍 Environment Variables

Set these in your hosting platform:

```bash
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

---

## 📊 Performance Considerations

### For Production:
1. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   ```
   Update `Procfile`:
   ```
   web: gunicorn web_app:app
   ```

2. **Add caching:**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

3. **Use a database:**
   - PostgreSQL for production
   - SQLite for development

---

## 🔒 Security Considerations

### For Production:
1. **Set secret key:**
   ```python
   app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
   ```

2. **Enable HTTPS:**
   - Most platforms provide this automatically
   - Use Let's Encrypt for self-hosted

3. **Add authentication:**
   ```python
   from flask_login import LoginManager
   # Add user authentication
   ```

---

## 📱 Mobile Responsiveness

The web app is already mobile-responsive with Bootstrap 5, but you can enhance it:

1. **Add PWA support:**
   - Create `manifest.json`
   - Add service worker

2. **Optimize for mobile:**
   - Touch-friendly buttons
   - Swipe gestures for tables

---

## 🚀 Quick Deploy Commands

### Heroku (Fastest):
```bash
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
heroku open
```

### Railway:
```bash
# Just push to GitHub, Railway handles the rest
git push origin main
```

### Render:
```bash
# Connect GitHub repo in Render dashboard
# Auto-deploys on push
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Heroku | 550 hours/month | $7+/month | Quick deployment |
| Railway | $5/month | $5+/month | Modern platform |
| Render | 750 hours/month | $7+/month | Free tier |
| DigitalOcean | No free tier | $5+/month | Full control |
| AWS | 12 months free | Pay-as-you-go | Enterprise |
| Google Cloud | $300 credit | Pay-as-you-go | Google ecosystem |

---

## 🛠️ Troubleshooting

### Common Issues:

1. **Port binding error:**
   ```python
   app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
   ```

2. **Memory issues:**
   - Use `gunicorn` with multiple workers
   - Add memory limits in platform settings

3. **Static files not loading:**
   - Check file paths
   - Use CDN for production

4. **Database connection:**
   - Use environment variables for connection strings
   - Add connection pooling

---

## 📈 Monitoring & Analytics

### Add monitoring:
```python
import logging
from flask import request

@app.before_request
def log_request_info():
    app.logger.info(f'{request.method} {request.url}')
```

### Health check endpoint:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions example:
```yaml
name: Deploy to Heroku
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"
```

---

## 📞 Support

For hosting issues:
1. Check platform documentation
2. Review logs in platform dashboard
3. Test locally first
4. Use platform-specific debugging tools

The web application is ready for deployment on any of these platforms!
