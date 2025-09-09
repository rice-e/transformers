# AI-Assisted Development Workflow Guide

**Note for AI Assistants**: This document is primarily a resource for AI (Claude) to understand the correct workflow for feature development. The key principle is that **implementation phases are defined in design documents, and AI helps implement each phase individually** using Plan Mode.

## Quick Reference

**Common Commands:**
- Start new feature: Create `docs/N.feature_name.md` with phases
- Implement phase: "Make a plan to implement Phase 1 from docs/N"
- Test phase: Human runs tests, AI suggests commands
- Style check: `make fixup` when completing phases or before pushing

**When to Use This Workflow:**
- ✅ **USE for**: New features, complex refactors, architecture changes (>50 lines)
- ❌ **SKIP for**: Simple bug fixes (<10 lines), typos, config updates

**AI's Role:**
- Collaborate on design documents when asked
- Create detailed phase implementation plans
- Implement code following specifications
- Suggest tests and quality checks
- Human retains all decision-making authority

## Executive Summary

This document describes a proven AI-assisted development workflow that maximizes the effectiveness of AI coding assistants like Claude Code. The workflow emphasizes **design-first development**, where comprehensive design documents guide AI implementation, resulting in higher quality code, fewer iterations, and better alignment with project goals.

**Core Principle**: *Design thoroughly, implement systematically, review iteratively.*

## 1. Workflow Philosophy

### Why Design-First Development with AI?

Traditional AI coding assistance often involves ad-hoc requests that lack context, leading to:
- Misaligned implementations
- Frequent rewrites
- Lost context between sessions
- Difficulty maintaining consistency across features

This workflow solves these problems by:
1. **Establishing Clear Context**: Design documents provide complete context for AI
2. **Enabling Systematic Implementation**: AI can work through well-defined stages
3. **Maintaining Consistency**: Templates ensure uniform approach across features
4. **Facilitating Review**: Clear before/after states make review straightforward
5. **Building Knowledge Base**: Design docs become living documentation

## 2. Example Design Document Structure

Every feature should have a design document. Here's an example structure that can be adapted based on the complexity and needs of your specific feature:

### Standard Design Document Sections

```markdown
# [Feature Name] Design

### 1. Executive Summary
Brief overview of what the feature does and why it's needed.

### 2. Problem Statement
### Context
Background information and current system state

### Challenges
Specific problems this feature addresses

### Objectives
Primary and secondary goals

### 3. High-Level Design
Conceptual overview of the solution approach

### 4. Architecture & Integration Points
### New Concept Entities
New classes, data structures, or abstractions

### Integration Points
Where and how the feature integrates with existing code

### Architecture Diagram
Visual representation of component relationships

### 5. New Workflow Logic
### Before (Current State)
How the system currently works

### After (With Feature)
How the system will work with the new feature

### Workflow Diagram
Visual flow comparison

### 6. Implementation Details
### Algorithm Design
Detailed algorithmic approach with pseudocode

### Data Structures
Specific data structure choices and rationale

### API Changes
New or modified interfaces

### 7. Implementation Phases
Break down implementation into logical phases for AI-assisted development. Under each phase, include necessary details for planning.

**Note**: Use **Stages** for substantial development steps (e.g., Stage 1: Foundation, Stage 2: Integration) and **Phases** for implementation sub-steps within each stage.

Example phases within a stage:
- [ ] Phase 1: Data Structures
- [ ] Phase 2: Core Algorithm  
- [ ] Phase 3: Integration
- [ ] Phase 4: Testing & Polish

```

### Best Practices for Design Documents

1. **Be Specific**: Include concrete examples, not just abstractions
2. **Show Comparisons**: Always include before/after states
3. **Use Diagrams When Helpful**: Visual representations clarify complex relationships (optional based on feature complexity)
4. **Include Code Snippets**: Show key interfaces and data structures
5. **Define Implementation Phases**: Break down work into logical phases for AI collaboration
6. **Track Status**: Maintain implementation checkboxes
7. **Reference Dependencies**: Link to related design documents

### Critical: Implementation Phases Section

**Every numbered feature document must include a Phases section** that breaks down implementation into logical steps. Each numbered document represents one complete stage. This enables effective AI collaboration through commands like:

