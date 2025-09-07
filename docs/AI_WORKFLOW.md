# AI-Assisted Development Workflow Guide

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

### Key Benefits

- **Reduced Implementation Time**: 50-70% faster than iterative trial-and-error
- **Higher Code Quality**: Implementations align with architectural principles
- **Better AI Performance**: Clear specifications enable optimal AI output
- **Knowledge Preservation**: Design decisions are documented for future reference
- **Parallel Development**: Multiple features can be designed before implementation

## 2. The Design Document Template

Every feature should have a design document following this structure:

### Standard Design Document Sections

```markdown
# [Feature Name] Design

## 1. Executive Summary
Brief overview of what the feature does and why it's needed.

## 2. Problem Statement
### Context
Background information and current system state

### Challenges
Specific problems this feature addresses

### Objectives
Primary and secondary goals

## 3. High-Level Design
Conceptual overview of the solution approach

## 4. Architecture & Integration Points
### New Concept Entities
New classes, data structures, or abstractions

### Integration Points
Where and how the feature integrates with existing code

### Architecture Diagram
Visual representation of component relationships

## 5. New Workflow Logic
### Before (Current State)
How the system currently works

### After (With Feature)
How the system will work with the new feature

### Workflow Diagram
Visual flow comparison

## 6. Implementation Details
### Algorithm Design
Detailed algorithmic approach with pseudocode

### Data Structures
Specific data structure choices and rationale

### API Changes
New or modified interfaces

## 7. Testing Strategy
### Unit Tests
Component-level testing approach

### Integration Tests
System-level testing requirements

### Validation Criteria
How to verify the feature works correctly

## 8. Implementation Status
- [ ] Design reviewed
- [ ] Implementation planned
- [ ] Core functionality implemented
- [ ] Tests written
- [ ] Documentation updated
- [ ] Production ready
```

### Best Practices for Design Documents

1. **Be Specific**: Include concrete examples, not just abstractions
2. **Show Comparisons**: Always include before/after states
3. **Use Diagrams**: Visual representations clarify complex relationships
4. **Include Code Snippets**: Show key interfaces and data structures
5. **Track Status**: Maintain implementation checkboxes
6. **Reference Dependencies**: Link to related design documents

## 3. Workflow Stages

### Stage 1: Problem Definition & Design Document Creation

**Duration**: 1-3 hours per feature
**Participants**: Engineers, AI Assistant (optional)

1. **Identify the Problem**
   - Clear problem statement
   - Current limitations
   - Success criteria

2. **Draft Initial Design**
   - High-level approach
   - Integration points
   - Key algorithms

3. **Create Design Document**
   - Follow template structure
   - Include all required sections
   - Add diagrams and examples

4. **Peer Review** (optional but recommended)
   - Architecture alignment
   - Edge case identification
   - Alternative approaches

### Stage 2: AI Review in Plan Mode

**Duration**: 30-60 minutes
**Tool**: Claude Code in Plan Mode

1. **Enable Plan Mode**
   ```
   Instruction: Review the design document at docs/[feature].md and create an implementation plan
   ```

2. **AI Analysis**
   - Design comprehension
   - Implementation approach
   - Potential issues identification

3. **Plan Generation**
   - Step-by-step implementation plan
   - File modifications required
   - Testing approach

4. **Human Review**
   - Validate understanding
   - Adjust plan if needed
   - Approve or iterate

### Stage 3: Implementation Planning

**Duration**: 30 minutes
**Output**: Detailed task list

1. **Break Down Tasks**
   ```markdown
   ## Implementation Tasks
   - [ ] Create new data structures
   - [ ] Modify existing interfaces
   - [ ] Implement core algorithm
   - [ ] Add error handling
   - [ ] Write unit tests
   - [ ] Update documentation
   ```

2. **Identify Dependencies**
   - Required prerequisites
   - Blocking relationships
   - Parallel opportunities

3. **Estimate Effort**
   - Task complexity ratings
   - Time estimates
   - Risk factors

### Stage 4: Iterative Implementation

**Duration**: 2-8 hours depending on complexity
**Workflow**: Human-AI collaboration

1. **Task Execution**
   ```
   AI Instruction: Implement the [specific task] from the design document
   ```

2. **Code Review Cycle**
   - AI implements
   - Human reviews
   - Adjustments made
   - Next task begins

