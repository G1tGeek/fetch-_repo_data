
# Claude vs Ollama AI Integration with Jenkins

This guide provides a **complete, production-grade Proof of Concept (POC)** for integrating **AI models into Jenkins CI/CD pipelines**, covering both:

- **Claude (Anthropic – Cloud-hosted LLM API)**
- **Ollama (Self-hosted / Local LLM runtime)**

It includes:
- End-to-end setup steps
- Secure Jenkins credential handling
- Jenkinsfile examples
- Cost, security, and architecture comparison
- Decision guidance for enterprise teams

---

## 1. Scope & Use Cases in Jenkins

Both Claude and Ollama can be used inside Jenkins to:

- Analyze build and test failures
- Summarize logs and error traces
- Perform automated code review on diffs
- Explain security scan results (Trivy, Snyk, SonarQube)
- Generate release notes and changelogs
- Assist with Jenkinsfile, Dockerfile, Terraform generation
- Produce human-readable RCA (Root Cause Analysis)

---

## 2. Architecture Overview

### Claude (Anthropic API)
Jenkins → HTTPS → Anthropic API → Response → Jenkins Console / PR Comment

### Ollama (Local LLM)
Jenkins → Local/Internal HTTP → Ollama Runtime → Response → Jenkins Console

---

## 3. Claude Integration – POC Steps

### 3.1 Create Anthropic Account & API Key
1. Visit https://console.anthropic.com
2. Enable billing
3. Create an API key (store securely)

### 3.2 Store API Key in Jenkins
- Manage Jenkins → Credentials → Add Credentials
- Kind: Secret Text
- ID: `CLAUDE_API_KEY`

### 3.3 Jenkinsfile Example (Claude)

```groovy
pipeline {
  agent any
  environment {
    CLAUDE_API_KEY = credentials('CLAUDE_API_KEY')
  }
  stages {
    stage('Claude Analysis') {
      steps {
        sh '''
        LOGS=$(tail -n 100 build.log | sed 's/"/\\"/g')
        curl https://api.anthropic.com/v1/messages \
          -H "x-api-key: $CLAUDE_API_KEY" \
          -H "anthropic-version: 2023-06-01" \
          -H "content-type: application/json" \
          -d "{
            \"model\":\"claude-3-sonnet\",
            \"max_tokens\":300,
            \"messages\":[{\"role\":\"user\",\"content\":\"Analyze this Jenkins failure:\n$LOGS\"}]
          }"
        '''
      }
    }
  }
}
```

---

## 4. Ollama Integration – POC Steps

### 4.1 Install Ollama

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Pull a Model
```bash
ollama pull llama3
```

Ensure Ollama is running on `http://localhost:11434`.

### 4.2 Jenkinsfile Example (Ollama)

```groovy
pipeline {
  agent any
  stages {
    stage('Ollama Analysis') {
      steps {
        sh '''
        LOGS=$(tail -n 100 build.log)
        curl http://localhost:11434/api/generate \
          -d "{
            \"model\":\"llama3\",
            \"prompt\":\"Analyze this Jenkins failure:\n$LOGS\",
            \"stream\":false
          }"
        '''
      }
    }
  }
}
```

---

## 5. Claude vs Ollama – Detailed Comparison

| Dimension | Claude (Anthropic) | Ollama (Local LLM) |
|--------|-------------------|------------------|
| Hosting | Cloud (Managed) | Self-hosted |
| Internet Required | Yes | No |
| Setup Time | Very fast | Moderate |
| Cost Model | Pay-per-token | Infra-based |
| Output Quality | Excellent | Good |
| Long Context | Very strong | Limited |
| Security | Data leaves env | Fully private |
| Scaling | Automatic | Manual |
| Best For | Deep reasoning | Private workloads |

---

## 6. Cost Comparison

### Claude (Example – Sonnet)
- ~500 input + 500 output tokens
- ≈ $0.009 per request
- 1,000 runs/month ≈ $9

### Ollama
- $0 token cost
- Hardware / VM / GPU cost applies
- Predictable fixed cost

---

## 7. Security Best Practices

### Common
- Never send secrets, tokens, or private keys
- Truncate logs (last 50–200 lines)
- Mask credentials using regex

### Claude-Specific
- Review data compliance policies
- Avoid sensitive IP or PII

### Ollama-Specific
- Secure Ollama API (firewall / localhost only)
- Control access to Jenkins agents

---

## 8. Recommended Hybrid Pattern

Use **both**:

- Ollama for:
  - Routine summaries
  - High-volume CI jobs
- Claude for:
  - Complex failures
  - Release notes
  - Architecture reviews

Fallback logic:
- Try Ollama first
- Escalate to Claude for critical or repeated failures

---

## 9. Troubleshooting

| Error | Cause |
|----|----|
| 401 (Claude) | Invalid API key / billing |
| Model not found | Wrong model ID |
| Timeout | Payload too large |
| Ollama connection refused | Service not running |

---

## 10. Final Checklist

- Jenkins credentials configured
- Logs truncated
- Timeouts & retries added
- Cost monitoring enabled
- Access controls reviewed

---

## 11. Conclusion

- **Claude** delivers best-in-class reasoning with minimal ops effort.
- **Ollama** offers privacy, offline usage, and cost predictability.
- A **hybrid approach** provides maximum flexibility and ROI for CI/CD pipelines.

---

Prepared for production Jenkins environments.