```
"Please make a plan to implement Phase 1 from docs/5.task_scheduler_design.md"
```

**Important**: When implementing, do not create additional stages or design documents within a single numbered document.

The AI will then create detailed implementation steps such as:
1. Create TaskQueue class with priority handling
2. Add PriorityCalculator with configurable weights  
3. Implement ResourceTracker with GPU monitoring
4. Add unit tests for core data structures

## 3. Workflow Stages

### Stage 1: Problem Definition & Design Document Creation

1. **Identify the Problem**
   - Clear problem statement
   - Current limitations
   - Success criteria

2. **Draft Initial Design with AI Collaboration**
   **AI can collaborate on design documents when asked:**
   - Research existing patterns and architectural approaches
   - Suggest implementation strategies and alternatives
   - Help structure the document and identify sections
   - Identify potential edge cases and integration points
   - Review and refine design language and clarity

3. **Define Implementation Phases**: The design document must include a clear Phases section that breaks down implementation within the current stage:
   ```markdown
   ## Implementation Phases
   
   ### Phase 1: Data Structures
   - [ ] Create TaskQueue class
   - [ ] Add PriorityCalculator component
   - [ ] Implement ResourceTracker
   
   ### Phase 2: Core Algorithm
   - [ ] Implement scheduling logic
   - [ ] Add conflict resolution
   - [ ] Optimize performance
   ```

### Stage 2: Phase Implementation Cycle

**Key Point**: AI plans and implements **individual phases only**, not entire features.

**For Each Phase** (repeat until all phases complete):

1. **Plan Phase**
   ```
   Human: "Please make a plan to implement Phase 1 from docs/5.task_scheduler_design.md"
   ```
   - AI reads phase requirements and creates implementation steps
   - Human reviews and approves plan

2. **Implement Phase**  
   - AI executes approved plan step-by-step
   - Human reviews implementation and requests adjustments
   - Update phase checkboxes in design document

3. **Test Phase**
   ```
   Human runs: pytest tests/scheduler/test_data_structures.py -v
   ```
   - Verify phase meets requirements before proceeding

### Stage 3: Final Integration Testing

1. **End-to-End Testing**
2. **Bug Fixes & Refinement**
   - Human identifies issues and references design document  
   - AI implements fixes and human retests

### Stage 4: Documentation and Closure

1. **Update Design Document**
   - Mark implementation status complete
   - Document any deviations and lessons learned

2. **Code Quality and Style Checks**
   Run when: completing features, preparing PRs, between major phases

3. **Knowledge Transfer**
   - Add entry to Key Design Decisions Log in central `0.` document  
   - Archive decisions

## 4. Document Organization

### Directory Structure
```
project/
├── docs/
│   ├── 0.unified_design.md          # Central design document
│   ├── 1.feature_a_design.md        # Numbered for ordering
│   ├── 2.feature_b_design.md
│   ├── ...
│   ├── 19.feature_x_design.md
│   ├── review.md                    # Issue tracking
│   └── todo.md                      # Future work
├── src/
│   └── ...
└── CLAUDE.md                         # AI assistant instructions
```

### Numbering Convention
- Use numeric prefixes (1-99) for implementation order
- 0 prefix for central/unified documents

### Document Types

1. **Central Design Document** (`0.*.md`)
   - System-wide architecture
   - Component relationships
   - Updated as features are added

2. **Feature Design Documents** (`N.feature_*.md`)
   - Individual feature designs
   - Follow standard template
   - Reference central design

## 5. Common Patterns and Anti-Patterns

### Patterns (Good Practices)

1. **Progressive Refinement**
   - Start with high-level design
   - Add details through iterations
   - Validate at each stage

2. **Clear Boundaries**
   - Design doc defines "what"
   - Implementation defines "how"
   - Tests validate "correctness"

3. **Continuous Documentation**
   - Update design docs during implementation
   - Document deviations and reasons
   - Capture lessons learned

### Anti-Patterns (Avoid These)

1. **Implementation Without Design**
   - Leads to inconsistent architecture
   - Causes frequent rewrites
   - Results in technical debt

