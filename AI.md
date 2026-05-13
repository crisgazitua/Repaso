# AI Use Declaration

## 1. Did you use AI tools?

- [ ] No AI tools were used at any stage of this assignment.
- [x] Yes, AI tools were used. Details are provided in Section 2 below.

## 2. AI Tool Usage Log

If you checked the second option above, fill out one block per tool:

### Tool 1
- **Name and version:** Claude (claude.ai / Claude Code — Sonnet 4.6/Opus 4.6/Opus 4.7)
- **Dates of use:** May 2026
- **Students who interacted with it:** Diego Llull
- **Purpose:** Design support and task organization. Claude was used to help plan and structure the submission requirements, clarify doubts about the CleverHub protocol, and assist in the design of the C4 diagrams, Domain Model, and UML sequence diagrams. This included identifying issues in early versions (e.g., an incorrect sensor type in the domain model), suggesting structural improvements, and proposing the content and flow of the sequence diagrams (e.g., the duplicate HOM case, the persistent TCP connection note, the recv_message buffer detail, and the read-only parameter validation). The student provided the context and direction; Claude helped shape and refine the design based on it.
- **How the output was integrated:** Suggestions were reviewed and filtered by the student. The final diagrams were created and rendered manually by the team using the agreed design. All final decisions remained with the team.

### Tool 2
- **Name and version:** Claude (claude.ai - Opus 4.7)
- **Dates of use:** May 2026
- **Students who interacted with it:** Cristobal Gazitua
- **Purpose:** Implementation guidance and code review for the Credentials, Console UI, Tests, and Infrastructure parts of the submission. Claude was used to discuss design decisions (abstract CredentialStore interface vs. concrete implementation, Command pattern for the Console UI, separation between presentation and transport layers), to draft the initial scaffolding for these modules, to write unit tests following the arrange/act/assert structure, and to set up the Dockerfile, docker-compose, and GitHub Actions workflow. Claude was also used to review code written by another team member (the TCP server) and identify a design issue where the protocol roles between the Platform and the CleverHub had been inverted in the GS/SS flow, which the team then corrected.
- **How the output was integrated:** All code was reviewed, executed locally, and validated against mypy and pytest before being committed. The student adapted variable names, error messages, and structural details to fit the team's conventions, and discussed each design decision with the team before push. The team retains full understanding of and responsibility for the submitted code.

### Tool 2
- **Name and version:** ChatGPT - OpenAI (5.5)
- **Dates of use:** May 2026
- **Students who interacted with it:** Carlos Rencoret
- **Purpose:** ChatGPT was used for the following cases:
        -Identifying limit cases in parsing, such as invalid messages and formats, as well as making sure the right error messages are displayed.
        -Consulted for which tests should be implemented, as some of these were not evident from the start to our team.
        -Proof reading markdown files for grammatical errors or redundancies.
        -Bugfixing, for when the error outputs where too vague, the AI was given the command line output to help is identify where the bug lies.

- **How the output was integrated:** All code was manually reviewed, as well as validated through mypy and pytest before any commits were done. Any changes that involved the logic or structure of the codebase were first reviewed by the team. 

_(Add more `### Tool N` blocks as needed.)_

## 3. Academic Responsibility Declaration

We, the students listed in [README.md](./README.md), declare that:

- We have critically reviewed all delivered content.
- We fully understand the work submitted and are able to explain and defend it academically.
- We assume full responsibility for the quality, accuracy, and originality of all submitted content, regardless of whether AI tools were used.
- The information declared in this document is truthful.
