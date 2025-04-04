CODING_RULES = {
    "imports": {
        "description": "Import organization rules",
        "rules": [
            "Place 'import' statements before 'from' imports",
            "Organize imports in alphanumerical order",
            "Group imports: standard library → third-party → local"
        ]
    },
    "formatting": {
        "description": "Code formatting rules",
        "rules": [
            "Avoid line continuation backslashes",
            "Single blank lines between logical sections",
            "Remove unnecessary whitespace",
            "120 character line length limit"
        ]
    },
    "naming": {
        "description": "Naming conventions",
        "rules": [
            "Descriptive names for variables/functions",
            "Underscore prefix for private methods (_private)",
            "UPPERCASE for constants",
            "Follow PEP8 naming conventions"
        ]
    },
    "documentation": {
        "description": "Documentation standards",
        "rules": [
            "Docstrings for all public methods/classes",
            "Type hints for parameters/returns",
            "Module and class-level docs",
            "Avoid redundant comments"
        ]
    },
    "logging": {
        "description": "Error handling and logging",
        "rules": [
            "Appropriate log levels (debug, info, warning, error)",
            "Context in error messages",
            "f-strings for log formatting",
            "Resource cleanup in error cases"
        ]
    }
}

REVIEW_PROMPT_TEMPLATE = """Analyze these code changes and provide a thorough code review.
Focus on these specific aspects:

### Import Organization
{import_rules}

### Code Formatting  
{formatting_rules}

### Naming Conventions
{naming_rules}

### Documentation
{documentation_rules}

### Error Handling
{logging_rules}

For each issue found, provide:
1. File and line number
2. Specific suggestion
3. Reasoning based on the rules

Format your response like this:

### Summary
[Brief overall assessment]

### Suggestions
- file.py:10 - Move import to proper section (standard library imports first)
- file.py:25 - Break long line (currently 135 characters)

### Issues
- file.py:42 - Missing error handling for file operation
- file.py:56 - Undocumented public method

Code changes to review:
{diff}"""

def format_rules_section(rules: dict) -> str:
    """Format a rules section for the prompt"""
    return "\n".join(f"- {rule}" for rule in rules["rules"])

# Initialize the template with formatted rules
REVIEW_PROMPT_TEMPLATE = REVIEW_PROMPT_TEMPLATE.format(
    import_rules=format_rules_section(CODING_RULES["imports"]),
    formatting_rules=format_rules_section(CODING_RULES["formatting"]),
    naming_rules=format_rules_section(CODING_RULES["naming"]),
    documentation_rules=format_rules_section(CODING_RULES["documentation"]),
    logging_rules=format_rules_section(CODING_RULES["logging"]),
    diff="{diff}"
)