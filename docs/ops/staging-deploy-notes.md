# Staging Deployment Notes

## Goal

Deploy main branch changes automatically to staging after CI checks and image build pass.

## Current baseline

- GitHub Actions workflow exists at .github/workflows/ci-cd.yml
- deploy-staging job is present and gated on successful checks/builds
- deployment command is a placeholder and must be wired to your infrastructure

## Next steps

1. Choose target runtime (VM + Docker Compose, ECS, Kubernetes, etc.)
2. Add repository secrets for staging credentials and target host/cluster
3. Replace deploy-staging placeholder with actual deployment command
4. Add post-deploy smoke test script (health, API, login, checkout sanity)
5. Configure GitHub environment protection for production manual approval
