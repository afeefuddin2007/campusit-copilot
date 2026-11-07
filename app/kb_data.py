"""
Authentic Georgia State University (GSU) ServiceNow Knowledge Base Dataset.
Modeled directly on IT support workflows from https://gsutech.service-now.com/sp
"""

from typing import List, Dict, Any

GSU_KB_ARTICLES: List[Dict[str, Any]] = [
    {
        "kb_id": "KB0010101",
        "title": "Duo Multi-Factor Authentication (MFA): Reactivating Duo Mobile on a New Phone or Device",
        "category": "Authentication & Duo MFA",
        "url": "https://gsutech.service-now.com/sp?id=kb_article_view&sys_kb_id=KB0010101",
        "updated": "2026-09-15",
        "keywords": [
            "duo", "new phone", "upgrade phone", "reactivate", "2fa", "mfa",
            "push not working", "qr code", "new iphone", "new android", "passcode",
            "duo mobile", "authentication", "device management", "same phone number"
        ],
        "summary": "Step-by-step instructions for GSU students, faculty, and staff who replaced or factory-reset their smartphone and need to reactivate Duo Push via the GSU Duo Self-Service Portal.",
        "steps": [
            "1. Download and install the official 'Duo Mobile' app from the Apple App Store or Google Play Store on your new phone.",
            "2. On a laptop or desktop browser, navigate to the GSU Duo Device Management Portal (https://duo.gsu.edu) or log into PAWS (https://paws.gsu.edu) and click 'Other Options' -> 'Manage Devices' at the Duo prompt.",
            "3. Authenticate using an available backup method: choose 'Text message passcodes (SMS)' or 'Phone call' if you kept the same phone number, or enter an existing backup passcode.",
            "4. Once inside Manage Devices, find your phone number/device and click 'I have a new phone' (or 'Reactivate Duo Mobile').",
            "5. Follow the on-screen wizard to generate a fresh QR barcode, then open Duo Mobile on your new phone, tap 'Add (+)' -> 'Use QR code', and scan the screen.",
            "6. Test by clicking 'Send a Duo Push' to confirm your new device receives notifications immediately."
        ],
        "notes": "IMPORTANT: If you changed BOTH your phone AND your phone number and do not have a backup tablet or saved bypass codes, self-service reactivation will fail. You must contact the GSU IIT Technology Service Desk at 404-413-HELP (4357) or submit a request via https://gsutech.service-now.com/sp with photo ID verification."
    },
    {
        "kb_id": "KB0010204",
        "title": "CampusID Password Reset, Expiring Passwords, and Account Lockout Recovery",
        "category": "CampusID & Passwords",
        "url": "https://gsutech.service-now.com/sp?id=kb_article_view&sys_kb_id=KB0010204",
        "updated": "2026-09-20",
        "keywords": [
            "password", "reset password", "forgot password", "campusid", "campus id",
            "locked out", "account locked", "expired password", "change password",
            "mycampusid", "login failed", "invalid credentials", "passphrase"
        ],
        "summary": "How to reset a forgotten or expired GSU CampusID password using mycampusid.gsu.edu, password complexity rules, and resolving 30-minute automatic lockouts after failed attempts.",
        "steps": [
            "1. Go to the official GSU CampusID Self-Service Portal at https://mycampusid.gsu.edu.",
            "2. Select 'Forgot / Reset Password' (or 'Change Password' if you still know your current password).",
            "3. Enter your GSU CampusID (e.g., jsmith42 — do NOT include @student.gsu.edu) and verify your identity using Duo MFA or your registered recovery email/SMS.",
            "4. Create a new passphrase that meets GSU security standards: minimum 14 characters, including uppercase, lowercase, numbers, or special characters, and cannot contain your name or CampusID.",
            "5. Wait 5 to 10 minutes for password synchronization across PAWS, iCollege, PantherMail (Microsoft 365), and eduroam Wi-Fi.",
            "6. CRITICAL POST-RESET STEP: Immediately update your saved password in your phone/laptop Wi-Fi settings ('eduroam') and mail apps so background devices do not lock your account out again with old cached credentials."
        ],
        "notes": "After 5 consecutive failed login attempts, your CampusID triggers an automatic 30-minute security lockout. Waiting 30 minutes clears temporary lockouts automatically, or you can clear it immediately by completing a password reset at https://mycampusid.gsu.edu."
    },
    {
        "kb_id": "KB0010312",
        "title": "Connecting to eduroam Campus Wi-Fi & Fixing 'Unable to Join Network' Errors",
        "category": "Wi-Fi & Network Connectivity",
        "url": "https://gsutech.service-now.com/sp?id=kb_article_view&sys_kb_id=KB0010312",
        "updated": "2026-10-01",
        "keywords": [
            "wifi", "wi-fi", "eduroam", "wireless", "internet", "unable to join",
            "certificate", "radius.gsu.edu", "macbook wifi", "iphone wifi", "android wifi",
            "windows wifi", "peap", "mschapv2", "disconnecting", "gsu-guest"
        ],
        "summary": "Official configuration parameters for connecting laptops and mobile devices to the encrypted 'eduroam' wireless network at Georgia State University and fixing authentication loops after password changes.",
        "steps": [
            "1. Open your device Wi-Fi settings and select the network named 'eduroam' (do NOT use GSU-Guest if you are an active student or employee).",
            "2. When prompted for username, enter your CampusID followed by '@gsu.edu' (Example: jsmith42@gsu.edu — note: use @gsu.edu even for students on eduroam RADIUS authentication).",
            "3. Enter your current GSU CampusID password.",
            "4. If prompted to trust a security certificate, click 'Trust' or 'Accept' for 'radius.gsu.edu' (Issued by InCommon RSA Server CA).",
            "5. For Android / Linux / Chromebook users, configure EAP settings manually: EAP Method = PEAP, Phase 2 Authentication = MSCHAPv2, CA Certificate = 'Use system certificates' (or 'Do not validate' on legacy Android), Domain = 'gsu.edu', Identity = 'campusid@gsu.edu'.",
            "6. TROUBLESHOOTING ('Unable to Join eduroam'): If you recently changed your CampusID password, open Wi-Fi settings, click 'Forget This Network' on eduroam, toggle Wi-Fi OFF for 10 seconds, turn it back ON, and reconnect with your new password."
        ],
        "notes": "Smart TVs, gaming consoles (PlayStation, Xbox, Nintendo Switch), and streaming sticks in University Housing do not support WPA2-Enterprise (eduroam). Register their MAC address on the 'GSU-ResNet' / 'MyDevices' portal via https://gsutech.service-now.com/sp."
    },
    {
        "kb_id": "KB0010408",
        "title": "PantherMail (Microsoft 365 / Outlook) Login Issues, Email Format, and License Provisioning",
        "category": "Email & Microsoft 365",
        "url": "https://gsutech.service-now.com/sp?id=kb_article_view&sys_kb_id=KB0010408",
        "updated": "2026-09-28",
        "keywords": [
            "email", "panthermail", "outlook", "office 365", "microsoft 365", "student email",
            "can't sign into email", "mailbox not found", "word", "excel", "teams",
            "onedrive", "@student.gsu.edu", "email login", "authenticator"
        ],
        "summary": "Resolving PantherMail (Microsoft 365) sign-in errors, distinguishing between @student.gsu.edu and @gsu.edu login formats, and fixing Outlook mobile/desktop authentication loops.",
        "steps": [
            "1. Navigate to https://panthermail.gsu.edu or https://outlook.office.com.",
            "2. Enter your full official email login format: Students MUST sign in as 'campusid@student.gsu.edu' (e.g., jsmith42@student.gsu.edu). Faculty and staff sign in as 'campusid@gsu.edu'.",
            "3. You will be redirected to the Georgia State University Single Sign-On (SSO) page. Enter your CampusID password and approve the Duo MFA prompt.",
            "4. If Outlook displays 'Something went wrong / Mailbox not found': verify you are not signed into a personal @outlook.com or high school Microsoft account in the same browser. Open an Incognito/Private window and retry.",
            "5. For the Outlook Mobile App (iOS/Android): delete and re-add the account using 'Microsoft 365' (not IMAP/POP) and authenticate via the GSU Duo web pop-up."
        ],
        "notes": "Newly admitted students receive PantherMail access within 24–48 hours after activating their CampusID at mycampusid.gsu.edu. Alumni retain email access for 2 semesters post-graduation before account deprovisioning."
    },
    {
        "kb_id": "KB0010519",
        "title": "GSU Anywhere VPN (Cisco Secure Client) & Virtual Lab (VLab) Off-Campus Access",
        "category": "VPN & Remote Access",
        "url": "https://gsutech.service-now.com/sp?id=kb_article_view&sys_kb_id=KB0010519",
        "updated": "2026-08-30",
        "keywords": [
            "vpn", "cisco", "anyconnect", "secure client", "remote access", "vlab",
            "virtual lab", "off campus", "spss", "matlab", "arcgis", "banner",
            "vpn.gsu.edu", "connection failed"
        ],
        "summary": "How to install and connect to the GSU Anywhere VPN (vpn.gsu.edu) using Cisco Secure Client and access virtualized campus software via VLab (vlab.gsu.edu).",
        "steps": [
            "1. Open a browser and navigate to https://vpn.gsu.edu. Log in with your CampusID and password, then approve the Duo MFA push.",
            "2. Download and install the 'Cisco Secure Client' (formerly Cisco AnyConnect) for Windows or macOS.",
            "3. Launch Cisco Secure Client, enter 'vpn.gsu.edu' in the server address bar, and click 'Connect'.",
            "4. Select the appropriate group profile (usually 'GSU-Default' for general resources or 'GSU-FullTunnel' for restricted departmental servers).",
            "5. Enter your CampusID (without @gsu.edu) and password. Approve the automatic Duo Push sent to your phone within 60 seconds.",
            "6. To access virtual lab software (SPSS, SAS, MATLAB, AutoCAD) without VPN: visit https://vlab.gsu.edu, log in via GSU SSO, and launch apps through Citrix Workspace."
        ],
        "notes": "Note: PAWS, iCollege, and PantherMail do NOT require the VPN from off-campus. Only connect to vpn.gsu.edu when accessing restricted internal servers, library databases, or research shares."
    },
    {
        "kb_id": "KB0010602",
        "title": "iCollege (Brightspace) & PAWS Login Troubleshooting and Missing Course Visibility",
        "category": "iCollege & PAWS",
        "url": "https://gsutech.service-now.com/sp?id=kb_article_view&sys_kb_id=KB0010602",
        "updated": "2026-09-10",
        "keywords": [
            "icollege", "paws", "missing class", "course not showing", "brightspace",
            "registration", "cookie error", "bad request", "400 error", "saml",
            "sso loop", "grades", "transcript"
        ],
        "summary": "Resolving iCollege and PAWS Single Sign-On (SSO) redirect loops, HTTP 400 'Bad Request / Header Too Long' errors, and understanding why newly registered courses take up to 24 hours to appear.",
        "steps": [
            "1. Access iCollege directly at https://icollege.gsu.edu and PAWS at https://paws.gsu.edu.",
            "2. Fixing SSO Redirect Loops or 'HTTP 400 Bad Request': Clear your browser's cached cookies for '*.gsu.edu', ensure third-party cookies are enabled for Brightspace/Kaltura video embeds, or test in a fresh Chrome/Edge Incognito window.",
            "3. Missing Course in iCollege: If you just registered or added a class in PAWS/Banner, allow 24 hours (overnight automated roster sync) for your enrollment to populate in iCollege.",
            "4. Check Course Start Date: Courses remain hidden or unclickable in iCollege until 12:01 AM on the official first day of classes unless the instructor manually opens the syllabus early."
        ],
        "notes": "If it has been more than 24 hours since registering in PAWS and the semester has started, check PAWS to verify you do not have a Registration Hold or dropped status for non-payment."
    },
    {
        "kb_id": "KB0010715",
        "title": "Compromised Accounts, Phishing Reports, Lost MFA Devices & Mandatory Service Desk Escalation",
        "category": "Security & Escalation Policy",
        "url": "https://gsutech.service-now.com/sp?id=kb_article_view&sys_kb_id=KB0010715",
        "updated": "2026-10-10",
        "keywords": [
            "hacked", "compromised", "phishing", "scam", "stolen phone", "lost phone no backup",
            "changed phone number", "security hold", "administrative hold", "disabled account",
            "unauthorized login", "duo locked out", "bypass code", "verify identity"
        ],
        "summary": "Official GSU Information Security & Service Desk escalation protocol for incidents requiring human identity verification: lost MFA devices with changed numbers, suspected phishing/compromise, and administrative account holds.",
        "steps": [
            "1. DO NOT attempt repeated logins if your account shows 'Account Disabled by Administrator' or if you suspect unauthorized access.",
            "2. For Lost/Stolen Phones with NO Backup MFA Method (or a changed phone number): Automated bots cannot issue Duo bypass codes. Contact the GSU IIT Technology Service Desk immediately at 404-413-HELP (404-413-4357) for a live video/ID verification check and temporary Duo bypass code.",
            "3. For Suspected Phishing or Compromised Accounts: Forward suspicious emails to phishing@gsu.edu, immediately reset your CampusID password at https://mycampusid.gsu.edu if still accessible, and call 404-413-HELP so an analyst can revoke active session tokens.",
            "4. To Submit an Official ServiceNow Ticket Online: Go to https://gsutech.service-now.com/sp, click 'Get Help / Submit a Ticket', or visit the walk-in IIT Support Center (Library North 2nd Floor, Atlanta Campus, or any Perimeter College Learning & Tutoring Center)."
        ],
        "notes": "MANDATORY ESCALATION POLICY: Any issue involving identity verification, MFA hard-lockouts without backup devices, compromised credentials, Banner/Registrar holds, or hardware damage must be escalated to a live GSU Service Desk technician."
    }
]

def get_article_by_id(kb_id: str) -> Dict[str, Any] | None:
    for article in GSU_KB_ARTICLES:
        if article["kb_id"].upper() == kb_id.upper():
            return article
    return None
