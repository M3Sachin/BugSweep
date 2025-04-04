import os
import hmac
import hashlib
import requests
import google.generativeai as genai
import logging
import ast
import py_compile
from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, Request, Response
from github import Github, GithubIntegration
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from prompt_config import REVIEW_PROMPT_TEMPLATE

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Track processed commits
processed_commits: Dict[str, Dict[int, str]] = {}


# Configuration validation
class Config:
    REQUIRED_KEYS = {
        'GITHUB_APP_ID': int,
        'WEBHOOK_SECRET': str,
        'GEMINI_API_KEY': str,
        'MODEL_NAME': str
    }

    @classmethod
    def validate(cls):
        missing = []
        for key, key_type in cls.REQUIRED_KEYS.items():
            value = os.getenv(key)
            if not value:
                missing.append(key)
                continue
            try:
                if key_type == int:
                    int(value)
            except ValueError:
                raise ValueError(f"Invalid type for {key}, expected {key_type.__name__}")

        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


try:
    Config.validate()
except (EnvironmentError, ValueError) as e:
    logger.critical(f"Configuration error: {str(e)}")
    raise

# Constants
GITHUB_PRIVATE_KEY_PATH = Path("GithubPrivate.pem")
GITHUB_APP_ID = int(os.getenv('GITHUB_APP_ID'))
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')


# Load GitHub private key
def load_private_key() -> str:
    try:
        if not GITHUB_PRIVATE_KEY_PATH.exists():
            raise FileNotFoundError("Private key file not found")
        return GITHUB_PRIVATE_KEY_PATH.read_text()
    except Exception as e:
        logger.critical(f"Failed to load private key: {str(e)}")
        raise


GITHUB_PRIVATE_KEY = load_private_key()


# Initialize Gemini
def initialize_gemini() -> genai.GenerativeModel:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        logger.critical(f"Gemini initialization failed: {str(e)}")
        raise


model = initialize_gemini()

app = FastAPI(
    title="AI Code Reviewer",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)


