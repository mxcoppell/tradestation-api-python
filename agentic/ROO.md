# Roo AI Agent System

## Introduction

**Roo** is an advanced AI-powered software engineering assistant that serves as an intelligent development partner for the TradeStation API Python project. Roo operates as a highly skilled software engineer with extensive knowledge across multiple programming languages, frameworks, design patterns, and best practices.

The primary role of Roo in this project is to:
- Assist with code development, refactoring, and optimization
- Provide architectural guidance and design recommendations
- Debug and troubleshoot issues systematically
- Maintain code quality and consistency across the codebase
- Automate DevOps tasks and infrastructure management
- Orchestrate complex, multi-step development workflows

Roo operates through a mode-based system, allowing it to specialize its behavior based on the task at hand while maintaining consistent coding standards and project conventions.

---

## Agent Modes

Roo operates in different specialized modes, each optimized for specific types of tasks:

### 💻 Code Mode (`code`)
**Primary Use**: Writing, modifying, or refactoring code

The Code mode is ideal for:
- Implementing new features and functionality
- Fixing bugs and issues
- Creating new files and modules
- Making code improvements and optimizations
- Refactoring existing code for better maintainability
- Working across any programming language or framework

### ❓ Ask Mode (`ask`)
**Primary Use**: Explanations, documentation, and technical answers

The Ask mode is best for:
- Understanding concepts and architectural decisions
- Analyzing existing code and its behavior
- Getting recommendations and best practices
- Learning about technologies without making changes
- Generating documentation and technical explanations
- Code reviews and feedback

### 🏗️ Architect Mode (`architect`)
**Primary Use**: Planning, design, and strategy

The Architect mode excels at:
- Breaking down complex problems into manageable components
- Creating technical specifications and architecture documents
- Designing system architecture and data flows
- Brainstorming solutions before implementation
- Planning project structure and organization
- Strategic decision-making for technical challenges

### 🪲 Debug Mode (`debug`)
**Primary Use**: Troubleshooting and diagnostics

The Debug mode specializes in:
- Systematic debugging of issues and errors
- Adding logging and diagnostic instrumentation
- Analyzing stack traces and error messages
- Identifying root causes of problems
- Investigation and diagnosis before applying fixes
- Performance profiling and optimization

### 🪃 Orchestrator Mode (`orchestrator`)
**Primary Use**: Complex, multi-step project coordination

The Orchestrator mode is ideal for:
- Breaking down large tasks into subtasks
- Managing workflows across multiple domains
- Coordinating work that spans different specialties
- Complex projects requiring multiple expertise areas
- High-level project management and coordination

### 🚀 DevOps Mode (`devops`)
**Primary Use**: Deployment, infrastructure, and automation

The DevOps mode handles:
- Deploying applications to various environments
- Managing cloud infrastructure and resources
- Setting up CI/CD pipelines and automation
- Provisioning and configuring infrastructure
- Environment management and configuration
- Setting up monitoring and alerting systems
- Infrastructure-as-Code operations

---

## Key Principles

### 🔒 Branch Protection & Pull Request Workflow

**CRITICAL**: All code changes in this project MUST follow these strict guidelines:

#### ⚠️ Never Commit Directly to Main/Master
- **ALL** future code changes MUST be done in a feature branch
- **NEVER** commit or push directly to the `main` or `master` branch
- The main branch is protected and should only be updated through Pull Requests

#### 🌿 Feature Branch Naming Convention
All feature branches must follow the standardized naming convention:

```
feature/issue-XXX-brief-description
```

Or for security-related fixes:

```
feature/security-fix-description
```

**Examples:**
- `feature/issue-123-add-streaming-support`
- `feature/issue-456-fix-rate-limiter`
- `feature/security-fix-token-validation`
- `feature/issue-789-refactor-market-data-service`

#### 📝 Pull Request Requirement
- **ALL** changes MUST use Pull Requests (PRs) to merge into the main branch
- PRs enable:
  - Code review and quality assurance
  - Automated testing and validation
  - Discussion and collaboration
  - Change tracking and documentation
  - Rollback capability if needed

