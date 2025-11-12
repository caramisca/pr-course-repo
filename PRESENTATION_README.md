# Concurrent Tasks and Futures - LaTeX Beamer Presentation

## Overview

This is a comprehensive LaTeX Beamer presentation about concurrent tasks and futures, created based on the content from [Issue #10](https://github.com/caramisca/pr-course-repo/issues/10).

## File Information

- **Filename**: `concurrent_tasks_futures_presentation.tex`
- **Document Class**: Beamer with 16:9 aspect ratio
- **Theme**: Copenhagen (professional blue theme)
- **Packages Used**: listings (for code syntax highlighting), xcolor, graphicx

## Content Structure

The presentation includes the following sections:

1. **Title Slide** - "Concurrent Tasks and Futures"
2. **Introduction** - Overview of concurrent tasks and futures
3. **Core Concepts** - Detailed explanation of concurrent tasks and futures
4. **Key Principles** - Threading, thread pooling, synchronization, callbacks/await/async, error handling
5. **Implementation Examples** - Code examples in Python, Java, and JavaScript
6. **Patterns, Pitfalls, and Best Practices** - Common issues and solutions
7. **Advanced Topics** - Chaining futures, composing tasks, progress reporting, cancellation
8. **Use Cases** - Real-world applications
9. **Discussion Questions** - 5 questions with detailed answers
10. **Conclusion** - Summary and key takeaways

## Compilation Instructions

### Prerequisites

You need a LaTeX distribution installed on your system:

- **Linux**: Install TeX Live
  ```bash
  sudo apt-get install texlive-full
  ```

- **macOS**: Install MacTeX
  ```bash
  brew install --cask mactex
  ```

- **Windows**: Install MiKTeX or TeX Live from their respective websites

### Compiling the Presentation

#### Using pdflatex (recommended)

```bash
pdflatex concurrent_tasks_futures_presentation.tex
pdflatex concurrent_tasks_futures_presentation.tex
```

Run it twice to generate the table of contents correctly.

#### Using xelatex (alternative)

```bash
xelatex concurrent_tasks_futures_presentation.tex
xelatex concurrent_tasks_futures_presentation.tex
```

#### Using latexmk (automatic compilation)

```bash
latexmk -pdf concurrent_tasks_futures_presentation.tex
```

### Output

The compilation will generate a PDF file: `concurrent_tasks_futures_presentation.pdf`

## Features

- **Professional Theme**: Uses Copenhagen theme with clean, modern styling
- **Syntax Highlighting**: Code blocks with proper syntax highlighting for Python, Java, and JavaScript
- **Code Examples**: Three complete, working code examples demonstrating futures/promises
- **Structured Content**: Well-organized sections with bullet points and emphasis
- **Discussion Questions**: 5 comprehensive Q&A pairs for learning reinforcement
- **Ready to Present**: Formatted for 16:9 displays (modern projectors and screens)

## Presentation Statistics

- **Total Sections**: 9
- **Total Frames**: 20
- **Code Examples**: 3 (Python, Java, JavaScript)
- **Discussion Questions**: 5

## Usage

This presentation is designed for:
- Academic courses on concurrent programming
- Technical training sessions
- Self-study and reference
- Team knowledge sharing

## Customization

You can customize the presentation by:
- Changing the theme: Modify `\usetheme{Copenhagen}` (alternatives: Madrid, Berkeley, Warsaw)
- Adjusting colors: Modify the color definitions in the preamble
- Adding content: Add new frames between `\begin{frame}` and `\end{frame}`
- Modifying code highlighting: Adjust the `lstdefinestyle` settings

## Troubleshooting

If you encounter compilation errors:

1. **Missing packages**: Install the full TeX Live distribution
2. **Font issues**: Use pdflatex instead of xelatex
3. **Syntax errors**: Check for unescaped special characters (%, &, #, etc.)

## License

This presentation is created for educational purposes as part of the Network Programming course at Technical University of Moldova.
