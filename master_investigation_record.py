import os
import re
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

try:
    from bitcoin_address_validation import validate_bitcoin_address
except ImportError:  # pragma: no cover - module ships with this project
    validate_bitcoin_address = None


# --------------------------------------------------
# LOST BITCOIN - MASTER INVESTIGATION RECORD
# Database foundation
# --------------------------------------------------

DATABASE_PATH = Path(
    os.environ.get("LOST_BITCOIN_DB", Path(__file__).with_name("lost_bitcoin.db"))
)


def set_database_path(path):
    """Point the module at a different database file (used by tests)."""
    global DATABASE_PATH
    DATABASE_PATH = Path(path)


def get_timestamp():
    """Return the current time in UTC."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


_WORD_RUN = re.compile(r"(?:\b[a-z]{3,8}\b[ ,]+){11,}\b[a-z]{3,8}\b")
_WIF_KEY = re.compile(r"^[5KL][1-9A-HJ-NP-Za-km-z]{50,51}$")


def contains_sensitive_secret(text):
    """
    Heuristic guard: ordinary answers must never contain a seed phrase
    or a private key. We refuse to store them rather than save a
    customer's keys in a general-purpose answer field.
    (12+ consecutive short lowercase words, or a WIF-format key.)
    """
    if not isinstance(text, str):
        return False
    stripped = text.strip()
    if _WIF_KEY.match(stripped):
        return True
    lowered = stripped.lower()
    words = lowered.split()
    return len(words) >= 12 and bool(_WORD_RUN.search(lowered))


def _require_investigation(cursor, investigation_id):
    cursor.execute(
        "SELECT 1 FROM investigations WHERE investigation_id = ?",
        (investigation_id,),
    )
    if cursor.fetchone() is None:
        raise ValueError("Investigation not found.")


def connect_database():
    """Connect to the Lost Bitcoin database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def initialize_database():
    """Create the database tables if they do not exist."""

    connection = connect_database()

    connection.executescript("""

    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT COLLATE NOCASE UNIQUE,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS investigations (
        investigation_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        starting_point TEXT NOT NULL
            CHECK (starting_point IN ('lost_bitcoin', 'bitcoin_address')),
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (customer_id)
            REFERENCES customers(customer_id)
    );

    CREATE TABLE IF NOT EXISTS answers (
        answer_id TEXT PRIMARY KEY,
        investigation_id TEXT NOT NULL,
        question_key TEXT NOT NULL,
        answer_value TEXT,
        source TEXT NOT NULL DEFAULT 'customer',
        created_at TEXT NOT NULL,
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id)
    );

    CREATE TABLE IF NOT EXISTS bitcoin_addresses (
        address_id TEXT PRIMARY KEY,
        investigation_id TEXT NOT NULL,
        address TEXT NOT NULL,
        label TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id),
        UNIQUE (investigation_id, address)
    );

    CREATE TABLE IF NOT EXISTS discoveries (
        discovery_id TEXT PRIMARY KEY,
        investigation_id TEXT NOT NULL,
        description TEXT NOT NULL,
        source_type TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id)
    );

    CREATE TABLE IF NOT EXISTS evidence (
        evidence_id TEXT PRIMARY KEY,
        investigation_id TEXT NOT NULL,
        discovery_id TEXT,
        evidence_type TEXT NOT NULL,
        description TEXT NOT NULL,
        confidence TEXT NOT NULL DEFAULT 'unknown'
            CHECK (confidence IN (
                'confirmed',
                'strong_possibility',
                'possible_lead',
                'unknown'
            )),
        verification_status TEXT NOT NULL DEFAULT 'unverified',
        created_at TEXT NOT NULL,
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id),
        FOREIGN KEY (discovery_id)
            REFERENCES discoveries(discovery_id)
    );

    CREATE TABLE IF NOT EXISTS recommendations (
        recommendation_id TEXT PRIMARY KEY,
        investigation_id TEXT NOT NULL,
        title TEXT NOT NULL,
        details TEXT,
        priority TEXT NOT NULL DEFAULT 'medium',
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL,
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id)
    );

    CREATE TABLE IF NOT EXISTS timeline_events (
        event_id TEXT PRIMARY KEY,
        investigation_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        summary TEXT NOT NULL,
        details TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id)
    );

    CREATE TABLE IF NOT EXISTS reports (
        report_id TEXT PRIMARY KEY,
        investigation_id TEXT NOT NULL,
        report_type TEXT NOT NULL,
        file_path TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id)
    );

    CREATE TABLE IF NOT EXISTS purchases (
        purchase_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        investigation_id TEXT,
        product TEXT NOT NULL,
        amount_minor INTEGER NOT NULL,
        currency TEXT NOT NULL DEFAULT 'USD',
        status TEXT NOT NULL DEFAULT 'pending',
        payment_provider_reference TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (customer_id)
            REFERENCES customers(customer_id),
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id)
    );

    CREATE INDEX IF NOT EXISTS idx_investigations_customer
        ON investigations(customer_id);

    CREATE INDEX IF NOT EXISTS idx_answers_investigation
        ON answers(investigation_id);

    CREATE INDEX IF NOT EXISTS idx_events_investigation
        ON timeline_events(investigation_id);

    """)

    connection.commit()
    connection.close()

    print("Lost Bitcoin database initialized successfully.")
    print(f"Database location: {DATABASE_PATH}")


