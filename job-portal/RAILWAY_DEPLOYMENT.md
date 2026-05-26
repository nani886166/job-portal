# Railway Deployment

## Required Railway variables

Set these in the Railway service variables:

```env
DEBUG=False
SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_HOSTS=localhost,127.0.0.1,.railway.app,.up.railway.app,.railway.internal,job-portal-production-1bb1.up.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app
CORS_ALLOWED_ORIGINS=https://dynamic-job-portal.vercel.app
CORS_ALLOW_ALL_ORIGINS=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=JobPortal <your-email@gmail.com>
```

Add a Railway PostgreSQL database to the project. Railway will provide `DATABASE_URL` automatically.

If the deploy still fails at the healthcheck step, check Railway's runtime logs
instead of only the build logs. The build can succeed while Gunicorn crashes at
startup because of a missing variable, bad database URL, or host validation.

## Frontend variables on Vercel

Set this in the Vercel frontend project variables:

```env
VITE_API_BASE_URL=https://job-portal-production-1bb1.up.railway.app/api
```

Redeploy the Vercel frontend after changing this variable.

## Deploy behavior

- `railway.toml` uses Railpack.
- Static files are collected during build.
- Migrations run as a pre-deploy command.
- Gunicorn starts the Django app using Railway's `$PORT`.
- Railway checks `/health/` after deploy.

## Important media note

Uploaded files in `backend/media/` are not permanent on Railway. Use Cloudinary, S3, or another external storage provider for production resumes and profile pictures.
