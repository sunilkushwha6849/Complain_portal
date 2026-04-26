"""
GrievAI — Twilio SMS OTP Service
Mobile number verify karne ke liye
"""
import os
import random
import string
from datetime import datetime, timedelta
from twilio.rest import Client
from database import get_conn

TWILIO_SID   = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM  = os.environ.get('TWILIO_PHONE_NUMBER', '')

OTP_EXPIRY_MINUTES = 10


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def format_mobile(mobile: str) -> str:
    """Ensure mobile has country code — default India +91"""
    mobile = mobile.strip().replace(' ', '').replace('-', '')
    if mobile.startswith('0'):
        mobile = mobile[1:]
    if not mobile.startswith('+'):
        mobile = '+91' + mobile
    return mobile


def send_otp(mobile: str) -> dict:
    """
    Send OTP via Twilio SMS.
    Returns: {success, message, expires_in}
    """
    mobile = format_mobile(mobile)

    # Validate Indian mobile number
    if not mobile.startswith('+91') or len(mobile) != 13:
        return {"success": False, "error": "Invalid mobile number. Use 10-digit Indian number."}

    otp        = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    # Save OTP to DB
    conn = get_conn()
    cur  = conn.cursor()
    # Invalidate old OTPs for this number
    cur.execute("UPDATE otp_verifications SET verified=TRUE WHERE mobile=%s AND verified=FALSE", (mobile,))
    cur.execute("""
        INSERT INTO otp_verifications(mobile, otp, verified, expires_at)
        VALUES (%s, %s, FALSE, %s)
    """, (mobile, otp, expires_at))
    conn.commit()
    cur.close()
    conn.close()

    # Send via Twilio
    try:
        client  = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(
            body=f"GrievAI Portal - Madhya Pradesh Government\n\nYour OTP is: {otp}\n\nValid for {OTP_EXPIRY_MINUTES} minutes.\nDo not share this OTP with anyone.",
            from_=TWILIO_FROM,
            to=mobile
        )
        return {
            "success":    True,
            "message":    f"OTP sent to {mobile[-4:].rjust(10,'*')}",
            "expires_in": OTP_EXPIRY_MINUTES * 60,
            "sid":        message.sid,
        }
    except Exception as e:
        return {"success": False, "error": f"SMS failed: {str(e)}"}


def verify_otp(mobile: str, otp: str) -> dict:
    """
    Verify OTP entered by user.
    Returns: {success, verified, message}
    """
    mobile = format_mobile(mobile)
    otp    = otp.strip()

    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("""
        SELECT id, otp, expires_at, verified
        FROM otp_verifications
        WHERE mobile=%s AND verified=FALSE
        ORDER BY created_at DESC LIMIT 1
    """, (mobile,))
    row = cur.fetchone()

    if not row:
        cur.close(); conn.close()
        return {"success": False, "error": "OTP nahi mila ya expire ho gaya. Dobara bhejo."}

    otp_id, stored_otp, expires_at, already_verified = row

    if datetime.now() > expires_at:
        cur.close(); conn.close()
        return {"success": False, "error": f"OTP expire ho gaya. Dobara bhejo."}

    if otp != stored_otp:
        cur.close(); conn.close()
        return {"success": False, "error": "Galat OTP. Dobara check karein."}

    # Mark OTP as verified
    cur.execute("UPDATE otp_verifications SET verified=TRUE WHERE id=%s", (otp_id,))

    # Upsert citizen record
    cur.execute("""
        INSERT INTO citizens(mobile, verified)
        VALUES (%s, TRUE)
        ON CONFLICT(mobile) DO UPDATE SET verified=TRUE
    """, (mobile,))

    conn.commit()
    cur.close()
    conn.close()

    return {"success": True, "verified": True, "message": "Mobile number verified!"}


def is_mobile_verified(mobile: str) -> bool:
    """Check if mobile is already verified (skip OTP for repeat users)"""
    mobile = format_mobile(mobile)
    conn   = get_conn()
    cur    = conn.cursor()
    cur.execute("SELECT verified FROM citizens WHERE mobile=%s", (mobile,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return bool(row and row[0])