if __name__ == "__main__":
    initialize_database()


def create_customer(name, email, starting_point="lost_bitcoin"):
    """
    Create a customer and their first investigation.

    starting_point must be:
    - lost_bitcoin
    - bitcoin_address
    """

    if starting_point not in ("lost_bitcoin", "bitcoin_address"):
        raise ValueError("Invalid investigation starting point.")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("A customer name is required.")

    if not isinstance(email, str):
        raise ValueError("A valid email address is required.")

    email = email.strip().lower()

    email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    if not re.match(email_pattern, email):
        raise ValueError("Please provide a valid email address.")

    connection = connect_database()
    cursor = connection.cursor()

    try:
        timestamp = get_timestamp()

        # Check whether this customer already exists.
        # One active investigation per starting point per email: an email
        # may hold both a lost-Bitcoin investigation AND a Wallet Report
        # (bitcoin_address) investigation at the same time. Starting the
        # other flow must never silently swap the customer into the old
        # record of the first flow (that hijack is what stranded a paid
        # Wallet Report on an empty investigation page on 2026-11-14).
        customer = None

        if email:
            cursor.execute(
                "SELECT customer_id FROM customers WHERE email = ?",
                (email,)
            )
            customer = cursor.fetchone()

        if customer:
            customer_id = customer[0]
            cursor.execute("""
                SELECT investigation_id FROM investigations
                WHERE customer_id = ?
                  AND starting_point = ?
                  AND status = 'active'
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 1
            """, (customer_id, starting_point))
            if cursor.fetchone():
                raise ValueError(
                    "This email already has an account. "
                    "Please resume the existing investigation."
                )
            # Same customer, different starting point: start a fresh
            # investigation for them instead of reusing the old one.
        else:
            customer_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO customers (
                    customer_id, name, email, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                customer_id, name, email, timestamp, timestamp
            ))

        # Start a new investigation.
        investigation_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO investigations (
                investigation_id, customer_id, starting_point,
                status, created_at, updated_at
            )
            VALUES (?, ?, ?, 'active', ?, ?)
        """, (
            investigation_id, customer_id, starting_point,
            timestamp, timestamp
        ))

        # Record the start in the investigation timeline.
        cursor.execute("""
            INSERT INTO timeline_events (
                event_id, investigation_id, event_type,
                summary, details, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            investigation_id,
            "investigation_started",
            "Customer investigation created.",
            starting_point,
            timestamp
        ))

        connection.commit()

        return {
            "customer_id": customer_id,
            "investigation_id": investigation_id,
            "starting_point": starting_point
        }
    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def resume_customer_investigation(email, starting_point=None):
    """
    Find a customer's most recent active investigation.
    Does not create a new customer or investigation.

    When starting_point is given, only an investigation of that type is
    returned, so resuming the Wallet Report flow never lands the customer
    in their lost-Bitcoin investigation (or vice versa).
    """

    if not email:
        raise ValueError("An email address is required.")

    email = email.strip().lower()

    if starting_point is not None and starting_point not in ("lost_bitcoin", "bitcoin_address"):
        raise ValueError("Invalid investigation starting point.")

    connection = connect_database()
    cursor = connection.cursor()

    try:
        query = """
            SELECT
                customers.customer_id,
                customers.name,
                investigations.investigation_id,
                investigations.starting_point,
                investigations.status
            FROM customers
            JOIN investigations
                ON customers.customer_id = investigations.customer_id
            WHERE customers.email = ?
              AND investigations.status = 'active'
        """
        params = [email]
        if starting_point is not None:
            query += " AND investigations.starting_point = ?"
            params.append(starting_point)
        query += """
            ORDER BY investigations.updated_at DESC, investigations.created_at DESC
            LIMIT 1
        """
        cursor.execute(query, params)

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "customer_id": row[0],
            "name": row[1],
            "investigation_id": row[2],
            "starting_point": row[3],
            "status": row[4]
        }

    finally:
        connection.close()

