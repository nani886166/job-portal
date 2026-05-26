# Railway Deployment

## Required Railway variables

Set these in the Railway service variables:

```env
DEBUG=False
SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_HOSTS=.railway.app,.up.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
CORS_ALLOW_ALL_ORIGINS=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=JobPortal <your-email@gmail.com>
```

Add a Railway PostgreSQL database to the project. Railway will provide `DATABASE_URL` automatically.

## Deploy behavior

- `railway.toml` uses Railpack.
- Static files are collected during build.
- Migrations run as a pre-deploy command.
- Gunicorn starts the Django app using Railway's `$PORT`.
- Railway checks `/health/` after deploy.

## Important media note

Uploaded files in `backend/media/` are not permanent on Railway. Use Cloudinary, S3, or another external storage provider for production resumes and profile pictures.
