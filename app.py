from flask import Flask, request, render_template_string, session
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Used for the temporary profile session.
# We will replace this with a real database/account system later.
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "ai-job-hunter-development-key"
)

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


# ============================================================
# SUPPORTED ADZUNA MARKETS
# ============================================================

COUNTRIES = {
    "United Kingdom": "gb",
    "United States": "us",
    "Canada": "ca",
    "Australia": "au",
    "New Zealand": "nz",
    "Germany": "de",
    "France": "fr",
    "Spain": "es",
    "Italy": "it",
    "Netherlands": "nl",
    "Poland": "pl",
    "Austria": "at",
    "Switzerland": "ch",
    "Brazil": "br",
    "Mexico": "mx",
    "India": "in",
    "Singapore": "sg",
    "South Africa": "za"
}


# ============================================================
# HTML
# ============================================================

HTML = """
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>AI Job Hunter</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background: #080b12;

    color: white;
}

.container {

    width: 92%;

    max-width: 1100px;

    margin: 30px auto 60px;
}

.header {

    text-align: center;

    margin-bottom: 25px;
}

.header h1 {

    font-size: 42px;

    margin: 0 0 10px;
}

.header p {

    color: #aeb7c7;

    font-size: 17px;
}


/* ============================================================
   NAV
   ============================================================ */

.nav {

    display: flex;

    justify-content: center;

    gap: 10px;

    margin-bottom: 25px;

    flex-wrap: wrap;
}

.nav a {

    color: white;

    text-decoration: none;

    background: #151d2b;

    border: 1px solid #2b3850;

    padding: 9px 16px;

    border-radius: 7px;

    font-size: 14px;
}

.nav a:hover {

    border-color: #2388ff;
}


/* ============================================================
   PROFILE
   ============================================================ */

.profile-box {

    background: #111722;

    border: 1px solid #263044;

    border-radius: 14px;

    padding: 25px;

    margin-bottom: 25px;
}

.profile-box h2 {

    margin-top: 0;
}

.profile-description {

    color: #9da9ba;

    font-size: 14px;

    line-height: 1.5;
}

.form-grid {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 17px;

    margin-top: 20px;
}

.field {

    display: flex;

    flex-direction: column;
}

.field-full {

    grid-column: 1 / -1;
}

label {

    margin-bottom: 8px;

    font-weight: bold;

    color: #dce4f3;
}

input,
select,
textarea {

    width: 100%;

    padding: 13px;

    border-radius: 8px;

    border: 1px solid #303b52;

    background: #0b1019;

    color: white;

    outline: none;

    font-family: inherit;
}

textarea {

    min-height: 90px;

    resize: vertical;
}

input:focus,
select:focus,
textarea:focus {

    border-color: #2388ff;
}

.button-area {

    margin-top: 20px;
}

button {

    width: 100%;

    padding: 14px;

    border: none;

    border-radius: 8px;

    background: #1877f2;

    color: white;

    font-size: 16px;

    font-weight: bold;

    cursor: pointer;
}

button:hover {

    background: #0f65d4;
}


/* ============================================================
   SUBSCRIPTION
   ============================================================ */

.subscription {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 15px;

    margin-top: 20px;
}

.plan {

    background: #0b1019;

    border: 1px solid #293449;

    border-radius: 10px;

    padding: 18px;
}

.plan h3 {

    margin-top: 0;
}

.plan p {

    color: #9da9ba;

    font-size: 13px;

    line-height: 1.5;
}

.plan ul {

    padding-left: 18px;

    color: #cbd5e1;

    font-size: 13px;

    line-height: 1.8;
}

.plan-free {

    border-color: #344054;
}

.plan-premium {

    border-color: #7c5cff;
}

.premium-label {

    display: inline-block;

    background: #7c5cff;

    color: white;

    padding: 4px 8px;

    border-radius: 5px;

    font-size: 11px;

    font-weight: bold;

    margin-bottom: 8px;
}


/* ============================================================
   SEARCH
   ============================================================ */

.search-box {

    background: #111722;

    padding: 25px;

    border-radius: 14px;

    border: 1px solid #263044;

    margin-bottom: 30px;
}

.search-box h2 {

    margin-top: 0;
}


/* ============================================================
   RESULTS
   ============================================================ */

.results-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 15px;
}

.results-header h2 {

    margin: 0;
}

.job-card {

    background: #111722;

    border: 1px solid #293449;

    border-radius: 10px;

    padding: 20px;

    margin-bottom: 18px;
}

.job-title {

    font-size: 21px;

    font-weight: bold;

    margin-bottom: 8px;
}

.company {

    color: #58a6ff;

    margin-bottom: 6px;
}

.location {

    color: #b7c0d0;

    margin-bottom: 6px;
}

.salary {

    color: #55d187;

    margin-bottom: 15px;
}


/* ============================================================
   MATCH
   ============================================================ */

.match-box {

    background: #0a1420;

    border: 1px solid #245a3d;

    border-radius: 9px;

    padding: 15px;

    margin: 15px 0;
}

.match-top {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 10px;
}

.match-score {

    font-size: 22px;

    font-weight: bold;

    color: #4ade80;
}

.match-label {

    font-size: 12px;

    color: #8fa0b5;
}

.progress {

    width: 100%;

    height: 8px;

    background: #202938;

    border-radius: 10px;

    overflow: hidden;

    margin-bottom: 12px;
}

.progress-bar {

    height: 100%;

    background: #22c55e;

    border-radius: 10px;
}

.match-reason {

    color: #cbd5e1;

    font-size: 13px;

    line-height: 1.55;
}


/* ============================================================
   JOB DESCRIPTION
   ============================================================ */

.description {

    color: #c2c9d5;

    line-height: 1.5;

    font-size: 14px;

    margin-bottom: 15px;
}

.apply-button {

    display: inline-block;

    background: #1877f2;

    color: white;

    text-decoration: none;

    padding: 10px 16px;

    border-radius: 6px;

    font-weight: bold;

    font-size: 14px;
}

.apply-button:hover {

    background: #0f65d4;
}

.source {

    font-size: 11px;

    color: #707b8f;

    margin-top: 10px;
}


/* ============================================================
   MESSAGES
   ============================================================ */

.success {

    background: #102819;

    border: 1px solid #28643b;

    padding: 14px;

    border-radius: 8px;

    color: #8df0a5;

    margin-bottom: 20px;
}

.error {

    background: #351519;

    border: 1px solid #71323a;

    padding: 15px;

    border-radius: 8px;

    color: #ffb4b4;

    margin-bottom: 20px;
}

.empty {

    text-align: center;

    padding: 40px;

    color: #9ca7b8;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 700px) {

    .form-grid {

        grid-template-columns: 1fr;
    }

    .field-full {

        grid-column: auto;
    }

    .subscription {

        grid-template-columns: 1fr;
    }

    .header h1 {

        font-size: 32px;
    }

    .container {

        width: 94%;
    }

}

</style>

</head>


<body>

<div class="container">


<!-- ==========================================================
     HEADER
     ========================================================== -->

<div class="header">

    <h1>
        AI Job Hunter
    </h1>

    <p>
        Find real jobs and discover how well they match you.
    </p>

</div>


<!-- ==========================================================
     NAVIGATION
     ========================================================== -->

<div class="nav">

    <a href="/">
        Job Search
    </a>

    <a href="#profile">
        My Profile
    </a>

    <a href="#plans">
        Plans
    </a>

</div>


{% if success %}

<div class="success">

    {{ success }}

</div>

{% endif %}


{% if error %}

<div class="error">

    {{ error }}

</div>

{% endif %}


<!-- ==========================================================
     PROFILE
     ========================================================== -->

<div
    class="profile-box"
    id="profile"
>

    <h2>
        👤 My Job Profile
    </h2>

    <div class="profile-description">

        Create your profile once.
        AI Job Hunter will use it to personalize
        your job matches.

    </div>


    <form
        method="POST"
        action="/profile"
    >


        <div class="form-grid">


            <!-- NAME -->

            <div class="field">

                <label>
                    Your Name
                </label>

                <input
                    type="text"
                    name="name"
                    placeholder="Your name"
                    value="{{ profile.name }}"
                >

            </div>


            <!-- TARGET JOB -->

            <div class="field">

                <label>
                    Target Job
                </label>

                <input
                    type="text"
                    name="target_job"
                    placeholder="e.g. Software Developer"
                    value="{{ profile.target_job }}"
                >

            </div>


            <!-- COUNTRY -->

            <div class="field">

                <label>
                    Preferred Country
                </label>

                <select name="profile_country">

                    {% for country_name, country_code in countries.items() %}

                    <option
                        value="{{ country_code }}"
                        {% if profile.country == country_code %}
                            selected
                        {% endif %}
                    >

                        {{ country_name }}

                    </option>

                    {% endfor %}

                </select>

            </div>


            <!-- CITY -->

            <div class="field">

                <label>
                    Preferred City / Location
                </label>

                <input
                    type="text"
                    name="profile_location"
                    placeholder="e.g. New York"
                    value="{{ profile.location }}"
                >

            </div>


            <!-- EXPERIENCE -->

            <div class="field">

                <label>
                    Experience Level
                </label>

                <select name="profile_experience">

                    <option
                        value="Any"
                        {% if profile.experience == "Any" %}
                            selected
                        {% endif %}
                    >
                        Any
                    </option>

                    <option
                        value="Entry Level"
                        {% if profile.experience == "Entry Level" %}
                            selected
                        {% endif %}
                    >
                        Entry Level
                    </option>

                    <option
                        value="Mid Level"
                        {% if profile.experience == "Mid Level" %}
                            selected
                        {% endif %}
                    >
                        Mid Level
                    </option>

                    <option
                        value="Senior"
                        {% if profile.experience == "Senior" %}
                            selected
                        {% endif %}
                    >
                        Senior
                    </option>

                </select>

            </div>


            <!-- JOB TYPE -->

            <div class="field">

                <label>
                    Preferred Job Type
                </label>

                <select name="profile_job_type">

                    <option
                        value="Any"
                        {% if profile.job_type == "Any" %}
                            selected
                        {% endif %}
                    >
                        Any
                    </option>

                    <option
                        value="Full-time"
                        {% if profile.job_type == "Full-time" %}
                            selected
                        {% endif %}
                    >
                        Full-time
                    </option>

                    <option
                        value="Part-time"
                        {% if profile.job_type == "Part-time" %}
                            selected
                        {% endif %}
                    >
                        Part-time
                    </option>

                    <option
                        value="Contract"
                        {% if profile.job_type == "Contract" %}
                            selected
                        {% endif %}
                    >
                        Contract
                    </option>

                </select>

            </div>


            <!-- SKILLS -->

            <div class="field field-full">

                <label>
                    Your Skills
                </label>

                <textarea
                    name="skills"
                    placeholder="e.g. Python, Flask, JavaScript, SQL, Git, HTML, CSS"
                >{{ profile.skills }}</textarea>

            </div>


            <!-- EDUCATION -->

            <div class="field field-full">

                <label>
                    Education
                </label>

                <input
                    type="text"
                    name="education"
                    placeholder="e.g. BSc Computer Science"
                    value="{{ profile.education }}"
                >

            </div>


        </div>


        <div class="button-area">

            <button type="submit">

                Save My Profile

            </button>

        </div>


    </form>

</div>


<!-- ==========================================================
     SUBSCRIPTION PLANS
     ========================================================== -->

<div
    class="profile-box"
    id="plans"
>

    <h2>
        ⭐ AI Job Hunter Plans
    </h2>

    <div class="profile-description">

        The subscription structure is ready for the
        payment system we will connect later.

    </div>


    <div class="subscription">


        <!-- FREE -->

        <div class="plan plan-free">

            <h3>
                Free
            </h3>

            <p>
                Start finding jobs without paying.
            </p>

            <ul>

                <li>
                    Real job search
                </li>

                <li>
                    Basic match score
                </li>

                <li>
                    Basic profile
                </li>

                <li>
                    Limited searches
                </li>

            </ul>

        </div>


        <!-- PREMIUM -->

        <div class="plan plan-premium">

            <span class="premium-label">
                PREMIUM
            </span>

            <h3>
                AI Job Hunter Pro
            </h3>

            <p>
                Advanced tools for serious job seekers.
            </p>

            <ul>

                <li>
                    Advanced AI job matching
                </li>

                <li>
                    Unlimited searches
                </li>

                <li>
                    AI CV customization
                </li>

                <li>
                    AI cover letters
                </li>

                <li>
                    Interview preparation
                </li>

                <li>
                    Application tracking
                </li>

                <li>
                    Job alerts
                </li>

            </ul>

        </div>


    </div>

</div>


<!-- ==========================================================
     SEARCH
     ========================================================== -->

<div class="search-box">

    <h2>
        🔎 Find Jobs
    </h2>


    <form method="POST">


        <div class="form-grid">


            <!-- JOB -->

            <div class="field">

                <label>
                    What job are you looking for?
                </label>

                <input
                    type="text"
                    name="job"
                    placeholder="e.g. Software Developer"
                    value="{{ search_data.job }}"
                    required
                >

            </div>


            <!-- COUNTRY -->

            <div class="field">

                <label>
                    Country / Market
                </label>

                <select
                    name="country"
                    required
                >

                    {% for country_name, country_code in countries.items() %}

                    <option
                        value="{{ country_code }}"
                        {% if search_data.country == country_code %}
                            selected
                        {% endif %}
                    >

                        {{ country_name }}

                    </option>

                    {% endfor %}

                </select>

            </div>


            <!-- LOCATION -->

            <div class="field">

                <label>
                    City or Location
                </label>

                <input
                    type="text"
                    name="location"
                    placeholder="e.g. New York"
                    value="{{ search_data.location }}"
                >

            </div>


            <!-- EXPERIENCE -->

            <div class="field">

                <label>
                    Experience Level
                </label>

                <select name="experience">

                    <option
                        value="Any"
                        {% if search_data.experience == "Any" %}
                            selected
                        {% endif %}
                    >
                        Any
                    </option>

                    <option
                        value="Entry Level"
                        {% if search_data.experience == "Entry Level" %}
                            selected
                        {% endif %}
                    >
                        Entry Level
                    </option>

                    <option
                        value="Mid Level"
                        {% if search_data.experience == "Mid Level" %}
                            selected
                        {% endif %}
                    >
                        Mid Level
                    </option>

                    <option
                        value="Senior"
                        {% if search_data.experience == "Senior" %}
                            selected
                        {% endif %}
                    >
                        Senior
                    </option>

                </select>

            </div>


            <!-- JOB TYPE -->

            <div class="field">

                <label>
                    Job Type
                </label>

                <select name="job_type">

                    <option
                        value="Any"
                        {% if search_data.job_type == "Any" %}
                            selected
                        {% endif %}
                    >
                        Any
                    </option>

                    <option
                        value="Full-time"
                        {% if search_data.job_type == "Full-time" %}
                            selected
                        {% endif %}
                    >
                        Full-time
                    </option>

                    <option
                        value="Part-time"
                        {% if search_data.job_type == "Part-time" %}
                            selected
                        {% endif %}
                    >
                        Part-time
                    </option>

                    <option
                        value="Contract"
                        {% if search_data.job_type == "Contract" %}
                            selected
                        {% endif %}
                    >
                        Contract
                    </option>

                </select>

            </div>


        </div>


        <div class="button-area">

            <button type="submit">

                Find My Jobs

            </button>

        </div>


    </form>

</div>


<!-- ==========================================================
     RESULTS
     ========================================================== -->

{% if searched %}


<div class="results-header">

    <h2>

        {{ jobs|length }} jobs found

    </h2>

</div>


{% if jobs %}


{% for job in jobs %}


<div class="job-card">


    <div class="job-title">

        {{ job.title }}

    </div>


    {% if job.company %}

    <div class="company">

        {{ job.company }}

    </div>

    {% endif %}


    {% if job.location %}

    <div class="location">

        📍 {{ job.location }}

    </div>

    {% endif %}


    {% if job.salary %}

    <div class="salary">

        💰 {{ job.salary }}

    </div>

    {% endif %}


    <!-- MATCH -->

    <div class="match-box">


        <div class="match-top">


            <div class="match-score">

                {{ job.match_score }}% Match

            </div>


            <div class="match-label">

                AI Job Match

            </div>


        </div>


        <div class="progress">


            <div
                class="progress-bar"
                style="width: {{ job.match_score }}%;"
            ></div>


        </div>


        <div class="match-reason">

            {{ job.match_reason }}

        </div>


    </div>


    <!-- DESCRIPTION -->

    <div class="description">

        {{ job.description }}

    </div>


    <!-- APPLY -->

    {% if job.redirect_url %}

    <a
        class="apply-button"
        href="{{ job.redirect_url }}"
        target="_blank"
        rel="noopener noreferrer"
    >

        Apply for Job

    </a>

    {% endif %}


    <div class="source">

        Job listing provided through Adzuna.

    </div>


</div>


{% endfor %}


{% else %}


<div class="empty">

    No jobs were found.

    <br><br>

    Try another job title, location, or country.

</div>


{% endif %}


{% endif %}


</div>

</body>

</html>
"""