def create_anonymous_investigation(starting_point="lost_bitcoin"):
    """
    Create an investigation with NO name or email attached.

    The investigation lives under an anonymous placeholder customer
    (a customers row whose name and email are NULL). That keeps the
    whole ownership model unchanged: the placeholder has a normal
    customer_id, so the signed-token machinery in app.py authorizes
    exactly this investigation and no one else's. The record is tied
    to a real person later by claim_investigation(); until then it
    must not be used for purchases (enforced in app.py).
    """

    if starting_point not in ("lost_bitcoin", "bitcoin_address"):
        raise ValueError("Invalid investigation starting point.")

    connection = connect_database()
    cursor = connection.cursor()

    try:
        timestamp = get_timestamp()
        customer_id = str(uuid.uuid4())
        investigation_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO customers (
                customer_id, name, email, created_at, updated_at
            )
            VALUES (?, NULL, NULL, ?, ?)
        """, (customer_id, timestamp, timestamp))

        cursor.execute("""
            INSERT INTO investigations (
                investigation_id, customer_id, starting_point,
                status, created_at, updated_at
            )
            VALUES (?, ?, ?, 'active', ?, ?)
        """, (
            investigation_id, customer_id, starting_point,
            timestamp, timestamp
        ))

        cursor.execute("""
            INSERT INTO timeline_events (
                event_id, investigation_id, event_type,
                summary, details, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            investigation_id,
            "investigation_started",
            "Anonymous investigation created (not yet saved to a customer).",
            starting_point,
            timestamp
        ))

        connection.commit()

        return {
            "customer_id": customer_id,
            "investigation_id": investigation_id,
            "starting_point": starting_point,
            "anonymous": True
        }
    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def is_anonymous_customer(customer_id):
    """True when the customer row is an anonymous placeholder (no email)."""

    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT email FROM customers WHERE customer_id = ?",
            (customer_id,)
        )
        row = cursor.fetchone()
        return row is not None and row[0] is None
    finally:
        connection.close()


