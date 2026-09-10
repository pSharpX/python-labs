from guardrails import Guard, OnFailAction, settings
from guardrails_ai.detect_pii import DetectPII
from guardrails_ai.detect_jailbreak import DetectJailbreak
from guardrails_ai.detect_system_prompt_leakage import DetectSystemPromptLeakage
from guardrails_ai.regex_match import RegexMatch
from guardrails_ai.toxic_language import ToxicLanguage

settings.disable_tracing = True
settings.rc.enable_metrics = False

def validate_language(user_input: str):
    guard = Guard().use(
        ToxicLanguage(
            threshold=0.5,
            on_fail="exception"
        ),
    )
    guard.validate(user_input)

def validate_pii(user_input: str):
    guard = Guard().use(
        DetectPII(
            pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD"],
            on_fail="exception"
        )
    )
    guard.validate(user_input)

def validate_pattern(user_input: str):
    guard = Guard().use(
        RegexMatch,
        regex="\(?\d{3}\)?-? *\d{3}-? *-?\d{4}",
        on_fail=OnFailAction.EXCEPTION
    )
    guard.validate(user_input)

def validate_jailbreak(user_input: str):
    guard = Guard().use(
        DetectJailbreak,
        threshold=0.81,
        on_fail="exception"
    )
    guard.validate(user_input)

def validate_system_prompt_leakage(user_input: str):
    guard = Guard().use(DetectSystemPromptLeakage)
    guard.validate(user_input)
