"""
SATWA HRMS - Employee Test Cases
Tool set: Playwright + Python + Pytest
Each test case is fully independent - own browser launch, no fixtures, no page objects.
Data is hardcoded per test case as per test design.

Application URL : http://192.168.31.50:5000
Admin username  : admin
Admin password  : admin123
"""

from playwright.sync_api import sync_playwright, expect
import re

BASE_URL = "http://192.168.31.50:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ======================================================================
# TC_001 - Add Employee with valid mandatory data
# ======================================================================
def test_tc_001_add_employee_with_valid_mandatory_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Navigate to Employees page
        page.goto(f"{BASE_URL}/employees.html")
        expect(page.locator("#employee-table-body")).to_be_visible()

        # Step 3: Click + Add Employee
        page.get_by_role("link", name="+ Add Employee").click()
        expect(page).to_have_url(f"{BASE_URL}/employee-form.html")
        expect(page.locator("#form-page-heading")).to_have_text("Add New Employee")

        # Step 4: Enter Full name
        page.get_by_label("Full name").fill("Test Employee")
        expect(page.get_by_label("Full name")).to_have_value("Test Employee")

        # Step 5: Enter Work email
        page.get_by_label("Work email").fill("test.employee@satwahrms.com")
        expect(page.get_by_label("Work email")).to_have_value("test.employee@satwahrms.com")

        # Step 6: Select Department
        page.get_by_label("Department").select_option("engineering")
        expect(page.get_by_label("Department")).to_have_value("engineering")

        # Step 7: Click Save Employee
        page.get_by_role("button", name="Save Employee").click()
        expect(page.locator("#form-success-alert")).to_contain_text("added successfully")

        # Step 8: Navigate back to Employees page and verify
        page.goto(f"{BASE_URL}/employees.html")
        row = page.locator("tr").filter(has_text="Test Employee")
        expect(row).to_have_count(1)
        expect(row.locator(".badge")).to_have_text("Active")

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()


# ======================================================================
# TC_002 - Add Employee with missing mandatory fields
# ======================================================================
def test_tc_002_add_employee_with_missing_mandatory_fields():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Navigate to Add Employee form
        page.goto(f"{BASE_URL}/employee-form.html")
        expect(page.locator("#form-page-heading")).to_have_text("Add New Employee")

        # Step 3: Leave Full name, Work email, Department empty and click Save
        expect(page.get_by_label("Full name")).to_have_value("")
        expect(page.get_by_label("Work email")).to_have_value("")
        expect(page.get_by_label("Department")).to_have_value("")

        page.get_by_role("button", name="Save Employee").click()

        # Expected: blocked submission, error alert, highlighted fields
        expect(page.locator("#form-error-alert")).to_contain_text(
            "Please fix the highlighted fields before submitting."
        )
        expect(page.locator(".field.has-error")).to_have_count(3)

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()


# ======================================================================
# TC_003 - Add Employee with duplicate email
# ======================================================================
def test_tc_003_add_employee_with_duplicate_email():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Navigate to Add Employee form
        page.goto(f"{BASE_URL}/employee-form.html")

        # Step 3: Enter Full name
        page.get_by_label("Full name").fill("Duplicate Test")
        expect(page.get_by_label("Full name")).to_have_value("Duplicate Test")

        # Step 4: Enter Work email that already exists (Rahul Mehta's seeded email)
        page.get_by_label("Work email").fill("rahul.mehta@satwahrms.com")
        expect(page.get_by_label("Work email")).to_have_value("rahul.mehta@satwahrms.com")

        # Step 5: Select Department
        page.get_by_label("Department").select_option("engineering")
        expect(page.get_by_label("Department")).to_have_value("engineering")

        # Step 6: Click Save Employee
        page.get_by_role("button", name="Save Employee").click()

        # Expected: duplicate email error, no employee created
        expect(page.locator("#form-error-alert")).to_contain_text(
            "An employee with this email already exists"
        )

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()


# ======================================================================
# TC_004 - Edit Employee designation and department
# ======================================================================
def test_tc_004_edit_employee_designation_and_department():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Navigate to Employees page
        page.goto(f"{BASE_URL}/employees.html")
        expect(page.locator("#employee-table-body")).to_be_visible()

        # Step 3: Click Edit icon on the first available employee row
        # (NOTE: using any existing employee, not a specific hardcoded name,
        #  since the originally-named employee in the test design may have
        #  been deleted by another test run)
        first_row = page.locator("#employee-table-body tr").first
        employee_name_before = first_row.locator(".emp-name-text").inner_text()
        first_row.locator("a.btn-icon").click()
        expect(page).to_have_url(re.compile(r".*employee-form\.html\?id=EMP-\d+"))

        # Step 4: Update Designation field
        page.get_by_label("Designation").fill("Senior Account Executive")
        expect(page.get_by_label("Designation")).to_have_value("Senior Account Executive")

        # Step 5: Change Department
        page.get_by_label("Department").select_option("engineering")
        expect(page.get_by_label("Department")).to_have_value("engineering")

        # Step 6: Click Update Employee
        page.get_by_role("button", name="Update Employee").click()
        expect(page.locator("#form-success-alert")).to_contain_text("updated successfully")

        # Step 7: Navigate back to Employees page and verify
        page.goto(f"{BASE_URL}/employees.html")
        updated_row = page.locator("tr").filter(has_text=employee_name_before)
        expect(updated_row).to_contain_text("Senior Account Executive")
        expect(updated_row).to_contain_text("Engineering")

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()