# ============================================================
# DEFAULT PROFILE
# ============================================================

DEFAULT_PROFILE = {

    "name": "",

    "target_job": "",

    "country": "us",

    "location": "",

    "experience": "Any",

    "job_type": "Any",

    "skills": "",

    "education": ""

}


# ============================================================
# GET PROFILE
# ============================================================

def get_profile():

    profile = session.get(
        "profile"
    )

    if not profile:

        profile = DEFAULT_PROFILE.copy()

    return profile


# ============================================================
# MATCH ENGINE
# ============================================================

def calculate_match_score(
    job,
    search_job,
    search_location,
    experience,
    job_type,
    profile=None
):

    profile = profile or {}

    title = (
        job.get("title") or ""
    ).lower()

    description = (
        job.get("description") or ""
    ).lower()


    location_data = job.get(
        "location",
        {}
    )


    if isinstance(
        location_data,
        dict
    ):

        job_location = location_data.get(
            "display_name",
            ""
        )

    else:

        job_location = ""


    job_location_lower = (
        job_location.lower()
    )


    # ========================================================
    # USE PROFILE WHEN AVAILABLE
    # ========================================================

    profile_target = (
        profile.get(
            "target_job",
            ""
        ).strip()
    )


    profile_skills = (
        profile.get(
            "skills",
            ""
        ).lower()
    )


    profile_location = (
        profile.get(
            "location",
            ""
        ).lower().strip()
    )


    profile_experience = (
        profile.get(
            "experience",
            "Any"
        )
    )


    profile_job_type = (
        profile.get(
            "job_type",
            "Any"
        )
    )


    # Use profile target if present.
    effective_job = (
        profile_target
        if profile_target
        else search_job
    )


    effective_job_lower = (
        effective_job.lower().strip()
    )


    # Use profile location if present.
    effective_location = (
        profile_location
        if profile_location
        else search_location.lower().strip()
    )


    # Use profile experience if search is Any.
    effective_experience = (

        profile_experience

        if experience == "Any"
        and profile_experience != "Any"

        else experience

    )


    # Use profile job type if search is Any.
    effective_job_type = (

        profile_job_type

        if job_type == "Any"
        and profile_job_type != "Any"

        else job_type

    )


    score = 0

    reasons = []

    warnings = []


    # ========================================================
    # 1. JOB TITLE — 40
    # ========================================================

    search_words = [

        word

        for word in effective_job_lower.split()

        if len(word) > 2

    ]


    title_matches = [

        word

        for word in search_words

        if word in title

    ]


    if search_words:

        title_ratio = (

            len(title_matches)
            /
            len(search_words)

        )


        if title_ratio >= 0.75:

            score += 40

            reasons.append(
                "The job title strongly matches your target role."
            )


        elif title_ratio >= 0.50:

            score += 30

            reasons.append(
                "The job title partially matches your target role."
            )


        elif title_ratio > 0:

            score += 18

            reasons.append(
                "Some target-role terms match the job title."
            )


        else:

            score += 5

            warnings.append(
                "The job title does not closely match your target role."
            )


    else:

        score += 20


    # ========================================================
    # 2. SKILLS — 25
    # ========================================================

    common_skills = [

        "python",
        "javascript",
        "typescript",
        "java",
        "c++",
        "c#",
        "php",
        "ruby",
        "go",
        "rust",
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "react",
        "angular",
        "vue",
        "node",
        "node.js",
        "flask",
        "django",
        "fastapi",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "git",
        "github",
        "html",
        "css",
        "excel",
        "power bi",
        "tableau",
        "machine learning",
        "artificial intelligence",
        "ai",
        "data analysis",
        "data science",
        "marketing",
        "sales",
        "customer service",
        "project management"

    ]


    requested_skills = []


    # Skills from user profile.
    for skill in common_skills:

        if skill in profile_skills:

            requested_skills.append(
                skill
            )


    # Skills directly typed into search.
    for skill in common_skills:

        if skill in effective_job_lower:

            if skill not in requested_skills:

                requested_skills.append(
                    skill
                )


    if requested_skills:


        matched_skills = [

            skill

            for skill in requested_skills

            if skill in title
            or skill in description

        ]


        skill_ratio = (

            len(matched_skills)
            /
            len(requested_skills)

        )


        skill_points = round(
            skill_ratio * 25
        )


        score += skill_points


        if matched_skills:

            reasons.append(

                "Matching skills found: "
                +
                ", ".join(
                    matched_skills[:6]
                )
                +
                "."

            )


        missing_skills = [

            skill

            for skill in requested_skills

            if skill not in matched_skills

        ]


        if missing_skills:

            warnings.append(

                "Skills not clearly found: "
                +
                ", ".join(
                    missing_skills[:4]
                )
                +
                "."

            )


    else:


        keyword_matches = sum(

            1

            for word in search_words

            if word in description

        )


        score += min(

            25,

            keyword_matches * 8

        )


    # ========================================================
    # 3. LOCATION — 15
    # ========================================================

    if effective_location:


        if effective_location in job_location_lower:

            score += 15

            reasons.append(
                "The job location matches your preference."
            )


        else:

            score += 3

            warnings.append(
                "The exact preferred location was not found."
            )


    else:

        score += 8


    # ========================================================
    # 4. EXPERIENCE — 10
    # ========================================================

    experience_words = {

        "Entry Level": [

            "entry level",
            "entry-level",
            "junior",
            "graduate",
            "trainee",
            "intern",
            "associate"

        ],

        "Mid Level": [

            "mid level",
            "mid-level",
            "intermediate",
            "experienced"

        ],

        "Senior": [

            "senior",
            "lead",
            "principal",
            "manager",
            "director"

        ]

    }


    if effective_experience == "Any":

        score += 10


    else:


        terms = experience_words.get(

            effective_experience,

            []

        )


        if any(

            term in title
            or term in description

            for term in terms

        ):

            score += 10

            reasons.append(

                "The experience level appears compatible "
                "with your profile."

            )


        else:

            score += 3

            warnings.append(

                "The required experience level is not clearly confirmed."

            )


    # ========================================================
    # 5. JOB TYPE — 10
    # ========================================================

    if effective_job_type == "Any":

        score += 10


    else:


        job_type_terms = {

            "Full-time": [

                "full-time",
                "full time",
                "permanent"

            ],

            "Part-time": [

                "part-time",
                "part time"

            ],

            "Contract": [

                "contract",
                "contractor",
                "contract position"

            ]

        }


        terms = job_type_terms.get(

            effective_job_type,

            []

        )


        if any(

            term in title
            or term in description

            for term in terms

        ):

            score += 10

            reasons.append(

                "The job type matches your preference."

            )


        else:

            score += 2

            warnings.append(

                "The job type is not clearly confirmed."

            )


    # ========================================================
    # FINAL SCORE
    # ========================================================

    score = max(

        1,

        min(
            score,
            100
        )

    )


    explanation_parts = []


    if reasons:

        explanation_parts.extend(
            reasons[:4]
        )


    if warnings:

        explanation_parts.append(

            "⚠️ "
            +
            " ".join(
                warnings[:2]
            )

        )


    if not explanation_parts:

        explanation_parts.append(

            "This job was returned based on your search criteria."

        )


    return score, " ".join(
        explanation_parts
    )


