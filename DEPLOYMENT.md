# Deployment Information

## Public URL
https://lab12-production-41a2.up.railway.app/

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://test-deploy-production-e257.up.railway.app/health
# Expected: {"status": "ok", "uptime_seconds": ..., "platform": "Railway", ...}
```

### API Test (with authentication)
```bash
# Thay THAY_KEY_CUA_BAN bằng API Key thực tế của bạn
curl -X POST https://test-deploy-production-e257.up.railway.app/ask \
  -H "X-API-Key: your-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Khách sạn được không?"}'
```

## Environment Variables Set
- `PORT=8000`
- `AGENT_API_KEY=your-secret-key-123`
- `OPENAI_API_KEY=sk-xxxx`

## Screenshots
*(Vì đây là bài Lab giả lập, hãy tự chụp và thêm link ảnh screenshot màn hình Railway Dashboard và kết quả test của bạn vào đây).*
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
