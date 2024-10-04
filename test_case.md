# Test Documentation

## 1. Project Overview

**Project Name**: CITS5206 Backend  
**Test Date**: 04/10/2024
**Tester**: Chen Shen 
**Testing Tools**: `unittest`, `coverage`  
**Test Command**: `coverage run -m unittest discover`

## 2. Scope of Testing

This test suite covers the core functionalities of the backend system, including:
- User Registration and Login
- User Profile and Password Management
- Podcast Management (Addition and Deletion)
- User Interests and Categories
- Note and Snippet Functionality

## 3. Testing Environment

- **Operating System**: Windows 10  
- **Python Version**: 3.11  
- **Database**: SQLite (in-memory database for testing purposes)  
- **Testing Framework**: `unittest`

## 4. Test Cases

### 4.1 User Authentication Tests

| Test Case ID | Test Case Name                    | Description                                                    | Expected Outcome                              | Test Result |
|--------------|-----------------------------------|----------------------------------------------------------------|----------------------------------------------|-------------|
| TC-01        | Successful Login                  | Login using valid username and password                        | Status Code: 201, Response includes Token    | Passed      |
| TC-02        | Failed Login - Incorrect Password | Attempt to login with an invalid password                      | Status Code: 401, Response indicates failure | Passed      |
| TC-03        | Successful Registration           | Register a new user with a unique username and password         | Status Code: 201, Registration is successful | Passed      |
| TC-04        | Registration Failed - User Exists | Attempt to register with an already existing username           | Status Code: 409, Registration fails         | Passed      |
| TC-05        | Successful Password Change        | Change the password with a valid Token                         | Status Code: 200, Password change successful | Passed      |
| TC-06        | Failed Password Change - Invalid Token | Attempt to change password using an invalid Token          | Status Code: 401, Token invalid or expired   | Passed      |

### 4.2 User Profile Management Tests

| Test Case ID | Test Case Name                    | Description                                                    | Expected Outcome                              | Test Result |
|--------------|-----------------------------------|----------------------------------------------------------------|----------------------------------------------|-------------|
| TC-07        | Successful User Info Update       | Update user information with valid data                        | Status Code: 200, Information updated        | Passed      |
| TC-08        | Failed User Info Update - Missing Data | Attempt to update user info with missing fields              | Status Code: 400, Request fails              | Passed      |

### 4.3 Podcast Management Tests

| Test Case ID | Test Case Name                    | Description                                                    | Expected Outcome                              | Test Result |
|--------------|-----------------------------------|----------------------------------------------------------------|----------------------------------------------|-------------|
| TC-09        | Successful Podcast Addition       | Add a new podcast with valid data and file upload              | Status Code: 201, Podcast added successfully | Passed      |
| TC-10        | Failed Podcast Deletion - Invalid Token | Attempt to delete podcast with an invalid Token             | Status Code: 401, Token invalid              | Passed      |
| TC-11        | Successful Podcast Deletion       | Delete a podcast with valid Token and podcast ID               | Status Code: 200, Podcast deleted successfully | Passed     |

### 4.4 Note and Snippet Tests

| Test Case ID | Test Case Name                    | Description                                                    | Expected Outcome                              | Test Result |
|--------------|-----------------------------------|----------------------------------------------------------------|----------------------------------------------|-------------|
| TC-12        | Successful Note Addition          | Add a note with valid Token and podcast ID                     | Status Code: 201, Note added successfully    | Passed      |
| TC-13        | Failed Note Addition - Invalid Token | Attempt to add a note using an invalid Token                | Status Code: 401, Token invalid              | Passed      |
| TC-14        | Successful Snippet Addition       | Add a podcast snippet with valid Token and podcast ID          | Status Code: 201, Snippet added successfully | Passed      |
| TC-15        | Successful Snippet Retrieval      | Retrieve all snippets for a valid podcast ID                   | Status Code: 200, Snippets retrieved         | Passed      |

### 4.5 Subscription Management Tests

| Test Case ID | Test Case Name                    | Description                                                    | Expected Outcome                              | Test Result |
|--------------|-----------------------------------|----------------------------------------------------------------|----------------------------------------------|-------------|
| TC-16        | Successful Subscription Listing   | List all subscriptions for the authenticated user              | Status Code: 200, Subscriptions listed       | Passed      |
| TC-17        | Failed Subscription Listing - Invalid Token | Attempt to list subscriptions using an invalid Token      | Status Code: 401, Token invalid              | Passed      |

## 5. Test Execution Summary

### Total Test Cases: 17  
### Passed: 17  
### Failed: 0  

All core functionalities have been tested, and no major issues were encountered. The system performs as expected under both normal and edge cases. Here is a summary of the test coverage and results for each module:

| Module                      | Total Test Cases | Passed | Failed |
|-----------------------------|------------------|--------|--------|
| User Authentication          | 6                | 6      | 0      |
| User Profile Management      | 2                | 2      | 0      |
| Podcast Management           | 3                | 3      | 0      |
| Note and Snippet Management  | 4                | 4      | 0      |
| Subscription Management      | 2                | 2      | 0      |

## 6. Code Coverage

By using `coverage` tool, the overall test coverage for the backend application has been measured. The total coverage is reported at 100%, indicating that all relevant parts of the codebase have been covered by the tests.

## 7. Conclusion

The backend system has been thoroughly tested, covering all essential functions. The tests confirm that the implemented features work as expected, including user authentication, podcast management, note taking, and snippet functionality. The system responds correctly to both valid and invalid inputs, demonstrating robustness in handling edge cases.

- **Areas of Strength**:  
  - High test coverage (100%) with comprehensive test cases.
  - The system handles invalid inputs and tokens gracefully.
  - User interactions, such as registration, login, password management, and podcast management, work as expected.

- **Potential Improvements**:  
  - Error handling could be further refined in some cases to provide more detailed feedback to the client. 
  - Ensure proper logging for troubleshooting in production.

The system is ready for deployment based on the test results. Future testing should continue to focus on integration with front-end components and stress testing under higher loads.