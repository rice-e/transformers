# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Code Quality and Style
```bash
# Fix style and consistency issues (use this frequently)
make fixup

# Check code quality without fixing
make quality

# Format and fix all files
make style

# Install quality dependencies
pip install -e .[quality]
```

### Testing
```bash
# Run all tests
make test
pytest -n auto --dist=loadfile -s -v ./tests/

# Run tests for specific model
pytest tests/models/[model_name]/test_modeling_[model_name].py

# Run tests for tokenizers/processors
pytest tests/models/[model_name]/test_tokenization_[model_name].py
pytest tests/models/[model_name]/test_processing_[model_name].py

# Install testing dependencies
pip install -e .[testing]
pip install torch accelerate  # if not already installed
```

### Environment and Dependencies
```bash
# Check environment info
transformers env
# or from repo root:
python src/transformers/commands/transformers_cli.py env
```

## High-level Architecture

### Core Structure
- `/src/transformers/`: Main source code
  - `/models/`: Individual model implementations (self-contained)
  - Base classes and utilities in root directory
- `/tests/`: Test classes (usually inherited rather than run directly)  
  - `/models/`: Model-specific tests that inherit from common test classes
- `/docs/`: Documentation, guides, tutorials, and API references

### Key Design Principles
- **Self-contained model files**: All necessary code for a model is in its `modeling_[model].py` file
- **Composition over abstraction**: Prefer explicit, readable code over complex inheritance
- **Duplicate code is acceptable**: If it improves readability and accessibility
- **Brief PRs**: Especially for bugfixes - often just 1-2 lines, no need for extensive comments

### Model Organization

#### Modular Files
Some models use a "modular" approach:
- `modular_[model].py`: Defines models using inheritance from other models
- Style tools automatically generate complete `modeling_[model].py` files
- **NEVER edit generated modeling files directly** - edit the modular file instead
- Run `make fixup` after editing modular files to update generated files

#### "Copied from" Syntax
Functions/classes can have comments like:
```python
# Copied from transformers.models.llama.modeling_llama.rotate_half
# Copied from transformers.models.t5.modeling_t5.T5LayerNorm with T5->MT5
```
- Automatically checked and updated by style tools
- To update: either update the base function and run `make fixup`, or remove the comment
- Use `make fixup` to propagate changes to all copies

## Development Workflow

### Making Changes
1. **Always run `make fixup`** after changes to update copies and modular files
2. **Test all affected models** - both the one you changed and any updated by `make fixup`
3. **Add tests to existing files** - only create new test directories for new models
4. **Keep PRs minimal** - especially bugfixes should be as small as possible

### Adding New Models
- Prefer the modular approach when possible (inherit from existing models)
- Follow the existing model structure and naming conventions
- Models should be self-contained in their modeling file
- See `docs/source/en/add_new_model.md` for detailed guidance

### Code Style
- Uses `ruff` for formatting and linting (line length: 119 characters)
- Python 3.9+ target
- Follow existing patterns in similar model files
- Code style is enforced in CI

## Testing Strategy

### Test Organization
- Tests inherit from common test classes in `/tests/` root
- Model tests go in `/tests/models/[model_name]/`
- Add to existing test files unless adding a completely new model
- Test files follow pattern: `test_modeling_[model].py`, `test_tokenization_[model].py`, etc.

### Running Tests
Always test changes thoroughly:
- Run tests for the model you modified
- Run tests for any models affected by `make fixup` 
- Use pytest markers to run specific test categories if needed

## Important Notes

- **Environment**: Supports Python 3.9+, PyTorch 2.1+, TensorFlow 2.6+, Flax 0.4.1+
- **Dependencies**: Use appropriate extras (e.g., `[testing]`, `[quality]`) when installing
- **CI Integration**: Code style and quality checks run automatically
- **Self-contained principle**: Each model file should contain all necessary implementation details

## Development Methodology

For planning and implementing new features, see `docs/AI_WORKFLOW.md` which contains guidance on design-first development methodology using structured design documents and AI-assisted implementation.
- At the beginning of each new chat, please reference docs/AI_WORKFLOW.md