def claim_investigation(investigation_id, name, email):
    """
    Tie an anonymous investigation to a real customer (the save step).

    Follows the same rules as create_customer / resume:
    - Email never seen before: the placeholder customer simply becomes
      the real customer (name/email set on the same row), so the
      investigation — and the token already issued for it — carry on.
    - Email exists but has no active investigation of this starting
      point: the claimed investigation is attached to that customer as
      its own record. The other flow's investigation is never touched
      (the 2026-11-14 record-hijack rule).
    - Email exists WITH an active investigation of the same starting
      point: resume semantics, exactly like /api/start — the existing
      investigation is returned with resumed=True and the anonymous
      record is left unclaimed. Nothing is merged or overwritten.
    """

    if not isinstance(name, str) or not name.strip():
        raise ValueError("A customer name is required.")

    if not isinstance(email, str):
        raise ValueError("A valid email address is required.")

    email = email.strip().lower()

    email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    if not re.match(email_pattern, email):
        raise ValueError("Please provide a valid email address.")

    name = name.strip()

    connection = connect_database()
    cursor = connection.cursor()

    try:
        _require_investigation(cursor, investigation_id)

        cursor.execute("""
            SELECT i.customer_id, i.starting_point, c.email
            FROM investigations i
            JOIN customers c ON c.customer_id = i.customer_id
            WHERE i.investigation_id = ?
        """, (investigation_id,))
        owner_id, starting_point, owner_email = cursor.fetchone()

        if owner_email is not None:
            raise ValueError(
                "This investigation is already saved to a customer.")

        timestamp = get_timestamp()

        cursor.execute(
            "SELECT customer_id FROM customers WHERE email = ?",
            (email,)
        )
        existing = cursor.fetchone()

        if existing is None:
            # Adopt the placeholder: same customer_id, now a real person.
            cursor.execute("""
                UPDATE customers
                SET name = ?, email = ?, updated_at = ?
                WHERE customer_id = ?
            """, (name, email, timestamp, owner_id))
            customer_id = owner_id
            resumed = False
        else:
            customer_id = existing[0]
            cursor.execute("""
                SELECT investigation_id FROM investigations
                WHERE customer_id = ?
                  AND starting_point = ?
                  AND status = 'active'
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 1
            """, (customer_id, starting_point))
            same_flow = cursor.fetchone()
            if same_flow:
                # Resume semantics: hand back the existing record; the
                # anonymous one stays unclaimed and untouched.
                connection.commit()
                return {
                    "customer_id": customer_id,
                    "investigation_id": same_flow[0],
                    "starting_point": starting_point,
                    "resumed": True
                }
            # Attach the claimed investigation to the real customer and
            # drop the now-empty placeholder row.
            cursor.execute("""
                UPDATE investigations
                SET customer_id = ?, updated_at = ?
                WHERE investigation_id = ?
            """, (customer_id, timestamp, investigation_id))
            cursor.execute(
                "DELETE FROM customers WHERE customer_id = ?",
                (owner_id,))
            resumed = False

        cursor.execute("""
            INSERT INTO timeline_events (
                event_id, investigation_id, event_type,
                summary, details, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            investigation_id,
            "investigation_claimed",
            "Investigation saved to the customer (name and email provided).",
            email,
            timestamp
        ))

        connection.commit()

        return {
            "customer_id": customer_id,
            "investigation_id": investigation_id,
            "starting_point": starting_point,
            "resumed": resumed
        }
    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_answer(investigation_id, question_key, answer_value, source="customer"):
    """
    Save an answer to an investigation.

    Every answer is stored as a new entry.
    Previous answers are never overwritten.
    """

    if not isinstance(question_key, str) or not question_key.strip():
        raise ValueError("A question key is required.")
    if answer_value is None:
        raise ValueError("An answer value is required.")
    if contains_sensitive_secret(str(answer_value)):
        raise ValueError(
            "This looks like a seed phrase or private key. "
            "Lost Bitcoin never asks for or stores those. "
            "Please remove it and keep it only with you."
        )

    connection = connect_database()
    cursor = connection.cursor()

    try:
        _require_investigation(cursor, investigation_id)
        timestamp = get_timestamp()
        answer_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO answers (
                answer_id,
                investigation_id,
                question_key,
                answer_value,
                source,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            answer_id,
            investigation_id,
            question_key,
            str(answer_value),
            source,
            timestamp
        ))

        cursor.execute("""
            UPDATE investigations
            SET updated_at = ?
            WHERE investigation_id = ?
        """, (timestamp, investigation_id))

        connection.commit()

        return answer_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_discovery(investigation_id, description, source_type="customer_statement"):
    """
    Save a new discovery to an investigation.

    Discoveries are appended and never overwrite previous findings.
    """

    if not isinstance(description, str) or not description.strip():
        raise ValueError("A discovery description is required.")

    connection = connect_database()
    cursor = connection.cursor()

    try:
        _require_investigation(cursor, investigation_id)
        timestamp = get_timestamp()
        discovery_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO discoveries (
                discovery_id,
                investigation_id,
                description,
                source_type,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            discovery_id,
            investigation_id,
            description,
            source_type,
            timestamp
        ))

        # Add the discovery to the investigation timeline.
        cursor.execute("""
            INSERT INTO timeline_events (
                event_id,
                investigation_id,
                event_type,
                summary,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            investigation_id,
            "discovery_recorded",
            "A new discovery was recorded.",
            description,
            timestamp
        ))

        cursor.execute("""
            UPDATE investigations
            SET updated_at = ?
            WHERE investigation_id = ?
        """, (timestamp, investigation_id))

        connection.commit()

        return discovery_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def save_evidence(
    investigation_id,
    evidence_type,
    description,
    confidence="unknown",
    discovery_id=None,
    verification_status="unverified"
):
    """
    Record evidence associated with an investigation.

    Evidence is never automatically treated as proof of ownership
    or proof that Bitcoin is recoverable.
    """

    allowed_confidence = (
        "confirmed",
        "strong_possibility",
        "possible_lead",
        "unknown"
    )

    if confidence not in allowed_confidence:
        raise ValueError("Invalid evidence confidence classification.")

    connection = connect_database()
    cursor = connection.cursor()

    try:
        _require_investigation(cursor, investigation_id)
        timestamp = get_timestamp()

        if discovery_id is not None:
            cursor.execute("""
                SELECT 1
                FROM discoveries
                WHERE discovery_id = ?
                  AND investigation_id = ?
            """, (discovery_id, investigation_id))

            if cursor.fetchone() is None:
                raise ValueError(
                    "The discovery does not belong to this investigation."
                )

        evidence_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO evidence (
                evidence_id,
                investigation_id,
                discovery_id,
                evidence_type,
                description,
                confidence,
                verification_status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evidence_id,
            investigation_id,
            discovery_id,
            evidence_type,
            description,
            confidence,
            verification_status,
            timestamp
        ))

        cursor.execute("""
            INSERT INTO timeline_events (
                event_id,
                investigation_id,
                event_type,
                summary,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            investigation_id,
            "evidence_recorded",
            "New evidence recorded: " + evidence_type,
            confidence + ": " + description,
            timestamp
        ))

        cursor.execute("""
            UPDATE investigations
            SET updated_at = ?
            WHERE investigation_id = ?
        """, (timestamp, investigation_id))

        connection.commit()

        return evidence_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_recommendation(
    investigation_id,
    title,
    details="",
    priority="medium"
):
    """
    Save a recommended next step for an investigation.
    """

    allowed_priorities = ("high", "medium", "low")

    if priority not in allowed_priorities:
        raise ValueError("Priority must be high, medium or low.")

    connection = connect_database()
    cursor = connection.cursor()

    try:
        timestamp = get_timestamp()

        cursor.execute("""
            SELECT 1
            FROM investigations
            WHERE investigation_id = ?
        """, (investigation_id,))

        if cursor.fetchone() is None:
            raise ValueError("Investigation not found.")

        recommendation_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO recommendations (
                recommendation_id,
                investigation_id,
                title,
                details,
                priority,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (
            recommendation_id,
            investigation_id,
            title,
            details,
            priority,
            timestamp
        ))

        cursor.execute("""
            INSERT INTO timeline_events (
                event_id,
                investigation_id,
                event_type,
                summary,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            investigation_id,
            "recommendation_created",
            "New recommendation: " + title,
            details,
            timestamp
        ))

        cursor.execute("""
            UPDATE investigations
            SET updated_at = ?
            WHERE investigation_id = ?
        """, (timestamp, investigation_id))

        connection.commit()

        return recommendation_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_investigation_history(investigation_id):
    """
    Retrieve the complete chronological timeline
    for a customer's investigation.
    """

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                event_type,
                summary,
                details,
                created_at
            FROM timeline_events
            WHERE investigation_id = ?
            ORDER BY created_at ASC, rowid ASC
        """, (investigation_id,))

        events = cursor.fetchall()

        history = []

        for event in events:
            history.append({
                "event_type": event[0],
                "summary": event[1],
                "details": event[2],
                "created_at": event[3]
            })

        return history

    finally:
        connection.close()


def print_investigation_history(investigation_id):
    """
    Display the investigation timeline in a readable format.
    """

    history = get_investigation_history(investigation_id)

    print("\n========================================")
    print("       LOST BITCOIN INVESTIGATION")
    print("========================================")

    if not history:
        print("No investigation history found.")
        return

    for event in history:
        print("\nDate:", event["created_at"])
        print("Event:", event["event_type"])
        print("Summary:", event["summary"])

        if event["details"]:
            print("Details:", event["details"])

    print("\n========================================")
    print("       END OF INVESTIGATION HISTORY")
    print("========================================")

def get_customer_record(customer_id):
    """
    Retrieve a customer and all their investigations.
    """

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                customer_id,
                name,
                email,
                created_at,
                updated_at
            FROM customers
            WHERE customer_id = ?
        """, (customer_id,))

        customer = cursor.fetchone()

        if not customer:
            return None

        cursor.execute("""
            SELECT
                investigation_id,
                starting_point,
                status,
                created_at,
                updated_at
            FROM investigations
            WHERE customer_id = ?
            ORDER BY created_at ASC
        """, (customer_id,))

        investigations = cursor.fetchall()

        return {
            "customer_id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "created_at": customer[3],
            "updated_at": customer[4],
            "investigations": [
                {
                    "investigation_id": item[0],
                    "starting_point": item[1],
                    "status": item[2],
                    "created_at": item[3],
                    "updated_at": item[4]
                }
                for item in investigations
            ]
        }

    finally:
        connection.close()


