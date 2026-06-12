# Public Deployment Test Evidence

URL: 
https://ai-agent-production-djyv.onrender.com
Date: 
2026-06-12T17:12:29

## /health
`json
{"status":"ok","version":"1.0.0","environment":"production","instance_id":"agent-e311fb66","uptime_seconds":264.5,"total_requests":48,"checks":{"llm":"mock","redis":"ok"},"timestamp":"2026-06-12T10:11:01.289323+00:00"}
`

## /ready
`json
{"ready":true,"instance_id":"agent-e311fb66"}
`

## /ask with API key
`json
{"user_id":"submission-test","session_id":"submission-test:ac31dba6cb0c4b39acf612fb5a618217","question":"What is deployment?","answer":"Deployment means moving code to a server or cloud platform where users can access it.","model":"mock-llm","served_by":"agent-e311fb66","timestamp":"2026-06-12T10:11:01.748289+00:00"}
`

## Rate limit status codes
`	ext
200,200,200,200,200,200,200,200,200,200,429,429
`
