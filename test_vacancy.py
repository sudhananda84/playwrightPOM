"""
SATWA HRMS - Vacancy Test Cases
Tool set: Playwright + Python + Pytest
Each test case is fully independent - own browser launch, no fixtures, no page objects.
Data is hardcoded per test case as per test design.

Application URL : http://192.168.31.50:5000
Admin username  : admin
Admin password  : admin123
"""

from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://192.168.31.50:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ======================================================================
# TC_008 - Add Vacancy with valid data
# ======================================================================
def test_tc_008_add_vacancy_with_valid_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Navigate to Vacancies page
        page.goto(f"{BASE_URL}/vacancies.html")
        expect(page.locator("#vacancy-table-body")).to_be_visible()

        # Step 3: Click + Create Vacancy
        page.get_by_role("button", name="+ Create Vacancy").click()
        expect(page.locator("#vacancy-modal-title")).to_have_text("Create Vacancy")

        # Step 4: Enter Position
        page.get_by_label("Vacancy Name / Position").fill("Senior QA Automation Engineer")
        expect(page.get_by_label("Vacancy Name / Position")).to_have_value(
            "Senior QA Automation Engineer"
        )

        # Step 5: Enter Minimum and Maximum Experience
        page.get_by_label("Minimum Experience (years)").fill("3")
        page.get_by_label("Maximum Experience (years)").fill("6")
        expect(page.get_by_label("Minimum Experience (years)")).to_have_value("3")
        expect(page.get_by_label("Maximum Experience (years)")).to_have_value("6")

        # Step 6: Enter Total Budget
        page.get_by_label("Total Budget").fill("1800000")
        expect(page.get_by_label("Total Budget")).to_have_value("1800000")

        # Step 7: Select Skills (multi-select)
        skills_select = page.get_by_test_id("vacancy-skills-select")
        skills_select.select_option(["Selenium", "Playwright", "Manual Testing"])
        expect(skills_select).to_have_values(["Selenium", "Playwright", "Manual Testing"])

        # Step 8: Click Save Vacancy
        page.get_by_test_id("vacancy-save-btn").click()
        expect(page.locator("#vacancy-success-alert")).to_contain_text(
            "created successfully"
        )

        # Verify the vacancy appears in the table with correct details
        row = page.locator("tr").filter(has_text="Senior QA Automation Engineer")
        expect(row).to_have_count(1)
        expect(row).to_contain_text("3 – 6 yrs")
        expect(row).to_contain_text("Selenium, Playwright, Manual Testing")
        expect(row.locator("select.vacancy-status-select")).to_have_value("open")

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()


# ======================================================================
# TC_009 - Add Vacancy with minimum experience greater than maximum
# ======================================================================
def test_tc_009_add_vacancy_min_experience_greater_than_max():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Navigate to Vacancies page
        page.goto(f"{BASE_URL}/vacancies.html")

        # Step 3: Click + Create Vacancy
        page.get_by_role("button", name="+ Create Vacancy").click()
        expect(page.locator("#vacancy-modal-title")).to_have_text("Create Vacancy")

        # Step 4: Enter Position
        page.get_by_label("Vacancy Name / Position").fill("Bad Vacancy")
        expect(page.get_by_label("Vacancy Name / Position")).to_have_value("Bad Vacancy")

        # Step 5: Enter Minimum Experience greater than Maximum Experience
        page.get_by_label("Minimum Experience (years)").fill("8")
        page.get_by_label("Maximum Experience (years)").fill("3")
        expect(page.get_by_label("Minimum Experience (years)")).to_have_value("8")
        expect(page.get_by_label("Maximum Experience (years)")).to_have_value("3")

        # Step 6: Enter Total Budget
        page.get_by_label("Total Budget").fill("1000000")
        expect(page.get_by_label("Total Budget")).to_have_value("1000000")

        # Step 7: Select Skill
        skills_select = page.get_by_test_id("vacancy-skills-select")
        skills_select.select_option(["Java"])
        expect(skills_select).to_have_values(["Java"])

        # Step 8: Click Save Vacancy
        page.get_by_test_id("vacancy-save-btn").click()

        # Expected: vacancy NOT created, error shown, modal remains open
        expect(page.locator("#vacancy-form-error")).to_contain_text(
            "Minimum experience cannot exceed maximum experience"
        )
        expect(page.locator("#vacancy-modal")).to_have_class("modal-overlay is-open")
        expect(page.get_by_label("Vacancy Name / Position")).to_have_value("Bad Vacancy")

        # Close modal before logout
        page.locator("#vacancy-modal").get_by_role("button", name="Cancel").click()

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()