3. **Progress Tracking**
   - Update task checkboxes
   - Document deviations
   - Note discoveries

4. **Issue Resolution**
   - Document blockers in review.md
   - Adjust design if needed
   - Track solutions

### Stage 5: Testing and Validation

**Duration**: 1-2 hours
**Focus**: Verification against design

1. **Test Implementation**
   ```
   AI Instruction: Write tests for the feature based on the testing strategy in the design document
   ```

2. **Validation Checklist**
   - [ ] All objectives met
   - [ ] Integration points working
   - [ ] Edge cases handled
   - [ ] Performance acceptable
   - [ ] Documentation complete

3. **Bug Fixes**
   - Identify issues
   - Reference design for intended behavior
   - Implement fixes
   - Retest

### Stage 6: Documentation and Closure

**Duration**: 30 minutes
**Output**: Updated documentation

1. **Update Design Document**
   - Mark implementation status complete
   - Document any deviations
   - Add lessons learned

2. **Update User Documentation**
   - API documentation
   - Usage examples
   - Configuration guides

3. **Knowledge Transfer**
   - Team notification
   - Demo if needed
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
- Higher numbers for dependent features

### Document Types

1. **Central Design Document** (`0.unified_*.md`)
   - System-wide architecture
   - Component relationships
   - Updated as features are added

2. **Feature Design Documents** (`N.feature_*.md`)
   - Individual feature designs
   - Follow standard template
   - Reference central design

3. **Review Document** (`review.md`)
   - Active issues
   - Design questions
   - Implementation notes

4. **Todo Document** (`todo.md`)
   - Future features
   - Technical debt
   - Optimization opportunities

## 5. Using AI Effectively

### Claude Code Configuration

Create a `CLAUDE.md` file in your project root:

```markdown
# CLAUDE.md

## Project Overview
[Brief description of the project]

## Development Workflow
This project uses design-first development. All features have design documents in the docs/ directory.

## Before Implementation
1. Always read the relevant design document in docs/
2. Use Plan Mode to create an implementation plan
3. Wait for human approval before making changes

## Implementation Guidelines
- Follow existing code patterns
- Maintain consistency with design documents
- Update implementation status in design docs
- Document any deviations

## Testing Requirements
- Write tests as specified in design documents
- Ensure all tests pass before marking complete
- Include edge cases identified during implementation
```

### Plan Mode Best Practices

1. **Always Start with Plan Mode**
   ```
   Instruction: Read docs/feature_design.md and create an implementation plan
   ```

2. **Be Specific About Context**
   ```
   Instruction: Implement the GPU allocation algorithm from docs/18.gpu_allocation_algorithm_design.md, 
   focusing on the head-tail splitting strategy described in section 4
   ```

3. **Request Incremental Implementation**
   ```
   Instruction: Implement only the data structures from the design document first, 
   we'll add the algorithms in the next step
   ```

4. **Validate Understanding**
   ```
   Instruction: Summarize your understanding of the critical path computation 
   from the design document before implementing
   ```

## 6. Example Workflow Execution



### Case Study: Implementing a Task Scheduler Feature

#### Step 1: Create Design Document

`docs/5.task_scheduler_design.md`:
```markdown
# Task Scheduler Design

## 1. Executive Summary
Implement a multi-level task scheduler that prioritizes tasks based on completion proximity...

## 2. Problem Statement
### Context
Multiple pipelines compete for limited GPU resources...

### Challenges
- Resource contention between pipelines
- Varying task priorities
- Dynamic workload changes
...
```

#### Step 2: AI Review in Plan Mode

```
Human: Review docs/5.task_scheduler_design.md and create an implementation plan

AI: [Reads document and creates plan]
## Implementation Plan for Task Scheduler

Based on the design document, I'll implement the feature in these stages:

1. **Data Structures** (30 min)
   - Create TaskQueue class
   - Add PriorityCalculator
   - Implement ResourceTracker

2. **Core Algorithm** (2 hours)
   - Implement three-level scheduling
   - Add SRJF prioritization
   - Create GPU allocation logic

3. **Integration** (1 hour)
   - Connect to existing pipeline
   - Update configuration system
   - Add monitoring hooks

4. **Testing** (1 hour)
   - Unit tests for each component
   - Integration test with mock pipelines
   - Performance benchmarks

Shall I proceed with implementing the data structures first?
```

