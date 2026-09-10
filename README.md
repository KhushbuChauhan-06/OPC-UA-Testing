OPC UA Client Testing & Automation Framework

Python-based industrial communication testing framework for automated OPC UA client-server validation using a deterministic simulated plant.







Overview

This project is a repeatable OPC UA client testing and automation framework built with Python, asyncua, and Pytest.

It simulates a small industrial plant through a local OPC UA server and validates how an OPC UA client behaves across:

Connection and session management
Node discovery and browsing
Data read/write operations
OPC UA method calls
Subscriptions and monitored items
Authentication
Certificate-based trust
Secure communication
Negative and failure scenarios
Automated test reporting and code coverage

The primary goal is to demonstrate how industrial communication interfaces can be tested systematically rather than relying on manual verification.

Scope: This is a portfolio/learning project using a simulated industrial plant. It is not an ABB production system, ABB hardware integration, or a representation of ABB's internal software architecture.

Why This Project?

Industrial automation systems depend on reliable communication between controllers, devices, applications, and supervisory systems.

Manual verification of communication behavior can become:

Time-consuming
Difficult to reproduce
Inconsistent between test runs
Difficult to scale across different scenarios
Challenging to validate for failure and security conditions

This framework addresses that problem by creating a deterministic test environment where the same communication scenarios can be executed repeatedly and automatically.

The framework follows a simple principle:

Create a controlled industrial environment → execute repeatable tests → capture evidence → detect regressions early.

Architecture
flowchart TD
    T[Pytest Test Suite]
    F[Test Fixtures]
    C[OPCUATestClient]
    S[OPC UA SecureChannel]
    P[Simulated Industrial Plant]
    R[Test Reports / Coverage / Logs]

    T --> F
    F --> C
    C --> S
    S --> P
    T --> R
Main Components
Component	Responsibility
Pytest	Test execution, parametrization, markers and assertions
Fixtures	Creates isolated server/client environments for integration tests
OPCUATestClient	Encapsulates low-level asyncua client operations
OPCUATestServer	Hosts the simulated industrial plant
Security Layer	Handles OPC UA security policies, certificates and authentication
Configuration	Centralizes reusable endpoints, timeouts and test data
Reporting	Generates HTML reports, logs and coverage information
GitHub Actions	Automatically executes the test suite in CI

The test environment is designed so that integration tests can start with a clean OPC UA server and client state, reducing dependencies between individual tests.

Simulated Industrial Plant

The local OPC UA server exposes a simplified industrial process through:

opc.tcp://127.0.0.1:4840/abb-test-server/

The simulated IndustrialPlant contains representative process and motor data.

Sensor Variables
Temperature
Pressure
Vibration
Motor Variables
Speed
Current
Status
Control Methods
StartMotor()
StopMotor()

This provides enough realistic behavior to test both read-only monitoring and control-oriented OPC UA operations.

Test Coverage

The framework is organized around different communication and validation concerns.

tests/
├── functional/
│   ├── connection
│   ├── browse
│   ├── read/write
│   └── methods
│
├── subscription/
│   └── monitored items
│
├── security/
│   ├── authentication
│   ├── certificate trust
│   └── secure communication
│
└── negative/
    └── invalid/failure scenarios
Functional Testing

Validates core OPC UA operations such as:

Establishing a client connection
Browsing the address space
Reading node values
Writing supported values
Calling server methods
Validating returned values and status
Subscription Testing

Validates OPC UA subscriptions and monitored items to ensure clients can receive changes from the server rather than continuously polling values.

Negative Testing

Tests expected failure behavior such as:

Invalid credentials
Unknown users
Untrusted certificates
Invalid communication conditions
Unexpected server-side responses

This is important because a communication test suite should validate not only the happy path, but also how the system behaves when something goes wrong.

OPC UA Security

Security is tested using OPC UA's native SecureChannel mechanisms.

The framework uses:

Policy:
Basic256Sha256

Modes:
Sign
SignAndEncrypt
Sign

Provides message integrity and authentication at the OPC UA SecureChannel level.

SignAndEncrypt

Adds confidentiality by encrypting SecureChannel messages in addition to integrity protection.

The project also validates:

Username/password authentication
Invalid credentials
Unknown users
Client certificate trust
Untrusted client certificates
Server certificate expectations
Secure communication configuration

Important: OPC UA SecureChannel security is distinct from TLS transport security.

Development certificates are generated dynamically for testing. Private keys, credentials, and secrets are not committed to the repository.

Project Structure
OPC-UA-Testing/
│
├── src/
│   └── opcua_framework/
│       ├── client/
│       │   └── OPCUATestClient
│       │
│       ├── server/
│       │   └── OPCUATestServer
│       │
│       ├── config/
│       │
│       └── utils/
│           └── certificate tooling
│
├── tests/
│   ├── functional/
│   ├── subscription/
│   ├── security/
│   └── negative/
│
├── config/
│   └── framework.yaml
│
├── reports/
├── logs/
├── pyproject.toml
└── README.md