def print_customer_record(customer_id):
    """
    Display a readable customer record.
    """

    customer = get_customer_record(customer_id)

    if not customer:
        print("Customer not found.")
        return

    print("\n========================================")
    print("         LOST BITCOIN CUSTOMER")
    print("========================================")

    print("Name:", customer["name"])
    print("Email:", customer["email"])
    print("Customer ID:", customer["customer_id"])
    print("Created:", customer["created_at"])

    print("\nINVESTIGATIONS")

    for investigation in customer["investigations"]:
        print("\nInvestigation ID:", investigation["investigation_id"])
        print("Starting point:", investigation["starting_point"])
        print("Status:", investigation["status"])
        print("Created:", investigation["created_at"])

    print("\n========================================")

def save_bitcoin_address(investigation_id, address, label=""):
    """
    Save a Bitcoin address to an investigation.

    Addresses are stored as customer-supplied information.
    Saving an address does not establish ownership.
    """

    if not isinstance(address, str):
        raise ValueError("Bitcoin address must be text.")

    address = address.strip()

    if not address:
        raise ValueError("Bitcoin address cannot be empty.")

    if validate_bitcoin_address is not None:
        # Raises ValueError with a plain-English reason on bad
        # charset / length / checksum. Format only: this does not
        # prove ownership or that any Bitcoin is present.
        validate_bitcoin_address(address)

    if label is None:
        label = ""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        timestamp = get_timestamp()

        cursor.execute("""
            SELECT 1
            FROM investigations
            WHERE investigation_id = ?
        """, (investigation_id,))

        if cursor.fetchone() is None:
            raise ValueError("Investigation not found.")

        cursor.execute("""
            SELECT 1 FROM bitcoin_addresses
            WHERE investigation_id = ? AND address = ?
        """, (investigation_id, address))
        if cursor.fetchone() is not None:
            raise ValueError(
                "This address is already saved to this investigation."
            )

        address_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO bitcoin_addresses (
                address_id,
                investigation_id,
                address,
                label,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            address_id,
            investigation_id,
            address,
            label,
            timestamp
        ))

        cursor.execute("""
            INSERT INTO timeline_events (
                event_id,
                investigation_id,
                event_type,
                summary,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            investigation_id,
            "bitcoin_address_added",
            "A Bitcoin address was added.",
            "Label: " + label,
            timestamp
        ))

        cursor.execute("""
            UPDATE investigations
            SET updated_at = ?
            WHERE investigation_id = ?
        """, (timestamp, investigation_id))

        connection.commit()

        return address_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_bitcoin_addresses(investigation_id):
    """Retrieve all Bitcoin addresses for an investigation."""

    connection = connect_database()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT address_id, address, label, created_at
            FROM bitcoin_addresses
            WHERE investigation_id = ?
            ORDER BY created_at ASC
        """, (investigation_id,))

        return cursor.fetchall()

    finally:
        connection.close()

