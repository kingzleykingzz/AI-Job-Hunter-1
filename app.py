from flask import (
    Flask,
    request,
    render_template_string,
    session,
    redirect,
    url_for
)

import requests
import os
import sqlite3
import re
from pathlib import Path
from werkzeug.utils import secure_filename

from dotenv import load_dotenv

from database import (
    init_database,
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_password
)


# ============================================================
# SETUP
# ============================================================

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-secret-key"
)

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


# ============================================================
# DATABASE
# ============================================================

init_database()


# ============================================================
# COUNTRIES
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
:root {
    --bg: #080d19;
    --panel: #101a2c;
    --panel2: #14223a;
    --border: #263650;
    --blue: #3987ff;
    --violet: #8665ff;
    --text: #f2f5fc;
    --muted: #93a2bb;
    --green: #35d49a;
}
* { box-sizing: border-box; }
html { min-height: 100%; }
body {
    margin: 0;
    min-height: 100vh;
    background: radial-gradient(ellipse at 85% 0%, #1a2850 0%, transparent 36%), var(--bg);
    color: var(--text);
    font-family: Inter, "Segoe UI", Arial, sans-serif;
    font-size: 15px;
    line-height: 1.6;
}
.container { width: min(1180px, 94%); margin: 0 auto; padding: 24px 0 56px; }
.header { padding: 30px 0 22px; }
.header h1 {
    margin: 0 0 8px; font-size: clamp(32px, 4vw, 46px); font-weight: 850;
    line-height: 1.15; letter-spacing: -1.5px;
    background: linear-gradient(100deg, #fff 12%, #8bb8ff 60%, #b5a2ff);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.header p { margin: 0; max-width: 680px; color: var(--muted); font-size: 16px; }
.nav {
    display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
    padding: 12px 14px; background: rgba(16,26,44,.92);
    border: 1px solid var(--border); border-radius: 15px;
    box-shadow: 0 12px 35px #0003;
}
.nav a { color: #dbe7ff; text-decoration: none; padding: 9px 13px; border-radius: 9px; font-weight: 650; transition: .2s ease; }
.nav a:hover { background: #233758; color: #fff; }
.plan-badge, .premium { display: inline-block; padding: 4px 9px; border-radius: 7px; font-size: 11px; font-weight: 800; letter-spacing: .6px; }
.pro-badge, .premium { color: #e5ddff; background: linear-gradient(100deg, #6245d7, #8a64ff); }
.free-badge { color: #c4d0e5; background: #27364d; }
.box, .auth-box, .plan, .job-card, .profile-info {
    background: linear-gradient(145deg, #121e32, #0d1627);
    border: 1px solid var(--border); border-radius: 18px;
    box-shadow: 0 12px 35px #0002;
}
.box { padding: clamp(18px, 3vw, 28px); margin: 18px 0 22px; }
.box h2, .auth-box h2 { margin: 0 0 18px; font-size: 23px; letter-spacing: -.4px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 19px; }
.field { display: flex; flex-direction: column; min-width: 0; }
.full { grid-column: 1 / -1; }
label { display: block; margin-bottom: 8px; color: #c9d6ed; font-weight: 650; }
input, select, textarea {
    width: 100%; min-height: 48px; padding: 12px 14px; color: var(--text);
    background: #091323; border: 1px solid #30415e; border-radius: 10px;
    outline: none; font: inherit; transition: border-color .2s, box-shadow .2s;
}
textarea { min-height: 100px; resize: vertical; }
input:focus, select:focus, textarea:focus { border-color: var(--blue); box-shadow: 0 0 0 3px #3987ff24; }
select option { background: #101a2c; color: white; }
.button-area { margin-top: 22px; }
button, .apply-button {
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    min-height: 46px; padding: 12px 20px; border: 0; border-radius: 10px;
    background: linear-gradient(100deg, var(--blue), var(--violet)); color: white;
    font: inherit; font-weight: 750; text-decoration: none; cursor: pointer;
    transition: transform .2s, filter .2s;
}
button { width: 100%; }
button:hover, .apply-button:hover { transform: translateY(-2px); filter: brightness(1.1); }
button:disabled { cursor: not-allowed; opacity: .75; transform: none; }
.auth-box { width: min(500px, 100%); margin: 24px auto; padding: clamp(20px, 4vw, 30px); }
.auth-box .field { margin-bottom: 17px; }
.auth-link { text-align: center; margin-top: 16px; color: var(--muted); }
.auth-link a { color: #82b3ff; }
.profile-info { padding: 22px; margin: 18px 0; color: #b6c4da; line-height: 1.7; }
.plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); gap: 18px; margin: 24px 0 4px; }
.plan { padding: 24px; transition: transform .2s, border-color .2s; }
.plan:hover { transform: translateY(-3px); border-color: #557ac0; }
.plan h3 { margin: 4px 0 10px; font-size: 22px; }
.plan p { color: var(--muted); font-size: 14px; }
.plan ul { padding-left: 21px; color: #c4d0e5; font-size: 14px; line-height: 1.9; }
.plan.pro { border-color: #7968e8; background: linear-gradient(145deg, #201b43, #11192d); }
.plan.vvip { border-color: #b99b4a; background: linear-gradient(145deg, #292315, #11192b 75%); }
.plan.vvip .premium { color: #fff0b8; background: linear-gradient(100deg, #92722c, #c5a95b); }
.success, .error { padding: 14px 17px; margin: 18px 0; border-radius: 11px; }
.success { color: #8af0c8; background: #12392f; border: 1px solid #226e55; }
.error { color: #ffb4bd; background: #3b1924; border: 1px solid #783343; overflow-wrap: anywhere; }
.job-card { padding: clamp(18px, 3vw, 24px); margin: 18px 0; transition: transform .2s, border-color .2s; }
.job-card:hover { transform: translateY(-2px); border-color: #4778c2; }
.job-title { margin: 0 0 8px; color: #f5f7ff; font-size: 21px; line-height: 1.35; font-weight: 750; overflow-wrap: anywhere; }
.company { color: #a8c5ff; margin-bottom: 6px; font-weight: 700; }
.location { color: #b7c5dc; margin-bottom: 6px; }
.salary { color: var(--green); margin: 10px 0 15px; font-weight: 750; }
.match-box { padding: 16px; margin: 18px 0; border: 1px solid #2c4163; border-radius: 12px; background: #0b1527; }
.match-top { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 10px; }
.match-score { color: #79aaff; font-size: 24px; font-weight: 850; }
.match-label { color: #c6d3e9; font-size: 13px; font-weight: 650; }
.progress { width: 100%; height: 8px; overflow: hidden; margin-bottom: 12px; background: #26344b; border-radius: 20px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, var(--blue), var(--violet)); border-radius: inherit; }
.match-reason, .description { color: #b7c4da; line-height: 1.7; }
.match-reason { font-size: 13px; }
.description { font-size: 14px; margin-bottom: 15px; }
.apply-button { width: auto; }
.locked-button { display: inline-flex; align-items: center; justify-content: center; min-height: 46px; padding: 11px 18px; border: 1px solid #4b5271; border-radius: 10px; background: #242941; color: #d4d9e9; text-decoration: none; font-weight: 700; }
.source { font-size: 11px; color: #8290a7; margin-top: 10px; }
.empty { padding: 30px 20px; text-align: center; color: var(--muted); background: #101a2c; border: 1px dashed #354663; border-radius: 15px; }
a { transition: color .2s; }
@media (max-width: 700px) {
    .container { width: 92%; padding-top: 14px; }
    .nav { gap: 4px; padding: 9px; }
    .nav a { padding: 8px 10px; font-size: 13px; }
    .header { padding: 23px 0 18px; }
    .form-grid { grid-template-columns: 1fr; gap: 15px; }
    .full { grid-column: auto; }
    .job-title { font-size: 19px; }
    .plans { grid-template-columns: 1fr; }
    .apply-button, .locked-button { max-width: 100%; }
}

/* Premium dashboard refinements */
.nav { position: sticky; top: 10px; z-index: 20; backdrop-filter: blur(16px); }
.nav a:first-child { background: linear-gradient(100deg, #1d4ed8, #6d5dfc); color: #fff; }
.nav .plan-badge { margin-left: auto; }
.box { position: relative; overflow: hidden; }
.box h2 { display: flex; align-items: center; gap: 10px; }
.section-kicker { color: #86aaff; font-size: 11px; font-weight: 800; letter-spacing: 1.6px; text-transform: uppercase; }
.dashboard-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 16px; margin: 18px 0 24px; }
.stat-card { padding: 20px; border-radius: 16px; border: 1px solid var(--border); background: linear-gradient(145deg, #14223a, #0d1627); }
.stat-card strong { display:block; font-size: 22px; margin: 5px 0; }
.stat-card span { color: var(--muted); font-size: 13px; }
.feature-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:18px; }
.feature-card { min-width:0; padding:20px; border:1px solid var(--border); border-radius:16px; background:linear-gradient(145deg,#14223a,#0d1627); }
.feature-icon { display:grid; place-items:center; width:42px; height:42px; border-radius:12px; margin-bottom:12px; background:#263b67; font-size:21px; }
.feature-card h3 { margin:0 0 7px; font-size:17px; }
.feature-card p { color:var(--muted); font-size:13px; }
.status-pill { display:inline-block; padding:4px 8px; border-radius:99px; color:#ffe8a3; background:#5b4820; font-size:10px; font-weight:800; letter-spacing:.5px; }
.form-note { color:var(--muted); font-size:12px; margin-top:5px; }
.auth-box { max-width:650px; }
.auth-box .form-grid { gap:15px; }
.plan { display:flex; flex-direction:column; }
.plan ul { flex:1; }
.plan .plan-action { margin-top:14px; }
.plan.vvip { box-shadow:0 0 0 1px #b99b4a22, 0 18px 50px #0003; }
.plan.vvip h3 { color:#ffe6a1; }
.plan .price { font-size:27px; font-weight:850; margin:10px 0; color:#fff; }
.plan .price small { font-size:12px; color:var(--muted); font-weight:500; }
.job-card { position:relative; }
.job-card:before { content:""; display:block; position:absolute; top:0; left:0; width:4px; height:100%; background:linear-gradient(var(--blue),var(--violet)); opacity:.85; }
input[type=checkbox] { width:auto; min-height:auto; accent-color:var(--blue); }
@media(max-width:850px){ .feature-grid{grid-template-columns:repeat(2,minmax(0,1fr));} .dashboard-grid{grid-template-columns:1fr;} }
@media(max-width:560px){ .feature-grid{grid-template-columns:1fr;} .nav .plan-badge{margin-left:0;} .auth-box .form-grid{grid-template-columns:1fr;} }


.community-layout{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(260px,1fr);gap:18px;align-items:start}
.community-card,.service-card,.video-card{padding:20px;margin:16px 0;background:linear-gradient(145deg,#121e32,#0d1627);border:1px solid var(--border);border-radius:16px;overflow-wrap:anywhere}
.post-form textarea{min-height:110px}.post-meta{display:flex;gap:8px;align-items:center;color:var(--muted);font-size:12px;margin-bottom:10px}.avatar{width:36px;height:36px;display:inline-grid;place-items:center;border-radius:50%;background:linear-gradient(130deg,var(--blue),var(--violet));color:white;font-weight:800}.profile-avatar{width:44px;height:44px;border-radius:50%;object-fit:cover;border:2px solid #39547d;background:#263b67}.service-owner{display:flex;align-items:center;gap:10px;margin:12px 0}.post-photo{display:block;max-width:100%;max-height:520px;object-fit:contain;border-radius:12px;margin:14px auto;background:#08101d}.community-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}.community-actions a{color:#a9c7ff;text-decoration:none}.service-grid,.video-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.service-card h3,.video-card h3{margin:0 0 8px}.service-category{display:inline-block;font-size:11px;color:#c9d7ff;background:#23365a;padding:4px 8px;border-radius:99px;margin-bottom:8px}.video-frame{width:100%;aspect-ratio:16/9;border:0;border-radius:12px;background:#060b14}.video-placeholder{display:grid;place-items:center;aspect-ratio:16/9;border-radius:12px;background:radial-gradient(circle at 50% 40%,#273f70,#0b1221 68%);font-size:42px;margin-bottom:12px}.muted{color:var(--muted)}
@media(max-width:760px){.community-layout,.service-grid,.video-grid{grid-template-columns:1fr}}

</style>

</head>


<body>


<div class="container">


<!-- ==========================================================
     NAV
     ========================================================== -->

<div class="nav">

    <a href="/">
        🔎 Job Search
    </a>


    {% if current_user %}

        <a href="/profile">
            👤 My Profile
        </a>

        <a href="/plans">
            ⭐ Plans
        </a>

        <a href="/vvip">
            👑 VVIP Suite
        </a>
        <a href="/community">🌐 Community</a>
        <a href="/services">🛍 Services</a>
        <a href="/academy">🎬 Video Hub</a>

        <a href="/logout">
            Logout
        </a>


        {% if current_user["plan"] == "pro" %}

            <span class="plan-badge pro-badge">
                PRO
            </span>

        {% else %}

            <span class="plan-badge free-badge">
                FREE
            </span>

        {% endif %}


    {% else %}

        <a href="/login">
            Login
        </a>

        <a href="/register">
            Create Account
        </a>
        <a href="/community">🌐 Community</a>
        <a href="/services">🛍 Services</a>
        <a href="/academy">🎬 Video Hub</a>

    {% endif %}

</div>


<!-- ==========================================================
     MESSAGES
     ========================================================== -->

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
     MAIN HEADER
     ========================================================== -->

<div class="header">

    <h1>
        AI Job Hunter
    </h1>

    <p>
        Find real jobs and discover how well they match you.
    </p>

</div>


{% if page == "home" %}


<!-- ==========================================================
     SEARCH
     ========================================================== -->

<div class="box">

    <h2>
        🔎 Find Jobs
    </h2>


    <form method="POST">


        <div class="form-grid">


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


            <div class="field">

                <label>
                    Country / Market
                </label>

                <select name="country">

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

<h2>
    {{ jobs|length }} jobs found
</h2>


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


    <div class="description">

        {{ job.description }}

    </div>


    <!-- ======================================================
         PRO-ONLY APPLY
         ====================================================== -->

    {% if current_user and current_user["plan"] == "pro" %}


        <a
            class="apply-button"
            href="/apply?url={{ job.redirect_url|urlencode }}"
        >

            Apply for Job

        </a>


    {% else %}


        <a
            class="locked-button"
            href="/plans"
        >

            🔒 Apply — Pro Required

        </a>


    {% endif %}


    <div class="source">

        Job listing provided through Adzuna.

    </div>


</div>


{% endfor %}


{% if not jobs %}

<div class="empty">

    No jobs were found.

</div>

{% endif %}


{% endif %}


{% elif page == "login" %}


<!-- ==========================================================
     LOGIN
     ========================================================== -->

<div class="box auth-box">

    <h2>
        🔐 Login
    </h2>


    <form method="POST">


        <div class="field">

            <label>
                Email
            </label>

            <input
                type="email"
                name="email"
                required
            >

        </div>


        <br>


        <div class="field">

            <label>
                Password
            </label>

            <input
                type="password"
                name="password"
                required
            >

        </div>


        <div class="button-area">

            <button type="submit">
                Login
            </button>

        </div>


    </form>


    <div class="auth-link">

        Don't have an account?

        <a href="/register">
            Create one
        </a>

    </div>

</div>


{% elif page == "register" %}

<div class="box auth-box">
    <div class="section-kicker">Start your next career move</div>
    <h2>✨ Create Your AI Job Hunter Account</h2>
    <p style="color:var(--muted);margin-top:-8px">Build your profile once so job matches can be more relevant.</p>
    <form method="POST">
        <div class="form-grid">
            <div class="field full"><label for="reg-name">Full name</label><input id="reg-name" type="text" name="name" placeholder="Your full name" autocomplete="name" required></div>
            <div class="field full"><label for="reg-email">Email address</label><input id="reg-email" type="email" name="email" placeholder="you@example.com" autocomplete="email" required></div>
            <div class="field"><label for="reg-password">Password</label><input id="reg-password" type="password" name="password" minlength="8" autocomplete="new-password" placeholder="At least 8 characters" required><span class="form-note">Use at least 8 characters.</span></div>
            <div class="field"><label for="reg-confirm">Confirm password</label><input id="reg-confirm" type="password" name="confirm_password" minlength="8" autocomplete="new-password" placeholder="Re-enter password" required></div>
            <div class="field"><label for="reg-country">Preferred country</label><select id="reg-country" name="country">{% for country_name, country_code in countries.items() %}<option value="{{ country_code }}" {% if country_code == 'us' %}selected{% endif %}>{{ country_name }}</option>{% endfor %}</select></div>
            <div class="field"><label for="reg-location">Preferred city / location</label><input id="reg-location" type="text" name="location" placeholder="e.g. Lagos, London, Remote"></div>
            <div class="field"><label for="reg-target">Target job title</label><input id="reg-target" type="text" name="target_job" placeholder="e.g. UGC Content Creator"></div>
            <div class="field"><label for="reg-experience">Experience level</label><select id="reg-experience" name="experience"><option>Any</option><option>Entry Level</option><option>Mid Level</option><option>Senior</option></select></div>
        </div>
        <div class="button-area"><button type="submit">Create Free Account →</button></div>
    </form>
    <div class="auth-link">Already have an account? <a href="/login">Login</a></div>
</div>

{% elif page == "profile" %}


<!-- ==========================================================
     PROFILE
     ========================================================== -->

<div class="box">

    <h2>
        👤 My Profile
    </h2>


    <div class="profile-info">

        Your profile helps AI Job Hunter personalize
        your job matching.

        <div class="service-owner">
            {% if profile.profile_image %}
                <img class="profile-avatar" src="{{ profile.profile_image }}" alt="Your profile photo">
            {% else %}
                <span class="avatar">{{ (profile.name or current_user.get('name') or 'M')[0]|upper }}</span>
            {% endif %}
            <div><strong>{{ profile.name or current_user.get('name') or 'Your profile' }}</strong><div class="muted">Your community identity</div></div>
        </div>
    </div>


    <form method="POST" enctype="multipart/form-data">>


        <div class="form-grid">


            <div class="field">

                <label>
                    Name
                </label>

                <input
                    type="text"
                    name="name"
                    value="{{ profile.name }}"
                >

            </div>


            <div class="field full">
                <label for="profile-photo">Profile picture</label>
                <input id="profile-photo" type="file" name="profile_image" accept="image/png,image/jpeg,image/webp,image/gif">
                <span class="form-note">PNG, JPG, WEBP or GIF, up to 5 MB.</span>
            </div>

            <div class="field">

                <label>
                    Target Job
                </label>

                <input
                    type="text"
                    name="target_job"
                    placeholder="Software Developer"
                    value="{{ profile.target_job }}"
                >

            </div>


            <div class="field">

                <label>
                    Country
                </label>

                <select name="country">

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


            <div class="field">

                <label>
                    City / Location
                </label>

                <input
                    type="text"
                    name="location"
                    value="{{ profile.location }}"
                >

            </div>


            <div class="field">

                <label>
                    Experience
                </label>

                <select name="experience">

                    {% for level in [
                        "Any",
                        "Entry Level",
                        "Mid Level",
                        "Senior"
                    ] %}

                    <option
                        value="{{ level }}"
                        {% if profile.experience == level %}
                            selected
                        {% endif %}
                    >

                        {{ level }}

                    </option>

                    {% endfor %}

                </select>

            </div>


            <div class="field">

                <label>
                    Job Type
                </label>

                <select name="job_type">

                    {% for type in [
                        "Any",
                        "Full-time",
                        "Part-time",
                        "Contract"
                    ] %}

                    <option
                        value="{{ type }}"
                        {% if profile.job_type == type %}
                            selected
                        {% endif %}
                    >

                        {{ type }}

                    </option>

                    {% endfor %}

                </select>

            </div>


            <div class="field full">

                <label>
                    Skills
                </label>

                <textarea
                    name="skills"
                    placeholder="Python, Flask, SQL, JavaScript, Git..."
                >{{ profile.skills }}</textarea>

            </div>


            <div class="field full">

                <label>
                    Education
                </label>

                <input
                    type="text"
                    name="education"
                    value="{{ profile.education }}"
                >

            </div>


        </div>


        <div class="button-area">

            <button type="submit">
                Save Profile
            </button>

        </div>


    </form>

</div>


{% elif page == "plans" %}


<!-- ==========================================================
     PLANS
     ========================================================== -->

<div class="box">

    <h2>
        ⭐ AI Job Hunter Plans
    </h2>


    <div class="plans">


        <div class="plan">

            <h3>
                Free
            </h3>

            <p>
                Start searching for jobs for free.
            </p>

            <ul>

                <li>Real job search</li>

                <li>Basic matching</li>

                <li>Basic profile</li>

                <li>Limited searches</li>

                <li>Apply locked</li>

            </ul>

        </div>


        <div class="plan pro">

            <span class="premium">
                PRO
            </span>

            <h3>
                AI Job Hunter Pro
            </h3>

            <p>
                Advanced tools for serious job seekers.
            </p>

            <ul>

                <li>Advanced job matching</li>

                <li>Unlimited searches</li>

                <li>Apply for jobs</li>

                <li>AI CV customization</li>

                <li>AI cover letters</li>

                <li>Interview preparation</li>

                <li>Job alerts</li>

                <li>Application tracking</li>

            </ul>


            {% if current_user and current_user["plan"] == "pro" %}

                <button disabled>
                    You are a Pro member
                </button>

            {% else %}

                <button disabled>
                    Payment Coming Next
                </button>

            {% endif %}


        </div>


        <div class="plan vvip">

            <span class="premium">VVIP · COMING SOON</span>

            <h3>AI Job Hunter VVIP</h3>

            <p>Designed for a more guided, premium job-search journey. These tools are planned and are not active yet.</p>

            <ul>
                <li>Personalized career strategy and role roadmap</li>
                <li>Role-specific CV and cover-letter studio</li>
                <li>Mock interview coach and answer practice</li>
                <li>Skill-gap planner and learning priorities</li>
                <li>International job-search planning</li>
            </ul>

            <button type="button" disabled>Coming Soon</button>

        </div>


    </div>

</div>

{% elif page == "vvip" %}

<div class="box">
    <div class="section-kicker">Premium career workspace</div>
    <h2>👑 VVIP Career Suite</h2>
    <p style="color:var(--muted);max-width:760px">A guided workspace planned for job seekers who want a more personal, structured route to their next role. These services are shown transparently as coming soon until their tools are connected.</p>
    <div class="dashboard-grid">
        <div class="stat-card"><span>CAREER DIRECTION</span><strong>Career Strategy</strong><span>Role targeting and a personalized job-search roadmap.</span></div>
        <div class="stat-card"><span>APPLICATION QUALITY</span><strong>CV & Cover Letters</strong><span>Role-specific document tailoring and improvement.</span></div>
        <div class="stat-card"><span>INTERVIEW READINESS</span><strong>Mock Interviews</strong><span>Practice questions, feedback, and preparation plans.</span></div>
    </div>
    <div class="feature-grid">
        <div class="feature-card"><div class="feature-icon">🎯</div><h3>Personal Career Strategy</h3><p>Set target roles, identify priorities, and build a focused job-search plan.</p><span class="status-pill">COMING SOON</span></div>
        <div class="feature-card"><div class="feature-icon">📄</div><h3>CV & Cover Letter Studio</h3><p>Plan role-specific CV edits and cover letters around each job description.</p><span class="status-pill">COMING SOON</span></div>
        <div class="feature-card"><div class="feature-icon">🎤</div><h3>Mock Interview Coach</h3><p>Practice interview questions and prepare stronger evidence-based answers.</p><span class="status-pill">COMING SOON</span></div>
        <div class="feature-card"><div class="feature-icon">🧭</div><h3>Skill-Gap Planner</h3><p>Compare target-role requirements with your profile and identify learning priorities.</p><span class="status-pill">COMING SOON</span></div>
        <div class="feature-card"><div class="feature-icon">🌍</div><h3>International Job Guidance</h3><p>Organize country preferences, role research, and application preparation.</p><span class="status-pill">COMING SOON</span></div>
        <div class="feature-card"><div class="feature-icon">📈</div><h3>Application Command Centre</h3><p>Planned tracking for applications, follow-ups, and interview stages.</p><span class="status-pill">COMING SOON</span></div>
    </div>
    <div class="button-area"><a class="apply-button" href="/profile">Complete My Career Profile</a> <a class="locked-button" href="/plans">View Membership Plans</a></div>
</div>

{% elif page == "community" %}
<div class="box">
  <div class="section-kicker">Career network</div><h2>🌐 Community Feed</h2>
  <p class="muted">Share career updates, portfolio work, useful advice, and wins. Be respectful and never post private information.</p>
  {% if current_user %}
  <div class="community-card post-form"><h3>Create a post</h3>
    <form method="POST" action="/community" enctype="multipart/form-data">
      <div class="field"><label for="post-body">What would you like to share?</label><textarea id="post-body" name="body" maxlength="2000" placeholder="Share an update, ask a career question, or show your work..." required></textarea></div>
      <div class="field" style="margin-top:12px"><label for="post-image">Add a picture (optional)</label><input id="post-image" type="file" name="image" accept="image/png,image/jpeg,image/webp,image/gif"></div>
      <div class="button-area"><button type="submit">Publish post</button></div>
    </form>
  </div>
  {% else %}<div class="community-card"><strong>Join the conversation</strong><p class="muted">Create a free account or log in to publish posts and pictures.</p><a class="apply-button" href="/register">Create account</a> <a class="locked-button" href="/login">Login</a></div>{% endif %}
  {% for post in posts %}
  <article class="community-card"><div class="post-meta">{% if post.author_image %}<img class="profile-avatar" src="{{ post.author_image }}" alt="{{ post.name }}">{% else %}<span class="avatar">{{ (post.name or 'M')[0]|upper }}</span>{% endif %}<div><strong>{{ post.name }}</strong><br><span>{{ post.created_at }}</span></div></div><div style="white-space:pre-wrap">{{ post.body }}</div>{% if post.image_path %}<img class="post-photo" src="{{ post.image_path }}" alt="Image shared by {{ post.name }}">{% endif %}</article>
  {% else %}<div class="empty">No community posts yet. Be the first to share a career update.</div>{% endfor %}
</div>

{% elif page == "services" %}
<div class="box"><div class="section-kicker">Member marketplace</div><h2>🛍 Services & Portfolios</h2><p class="muted">Discover services offered by community members, from design and video editing to CV support and marketing.</p>
{% if current_user %}<div class="community-card"><h3>List a service</h3><form method="POST" action="/services"><div class="form-grid"><div class="field"><label>Service title</label><input name="title" maxlength="100" placeholder="e.g. Short-form video editing" required></div><div class="field"><label>Category</label><select name="category"><option>Design</option><option>Video & Content</option><option>Writing & CV</option><option>Marketing</option><option>Technology</option><option>Career Coaching</option><option>Other</option></select></div><div class="field full"><label>Description</label><textarea name="description" maxlength="1200" placeholder="Describe what you offer, your experience, and deliverables." required></textarea></div><div class="field full"><label>Contact link (optional)</label><input name="contact" maxlength="300" placeholder="Portfolio, website, or professional contact URL"></div></div><div class="button-area"><button type="submit">Publish service</button></div></form></div>{% else %}<div class="community-card"><a class="apply-button" href="/register">Create an account to list your service</a></div>{% endif %}
<div class="service-grid">{% for service in services %}<article class="service-card"><span class="service-category">{{ service.category }}</span><h3>{{ service.title }}</h3><p>{{ service.description }}</p><div class="service-owner">{% if service.provider_image %}<img class="profile-avatar" src="{{ service.provider_image }}" alt="{{ service.name }}">{% else %}<span class="avatar">{{ (service.name or 'M')[0]|upper }}</span>{% endif %}<span class="muted">Offered by <strong>{{ service.name }}</strong></span></div>{% if service.contact and service.contact.startswith('https://') %}<a class="apply-button" href="{{ service.contact }}" target="_blank" rel="noopener noreferrer">View portfolio / contact</a>{% elif service.contact and service.contact.startswith('http://') %}<a class="apply-button" href="{{ service.contact }}" target="_blank" rel="noopener noreferrer">View portfolio / contact</a>{% endif %}</article>{% else %}<div class="empty">No services listed yet. Members can publish the first service.</div>{% endfor %}</div></div>

{% elif page == "academy" %}
 <div class="box"><div class="section-kicker">Learn and level up</div><h2>🎬 AI Job Hunter Video Hub</h2><p class="muted">Watch these short walkthroughs to learn about job search, AI matching, CVs, cover letters, and interview preparation.</p><div class="video-grid">
 <article class="video-card"><iframe class="video-frame" src="https://www.youtube-nocookie.com/embed/d_H-L5icg2U" title="Welcome to AI Job Hunter" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><h3>1. Welcome to AI Job Hunter</h3><p class="muted">An introduction to job search, matching, and your career workspace.</p><a class="apply-button" href="https://youtu.be/d_H-L5icg2U" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></article>
 <article class="video-card"><iframe class="video-frame" src="https://www.youtube-nocookie.com/embed/zXJ8KomjYWI" title="Find Jobs and Discover Opportunities" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><h3>2. Find Jobs &amp; Discover Opportunities</h3><p class="muted">Learn how to search, review match scores, and evaluate job listings.</p><a class="apply-button" href="https://youtu.be/zXJ8KomjYWI" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></article>
 <article class="video-card"><iframe class="video-frame" src="https://www.youtube-nocookie.com/embed/XVRrEXeIINU" title="VVIP Career Suite Overview" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><h3>3. VVIP Career Suite Overview</h3><p class="muted">Explore the planned premium career workspace and its proposed tools.</p><a class="apply-button" href="https://youtu.be/XVRrEXeIINU" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></article>
 <article class="video-card"><iframe class="video-frame" src="https://www.youtube-nocookie.com/embed/bksUXwoq6ys" title="How AI Matches Jobs" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><h3>4. How AI Matches Jobs</h3><p class="muted">Understand how job listings are assessed against role and profile details.</p><a class="apply-button" href="https://youtu.be/bksUXwoq6ys" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></article>
 <article class="video-card"><iframe class="video-frame" src="https://www.youtube-nocookie.com/embed/6VRswrV-ckQ" title="AI CV Builder" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><h3>5. AI CV Builder</h3><p class="muted">Practical guidance for building and tailoring a CV to a role.</p><a class="apply-button" href="https://youtu.be/6VRswrV-ckQ" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></article>
 <article class="video-card"><iframe class="video-frame" src="https://www.youtube-nocookie.com/embed/DvTUPodNlQs" title="AI Cover Letter Generator" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><h3>6. AI Cover Letter Generator</h3><p class="muted">Learn about creating a cover letter tailored to a job opportunity.</p><a class="apply-button" href="https://youtu.be/DvTUPodNlQs" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></article>
 <article class="video-card"><iframe class="video-frame" src="https://www.youtube-nocookie.com/embed/z6C9rUR_Xps" title="Interview Coach" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><h3>7. Interview Coach</h3><p class="muted">Prepare examples, practice answers, and build interview confidence.</p><a class="apply-button" href="https://youtu.be/z6C9rUR_Xps" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></article>
 </div><div class="button-area"><a class="apply-button" href="/vvip">Explore VVIP Career Suite</a> <a class="locked-button" href="/plans">View plans</a></div></div>

{% endif %}


</div>

</body>

</html>
"""


# ============================================================
# USER HELPER
# ============================================================

def get_current_user():
    """Return the logged-in user as a regular dict for templates."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = get_user_by_id(user_id)
    if user is None:
        return None
    try:
        return dict(user)
    except (TypeError, ValueError):
        return user


# ============================================================
# PROFILE HELPER
# ============================================================

def get_profile():

    profile = session.get(
        "profile"
    )

    if not profile:
        profile = DEFAULT_PROFILE.copy()
    else:
        profile = profile.copy()
    profile.update(get_community_profile(session.get("user_id")))
    return profile


# ============================================================
# MATCH SCORE
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


    job_location = job_location.lower()


    target_job = (
        profile.get("target_job")
        or search_job
    ).lower().strip()


    preferred_location = (
        profile.get("location")
        or search_location
    ).lower().strip()


    preferred_experience = (

        profile.get("experience")

        if experience == "Any"

        else experience

    )


    preferred_job_type = (

        profile.get("job_type")

        if job_type == "Any"

        else job_type

    )


    skills_text = (
        profile.get("skills", "")
        .lower()
    )


    score = 0

    reasons = []

    warnings = []


    # ========================================================
    # TITLE — 40
    # ========================================================

    words = [

        word

        for word in target_job.split()

        if len(word) > 2

    ]


    matches = [

        word

        for word in words

        if word in title

    ]


    if words:

        ratio = len(matches) / len(words)


        if ratio >= 0.75:

            score += 40

            reasons.append(
                "The job title strongly matches your target role."
            )

        elif ratio >= 0.5:

            score += 30

            reasons.append(
                "The job title partially matches your target role."
            )

        elif ratio > 0:

            score += 18

            reasons.append(
                "Some target-role terms match the title."
            )

        else:

            score += 5

            warnings.append(
                "The job title does not closely match your target role."
            )

    else:

        score += 20


    # ========================================================
    # SKILLS — 25
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


    requested_skills = [

        skill

        for skill in common_skills

        if skill in skills_text

    ]


    if requested_skills:

        matched_skills = [

            skill

            for skill in requested_skills

            if skill in title
            or skill in description

        ]


        ratio = (

            len(matched_skills)
            /
            len(requested_skills)

        )


        score += round(
            ratio * 25
        )


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


        missing = [

            skill

            for skill in requested_skills

            if skill not in matched_skills

        ]


        if missing:

            warnings.append(

                "Skills not clearly found: "
                +
                ", ".join(
                    missing[:4]
                )
                +
                "."

            )


    else:

        score += 10


    # ========================================================
    # LOCATION — 15
    # ========================================================

    if preferred_location:

        if preferred_location in job_location:

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
    # EXPERIENCE — 10
    # ========================================================

    experience_terms = {

        "Entry Level": [
            "entry level",
            "entry-level",
            "junior",
            "graduate",
            "trainee",
            "intern"
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


    if preferred_experience == "Any":

        score += 10

    else:

        terms = experience_terms.get(
            preferred_experience,
            []
        )


        if any(
            term in title
            or term in description
            for term in terms
        ):

            score += 10

            reasons.append(
                "The experience level appears compatible."
            )

        else:

            score += 3

            warnings.append(
                "The required experience level is not clearly confirmed."
            )


    # ========================================================
    # JOB TYPE — 10
    # ========================================================

    if preferred_job_type == "Any":

        score += 10

    else:

        type_terms = {

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
                "contractor"
            ]

        }


        terms = type_terms.get(
            preferred_job_type,
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


    score = max(
        1,
        min(score, 100)
    )


    explanation = []


    explanation.extend(
        reasons[:4]
    )


    if warnings:

        explanation.append(
            "⚠️ "
            +
            " ".join(
                warnings[:2]
            )
        )


    if not explanation:

        explanation.append(
            "This job matches your search criteria."
        )


    return score, " ".join(
        explanation
    )


# ============================================================
# COMMUNITY AND SERVICE MARKETPLACE STORAGE
# ============================================================

COMMUNITY_DB = os.getenv("COMMUNITY_DATABASE_PATH", "community.db")
UPLOAD_DIR = Path(app.root_path) / "static" / "community_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def community_connection():
    conn = sqlite3.connect(COMMUNITY_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_community_database():
    with community_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS community_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            body TEXT NOT NULL,
            image_path TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS community_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            contact TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS community_profiles (
            user_id INTEGER PRIMARY KEY,
            profile_image TEXT,
            bio TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")


init_community_database()


def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def display_name(user):
    if not user:
        return "Community member"
    try:
        name = user.get("name")
    except AttributeError:
        try:
            name = user["name"]
        except (KeyError, IndexError, TypeError):
            name = None
    return name or "Community member"


def current_user_id(user=None):
    user = user or get_current_user()
    if not user:
        return None
    try:
        user_id = user.get("id") or user.get("user_id")
    except AttributeError:
        try:
            user_id = user["id"]
        except (KeyError, IndexError, TypeError):
            user_id = None
    return user_id or session.get("user_id")


def get_community_profile(user_id):
    if not user_id:
        return {"profile_image": None, "bio": ""}
    with community_connection() as conn:
        row = conn.execute(
            "SELECT profile_image, bio FROM community_profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()
    return dict(row) if row else {"profile_image": None, "bio": ""}


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )
        confirm_password = request.form.get("confirm_password", "")
        country = request.form.get("country", "us")
        location = request.form.get("location", "").strip()
        target_job = request.form.get("target_job", "").strip()
        experience = request.form.get("experience", "Any")


        if not name or not email or not password or not confirm_password:

            return render_template_string(
                HTML,
                page="register",
                current_user=get_current_user(),
                countries=COUNTRIES,
                error="Please complete all fields.",
                success=None
            )


        if password != confirm_password:
            return render_template_string(
                HTML,
                page="register",
                current_user=get_current_user(),
                countries=COUNTRIES,
                error="Your passwords do not match.",
                success=None
            )

        if len(password) < 8:

            return render_template_string(
                HTML,
                page="register",
                current_user=get_current_user(),
                countries=COUNTRIES,
                error="Password must be at least 8 characters.",
                success=None
            )


        user_id = create_user(
            name,
            email,
            password
        )


        if user_id is None:

            return render_template_string(
                HTML,
                page="register",
                current_user=get_current_user(),
                countries=COUNTRIES,
                error="An account with that email already exists.",
                success=None
            )


        session["user_id"] = user_id
        session["profile"] = {
            "name": name,
            "target_job": target_job,
            "country": country if country in COUNTRIES.values() else "us",
            "location": location,
            "experience": experience if experience in ["Any", "Entry Level", "Mid Level", "Senior"] else "Any",
            "job_type": "Any",
            "skills": "",
            "education": ""
        }

        return redirect("/profile")


    return render_template_string(
        HTML,
        page="register",
        current_user=get_current_user(),
        countries=COUNTRIES,
        error=None,
        success=None
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        user = get_user_by_email(
            email
        )


        if not user:

            return render_template_string(
                HTML,
                page="login",
                current_user=None,
                countries=COUNTRIES,
                error="Invalid email or password.",
                success=None
            )


        if not verify_password(
            user["password"],
            password
        ):

            return render_template_string(
                HTML,
                page="login",
                current_user=None,
                countries=COUNTRIES,
                error="Invalid email or password.",
                success=None
            )


        session["user_id"] = user["id"]


        return redirect(
            "/"
        )


    return render_template_string(
        HTML,
        page="login",
        current_user=get_current_user(),
        countries=COUNTRIES,
        error=None,
        success=None
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ============================================================
# PROFILE
# ============================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    current_user = get_current_user()


    if not current_user:

        return redirect(
            "/login"
        )


    profile_data = get_profile()


    if request.method == "POST":

        uploaded_photo = request.files.get("profile_image")
        existing_community_profile = get_community_profile(current_user_id(current_user))
        profile_image = existing_community_profile.get("profile_image")

        if uploaded_photo and uploaded_photo.filename:
            if not allowed_image(uploaded_photo.filename):
                return render_template_string(
                    HTML, page="profile", current_user=current_user, countries=COUNTRIES,
                    profile=get_profile(), error="Please upload a PNG, JPG, WEBP, or GIF image.", success=None
                )
            import uuid
            ext = secure_filename(uploaded_photo.filename).rsplit(".", 1)[1].lower()
            safe_name = f"avatar_{uuid.uuid4().hex}.{ext}"
            uploaded_photo.save(UPLOAD_DIR / safe_name)
            profile_image = f"/static/community_uploads/{safe_name}"

        with community_connection() as conn:
            conn.execute(
                """INSERT INTO community_profiles (user_id, profile_image, bio, updated_at)
                   VALUES (?, ?, COALESCE((SELECT bio FROM community_profiles WHERE user_id = ?), ''), CURRENT_TIMESTAMP)
                   ON CONFLICT(user_id) DO UPDATE SET profile_image = excluded.profile_image, updated_at = CURRENT_TIMESTAMP""",
                (current_user_id(current_user), profile_image, current_user_id(current_user))
            )

        profile_data = {

            "name":
                request.form.get(
                    "name",
                    ""
                ).strip(),

            "target_job":
                request.form.get(
                    "target_job",
                    ""
                ).strip(),

            "country":
                request.form.get(
                    "country",
                    "us"
                ),

            "location":
                request.form.get(
                    "location",
                    ""
                ).strip(),

            "experience":
                request.form.get(
                    "experience",
                    "Any"
                ),

            "job_type":
                request.form.get(
                    "job_type",
                    "Any"
                ),

            "skills":
                request.form.get(
                    "skills",
                    ""
                ).strip(),

            "education":
                request.form.get(
                    "education",
                    ""
                ).strip()

        }


        profile_data["profile_image"] = profile_image
        session["profile"] = profile_data


        return render_template_string(
            HTML,
            page="profile",
            current_user=get_current_user(),
            countries=COUNTRIES,
            profile=profile_data,
            error=None,
            success="Your profile has been saved."
        )


    return render_template_string(
        HTML,
        page="profile",
        current_user=current_user,
        countries=COUNTRIES,
        profile=profile_data,
        error=None,
        success=None
    )


# ============================================================
# PLANS
# ============================================================

@app.route("/plans")
def plans():

    return render_template_string(
        HTML,
        page="plans",
        current_user=get_current_user(),
        countries=COUNTRIES,
        error=None,
        success=None
    )


# ============================================================
# VVIP CAREER SUITE
# ============================================================

@app.route("/vvip")
def vvip():
    return render_template_string(
        HTML,
        page="vvip",
        current_user=get_current_user(),
        countries=COUNTRIES,
        error=None,
        success=None
    )


# ============================================================
# COMMUNITY FEED
# ============================================================

@app.route("/community", methods=["GET", "POST"])
def community():
    current_user = get_current_user()
    if request.method == "POST":
        if not current_user:
            return redirect(url_for("login"))
        body = request.form.get("body", "").strip()
        if not body:
            return redirect(url_for("community"))
        if len(body) > 2000:
            body = body[:2000]
        image_path = None
        upload = request.files.get("image")
        if upload and upload.filename:
            if not allowed_image(upload.filename):
                return render_template_string(HTML, page="community", current_user=current_user, countries=COUNTRIES, posts=[], error="Please upload a PNG, JPG, WEBP, or GIF image.", success=None)
            filename = secure_filename(upload.filename)
            ext = filename.rsplit(".", 1)[1].lower()
            import uuid
            safe_name = f"post_{uuid.uuid4().hex}.{ext}"
            upload.save(UPLOAD_DIR / safe_name)
            image_path = f"/static/community_uploads/{safe_name}"
        with community_connection() as conn:
            conn.execute("INSERT INTO community_posts (user_id, name, body, image_path) VALUES (?, ?, ?, ?)", (current_user_id(current_user), display_name(current_user), body, image_path))
        return redirect(url_for("community"))
    with community_connection() as conn:
        posts = [dict(row) for row in conn.execute("""
            SELECT p.*, cp.profile_image AS author_image
            FROM community_posts p
            LEFT JOIN community_profiles cp ON cp.user_id = p.user_id
            ORDER BY p.id DESC LIMIT 100
        """).fetchall()]
    return render_template_string(HTML, page="community", current_user=current_user, countries=COUNTRIES, posts=posts, error=None, success=None)


# ============================================================
# SERVICES MARKETPLACE
# ============================================================

@app.route("/services", methods=["GET", "POST"])
def services():
    current_user = get_current_user()
    if request.method == "POST":
        if not current_user:
            return redirect(url_for("login"))
        title = request.form.get("title", "").strip()[:100]
        category = request.form.get("category", "Other").strip()[:60]
        description = request.form.get("description", "").strip()[:1200]
        contact = request.form.get("contact", "").strip()[:300]
        if title and description:
            if contact and not (contact.startswith("https://") or contact.startswith("http://")):
                contact = ""
            with community_connection() as conn:
                conn.execute("INSERT INTO community_services (user_id, name, title, category, description, contact) VALUES (?, ?, ?, ?, ?, ?)", (current_user_id(current_user), display_name(current_user), title, category, description, contact))
        return redirect(url_for("services"))
    with community_connection() as conn:
        services_list = [dict(row) for row in conn.execute("""
            SELECT s.*, cp.profile_image AS provider_image
            FROM community_services s
            LEFT JOIN community_profiles cp ON cp.user_id = s.user_id
            ORDER BY s.id DESC LIMIT 100
        """).fetchall()]
    return render_template_string(HTML, page="services", current_user=current_user, countries=COUNTRIES, services=services_list, error=None, success=None)


# ============================================================
# VIDEO HUB
# ============================================================

@app.route("/academy")
def academy():
    return render_template_string(HTML, page="academy", current_user=get_current_user(), countries=COUNTRIES, error=None, success=None)


# ============================================================
# PRO-ONLY APPLY ROUTE
# ============================================================

@app.route("/apply")
def apply():

    current_user = get_current_user()


    # --------------------------------------------------------
    # SERVER-SIDE SUBSCRIPTION CHECK
    # --------------------------------------------------------

    if not current_user:

        return redirect(
            "/login"
        )


    if current_user["plan"] != "pro":

        return redirect(
            "/plans"
        )


    job_url = request.args.get(
        "url",
        ""
    )


    if not job_url:

        return redirect("/")


    # --------------------------------------------------------
    # PRO USER CAN CONTINUE
    # --------------------------------------------------------

    return redirect(
        job_url
    )


# ============================================================
# HOME / JOB SEARCH
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    current_user = get_current_user()

    jobs = []

    error = None

    success = None

    searched = False


    search_data = {

        "job": "",

        "country": "us",

        "location": "",

        "experience": "Any",

        "job_type": "Any"

    }


    profile = get_profile()


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
                "Adzuna API credentials are missing."
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


                    for item in data.get(
                        "results",
                        []
                    ):


                        title = item.get(
                            "title",
                            "Untitled Job"
                        )


                        company_data = item.get(
                            "company",
                            {}
                        )


                        company = (

                            company_data.get(
                                "display_name",
                                ""
                            )

                            if isinstance(
                                company_data,
                                dict
                            )

                            else ""

                        )


                        location_data = item.get(
                            "location",
                            {}
                        )


                        job_location = (

                            location_data.get(
                                "display_name",
                                ""
                            )

                            if isinstance(
                                location_data,
                                dict
                            )

                            else ""

                        )


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


                        score, reason = (
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
                                    ""
                                ),

                            "match_score":
                                score,

                            "match_reason":
                                reason

                        })


                    jobs.sort(
                        key=lambda x:
                            x["match_score"],
                        reverse=True
                    )


            except requests.exceptions.Timeout:

                error = (
                    "The job search timed out."
                )


            except requests.exceptions.RequestException:

                error = (
                    "Could not connect to the job service."
                )


            except Exception as e:

                error = (
                    "Something went wrong: "
                    +
                    str(e)
                )


    return render_template_string(

        HTML,

        page="home",

        current_user=current_user,

        countries=COUNTRIES,

        jobs=jobs,

        searched=searched,

        search_data=search_data,

        error=error,

        success=success

    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),
        debug=True
    )