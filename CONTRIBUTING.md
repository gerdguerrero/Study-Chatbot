# Contributing to AI Study Chatbot

Thank you for your interest in contributing to the AI Study Chatbot! 🎉

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/Study-Chatbot.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up your `.env` file with OpenAI API key

## Development Setup

1. **Environment Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Run Tests** (when available):
   ```bash
   pytest tests/
   ```

## Areas for Contribution

### High Priority
- [ ] **Testing**: Unit tests for core components
- [ ] **Security**: Input validation and file sanitization
- [ ] **Error Handling**: Better user-friendly error messages
- [ ] **Performance**: Caching and optimization

### Medium Priority
- [ ] **Documentation**: API documentation and tutorials
- [ ] **Features**: Support for DOCX, TXT files
- [ ] **UI/UX**: Improved interface design
- [ ] **Multi-language**: Support for non-English content

### Low Priority
- [ ] **Analytics**: Usage tracking and metrics
- [ ] **Deployment**: Docker containerization
- [ ] **Collaboration**: Multi-user features

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and small

## Submitting Changes

1. **Create Pull Request**:
   - Describe what your changes do
   - Include screenshots if UI changes
   - Reference any related issues

2. **Code Review**:
   - Address review comments
   - Keep PR scope focused
   - Update documentation if needed

## Reporting Issues

- Use the GitHub Issues template
- Include error messages and logs
- Describe steps to reproduce
- Mention your environment (Python version, OS, etc.)

## Questions?

- Open a GitHub Discussion
- Check existing issues and documentation
- Be respectful and helpful to other contributors

Thank you for helping make study more effective with AI! 🚀