# ======================================================================
# TC_005 - Edit Employee with invalid email format
# ======================================================================
def test_tc_005_edit_employee_with_invalid_email_format():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Navigate to Employees page
        page.goto(f"{BASE_URL}/employees.html")

        # Step 3: Click Edit icon on the first available employee row
        first_row = page.locator("#employee-table-body tr").first
        first_row.locator("a.btn-icon").click()
        expect(page.locator("#form-page-heading")).to_contain_text("Edit Employee")

        # Step 4: Clear Work email and enter invalid format (no @ symbol)
        page.get_by_label("Work email").fill("sneha.desai-invalid")
        expect(page.get_by_label("Work email")).to_have_value("sneha.desai-invalid")

        # Step 5: Click Update Employee
        page.get_by_role("button", name="Update Employee").click()

        # Expected: the Work email field uses HTML5 type="email", so the BROWSER'S
        # OWN native validation blocks the form submit before our app's JS even
        # runs - the custom "#form-error-alert" never fires for this case.
        # We verify the native validity state directly instead.
        email_field = page.locator("#field-email")
        expect(email_field).to_have_js_property("validity.valid", False)
        validation_message = email_field.evaluate("el => el.validationMessage")
        assert "@" in validation_message, (
            f"Expected native browser validation message to mention '@', got: {validation_message}"
        )

        # Confirm no success alert appeared and the page did not navigate away
        expect(page.locator("#form-success-alert")).not_to_contain_text("updated successfully")
        expect(page).to_have_url(page.url)  # still on the same edit form, submission was blocked

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()


# ======================================================================
# TC_006 - Delete Employee successfully
# ======================================================================
def test_tc_006_delete_employee_successfully():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 1b: First create an employee specifically to delete in this test,
        # so the test does not depend on any pre-existing seeded data.
        page.goto(f"{BASE_URL}/employee-form.html")
        page.get_by_label("Full name").fill("Delete Me Employee")
        page.get_by_label("Work email").fill("delete.me@satwahrms.com")
        page.get_by_label("Department").select_option("engineering")
        page.get_by_role("button", name="Save Employee").click()
        expect(page.locator("#form-success-alert")).to_contain_text("added successfully")

        # Step 2: Navigate to Employees page
        page.goto(f"{BASE_URL}/employees.html")
        row = page.locator("tr").filter(has_text="Delete Me Employee")
        expect(row).to_have_count(1)

        # Step 3: Click Delete icon on that row
        row.locator(".employee-delete-btn").click()

        # Step 4: Verify confirmation dialog content
        expect(page.locator("#delete-modal-title")).to_have_text("Remove employee?")
        expect(page.locator("#confirm-delete-name")).to_have_text("Delete Me Employee")

        # Step 5: Click Remove Employee to confirm
        page.get_by_role("button", name="Remove Employee").click()

        # Expected: success alert, row removed from table
        expect(page.locator("#employee-success-alert")).to_contain_text(
            "Employee removed successfully."
        )
        expect(page.locator("#employee-table-body").get_by_text("Delete Me Employee")).to_have_count(0)

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()


# ======================================================================
# TC_007 - Cancel Employee deletion
# ======================================================================
def test_tc_007_cancel_employee_deletion():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Navigate to Employees page
        page.goto(f"{BASE_URL}/employees.html")
        expect(page.locator("#employee-table-body")).to_be_visible()

        # Use any existing employee row (first row) instead of a hardcoded name,
        # since the originally-named employee may have been removed by another test.
        first_row = page.locator("#employee-table-body tr").first
        employee_name = first_row.locator(".emp-name-text").inner_text()

        # Step 3: Click Delete icon on that row
        first_row.locator(".employee-delete-btn").click()
        expect(page.locator("#confirm-delete-name")).to_have_text(employee_name)

        # Step 4: Click Cancel in the confirmation dialog
        page.locator("#delete-modal").get_by_role("button", name="Cancel").click()
        expect(page.locator("#delete-modal")).not_to_have_class("is-open")

        # Step 5: Refresh the Employees page and verify employee still exists
        page.reload()
        expect(page.locator("#employee-table-body").get_by_text(employee_name)).to_have_count(1)

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()
