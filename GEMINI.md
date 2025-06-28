# Coding Standards & Best Practices

This document outlines the development standards and rules for this project. As your AI coding assistant, I will adhere to these principles to ensure the code I produce is professional, maintainable, secure, and error-free.

## 1. Code Style & Formatting

-   **Python**: All Python code will strictly adhere to the **PEP 8** style guide. We will use `black` for automated code formatting to ensure consistency.
-   **TypeScript/JavaScript**: All frontend code will be formatted using `prettier`.
-   **Clarity**: Code will be written to be as clear and readable as possible. Variable and function names will be descriptive and unambiguous.

## 2. Type Safety

-   **Python**: Full type hints will be used for all function signatures and variable declarations. We will use `mypy` for static type checking to catch errors before runtime.
-   **TypeScript**: The frontend will be written in TypeScript, leveraging its static typing features to ensure component props and data structures are well-defined.

## 3. Security

-   **No Hardcoded Secrets**: No API keys, passwords, or other secrets will ever be hardcoded in the source code. All secrets will be loaded from environment variables or a secure secret manager (Google Secret Manager).
-   **Input Validation**: All data coming from external sources (API requests, webhooks, user input) will be rigorously validated using Pydantic on the backend before being processed.
-   **Principle of Least Privilege**: Services and roles will only be granted the minimum permissions necessary to perform their function.
-   **Dependency Security**: We will regularly scan dependencies for known vulnerabilities.

## 4. Modularity & Reusability

-   **Separation of Concerns**: Logic will be clearly separated. For example, API endpoint definitions, business logic (services), and data access (models) will reside in separate modules.
-   **DRY (Don't Repeat Yourself)**: Common logic will be extracted into reusable functions, classes, or dependencies.
-   **Single Responsibility Principle**: Each function and class will have a single, well-defined purpose.

## 5. Error Handling & Logging

-   **Robust Error Handling**: The application will gracefully handle expected errors (e.g., API failures, invalid input) and return clear, informative error messages to the client.
-   **Structured Logging**: All log entries will be structured (e.g., JSON format) and include important context like timestamps, severity levels, and request IDs.
-   **No Sensitive Data in Logs**: Logging will be configured to automatically redact sensitive information (e.g., tokens, PII) to prevent exposure.

## 6. Testing

-   **Testable Code**: Code will be written in a way that is easy to test, favoring dependency injection and avoiding tight coupling.
-   **Unit Tests**: Core business logic within services will be covered by unit tests that mock external dependencies.
-   **Integration Tests**: Key user flows (e.g., the full email-to-deal process) will be tested with integration tests that interact with live or containerized versions of dependencies.

## 7. Documentation

-   **Docstrings**: All public modules, classes, and functions will have clear, concise docstrings explaining their purpose, arguments, and return values.
-   **READMEs**: Key directories will contain `README.md` files explaining the purpose of the code within them.
-   **Architectural Decisions**: Significant architectural choices will be documented, explaining the "why" behind the decision.

By following these rules consistently, we will build a high-quality, professional-grade application that is easy to maintain, scale, and extend.