def save_report(investigation_id, report_type, file_path=""):
    """
    Record a report generated for an investigation.

    This tracks the report without storing sensitive
    customer information unnecessarily.
    """

    connection = connect_database()
    cursor = connection.cursor()

    try:
        _require_investigation(cursor, investigation_id)
        timestamp = get_timestamp()
        report_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO reports (
                report_id,
                investigation_id,
                report_type,
                file_path,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            report_id,
            investigation_id,
            report_type,
            file_path,
            timestamp
        ))

        cursor.execute("""
            INSERT INTO timeline_events (
                event_id,
                investigation_id,
                event_type,
                summary,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            investigation_id,
            "report_generated",
            "An investigation report was generated.",
            report_type,
            timestamp
        ))

        cursor.execute("""
            UPDATE investigations
            SET updated_at = ?
            WHERE investigation_id = ?
        """, (timestamp, investigation_id))

        connection.commit()

        return report_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def save_purchase(
    customer_id,
    product,
    amount_minor,
    investigation_id=None,
    currency="USD",
    status="pending",
    payment_provider_reference=None
):
    """
    Record a customer purchase.

    Amounts are stored in the smallest currency unit.
    Example: $9.99 USD = 999.
    
    Never store credit card numbers or security codes.
    """

    allowed_statuses = (
        "pending",
        "completed",
        "refunded",
        "failed"
    )

    if status not in allowed_statuses:
        raise ValueError("Invalid purchase status.")

    if not isinstance(amount_minor, int) or isinstance(amount_minor, bool) or amount_minor < 0:
        raise ValueError("Purchase amount must be a non-negative integer.")

    connection = connect_database()
    cursor = connection.cursor()

    try:
        timestamp = get_timestamp()

        cursor.execute(
            "SELECT 1 FROM customers WHERE customer_id = ?",
            (customer_id,),
        )
        if cursor.fetchone() is None:
            raise ValueError("Customer not found.")

        if payment_provider_reference:
            cursor.execute("""
                SELECT 1 FROM purchases
                WHERE payment_provider_reference = ?
            """, (payment_provider_reference,))
            if cursor.fetchone() is not None:
                raise ValueError(
                    "This payment has already been recorded. "
                    "Duplicate payment confirmations are ignored."
                )

        if investigation_id is not None:
            cursor.execute("""
                SELECT 1
                FROM investigations
                WHERE investigation_id = ?
                  AND customer_id = ?
            """, (investigation_id, customer_id))

            if cursor.fetchone() is None:
                raise ValueError(
                    "This investigation does not belong to this customer."
                )

        purchase_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO purchases (
                purchase_id,
                customer_id,
                investigation_id,
                product,
                amount_minor,
                currency,
                status,
                payment_provider_reference,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            purchase_id,
            customer_id,
            investigation_id,
            product,
            amount_minor,
            currency.upper(),
            status,
            payment_provider_reference,
            timestamp
        ))

        if investigation_id:
            cursor.execute("""
                INSERT INTO timeline_events (
                    event_id,
                    investigation_id,
                    event_type,
                    summary,
                    details,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                investigation_id,
                "purchase_recorded",
                "A purchase was recorded.",
                product + " - " + status,
                timestamp
            ))

        if investigation_id:
            cursor.execute("""
                UPDATE investigations
                SET updated_at = ?
                WHERE investigation_id = ?
            """, (timestamp, investigation_id))

        connection.commit()

        return purchase_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_complete_investigation(investigation_id):
    """
    Retrieve all information associated with an investigation.
    """

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                i.investigation_id,
                i.starting_point,
                i.status,
                i.created_at,
                c.customer_id,
                c.name,
                c.email
            FROM investigations i
            JOIN customers c
                ON i.customer_id = c.customer_id
            WHERE i.investigation_id = ?
        """, (investigation_id,))

        investigation = cursor.fetchone()

        if not investigation:
            return None

        record = {
            "investigation_id": investigation[0],
            "starting_point": investigation[1],
            "status": investigation[2],
            "created_at": investigation[3],
            "customer": {
                "customer_id": investigation[4],
                "name": investigation[5],
                "email": investigation[6]
            }
        }

        queries = {
            "answers": """
                SELECT question_key, answer_value, source, created_at
                FROM answers WHERE investigation_id = ?
                ORDER BY created_at
            """,
            "addresses": """
                SELECT address, label, created_at
                FROM bitcoin_addresses WHERE investigation_id = ?
                ORDER BY created_at
            """,
            "discoveries": """
                SELECT description, source_type, created_at
                FROM discoveries WHERE investigation_id = ?
                ORDER BY created_at
            """,
            "evidence": """
                SELECT evidence_type, description, confidence,
                       verification_status, created_at
                FROM evidence WHERE investigation_id = ?
                ORDER BY created_at
            """,
            "recommendations": """
                SELECT title, details, priority, status, created_at
                FROM recommendations WHERE investigation_id = ?
                ORDER BY created_at
            """,
            "timeline": """
                SELECT event_type, summary, details, created_at
                FROM timeline_events WHERE investigation_id = ?
                ORDER BY created_at, rowid
            """,
            "reports": """
                SELECT report_type, file_path, created_at
                FROM reports WHERE investigation_id = ?
                ORDER BY created_at
            """
        }

  
        for section, query in queries.items():
            cursor.execute(query, (investigation_id,))
            rows = cursor.fetchall()

            if section == "answers":
                record[section] = rows_to_dictionaries(
                    rows,
                    ["question_key", "answer_value", "source", "created_at"]
                )
            elif section == "addresses":
                record[section] = rows_to_dictionaries(
                    rows,
                    ["address", "label", "created_at"]
                )
            elif section == "discoveries":
                record[section] = rows_to_dictionaries(
                    rows,
                    ["description", "source_type", "created_at"]
                )
            elif section == "evidence":
                record[section] = rows_to_dictionaries(
                    rows,
                    ["evidence_type", "description", "confidence", "verification_status", "created_at"]
                )
            elif section == "recommendations":
                record[section] = rows_to_dictionaries(
                    rows,
                    ["title", "details", "priority", "status", "created_at"]
                )
            elif section == "timeline":
                record[section] = rows_to_dictionaries(
                    rows,
                    ["event_type", "summary", "details", "created_at"]
                )
            elif section == "reports":
                record[section] = rows_to_dictionaries(
                    rows,
                    ["report_type", "file_path", "created_at"]
                )
            else:
                record[section] = rows

        cursor.execute("""
            SELECT product, amount_minor, currency, status, created_at
            FROM purchases
            WHERE investigation_id = ?
            ORDER BY created_at
        """, (investigation_id,))

        record["purchases"] = rows_to_dictionaries(
            cursor.fetchall(),
            ["product", "amount_minor", "currency", "status", "created_at"]
        )

        return record

    finally:
        connection.close()


def print_complete_investigation(investigation_id):
    """Display the complete investigation record."""

    record = get_complete_investigation(investigation_id)

    if not record:
        print("Investigation not found.")
        return

    print("\n========================================")
    print("       COMPLETE INVESTIGATION")
    print("========================================")

    print("\nCUSTOMER")
    print("Name:", record["customer"]["name"])
    print("Email:", record["customer"]["email"])

    print("\nINVESTIGATION")
    print("ID:", record["investigation_id"])
    print("Starting point:", record["starting_point"])
    print("Status:", record["status"])

    for section in (
        "answers",
        "addresses",
        "discoveries",
        "evidence",
        "recommendations",
        "timeline",
        "reports",
        "purchases"
    ):
        print("\n" + section.upper())
        for item in record[section]:
            print(item)
        if not record[section]:
            print("No records found.")

    print("\n========================================")
def rows_to_dictionaries(rows, field_names):
    """
    Convert database rows into easy-to-read dictionaries.
    """

    return [
        dict(zip(field_names, row))
        for row in rows
    ]