def verify_webhook(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature.

    Args:
        payload: Raw request body bytes
        signature: X-Hub-Signature-256 header value

    Returns:
        bool: True if signature matches, False otherwise
    """
    try:
        key = WEBHOOK_SECRET.encode()
        expected = hmac.new(key, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)
    except Exception as e:
        logger.error(f"Webhook verification failed: {str(e)}")
        return False


async def generate_review(diff: str) -> Optional[str]:
    """Generate code review using Gemini API.

    Args:
        diff: Git diff string to analyze

    Returns:
        str: Generated review text or None on failure
    """
    try:
        logger.info("Generating code review...")
        response = model.generate_content(
            REVIEW_PROMPT_TEMPLATE.format(diff=diff),
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1000
            },
            request_options={"timeout": 15}
        )
        return response.text
    except Exception as e:
        logger.error(f"Review generation failed: {str(e)}")
        return None


def format_review_response(review_text: str) -> Optional[Dict]:
    """Format the review response with strict location-based deduplication.

    Args:
        review_text: Raw review text from Gemini

    Returns:
        dict: Formatted review comment structure or None on error
    """
    if not review_text:
        return None

    try:
        def extract_location(entry: str) -> Optional[Tuple[str, str]]:
            parts = entry.split(' - ', 1)
            if not parts or ':' not in parts[0]:
                return None
            file_line = parts[0].split(':', 1)
            return (file_line[0].strip(), file_line[1].split()[0].strip())

        suggestions = []
        issues = []
        summary = ""
        current_section = ""

        for line in review_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith("### "):
                current_section = line[4:].lower().strip()
            elif line.startswith("- "):
                entry = line[2:].strip()
                if current_section == "suggestions":
                    suggestions.append(entry)
                elif current_section == "issues":
                    issues.append(entry)
            elif current_section == "summary":
                summary += line + "\n"

        # Deduplication logic
        issue_locations = set()
        for issue in issues:
            if loc := extract_location(issue):
                issue_locations.add(loc)

        final_suggestions = [
            s for s in suggestions
            if (loc := extract_location(s)) and loc not in issue_locations
        ]

        comment_body = "🚀 **AI Code Review**\n\n"
        sections = []

        if summary.strip():
            sections.append(f"### Summary\n{summary.strip()}")

        if final_suggestions:
            sections.append("### Suggestions\n" + "\n".join(f"- {s}" for s in final_suggestions))

        if issues:
            sections.append("### Issues\n" + "\n".join(f"- {i}" for i in issues))

        comment_body += "\n\n".join(sections)

        if not final_suggestions and not issues:
            if summary.strip():
                return {"body": f"{comment_body}\n\nLGTM 👍 No issues found", "event": "APPROVE"}
            return {"body": "🚀 **AI Code Review**\n\nLGTM 👍 No issues found", "event": "APPROVE"}

        return {"body": comment_body.strip(), "event": "COMMENT"}

    except Exception as e:
        logger.error(f"Formatting failed: {str(e)}", exc_info=True)
        return None


def validate_python_syntax(content: str, filename: str) -> List[str]:
    """Validate Python 3.11+ syntax.

    Args:
        content: Python source code
        filename: Name of file being validated

    Returns:
        list: List of syntax issues
    """
    issues = []

    try:
        ast.parse(content, filename=filename, feature_version=(3, 11))
    except SyntaxError as e:
        issues.append(f"{filename}:{e.lineno} - SyntaxError: {e.msg} (Python 3.11+ validation)")

    try:
        with NamedTemporaryFile(mode='w', suffix=".py", delete=True, encoding='utf-8') as temp_file:
            temp_file.write(content)
            temp_file.flush()
            py_compile.compile(temp_file.name, doraise=True)
    except py_compile.PyCompileError as e:
        issues.append(f"{filename}:{e.lineno} - CompileError: {e.msg}")
    except Exception as e:
        logger.error(f"Syntax validation failed: {str(e)}")
        issues.append(f"{filename}:0 - ValidationError: Could not complete syntax check")

    return issues


async def process_pr_review(event: dict) -> bool:
    """Process a pull request review event.

    Args:
        event: GitHub webhook payload

    Returns:
        bool: True if review was posted successfully
    """
    try:
        pr_data = event["pull_request"]
        repo_name = event["repository"]["full_name"]
        pr_number = pr_data["number"]
        current_sha = pr_data["head"]["sha"]
        action = event.get("action")

        logger.info(f"Processing PR #{pr_number} in {repo_name} (SHA: {current_sha[:7]})")

        if current_sha == processed_commits.get(repo_name, {}).get(pr_number):
            logger.info("Already processed this commit, skipping")
            return False

        if action not in ["opened", "synchronize"]:
            logger.info("Ignoring non-PR-update event")
            return False

        # GitHub authentication
        integration = GithubIntegration(GITHUB_APP_ID, GITHUB_PRIVATE_KEY)
        access_token = integration.get_access_token(event["installation"]["id"]).token
        github = Github(access_token, timeout=15)
        repo = github.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        # Syntax validation
        syntax_issues = []
        for file in pr.get_files():
            if file.filename.endswith('.py') and Path(file.filename).name != "prompt_config.py":
                try:
                    content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()
                    syntax_issues += validate_python_syntax(content, file.filename)
                except Exception as e:
                    logger.error(f"Failed to check {file.filename}: {str(e)}")

        # Get PR diff
        try:
            diff_response = requests.get(pr.diff_url, timeout=10)
            diff_response.raise_for_status()
            diff = diff_response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch diff: {str(e)}")
            return False

        # Generate review
        review_text = await generate_review(diff)
        review_comment = format_review_response(review_text)

        # Combine results
        if syntax_issues:
            syntax_section = "### Syntax Validation Issues\n" + "\n".join(f"- {issue}" for issue in syntax_issues)

            if review_comment:
                review_comment["body"] = review_comment["body"].replace(
                    "🚀 **AI Code Review**\n\n",
                    f"🚀 **AI Code Review**\n\n{syntax_section}\n\n"
                )
            else:
                review_comment = {
                    "body": f"🚀 **AI Code Review**\n\n{syntax_section}",
                    "event": "COMMENT"
                }

        # Post review
        if review_comment:
            try:
                pr.create_review(**review_comment)
                logger.info(f"Posted review for commit {current_sha[:7]}")
                processed_commits.setdefault(repo_name, {})[pr_number] = current_sha
                return True
            except Exception as e:
                logger.error(f"Failed to post review: {str(e)}")
                return False

        return False

    except KeyError as e:
        logger.error(f"Missing key in event payload: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"PR processing failed: {str(e)}", exc_info=True)
        return False


@app.post("/webhook")
async def handle_webhook(request: Request):
    """Handle GitHub webhook events"""
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'self'"
    }

    try:
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")

        if not verify_webhook(body, signature):
            logger.warning("Invalid webhook signature")
            return Response(
                content="Invalid signature",
                status_code=401,
                headers=security_headers
            )

        event_type = request.headers.get("X-GitHub-Event")
        if event_type != "pull_request":
            logger.info(f"Ignoring non-PR event: {event_type}")
            return Response(
                content="Event type not supported",
                status_code=200,
                headers=security_headers
            )

        event = await request.json()
        success = await process_pr_review(event)

        return Response(
            content="Review posted" if success else "No review needed",
            status_code=200,
            headers=security_headers
        )

    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}", exc_info=True)
        return Response(
            content="Internal server error",
            status_code=500,
            headers=security_headers
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_config=None
    )