#### Step 3: Iterative Implementation

```
Human: Yes, implement the data structures

AI: [Implements TaskQueue, PriorityCalculator, ResourceTracker with full code]
```
Human: Now review the implementation

AI: I'll review the implementation against our design requirements...
[Reviews code, identifies issues, suggests improvements]
```

#### Step 4: Testing and Validation

```
Human: Write comprehensive tests for the scheduler

AI: [Creates unit tests, integration tests, and performance benchmarks]
```

#### Step 5: Documentation Update

```
Human: Update the design document with implementation status

AI: [Updates design doc checkboxes and adds implementation notes]
```

## 7. Common Patterns and Anti-Patterns

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

4. **Parallel Design**
   - Multiple features can be designed simultaneously
   - Dependencies identified early
   - Enables better resource planning

### Anti-Patterns (Avoid These)

1. **Implementation Without Design**
   - Leads to inconsistent architecture
   - Causes frequent rewrites
   - Results in technical debt

2. **Over-Detailed Design**
   - Spending too much time on minor details
   - Inflexible to discoveries during implementation
   - Delays actual coding

3. **Ignoring Design During Implementation**
   - Deviating without documentation
   - Not updating design with learnings
   - Breaking architectural consistency

4. **Batch Implementation**
   - Trying to implement everything at once
   - Missing feedback opportunities
   - Harder to debug issues

## 8. Metrics and Success Indicators

### Quantitative Metrics

- **Implementation Speed**: Features completed 50-70% faster
- **Rework Reduction**: 80% fewer major rewrites
- **Code Quality**: 60% fewer architectural violations
- **Documentation Coverage**: 100% of features documented

### Qualitative Indicators

- **Developer Satisfaction**: Less frustration with AI interactions
- **Code Consistency**: Uniform patterns across features
- **Knowledge Transfer**: New team members onboard faster
- **Technical Debt**: Reduced accumulation over time

## 9. Tools and Resources

### Recommended Tools

1. **Documentation**
   - Markdown editors with preview
   - Diagramming tools (Mermaid, PlantUML)
   - Version control for docs

2. **AI Assistants**
   - Claude Code for implementation
   - GitHub Copilot for code completion
   - ChatGPT for design discussions

3. **Project Management**
   - GitHub Issues for tracking
   - Linear/Jira for planning
   - Notion for knowledge base

### Templates and Examples

Create a `templates/` directory with:
- `design_template.md`: Standard design document template
- `review_template.md`: Code review checklist
- `test_plan_template.md`: Testing strategy template

## 10. Troubleshooting Guide

### Common Issues and Solutions

**Issue**: AI doesn't understand the design
- **Solution**: Add more specific examples and code snippets

**Issue**: Implementation deviates significantly from design
- **Solution**: Break into smaller increments, validate more frequently

**Issue**: Design documents become outdated
- **Solution**: Update during implementation, not after

**Issue**: Too much time spent on design
- **Solution**: Time-box design phase, iterate based on learnings

## 11. Advanced Techniques

### Multi-Phase Features

For complex features spanning multiple releases:

1. **Phase 0**: Core infrastructure
2. **Phase 1**: Basic functionality
3. **Phase 2**: Advanced features
4. **Phase 3**: Optimizations

Each phase has its own design section but references the overall vision.

### Cross-Team Collaboration

When multiple teams are involved:

1. **Shared Design Repository**: Central location for all designs
2. **Design Review Board**: Regular cross-team reviews
3. **Interface Contracts**: Clear API boundaries defined in designs
4. **Integration Tests**: Specified in design documents

### Performance Considerations

Include in design documents:
- Expected load and scale
- Performance requirements
- Optimization strategies
- Monitoring approach

## 12. Conclusion

The AI-assisted design-first development workflow transforms how we build software with AI assistance. By investing time in thoughtful design, we enable AI to be a powerful implementation partner rather than a source of frustration.

### Key Takeaways

1. **Design is an investment, not overhead**
2. **Clear specifications enable better AI performance**
3. **Iterative implementation with continuous validation**
4. **Documentation is a living artifact**
5. **Consistency comes from following patterns**

### Getting Started

1. Choose a small feature for your first attempt
2. Follow the template strictly
3. Use Plan Mode for AI review
4. Iterate based on learnings
5. Share experiences with your team

### Additional Resources

- Example design documents from real projects
- Video walkthroughs of the workflow
- Community forums for best practices
- Regular updates as AI capabilities evolve

---

*This workflow guide is a living document. As AI tools evolve and we learn from experience, update this guide to reflect best practices.*

## Appendix A: Quick Reference

### Design Document Checklist
- [ ] Executive summary written
- [ ] Problem clearly stated
- [ ] Architecture diagram included
- [ ] Before/after comparison shown
- [ ] Implementation details specified
- [ ] Testing strategy defined
- [ ] Status tracking added

### AI Instruction Templates

**For Design Review**:
```
Review the design document at docs/[feature].md. Identify any ambiguities, potential issues, or missing components. Create an implementation plan.
```

**For Implementation**:
```
Implement [specific component] from docs/[feature].md, following the algorithm in section [N]. Ensure consistency with existing patterns.
```

**For Testing**:
```
Create comprehensive tests for [feature] based on the testing strategy in docs/[feature].md. Include unit tests, integration tests, and edge cases.
```

**For Documentation**:
```
Update docs/[feature].md with the current implementation status. Document any deviations from the original design and explain the reasons.
```

## Appendix B: Example Design Document

See `/docs/0.unified_scheduler_design.md` in the ROLL project for a comprehensive example of a well-structured design document that successfully guided AI implementation of a complex scheduling system.

## 13. Design Document Evolution and Patterns

### Design Document as Living Artifacts

Design documents should evolve throughout implementation rather than being static specifications. They serve as both planning tools and historical records of design decisions.

#### The Key Design Decisions Log Pattern

**IMPORTANT**: The Key Design Decisions Log is for tracking **COMPLETED features only**, not initial design plans or intentions.

**Workflow**:
1. **During Planning**: Create individual feature design documents (e.g., `1.partial_gpu_allocation.md`) with detailed phases and implementation plans
2. **During Development**: Update feature-specific design documents with discoveries and refinements  
3. **After Completion**: Once feature is implemented and pushed to working branch, add a summary entry to the central `0.` document's log
4. **Historical Record**: The log becomes a permanent record of what was actually built and why

**When to Add Log Entries**: 
- ✅ Feature fully implemented and merged to working branch
- ✅ Major architectural changes completed
- ✅ Performance optimizations deployed
- ❌ NOT for initial design plans or intentions
- ❌ NOT for features still in development

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

**Example Entry** (from unified scheduler):
```markdown  
### 1. Partial GPU Allocation for Generation Tasks
**Decision**: Support partial DP worker allocation (minimum 1 worker) for generation tasks only.
- Generation tasks: `{"pipeline_0_step_0_generation": [0, 2, 3]}`
- Non-generation tasks: `{"pipeline_0_step_0_training": None}`
- **Rationale**: Generation tasks can run with reduced parallelism, enabling better GPU utilization
```

#### When to Append vs Modify

**Always Append:**
- New architectural decisions
- Changes to core algorithms
- Major scope additions or cuts
- Performance optimization decisions
- Security or safety considerations

**Modify Existing Sections:**
- Implementation status updates
- Correcting technical errors
- Adding clarification to existing designs
- Updating code examples with better versions

### Document Naming Conventions

#### Central/Unified Documents
Use `0.` prefix for system-wide or central design documents:
- `0.unified_system_design.md` - Overall system architecture
- `0.safety_checker_design.md` - Central safety infrastructure
- `0.authentication_design.md` - System-wide auth strategy

#### Feature Documents
Use numeric prefixes (1-99) for feature-specific designs:
- `1.partial_gpu_allocation.md` - Individual feature planning with detailed phases
- `2.sched_planning_design.md` - Scheduling algorithm planning
- `18.gpu_allocation_algorithm_design.md` - GPU allocation feature planning

**Purpose of Numbered Documents**:
- **Planning Focus**: These contain detailed implementation phases, algorithms, and technical specifications for individual features
- **Implementation Guide**: Step-by-step plans that guide AI-assisted development 
- **Reference During Development**: Updated with discoveries, refinements, and lessons learned
- **Detailed Technical Specs**: Include code examples, data structures, and API designs
- **Cross-Referenced**: The `0.` document references these with `@./N.feature_name.md` links

**Ordering Strategy**: Use numbers to indicate implementation priority or dependency order, not chronological creation order.

**Lifecycle**: 
1. **Created during feature planning** (before implementation starts)
2. **Updated during development** with discoveries and changes
3. **Summarized in central log** once implementation is complete
4. **Archived as reference** for future similar features

### Design Document Lifecycle

#### Phase 1: Initial Design (1-3 hours)
- Complete template sections 1-7
- Focus on clear problem definition
- Include architectural diagrams
- Get peer review before implementation

#### Phase 2: Implementation Refinement (Throughout development)
- Update implementation status regularly
- Document discovered issues and solutions  
- Update feature-specific design documents (`N.feature_name.md`) with refinements
- Maintain before/after workflow accuracy

#### Phase 3: Post-Implementation Documentation (30 minutes)
- Mark all implementation status complete
- Add final performance characteristics  
- **Add entry to Key Design Decisions Log** in central `0.` document
- Document lessons learned for future features
- Archive key insights for team knowledge

## 14. Defensive Programming Principles for AI Development

### The Complexity Trap

AI-assisted development can lead to over-engineering because it's easy to ask AI to "add safety checks" or "handle edge cases." This often creates more bugs than it prevents.

#### Core Principle: Simple Failures Over Complex Fallbacks

**The Problem**: Each layer of defensive programming adds potential failure points and makes debugging harder.

```python
# AVOID: Defensive complexity that hides real issues
def process_data(data):
    try:
        if not validate_data(data):
            try:
                data = fix_data(data)
                if not validate_data(data):
                    try:
                        data = fallback_data_source()
                    except FallbackError:
                        return default_empty_result()
            except FixError:
                return default_empty_result()
        return expensive_processing(data)
    except Exception as e:
        logger.warning(f"Processing failed: {e}")
        return default_empty_result()

