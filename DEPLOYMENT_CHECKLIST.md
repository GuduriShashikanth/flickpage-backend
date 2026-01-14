# CineLibre Deployment Checklist

## Pre-Deployment

### Database
- [ ] Supabase project created
- [ ] `database_schema.sql` executed successfully
- [ ] All tables created (users, movies, books, ratings, interactions)
- [ ] Vector indexes created
- [ ] RPC functions working (test with SQL editor)

### Data
- [ ] Initial movie data synced (2000+ movies)
- [ ] Book data synced (optional)
- [ ] Embeddings generated for all items
- [ ] Sample data verified in Supabase dashboard

### Environment Variables
- [ ] `SUPABASE_URL` set
- [ ] `SUPABASE_KEY` set (service role key, not anon key!)
- [ ] `JWT_SECRET_KEY` generated (32+ characters)
- [ ] `TMDB_API_KEY` set (for sync engine)
- [ ] `PORT` configured (Koyeb auto-sets this)

### Code
- [ ] All dependencies in `requirements.txt`
- [ ] `Procfile` configured for Gunicorn
- [ ] Memory optimizations in place (OMP_NUM_THREADS=1)
- [ ] CORS configured for your frontend domain
- [ ] No hardcoded secrets in code

### Testing
- [ ] Local server starts without errors
- [ ] Health check returns 200
- [ ] User registration works
- [ ] Login returns valid JWT
- [ ] Semantic search returns results
- [ ] Rating creation works
- [ ] Recommendations endpoint works
- [ ] Memory usage < 400MB (run `scripts/check_memory.py`)

---

## Koyeb Deployment

### Repository Setup
- [ ] Code pushed to GitHub
- [ ] `.env` file in `.gitignore` (never commit secrets!)
- [ ] `api/.env` excluded from repo

### Koyeb Configuration
- [ ] GitHub account connected to Koyeb
- [ ] New service created from repository
- [ ] Branch selected (main/master)
- [ ] Build command: (leave empty, uses Procfile)
- [ ] Instance type: **Nano (512MB RAM, 0.1 vCPU)**
- [ ] Region selected (closest to users)

### Environment Variables in Koyeb
- [ ] `SUPABASE_URL` added
- [ ] `SUPABASE_KEY` added
- [ ] `JWT_SECRET_KEY` added
- [ ] `PORT` (auto-set by Koyeb, verify it's there)

### Deployment
- [ ] Initial deployment successful
- [ ] Health check endpoint accessible
- [ ] Logs show "Model loaded successfully"
- [ ] No memory errors in logs
- [ ] API responds to requests

---

## GitHub Actions (Daily Sync)

### Repository Secrets
- [ ] `TMDB_API_KEY` added to GitHub secrets
- [ ] `SUPABASE_URL` added to GitHub secrets
- [ ] `SUPABASE_KEY` added to GitHub secrets
- [ ] `HF_TOKEN` added (optional, for Hugging Face)

### Workflow
- [ ] `.github/workflows/sync.yml` exists
- [ ] Workflow enabled in GitHub Actions
- [ ] Manual trigger works (workflow_dispatch)
- [ ] Scheduled run configured (daily at midnight UTC)
- [ ] First sync completed successfully

---

## Post-Deployment Verification

### API Endpoints
- [ ] `GET /` - Health check returns 200
- [ ] `POST /auth/register` - Creates user
- [ ] `POST /auth/login` - Returns JWT
- [ ] `GET /auth/me` - Returns user profile (with JWT)
- [ ] `GET /search/semantic` - Returns search results
- [ ] `POST /ratings` - Saves rating (with JWT)
- [ ] `GET /recommendations/personalized` - Returns recommendations (with JWT)
- [ ] `GET /recommendations/popular` - Returns popular items
- [ ] `GET /movies` - Lists movies

### Performance
- [ ] Response time < 500ms for search
- [ ] Response time < 1s for recommendations
- [ ] No 503 errors (cold starts)
- [ ] No 500 errors in logs
- [ ] Memory usage stable (check Koyeb metrics)

### Security
- [ ] JWT tokens expire correctly (7 days)
- [ ] Invalid tokens rejected (401)
- [ ] Password hashing works (bcrypt)
- [ ] CORS restricted to your domain (or * for testing)
- [ ] No sensitive data in logs
- [ ] HTTPS enabled (Koyeb provides this)

---

## Monitoring Setup (Optional)

### Koyeb Metrics
- [ ] CPU usage monitored
- [ ] Memory usage monitored
- [ ] Request count tracked
- [ ] Error rate tracked

### Custom Monitoring
- [ ] Prometheus endpoint added (optional)
- [ ] Grafana dashboard configured (optional)
- [ ] Alert rules set up (optional)

---

## Frontend Integration

### API URL
- [ ] Frontend configured with production API URL
- [ ] CORS allows frontend domain
- [ ] JWT stored securely (httpOnly cookies or localStorage)

### Testing
- [ ] Registration flow works
- [ ] Login flow works
- [ ] Search works
- [ ] Rating works
- [ ] Recommendations display correctly

---

## Rollback Plan

### If Deployment Fails
1. Check Koyeb logs for errors
2. Verify environment variables
3. Test locally with same config
4. Rollback to previous deployment in Koyeb
5. Fix issues and redeploy

### Common Issues
- **Out of Memory**: Reduce workers to 1, check OMP_NUM_THREADS
- **Database Connection**: Verify SUPABASE_KEY is service role key
- **Model Loading**: Check internet connection, fastembed downloads on first run
- **Slow Responses**: Check database indexes, optimize queries

---

## Production Checklist

### Security
- [ ] Change default JWT secret
- [ ] Use strong passwords for test accounts
- [ ] Enable rate limiting (optional)
- [ ] Add request validation
- [ ] Sanitize user inputs

### Performance
- [ ] Database indexes optimized
- [ ] Query performance tested
- [ ] Caching strategy planned
- [ ] CDN for static assets (if applicable)

### Scalability
- [ ] Database connection pooling configured
- [ ] Horizontal scaling plan (if needed)
- [ ] Load balancing strategy (if needed)

### Maintenance
- [ ] Backup strategy for database
- [ ] Log retention policy
- [ ] Update schedule for dependencies
- [ ] Monitoring alerts configured

---

## Success Criteria

✅ **Deployment is successful when:**
- Health check returns 200
- Users can register and login
- Search returns relevant results
- Recommendations work for users with ratings
- Memory usage stays under 400MB
- No errors in production logs
- Response times < 1 second

---

## Support

If you encounter issues:
1. Check Koyeb logs
2. Review `BACKEND_SETUP.md`
3. Run `test_api.py` locally
4. Check Supabase logs
5. Verify environment variables

---

**Last Updated**: January 2026
**Version**: 2.0.0
