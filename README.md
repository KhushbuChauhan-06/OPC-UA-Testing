# OPC UA Client Testing & Automation Framework

> Python-based industrial communication testing framework for automated OPC UA client-server validation using a deterministic simulated industrial plant.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![OPC UA](https://img.shields.io/badge/Protocol-OPC%20UA-orange)
![Pytest](https://img.shields.io/badge/Test%20Framework-Pytest-green)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black)

---

## Overview

This project is a **repeatable OPC UA client testing and automation framework** built with Python, `asyncua`, and Pytest.

It provides a controlled local OPC UA environment where client-server communication can be tested automatically across functional, subscription, negative, and security scenarios.

The framework validates:

- OPC UA connection and session handling
- Address-space browsing
- Data read/write operations
- OPC UA method calls
- Subscriptions and monitored items
- Username/password authentication
- X.509 certificate trust
- Secure communication
- Negative and failure scenarios
- Automated test reporting
- Code coverage
- Continuous integration

The main objective is to demonstrate how industrial communication interfaces can be tested **systematically, repeatedly, and automatically** instead of relying only on manual verification.

> **Project scope:** This is a portfolio and learning project using a simulated industrial plant. It is **not an ABB production system, ABB hardware integration, or a representation of ABB's internal software architecture.**

---

## Why This Project?

Industrial automation systems rely on reliable communication between controllers, devices, applications, and supervisory systems.

Manual communication testing can become:

- Time-consuming
- Difficult to reproduce
- Inconsistent between test runs
- Difficult to scale
- Difficult to validate for failure conditions
- Difficult to maintain as test coverage grows

This framework addresses these challenges by providing a **deterministic and isolated OPC UA test environment**.

The testing workflow is:

```text
Controlled Environment
        ↓
OPC UA Client Connection
        ↓
Communication & Control
        ↓
Functional Validation
        ↓
Negative & Security Testing
        ↓
Reports & Coverage
        ↓
Continuous Integration
Architecture
Main Components
Component	Responsibility
Pytest	Test execution, assertions, markers and parametrization
Test Fixtures	Creates isolated server/client environments for integration tests
OPCUATestClient	Encapsulates low-level asyncua client operations
OPCUATestServer	Hosts the simulated industrial plant
Security Layer	Handles OPC UA security policies, certificates and authentication
Configuration	Centralizes endpoints, timeouts and reusable test data
Reporting	Generates HTML reports, logs and coverage
GitHub Actions	Executes automated tests in CI

Function-scoped fixtures are used to create a clean server and connected client for integration tests, reducing dependencies between individual test cases.

Simulated Industrial Plant

The framework uses a local OPC UA server representing a simplified industrial plant.

OPC UA Endpoint
opc.tcp://127.0.0.1:4840/abb-test-server/

The simulated IndustrialPlant exposes representative sensor and motor data.

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

This provides a realistic test target for both monitoring and control-oriented OPC UA operations.

Test Coverage

The test suite is organized around different communication and validation concerns.

tests/
│
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

Validates core OPC UA operations including:

Establishing client connections
Browsing the OPC UA address space
Reading node values
Writing supported values
Calling server methods
Validating returned values and status codes
Subscription Testing

Validates OPC UA subscriptions and monitored items.

Instead of continuously polling values, the client can subscribe to changes from the server and validate that monitored data is delivered correctly.

This helps verify event-driven communication behavior commonly used in industrial systems.

Negative Testing

The framework also validates expected failure behavior.

Examples include:

Invalid credentials
Unknown users
Untrusted certificates
Invalid security configuration
Communication failures
Unexpected server-side responses

Testing failure scenarios is important because a reliable automation framework should validate both expected behavior and controlled failure behavior.

OPC UA Security

The security tests use OPC UA's native SecureChannel mechanisms.

Security Policy
Basic256Sha256
Security Modes
Sign
SignAndEncrypt
Sign

Provides message integrity and authentication at the OPC UA SecureChannel level.

SignAndEncrypt

Provides message integrity and authentication while also protecting the confidentiality of SecureChannel messages through encryption.

The framework validates:

Username/password authentication
Invalid credentials
Unknown users
Client certificate trust
Untrusted client certificates
Expected server certificate validation
Secure communication configuration

Note: OPC UA SecureChannel security is different from TLS transport security.

Development certificates are generated dynamically for testing.

Private keys, credentials, and secrets are never committed to the repository.

Project Structure
OPC-UA-Testing/
│
├── src/
│   └── opcua_framework/
│       │
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

The framework separates the client abstraction, simulated server, configuration, utilities, and tests, making it easier to maintain and extend.

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
X.509 Certificates	OPC UA application trust and security
Installation
1. Clone the Repository
git clone https://github.com/KhushbuChauhan-06/OPC-UA-Testing.git
cd OPC-UA-Testing
2. Create a Virtual Environment
py -3.11 -m venv .venv
3. Activate the Virtual Environment
.\.venv\Scripts\Activate.ps1
4. Install the Project
python -m pip install --upgrade pip
pip install -e .
Running the Tests

The test fixtures automatically start and manage the simulated OPC UA server during integration tests.

Run the Complete Test Suite
pytest
Run Specific Test Categories
pytest -m smoke
pytest -m functional
pytest -m subscription
pytest -m security
pytest -m negative

This allows developers to execute either the complete validation suite or a focused group of tests during development.

Running the OPC UA Server Manually

The server can also be started independently for manual testing and experimentation.

py -3.11 -m opcua_framework.server

The default endpoint is:

opc.tcp://127.0.0.1:4840/abb-test-server/

A different local endpoint can be configured using:

$env:OPCUA_ENDPOINT="opc.tcp://127.0.0.1:4841/abb-test-server/"
Test Reports & Code Coverage
Generate an HTML Test Report
pytest --html=reports/report.html --self-contained-html
Generate Code Coverage
pytest --cov=src --cov-report=html:reports/coverage

Generated artifacts include:

reports/
├── report.html
└── coverage/

logs/
└── test-run.log

The reports provide visibility into:

Test names
Pass/fail status
Execution duration
Captured output
Failure details
Code coverage
CI/CD

The project uses GitHub Actions to automatically execute the test suite on:

Pushes
Pull requests

The CI workflow follows:

The CI environment does not require a persistent OPC UA server.

Test fixtures automatically create and manage the simulated server, allowing the same integration tests to run consistently in local development and CI.

Only test logs and reports are uploaded as CI artifacts.

Private keys, certificates containing sensitive material, credentials, and secrets are excluded from source control and CI artifacts.

Configuration

Reusable non-secret configuration is stored in:

config/framework.yaml

Configuration includes:

OPC UA endpoint
Connection timeouts
Subscription publishing interval
Sensor ranges
Test data
Security-related test configuration

The endpoint can be overridden using:

$env:OPCUA_ENDPOINT="opc.tcp://127.0.0.1:4841/abb-test-server/"

Credentials and private-key paths must never be committed to Git.

Development Certificates

Development certificates can be generated for manual security experiments:

py -3.11 -m opcua_framework.utils.generate_certificates

These certificates are intended for local development and testing only.

The project does not attempt to reproduce a production PKI/CA infrastructure.

Engineering Focus

This project demonstrates practical skills relevant to industrial software, communication testing, and test automation.

Industrial Communication
OPC UA client-server architecture
OPC UA address-space browsing
Node interaction
Data read/write operations
OPC UA methods
Subscriptions
Monitored items
Test Automation
Pytest-based test architecture
Fixtures and test isolation
Functional testing
Negative testing
Regression testing
Automated reporting
Code coverage
Security Testing
OPC UA SecureChannel
Security policies
Sign mode
SignAndEncrypt mode
Username authentication
X.509 certificate trust
Certificate-based negative testing
Software Engineering
Modular architecture
Configuration-driven testing
Reusable client abstraction
Asynchronous programming
CI automation
Test evidence and reporting
Design Principles

The framework is built around a few key engineering principles:

Repeatability

Tests should produce consistent results when executed against the same deterministic environment.

Isolation

Each integration test should start from a controlled client/server state to minimize test-order dependencies.

Abstraction

Low-level OPC UA communication is encapsulated inside the client wrapper so test cases remain readable and focused on behavior.

Failure Awareness

The test suite validates both successful operations and expected failure conditions.

Security by Testing

Authentication, certificates, trust relationships, and SecureChannel modes are treated as testable system behavior rather than configuration that is assumed to be correct.

Automation

The same test suite can run locally and inside CI without requiring manual server setup.

Troubleshooting
Python Is Not Found

If PowerShell cannot find Python:

py --version

Install Python 3.11+ and reopen PowerShell.

Dependencies Are Missing

Activate the virtual environment and reinstall the project:

.\.venv\Scripts\Activate.ps1
pip install -e .
Port 4840 Is Already in Use

Stop the process using the port or configure another local endpoint:

$env:OPCUA_ENDPOINT="opc.tcp://127.0.0.1:4841/abb-test-server/"
Security Tests Fail

Ensure that:

Loopback OPC UA TCP communication is available
Required dependencies are installed
Test certificates can be generated
No stale certificate configuration is interfering with the test environment

The security tests generate their own development certificates and do not require a production certificate authority.

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

The simulated OPC UA server is localhost-only and is intended for automated QA, experimentation, and learning.

Future Improvements

Potential extensions include:

Parameterized test matrices for different OPC UA configurations
Fault-injection testing
Connection interruption and recovery testing
Subscription reconnect scenarios
Performance and latency measurements
Larger simulated industrial processes
Expanded security negative testing
Test-result dashboards
Containerized OPC UA test environments
Parallelized test execution
Key Takeaway

The project demonstrates a practical approach to testing industrial communication software:

Simulate
   ↓
Connect
   ↓
Browse & Interact
   ↓
Read / Write / Control
   ↓
Monitor Subscriptions
   ↓
Validate Failures & Security
   ↓
Generate Evidence
   ↓
Automate in CI

The primary focus is on:

Repeatability · Test Isolation · Communication Reliability · Security Validation · Maintainable Automation

Disclaimer

This is an independent portfolio project created for learning and demonstrating OPC UA testing and automation concepts.

It is not affiliated with, endorsed by, or representative of ABB, and it does not use real ABB hardware or proprietary ABB software.

The simulated server and industrial plant are designed solely to provide a controlled environment for automated OPC UA testing.


You can paste that entire block directly into **`README.md`** on GitHub.
