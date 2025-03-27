# 🤖 AI DevOps Automation Lab

This repository is a sandbox for experimenting with **AI-powered DevOps automation**, focusing on:
- ✅ AI-driven **code review**
- ✅ Automated **unit test generation**
- ✅ Smart **code refactoring**

The project is built around a simulated multi-repo microservice environment, with each component representing a real-world stack. All automation is designed to work **both locally in VS Code** and inside **CI/CD environments like Azure DevOps**.

---

## 📦 Project Structure

| Folder     | Purpose                        | Tech Stack                                     | Base Repo Source |
|------------|--------------------------------|------------------------------------------------|------------------|
| `kj-BE/`   | Main backend (Product logic)   | Next.js, API routes, PostgreSQL, Stripe        | [nextjs/saas-starter](https://github.com/nextjs/saas-starter) |
| `sc-RP/`   | AI-powered backend service     | FastAPI, Celery, SQLModel, Docker              | [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) |
| `kj-MB/`   | Mobile app (Product client)    | React Native, Redux, Navigation                | [mcnamee/react-native-starter-kit](https://github.com/mcnamee/react-native-starter-kit) |
| `kj-FE/`   | Admin dashboard (Frontend)     | React, CoreUI, Bootstrap                       | [coreui/coreui-free-react-admin-template](https://github.com/coreui/coreui-free-react-admin-template) |
| `tools/`   | Shared AI scripts (DevOps)     | Python (OpenAI), CLI-automated workflows       | Custom scripts   |

---

## ⚙️ Automation Goals

| Task                        | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `✅ AI Code Review`         | Use OpenAI models to analyze diffs and PRs for security, style, and logic issues |
| `🔜 Unit Test Generation`   | Automatically generate unit tests based on function signatures and logic    |
| `🔜 Code Refactoring`       | Use LLMs to suggest or apply cleaner, more efficient implementations        |

---

## 🛠 How to Use (WIP)

### 🔁 Clone the Repo
```bash
git clone https://github.com/udhtaz/ai-devops-automation-lab.git
cd ai-devops-automation-lab