# PREFER: Clear failure modes with actionable errors
def process_data(data):
    if not validate_data(data):
        raise InvalidDataError(f"Data validation failed: {get_validation_errors(data)}")
    
    return expensive_processing(data)
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

**Example of Good Defensive Code:**
```python
def generate_with_safety(model, prompt, safety_checker=None):
    """Generate text with optional safety checking."""
    # Early validation with clear errors
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty or whitespace")
    
    # Generate with proper resource management
    try:
        output = model.generate(prompt)
    except OutOfMemoryError:
        # Don't try to recover - let it fail clearly
        logger.error(f"OOM during generation for prompt length: {len(prompt)}")
        raise
    
    # Apply safety if requested
    if safety_checker:
        return safety_checker.check_and_filter(output)
    
    return output
```

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

#### 4. Use Assertions for Developer Errors
```python
# Good: Catches programming errors during development
def process_batch(items):
    assert len(items) > 0, "Batch cannot be empty - check calling code"
    assert all(item.is_valid() for item in items), "All items must be valid"
    # ... processing logic
```

#### 5. Document What You're NOT Handling
```python
def load_model(model_path):
    """Load model from path.
    
    Note: Does not handle network timeouts - caller should implement 
    retry logic if needed for remote paths.
    """
    # Simple, clear loading logic
```

### Common Anti-Patterns in AI Development

#### The "Just in Case" Pattern
```python
# AVOID: Adding safety for theoretical problems
try:
    result = simple_function()
except Exception as e:  # Too broad!
    # "Just in case" handling that hides real bugs
    logger.warning(f"Unexpected error: {e}")
    return None
```

#### The "Belt and Suspenders" Pattern  
```python
# AVOID: Multiple redundant safety checks
if data and len(data) > 0 and data is not None:
    if validate_data(data) and data.is_valid() and check_data_integrity(data):
        # Excessive validation that slows development
```

#### The "Swiss Army Knife" Pattern
```python
# AVOID: One function that handles every possible edge case
def universal_text_processor(text, mode="normal", fallback=True, 
                           validate=True, clean=True, normalize=True,
                           handle_unicode=True, fix_encoding=True, ...):
    # Too many options create complexity and bugs
```

**Remember**: The goal is reliable software, not defensive software. Each defensive feature should solve a real, observed problem with clear benefit that outweighs the complexity cost.

---

*Version 1.0 - Based on successful implementation patterns from the ROLL project*