2. **Over-Detailed Design**
   - Spending too much time on minor details
   - Inflexible to discoveries during implementation
   - Delays actual coding

3. **Batch Implementation**
   - Trying to implement everything at once
   - Missing feedback opportunities
   - Harder to debug issues

---


## 6. Design Document Evolution and Patterns

### Design Document as Living Artifacts

Design documents should evolve throughout implementation rather than being static specifications. They serve as both planning tools and historical records of design decisions.

#### The Key Design Decisions Log Pattern

**IMPORTANT**: The Key Design Decisions Log is for tracking **COMPLETED features only**, not initial design plans or intentions.

**Workflow**:
1. **During Planning**: Create individual feature design documents (e.g., `1.partial_gpu_allocation.md`) with detailed phases and implementation plans
2. **During Development**: Update feature-specific design documents with discoveries and refinements  
3. **After Completion**: Once feature is implemented and pushed to working branch, add a summary entry to the central `0.` document's log
4. **Historical Record**: The log becomes a permanent record of what was actually built and why

**Format**:
```markdown
## Key Design Decisions Log
This section is append-only and records all design decisions and features added throughout development. Later decisions take precedence over earlier ones in case of conflicts.

### 1. [Completed Feature Name]  
**Decision**: [What was actually implemented]
- [Key implementation details]
- [Final architecture choices]
- **Rationale**: [Why this approach was taken]
- **Details**: See @./1.feature_name_design.md for complete implementation design

### 2. [Next Completed Feature]
...
```


## 7. Defensive Programming Principles for AI Development

### The Complexity Trap

AI-assisted development can lead to over-engineering because it's easy to ask AI to "add safety checks" or "handle edge cases." This often creates more bugs than it prevents.

#### Core Principle: Simple Failures Over Complex Fallbacks

**The Problem**: Each layer of defensive programming adds potential failure points and makes debugging harder.

### Example: Anti-Pattern vs Good Pattern

```python
# ❌ AVOID: Defensive complexity that hides real issues
def process_data_badly(data):
    # This is a conceptual example showing problematic patterns
    try:
        if not data_is_valid(data):
            try:
                data = attempt_fix(data)
                if not data_is_valid(data):
                    try:
                        data = get_fallback_data()
                    except Exception:
                        return None  # Hidden failure!
            except Exception:
                return None  # Another hidden failure!
        return do_processing(data)
    except Exception as e:
        print(f"Processing failed: {e}")  # Logs but still hides failure
        return None

# ✅ PREFER: Clear failure modes with actionable errors  
def process_data_well(data):
    """Process data with clear error handling."""
    if not data_is_valid(data):
        raise ValueError(f"Invalid data: {get_validation_errors(data)}")
    
    return do_processing(data)
```

#### When NOT to Add Defensive Code

1. **Performance Edge Cases**: Don't add safety checks for theoretical performance issues
2. **Input Validation Excess**: Trust well-tested library input validation  
3. **State Consistency Paranoia**: Avoid redundant validation of proven-stable state
4. **Recovery Complexity**: Don't try to recover from fundamental system errors

#### The Right Kind of Defensive Programming

**Good Defensive Patterns:**
- **Assertions for invariants** during development (removed in production)
- **Early parameter validation** with clear error messages
- **Resource cleanup** in finally blocks or context managers  
- **Type hints and contracts** that prevent misuse
- **Comprehensive logging** of actual failures (not potential failures)

### Defensive Principles for AI-Assisted Development

#### 1. Let AI Handle Complexity, Keep Safety Simple
- Use AI for complex algorithms and data structures
- Keep error handling and edge case management simple and explicit
- Don't ask AI to "make it more robust" - ask for specific error handling

#### 2. Prefer Library Defaults
- Trust well-tested libraries (like transformers) for standard validation
- Don't wrap library calls unless you have specific requirements
- Focus defensive energy on your novel logic, not library integration

#### 3. Fail Fast with Context  
- Provide detailed error messages that help users fix problems
- Include relevant context (model name, parameter values, system state)
- Don't catch and ignore exceptions unless you have specific recovery logic

---

*A collaborative methodology for design-first AI-assisted software development*