# ============================================================
# PROFILE ROUTE
# ============================================================

@app.route(
    "/profile",
    methods=["POST"]
)
def save_profile():

    profile = {

        "name": request.form.get(
            "name",
            ""
        ).strip(),

        "target_job": request.form.get(
            "target_job",
            ""
        ).strip(),

        "country": request.form.get(
            "profile_country",
            "us"
        ),

        "location": request.form.get(
            "profile_location",
            ""
        ).strip(),

        "experience": request.form.get(
            "profile_experience",
            "Any"
        ),

        "job_type": request.form.get(
            "profile_job_type",
            "Any"
        ),

        "skills": request.form.get(
            "skills",
            ""
        ).strip(),

        "education": request.form.get(
            "education",
            ""
        ).strip()

    }


    session["profile"] = profile


    # Redirect back to homepage.
    from flask import redirect

    return redirect(
        "/?profile_saved=1#profile"
    )


# ============================================================
# HOME
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    jobs = []

    error = None

    success = None

    searched = False


    profile = get_profile()


    if request.args.get(
        "profile_saved"
    ):

        success = (
            "Your profile has been saved. "
            "AI Job Hunter will use it for matching."
        )


    search_data = {

        "job": "",

        "country": "us",

        "location": "",

        "experience": "Any",

        "job_type": "Any"

    }


    # ========================================================
    # SEARCH
    # ========================================================

    if request.method == "POST":


        searched = True


        search_job = request.form.get(
            "job",
            ""
        ).strip()


        country = request.form.get(
            "country",
            "us"
        )


        location = request.form.get(
            "location",
            ""
        ).strip()


        experience = request.form.get(
            "experience",
            "Any"
        )


        job_type = request.form.get(
            "job_type",
            "Any"
        )


        search_data = {

            "job": search_job,

            "country": country,

            "location": location,

            "experience": experience,

            "job_type": job_type

        }


        if not search_job:

            error = (
                "Please enter the job you are looking for."
            )


        elif not ADZUNA_APP_ID or not ADZUNA_APP_KEY:

            error = (
                "Adzuna API credentials are missing. "
                "Please check your .env file."
            )


        else:


            try:


                url = (

                    "https://api.adzuna.com/v1/api/jobs/"

                    +
                    country

                    +
                    "/search/1"

                )


                params = {

                    "app_id":
                        ADZUNA_APP_ID,

                    "app_key":
                        ADZUNA_APP_KEY,

                    "results_per_page":
                        10,

                    "what":
                        search_job,

                    "content-type":
                        "application/json"

                }


                if location:

                    params["where"] = location


                if job_type == "Full-time":

                    params["full_time"] = 1


                elif job_type == "Part-time":

                    params["part_time"] = 1


                elif job_type == "Contract":

                    params["contract"] = 1


                response = requests.get(

                    url,

                    params=params,

                    timeout=20

                )


                if response.status_code != 200:

                    error = (
                        f"Adzuna returned an error "
                        f"({response.status_code})."
                    )


                else:


                    data = response.json()


                    raw_jobs = data.get(
                        "results",
                        []
                    )


                    for item in raw_jobs:


                        title = item.get(
                            "title",
                            "Untitled Job"
                        )


                        company_data = item.get(
                            "company",
                            {}
                        )


                        if isinstance(
                            company_data,
                            dict
                        ):

                            company = (
                                company_data.get(
                                    "display_name",
                                    ""
                                )
                            )

                        else:

                            company = ""


                        location_data = item.get(
                            "location",
                            {}
                        )


                        if isinstance(
                            location_data,
                            dict
                        ):

                            job_location = (
                                location_data.get(
                                    "display_name",
                                    ""
                                )
                            )

                        else:

                            job_location = ""


                        salary_min = item.get(
                            "salary_min"
                        )


                        salary_max = item.get(
                            "salary_max"
                        )


                        if salary_min and salary_max:

                            salary = (

                                f"{salary_min:,.0f}"
                                " - "
                                f"{salary_max:,.0f}"

                            )


                        elif salary_min:

                            salary = (
                                "From "
                                f"{salary_min:,.0f}"
                            )


                        elif salary_max:

                            salary = (
                                "Up to "
                                f"{salary_max:,.0f}"
                            )


                        else:

                            salary = ""


                        description = item.get(
                            "description",
                            ""
                        )


                        if len(description) > 600:

                            description = (
                                description[:600]
                                + "..."
                            )


                        match_score, match_reason = (

                            calculate_match_score(

                                item,

                                search_job,

                                location,

                                experience,

                                job_type,

                                profile

                            )

                        )


                        jobs.append({

                            "title":
                                title,

                            "company":
                                company,

                            "location":
                                job_location,

                            "salary":
                                salary,

                            "description":
                                description,

                            "redirect_url":
                                item.get(
                                    "redirect_url",
                                    "#"
                                ),

                            "match_score":
                                match_score,

                            "match_reason":
                                match_reason

                        })


                    jobs.sort(

                        key=lambda job:
                            job["match_score"],

                        reverse=True

                    )


            except requests.exceptions.Timeout:

                error = (
                    "The job search timed out. "
                    "Please try again."
                )


            except requests.exceptions.RequestException:

                error = (
                    "Could not connect to the job service. "
                    "Please check your internet connection."
                )


            except Exception as e:

                error = (
                    "Something went wrong: "
                    +
                    str(e)
                )


    return render_template_string(

        HTML,

        jobs=jobs,

        countries=COUNTRIES,

        search_data=search_data,

        searched=searched,

        error=error,

        success=success,

        profile=profile

    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=True
)