# ======================================================================
# TC_010 - Edit Vacancy status, then Delete Vacancy with linked candidate (cascade)
# ======================================================================
def test_tc_010_edit_vacancy_status_and_delete_with_cascade():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Step 1: Log in
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url(f"{BASE_URL}/dashboard.html")

        # Step 2: Create a vacancy named "Backend Developer"
        page.goto(f"{BASE_URL}/vacancies.html")
        page.get_by_role("button", name="+ Create Vacancy").click()
        page.get_by_label("Vacancy Name / Position").fill("Backend Developer")
        page.get_by_label("Minimum Experience (years)").fill("2")
        page.get_by_label("Maximum Experience (years)").fill("5")
        page.get_by_label("Total Budget").fill("1500000")
        page.get_by_test_id("vacancy-skills-select").select_option(["Java"])
        page.get_by_test_id("vacancy-save-btn").click()
        expect(page.locator("#vacancy-success-alert")).to_contain_text("created successfully")

        vacancy_row = page.locator("tr").filter(has_text="Backend Developer")
        expect(vacancy_row.locator("select.vacancy-status-select")).to_have_value("open")

        # Step 3: Change status from open to on-hold
        vacancy_row.locator("select.vacancy-status-select").select_option("on-hold")
        expect(page.locator("#vacancy-success-alert")).to_contain_text(
            'Status updated to "on-hold"'
        )
        expect(vacancy_row.locator("select.vacancy-status-select")).to_have_value("on-hold")

        # Capture the vacancy ID for later linkage to the candidate
        vacancy_id = vacancy_row.locator("td code").inner_text()

        # Step 4: Navigate to Candidates page and add a candidate linked to this vacancy
        page.goto(f"{BASE_URL}/candidates.html")
        page.get_by_role("button", name="+ Add Candidate").click()
        page.get_by_label("Candidate Name").fill("Karthik Subramaniam")
        page.get_by_label("Experience — Years").fill("4")
        page.get_by_label("Experience — Months").fill("6")
        page.get_by_test_id("candidate-vacancy-select").select_option(vacancy_id)
        page.get_by_test_id("candidate-primary-skills-select").select_option(["Java"])
        page.get_by_label("Current CTC").fill("1200000")
        page.get_by_label("Expected CTC").fill("1600000")

        # Create a temporary resume file to upload
        import os
        resume_path = "/tmp/tc010_resume.pdf"
        with open(resume_path, "wb") as f:
            f.write(b"%PDF-1.4 dummy resume content")
        page.locator("#candidate-resume").set_input_files(resume_path)

        page.get_by_test_id("candidate-save-btn").click()
        expect(page.locator("#candidate-success-alert")).to_contain_text("added successfully")

        candidate_row = page.locator("tr").filter(has_text="Karthik Subramaniam")
        expect(candidate_row).to_have_count(1)
        expect(candidate_row).to_contain_text("Backend Developer")
        os.remove(resume_path)

        # Step 5: Navigate back to Vacancies page, click Delete on Backend Developer
        page.goto(f"{BASE_URL}/vacancies.html")
        vacancy_row = page.locator("tr").filter(has_text="Backend Developer")
        vacancy_row.locator(".vacancy-delete-btn").click()

        # Step 6: Verify delete confirmation message mentions the linked candidate
        expect(page.locator("#vacancy-delete-title")).to_have_text("Delete vacancy?")
        expect(page.locator("#vacancy-delete-message")).to_contain_text("Backend Developer")
        expect(page.locator("#vacancy-delete-message")).to_contain_text(
            "This vacancy has 1 linked candidate(s) — they will also be removed."
        )

        # Step 7: Confirm deletion
        page.get_by_role("button", name="Delete Vacancy").click()
        expect(page.locator("#vacancy-success-alert")).to_contain_text("deleted")
        expect(page.locator("tr").filter(has_text="Backend Developer")).to_have_count(0)

        # Step 8: Navigate to Candidates page and verify cascade removed the candidate
        page.goto(f"{BASE_URL}/candidates.html")
        expect(page.locator("#active-candidate-table-body").get_by_text("Karthik Subramaniam")).to_have_count(0)
        page.get_by_role("tab", name="Rejected").click()
        expect(page.locator("#rejected-candidate-table-body").get_by_text("Karthik Subramaniam")).to_have_count(0)

        # Logout
        page.get_by_role("link", name="Logout").click()
        expect(page).to_have_url(f"{BASE_URL}/index.html")

        browser.close()
