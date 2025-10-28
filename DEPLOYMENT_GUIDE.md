# Free Cloud Deployment Guide

This guide will help you deploy your SITREP application using the free hosting stack:
- **Frontend**: Vercel (static assets)
- **Backend**: Railway (Flask API)
- **Database**: Supabase (PostgreSQL)
- **LLM**: OpenRouter (free tier)
- **Maps**: Public tile services (OpenStreetMap, Mapbox)

## Prerequisites

1. **Accounts needed**:
   - [Supabase](https://supabase.com) account
   - [Railway](https://railway.app) account
   - [Vercel](https://vercel.com) account
   - [OpenRouter](https://openrouter.ai) account
   - [Mapbox](https://mapbox.com) account (optional, for satellite tiles)

2. **Tools required**:
   - Git
   - Python 3.8+
   - Node.js (for local development)

## Step 1: Set Up Supabase Database

1. **Create a new Supabase project**:
   - Go to [Supabase Dashboard](https://app.supabase.com)
   - Click "New Project"
   - Choose your organization and set project details
   - Wait for the project to be created

2. **Get database credentials**:
   - Go to Settings → Database
   - Copy the "Connection string" (URI format)
   - It should look like: `postgresql://postgres:[password]@[host]:5432/postgres`

3. **Configure database access**:
   - Go to Settings → API
   - Note down your project URL and anon key (for future use)

## Step 2: Set Up OpenRouter API

1. **Create OpenRouter account**:
   - Go to [OpenRouter](https://openrouter.ai)
   - Sign up and verify your account

2. **Get API key**:
   - Go to [API Keys](https://openrouter.ai/keys)
   - Create a new API key
   - Copy the key (starts with `sk-or-...`)

3. **Choose a free model**:
   - Recommended free models:
     - `microsoft/wizardlm-2-8x22b` (free tier)
     - `meta-llama/llama-3.1-8b-instruct:free`
     - `mistralai/mistral-7b-instruct:free`

## Step 3: Get Mapbox Access Token (Optional)

1. **Create Mapbox account**:
   - Go to [Mapbox](https://mapbox.com)
   - Sign up for a free account

2. **Get access token**:
   - Go to your [Account page](https://account.mapbox.com/)
   - Copy your "Default public token"
   - Or create a new token with appropriate scopes

## Step 4: Migrate Database

1. **Set up environment variables**:
   ```bash
   # Create .env file
   cp .env.example .env
   ```

2. **Edit .env file**:
   ```env
   # Flask Configuration
   FLASK_ENV=production
   FLASK_DEBUG=False
   SECRET_KEY=your-secret-key-here

   # Supabase Database
   SUPABASE_DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres

   # OpenRouter API
   OPENROUTER_API_KEY=sk-or-your-api-key-here
   OPENROUTER_MODEL=microsoft/wizardlm-2-8x22b

   # Mapbox (optional)
   MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token-here

   # CORS (will be updated with your Railway URL)
   CORS_ORIGINS=http://localhost:5050,https://your-app.railway.app

   # File uploads
   MAX_CONTENT_LENGTH=16777216
   UPLOAD_FOLDER=uploads
   ```

3. **Run migration script**:
   ```bash
   python migrate_to_supabase.py
   ```

## Step 5: Deploy Backend to Railway

1. **Prepare your repository**:
   ```bash
   # Initialize git if not already done
   git init
   git add .
   git commit -m "Initial commit for deployment"
   
   # Push to GitHub (create a new repository first)
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Deploy to Railway**:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect it's a Python app

3. **Configure environment variables in Railway**:
   - Go to your project → Variables
   - Add all variables from your .env file:
     ```
     FLASK_ENV=production
     FLASK_DEBUG=False
     SECRET_KEY=your-secret-key-here
     SUPABASE_DATABASE_URL=postgresql://...
     OPENROUTER_API_KEY=sk-or-...
     OPENROUTER_MODEL=microsoft/wizardlm-2-8x22b
     MAPBOX_ACCESS_TOKEN=pk.your-token...
     CORS_ORIGINS=https://your-app.railway.app
     MAX_CONTENT_LENGTH=16777216
     UPLOAD_FOLDER=uploads
     HOST=0.0.0.0
     PORT=8080
     ```

4. **Get your Railway URL**:
   - After deployment, Railway will provide a URL like `https://your-app.railway.app`
   - Update the `CORS_ORIGINS` variable with this URL

## Step 6: Deploy Frontend to Vercel

1. **Update vercel.json**:
   - Edit `vercel.json` and replace `your-railway-backend.railway.app` with your actual Railway URL

2. **Deploy to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically deploy

3. **Configure build settings** (if needed):
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `npm install` (if you have package.json)

## Step 7: Test Your Deployment

1. **Test backend**:
   - Visit your Railway URL: `https://your-app.railway.app`
   - Check `/api/sitreps` endpoint
   - Test chatbot functionality

2. **Test frontend**:
   - Visit your Vercel URL
   - Verify map loads with public tiles
   - Test all features

3. **Test database**:
   - Create a new SITREP
   - Verify it appears in Supabase dashboard

## Step 8: Update CORS and Final Configuration

1. **Update CORS in Railway**:
   ```
   CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-app.railway.app
   ```

2. **Test cross-origin requests**:
   - Access frontend via Vercel URL
   - Verify API calls work to Railway backend

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Verify Supabase connection string
   - Check if database tables were created
   - Ensure Supabase project is not paused

2. **CORS errors**:
   - Update CORS_ORIGINS with correct URLs
   - Ensure both frontend and backend URLs are included

3. **OpenRouter API errors**:
   - Verify API key is correct
   - Check if you have credits/free tier access
   - Try a different free model

4. **Map tiles not loading**:
   - Check browser console for errors
   - Verify Mapbox token (if using Mapbox tiles)
   - Ensure public tile services are accessible

### Monitoring and Logs

1. **Railway logs**:
   - Go to your Railway project → Deployments
   - Click on latest deployment to view logs

2. **Vercel logs**:
   - Go to your Vercel project → Functions
   - View real-time logs

3. **Supabase monitoring**:
   - Go to Supabase Dashboard → Logs
   - Monitor database queries and errors

## Cost Optimization

### Free Tier Limits

1. **Railway**: 500 hours/month, $5 credit
2. **Vercel**: 100GB bandwidth, 1000 serverless function invocations
3. **Supabase**: 500MB database, 2GB bandwidth
4. **OpenRouter**: Varies by model, some models are free

### Tips to Stay Within Limits

1. **Optimize database queries**
2. **Use caching where possible**
3. **Monitor usage regularly**
4. **Consider upgrading if you exceed limits**

## Security Considerations

1. **Environment Variables**:
   - Never commit .env files to git
   - Use strong, unique secret keys
   - Rotate API keys regularly

2. **Database Security**:
   - Enable Row Level Security in Supabase
   - Use proper authentication
   - Limit database access

3. **API Security**:
   - Implement rate limiting
   - Validate all inputs
   - Use HTTPS only

## Next Steps

1. **Custom Domain** (optional):
   - Configure custom domain in Vercel
   - Update CORS settings accordingly

2. **Monitoring**:
   - Set up error tracking (Sentry)
   - Monitor performance metrics
   - Set up uptime monitoring

3. **Backup Strategy**:
   - Regular database backups
   - Export important data
   - Document recovery procedures

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review platform-specific documentation:
   - [Railway Docs](https://docs.railway.app)
   - [Vercel Docs](https://vercel.com/docs)
   - [Supabase Docs](https://supabase.com/docs)
3. Check application logs for specific error messages

---

**Congratulations!** Your SITREP application is now deployed on a completely free hosting stack! 🎉