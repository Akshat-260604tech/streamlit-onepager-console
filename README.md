# Streamlit Admin Console Deployment Guide

This guide explains how to deploy your One-Pager Admin Console to Streamlit Cloud while keeping your existing backend deployments intact.

## 🚀 Quick Start

### Option 1: Direct Deployment (Recommended)
1. Push the `streamlit-deploy` folder to a new GitHub repository
2. Connect to Streamlit Cloud
3. Deploy using the main app file

### Option 2: Subfolder Deployment
1. Add the `streamlit-deploy` folder to your existing repository
2. Deploy using the subfolder path

## 📁 Project Structure

```
streamlit-deploy/
├── app.py                          # Main Streamlit app (uses .env)
├── app_with_secrets.py             # Alternative app using Streamlit secrets
├── requirements.txt                # Dependencies for Streamlit Cloud
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── secrets.toml.example            # Example secrets configuration
└── README.md                       # This file
```

## 🔧 Configuration Options

### Method 1: Environment Variables (.env file)
- Uses `python-dotenv` to load environment variables
- Good for local development
- **File**: `app.py`

### Method 2: Streamlit Secrets (Recommended for Cloud)
- Uses Streamlit's built-in secrets management
- More secure for production deployment
- **File**: `app_with_secrets.py`

## 🛠️ Deployment Steps

### Step 1: Prepare Your Repository

#### Option A: New Repository
```bash
# Create a new repository for the admin console
mkdir one-pager-admin-console
cd one-pager-admin-console
cp -r /path/to/streamlit-deploy/* .
git init
git add .
git commit -m "Initial admin console setup"
git remote add origin https://github.com/yourusername/one-pager-admin-console.git
git push -u origin main
```

#### Option B: Add to Existing Repository
```bash
# Add to your existing repository
cd /path/to/your/existing/repo
mkdir streamlit-admin
cp -r /path/to/streamlit-deploy/* streamlit-admin/
git add streamlit-admin/
git commit -m "Add Streamlit admin console"
git push
```

### Step 2: Configure Secrets

#### For Streamlit Secrets (Recommended)
1. Go to your Streamlit Cloud dashboard
2. Select your app
3. Go to "Settings" → "Secrets"
4. Add the following secrets:

```toml
[supabase]
url = "your_supabase_url_here"
key = "your_supabase_anon_key_here"

[azure]
connection_string = "your_azure_connection_string_here"
account_name = "your_azure_account_name_here"
account_key = "your_azure_account_key_here"

[openai]
api_key = "your_openai_api_key_here"

[serpapi]
api_key = "your_serpapi_key_here"
```

#### For Environment Variables
1. Create a `.env` file in your repository root
2. Add your environment variables:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string_here
# ... other variables
```

### Step 3: Deploy to Streamlit Cloud

1. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
2. **Click "New app"**
3. **Connect your GitHub repository**
4. **Configure the deployment:**
   - **Main file path**: `streamlit-deploy/app_with_secrets.py` (or `app.py` for env vars)
   - **Python version**: 3.9 or higher
   - **Dependencies**: `requirements.txt` (auto-detected)

5. **Click "Deploy"**

## 🔒 Security Best Practices

### 1. Use Streamlit Secrets
- Never commit secrets to your repository
- Use Streamlit's built-in secrets management
- Rotate keys regularly

### 2. Environment Isolation
- Use different Supabase projects for different environments
- Separate Azure storage accounts if needed
- Use different API keys for staging/production

### 3. Access Control
- Consider adding authentication if needed
- Use Supabase RLS (Row Level Security) policies
- Monitor access logs

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```
❌ Database connection failed: Invalid API key
```
**Solution**: Check your Supabase URL and key in secrets

#### 2. Import Errors
```
ModuleNotFoundError: No module named 'app.services'
```
**Solution**: Ensure the backend_py folder is accessible or copy the required services

#### 3. Memory Issues
```
MemoryError: Unable to allocate array
```
**Solution**: Reduce the number of records loaded or add pagination

#### 4. Slow Loading
**Solution**:
- Add caching with `@st.cache_data`
- Implement pagination
- Use database queries with limits

### Debug Mode
To enable debug mode, add this to your secrets:
```toml
[app]
debug = true
```

## 📊 Performance Optimization

### 1. Caching
Add caching to expensive operations:
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_recent_records(limit: int = 100):
    # Your database query here
    pass
```

### 2. Pagination
Implement pagination for large datasets:
```python
# In your table rendering
page_size = 20
total_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)
```

### 3. Database Optimization
- Use database indexes on frequently queried columns
- Implement proper database connection pooling
- Use async operations where possible

## 🔄 Updates and Maintenance

### Updating the App
1. Make changes to your local files
2. Commit and push to GitHub
3. Streamlit Cloud will automatically redeploy

### Monitoring
- Check Streamlit Cloud logs for errors
- Monitor database performance
- Set up alerts for critical failures

### Backup
- Regular database backups
- Export important data periodically
- Keep configuration backups

## 📈 Scaling Considerations

### For High Traffic
- Consider using Streamlit's paid plans
- Implement proper caching strategies
- Use CDN for static assets
- Consider database read replicas

### For Large Datasets
- Implement data pagination
- Use database views for complex queries
- Consider data archiving strategies
- Implement search and filtering

## 🆘 Support

If you encounter issues:

1. **Check the logs** in Streamlit Cloud dashboard
2. **Verify secrets** are correctly configured
3. **Test locally** first with the same configuration
4. **Check database connectivity** from the deployed environment

## 📝 Additional Notes

- The admin console is read-only by default
- All database operations are through your existing Supabase setup
- No changes to your existing backend are required
- The deployment is completely isolated from your other services

## 🎯 Next Steps

1. Deploy using the steps above
2. Test all functionality
3. Set up monitoring and alerts
4. Consider adding authentication if needed
5. Optimize performance based on usage patterns