#### 🔄 Standard Workflow Summary
```
1. Create feature branch from main
2. Make changes in feature branch
3. Commit changes to feature branch
4. Push feature branch to remote
5. Create Pull Request to merge into main
6. Review and approve PR
7. Merge PR into main
8. Delete feature branch (optional cleanup)
```

---

## Workflow

### Standard Development Workflow

When working with Roo on this project, follow this standard workflow:

#### 1. **Task Analysis**
```
→ Understand the requirement or issue
→ Determine the appropriate Roo mode for the task
→ Review existing code and documentation
```

#### 2. **Branch Creation**
```bash
# Ensure you're on the main branch
git checkout main

# Pull the latest changes
git pull origin main

# Create a new feature branch
git checkout -b feature/issue-XXX-brief-description
```

#### 3. **Development**
```
→ Work with Roo in the appropriate mode
→ Make incremental changes
→ Test changes locally
→ Commit changes with clear messages
```

#### 4. **Testing & Validation**
```bash
# Run tests
pytest

# Check code quality
# (Add linting/formatting commands as needed)
```

#### 5. **Commit & Push**
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: brief description of changes"

# Push to remote
git push origin feature/issue-XXX-brief-description
```

#### 6. **Pull Request**
```
→ Create PR on GitHub/GitLab/etc.
→ Provide clear description of changes
→ Link to relevant issues
→ Request review from team members
→ Address review feedback
```

#### 7. **Merge & Cleanup**
```
→ Merge PR after approval
→ Delete feature branch (optional)
→ Pull updated main branch locally
```

### Iterative Development with Roo

Roo works iteratively, breaking down complex tasks into manageable steps:

1. **Goal Setting**: Roo analyzes your task and sets clear, achievable goals
2. **Sequential Execution**: Each goal is addressed one at a time
3. **Tool Utilization**: Roo uses available tools effectively (file operations, command execution, etc.)
4. **Feedback Loop**: After each step, Roo receives feedback and adapts accordingly
5. **Completion**: Once the task is complete, Roo presents the final result

### Best Practices

- **Be Specific**: Provide clear, detailed requirements to Roo
- **Context Matters**: Share relevant background information and constraints
- **Iterative Refinement**: Review Roo's work and provide feedback for improvements
- **Follow Standards**: Ensure all code follows project conventions and style guides
- **Document Changes**: Keep documentation up-to-date with code changes
- **Test Thoroughly**: Always test changes before creating a PR

---

## Related Documentation

For more detailed information about working with Roo and this project, refer to these additional documents:

### 📋 [AGENT-INSTRUCTION.md](./AGENT-INSTRUCTION.md)
Comprehensive instructions and guidelines for the AI agent system, including:
- Detailed operational procedures
- Code quality standards
- Testing requirements
- Project-specific conventions

### 🎓 [CONTINUOUS-SELF-LEARNING.md](./CONTINUOUS-SELF-LEARNING.md)
Framework for continuous improvement and learning, covering:
- Learning from past interactions
- Adapting to project patterns
- Knowledge base building
- Performance optimization

### 📊 [PLANNING.md](./PLANNING.md)
Project planning and roadmap documentation, including:
- Feature planning and prioritization
- Technical debt tracking
- Future enhancements
- Development milestones

---

## Tips for Effective Collaboration with Roo

1. **Start with Clear Objectives**: Define what you want to accomplish before engaging Roo
2. **Use the Right Mode**: Select the appropriate mode for your task (Code, Debug, Architect, etc.)
3. **Provide Context**: Share relevant files, error messages, or background information
4. **Review Incrementally**: Check Roo's work after each significant step
5. **Ask Questions**: Use Ask mode when you need clarification or explanations
6. **Follow the Workflow**: Always use feature branches and PRs as outlined above
7. **Stay Organized**: Keep your workspace clean and organized for better results

---

## Summary

Roo is your intelligent development partner, designed to accelerate development while maintaining high code quality standards. By leveraging Roo's various modes and following the established workflow principles—especially the **mandatory feature branch and Pull Request workflow**—you can efficiently build, maintain, and evolve the TradeStation API Python project.

Remember: **Never commit directly to main. Always use feature branches and Pull Requests.**

---

*Last Updated: 2026-01-03*
