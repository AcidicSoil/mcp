# 🐳 Codex Container Solution

## Overview

This document describes the implementation of the **Phase 1 Environment Variable Solution** for running Codex in Docker containers. This solution addresses the core issues preventing Codex CLI from working properly in containerized environments.

## ⚠️ Problem Background

Codex CLI had the following issues when running in containers:

1. **Interactive UI Framework**: Codex uses the Ink UI framework which requires interactive stdin, but Docker containers can't provide proper stdin for interactive prompts
2. **Git Repository Check**: Git repository validation occurs BEFORE command-line flag processing, causing failures even with approval flags
3. **Missing Container Flags**: TypeScript CLI lacks `--skip-git-repo-check` flag (exists only in Rust version)

## ✅ Solution Implementation

### Environment Variables Added

The container now sets these environment variables to bypass interactive issues:

- `CODEX_QUIET_MODE=1` - Enables quiet mode, completely bypassing Ink UI framework
- `CODEX_DISABLE_PROJECT_DOC=1` - Disables project documentation loading
- `GIT_CONFIG_NOSYSTEM=1` - Bypasses system git configuration issues

### Command Line Changes

Changed from:

```bash
codex --dangerously-auto-approve-everything ${quoted_args}
```

To:

```bash
CODEX_QUIET_MODE=1 \
CODEX_DISABLE_PROJECT_DOC=1 \
GIT_CONFIG_NOSYSTEM=1 \
codex --quiet --full-auto ${quoted_args}
```

### Git Repository Initialization

Added automatic git repository initialization to prevent git-related failures:

```bash
git init && git config user.email 'container@codex.local' && git config user.name 'Codex Container'
```

## 🚀 Usage

### Building the Container

```bash
cd codex-cli
./scripts/build_container.sh
```

### Running Commands in Container

```bash
# Basic usage
./scripts/run_in_container.sh "your command here"

# With custom work directory
./scripts/run_in_container.sh --work_dir /path/to/project "your command here"

# Example: List files
./scripts/run_in_container.sh "list all files in this directory"
```

### Testing the Solution

Run the comprehensive test suite:

```bash
./scripts/test_container.sh
```

This will test:

- File operations
- Git functionality
- Environment variables
- Basic Codex commands

## 🔧 Configuration

### Local LLM Integration

The container automatically detects local LLM servers and adjusts configuration:

**For LM Studio or local servers:**

```bash
export OPENAI_BASE_URL="http://127.0.0.1:1234/v1"
export OPENAI_API_KEY="lm-studio"  # or your key
./scripts/run_in_container.sh "your command"
```

**Model configuration is automatically set to:**

- Local servers: `qwen3-4b-64k-128k-256k-context`
- Remote servers: `codex-mini-latest`

### Network Configuration

The container uses `--network=host` to enable:

- Connection to local LLM servers (127.0.0.1, localhost)
- Simplified networking without port mapping issues

### Security Features

Container maintains security through:

- Non-root user execution (node user)
- Network restrictions via iptables (for remote APIs)
- Directory sandboxing
- Allowed domain controls

## 🏗️ Architecture

### Container Build Process

1. **Build Phase** (`build_container.sh`):

   - Installs dependencies via pnpm
   - Builds the project
   - Packages as npm tarball
   - Creates Docker image with Codex CLI

2. **Runtime Phase** (`run_in_container.sh`):
   - Sets environment variables for quiet mode
   - Initializes git repository if needed
   - Configures network and security
   - Executes Codex with proper flags

### File Structure

```
codex-cli/
├── scripts/
│   ├── build_container.sh      # Build the container
│   ├── run_in_container.sh     # Run commands in container (MODIFIED)
│   ├── test_container.sh       # Test the container solution (NEW)
│   └── init_firewall.sh        # Container firewall setup
├── Dockerfile                  # Container definition
└── CONTAINER_SOLUTION.md       # This documentation (NEW)
```

## 🧪 Testing

### Automated Tests

The `test_container.sh` script validates:

1. **File Operations**: Can read/write files in mounted directories
2. **Git Operations**: Git commands work after initialization
3. **Environment Variables**: All required variables are set
4. **Codex Commands**: Basic Codex functionality works

### Manual Testing

Test with simple commands first:

```bash
# Test file listing
./scripts/run_in_container.sh "ls -la"

# Test git status
./scripts/run_in_container.sh "git status"

# Test environment check
./scripts/run_in_container.sh "env | grep CODEX"
```

## 🐛 Troubleshooting

### Common Issues

**1. "Repository not found" errors:**

- Solution: The script now auto-initializes git repositories
- Manual fix: Run `git init` in your project directory

**2. "Interactive prompt" errors:**

- Solution: Environment variables should prevent this
- Check: Ensure `CODEX_QUIET_MODE=1` is set

**3. "Model not found" errors:**

- Check your `OPENAI_BASE_URL` and `OPENAI_API_KEY`
- Verify LM Studio is running and accessible

**4. Network connection issues:**

- For local LLMs: Ensure LM Studio allows local connections
- For remote APIs: Check firewall configuration

### Debug Mode

Add debug output to container execution:

```bash
# Add to run_in_container.sh for debugging
docker exec "$CONTAINER_NAME" bash -c "set -x; cd \"/app$WORK_DIR\" && ..."
```

## 📈 Performance Considerations

### Container Overhead

- Container startup: ~2-3 seconds
- Command execution: Similar to host performance
- Memory usage: Slightly higher due to container overhead

### Optimization Tips

1. **Reuse containers**: The script reuses existing containers when possible
2. **Local LLMs**: Use `--network=host` for best local LLM performance
3. **Volume mounting**: Projects are mounted read-write for full functionality

## 🔄 Future Improvements

### Planned Enhancements

1. **Better Error Handling**: More specific error messages and recovery
2. **Logging Integration**: Container-specific logging configuration
3. **Performance Optimization**: Reduce container startup time
4. **Multi-platform Support**: ARM64 container images

### Monitoring Codex Updates

Watch for these potential upstream improvements:

- `--skip-git-repo-check` flag in TypeScript CLI
- Native container mode support
- Better quiet mode features

## 🤝 Contributing

When modifying the container solution:

1. **Test thoroughly**: Run `test_container.sh` after changes
2. **Update documentation**: Keep this file current
3. **Maintain backward compatibility**: Ensure existing workflows continue working
4. **Security first**: Don't compromise container security for convenience

## 📚 Additional Resources

- [Codex CLI Documentation](../README.md)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [LM Studio Documentation](https://lmstudio.ai/docs)

---

**Implementation Status**: ✅ Phase 1 Complete - Environment Variable Solution
**Next Phase**: Monitor usage and consider source code modifications if needed
**Tested With**: Docker 24.x, Node.js 22, LM Studio 0.3.x