The separation between the client wrapper, simulated server, configuration, utilities, and tests keeps the framework easier to extend as new test scenarios are introduced.

Technology Stack
Technology	Purpose
Python 3.11+	Framework implementation
asyncua 2.x	OPC UA client/server communication
Pytest	Test automation
pytest-asyncio	Async test execution
pytest-html	HTML test reports
pytest-cov	Code coverage
PyYAML	Configuration and test data
GitHub Actions	Continuous integration
X.509 Certificates	OPC UA application trust/security
Installation
1. Clone the repository
git clone https://github.com/KhushbuChauhan-06/OPC-UA-Testing.git
cd OPC-UA-Testing
2. Create a virtual environment
py -3.11 -m venv .venv
3. Activate the environment
.\.venv\Scripts\Activate.ps1
4. Install the project
python -m pip install --upgrade pip
pip install -e .
Running the Tests

The test fixtures automatically start and manage the simulated OPC UA server for integration testing.

Run the complete test suite:

pytest

Run specific test categories:

pytest -m smoke
pytest -m functional
pytest -m subscription
pytest -m security
pytest -m negative

This allows developers to run either the complete validation suite or a focused subset during development.

Running the OPC UA Server Manually

The server can also be started independently for manual experimentation:

py -3.11 -m opcua_framework.server

The default endpoint is:

opc.tcp://127.0.0.1:4840/abb-test-server/

A different local endpoint can be supplied through:

$env:OPCUA_ENDPOINT="opc.tcp://127.0.0.1:4841/abb-test-server/"
Test Reports & Coverage

Generate an HTML test report:

pytest --html=reports/report.html --self-contained-html

Generate code coverage:

pytest --cov=src --cov-report=html:reports/coverage

The framework produces:

reports/
├── report.html
└── coverage/

logs/
└── test-run.log

These artifacts make test execution results easier to review and help identify areas requiring additional automated coverage.

CI/CD

The project uses GitHub Actions to execute the automated test suite on:

Pushes
Pull requests

The CI pipeline:

flowchart LR
    A[Code Push / PR] --> B[Install Python 3.11]
    B --> C[Install Dependencies]
    C --> D[Run OPC UA Test Suite]
    D --> E[Generate Reports]
    E --> F[Publish Test Artifacts]

The CI environment does not require a persistent OPC UA server.

Test fixtures create the simulated server automatically, allowing the same integration tests to run consistently in local development and CI.

Only test logs and reports are published as artifacts.

Certificates, private keys, credentials, and secrets are excluded from CI artifacts and source control.

Configuration

Reusable non-secret configuration is stored in:

config/framework.yaml

Configuration includes items such as:

OPC UA endpoint
Connection timeouts
Subscription publishing interval
Sensor ranges
Test data
Security-related test configuration

The endpoint can be overridden using:

$env:OPCUA_ENDPOINT="opc.tcp://127.0.0.1:4841/abb-test-server/"

Credentials and private-key locations should always be supplied through secure configuration mechanisms and must not be committed to Git.

Development Certificates

The framework can generate development certificates for manual security experiments:

py -3.11 -m opcua_framework.utils.generate_certificates

These certificates are intended for local testing only.

The project does not attempt to reproduce a production PKI infrastructure.

Engineering Focus

This project is primarily designed to demonstrate practical skills relevant to industrial software and test automation, including:

Industrial Communication
OPC UA client-server architecture
Address-space browsing
Node interaction
Methods
Subscriptions
Monitored items
Test Automation
Pytest-based test architecture
Fixtures and test isolation
Functional testing
Negative testing
Regression testing
Automated reporting
Security Testing
OPC UA SecureChannel
Security policies
Sign / SignAndEncrypt
Username authentication
X.509 certificate trust
Software Engineering
Modular architecture
Configuration-driven testing
Reusable client abstraction
Async programming
CI automation
Test evidence and reporting
Limitations & Scope

This project intentionally focuses on automated OPC UA communication testing using a deterministic local simulation.

It does not implement:

Production ABB hardware integration
Real PLC/controller communication
Production PKI/CA infrastructure
Certificate revocation infrastructure
TLS transport
Production deployment architecture
Safety-critical control logic

The OPC UA server is localhost-only and exists specifically to provide a controlled environment for automated QA and learning.

Future Improvements

Potential extensions include:

Parameterized test matrices for multiple OPC UA configurations
Fault-injection testing
Connection interruption and recovery testing
Subscription reconnect scenarios
Performance and latency measurements
Larger simulated industrial processes
More comprehensive security negative testing
Test-result dashboards
Containerized OPC UA test environments
Key Takeaway

This project demonstrates a practical approach to testing industrial communication software:

Simulate
   ↓
Connect
   ↓
Interact
   ↓
Validate
   ↓
Test Failure & Security
   ↓
Report
   ↓
Automate in CI

The emphasis is on repeatability, test isolation, communication reliability, security validation, and maintainable automation rather than manual OPC UA verification.
